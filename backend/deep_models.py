"""Small, trainable structural reproductions. No official pretrained checkpoints.
All preprocessing is fitted on train; validation selects weights; test is read-only.
The JSON artifact contains weights, preprocessing and architecture, never executable pickle.
"""
from __future__ import annotations
import copy
import math
import time
from collections import defaultdict
import numpy as np
try:
    import torch
except ImportError:
    # Development-only optional path; normal installation uses requirements.txt.
    import sys
    from pathlib import Path
    if Path('/tmp/task_torch/torch').exists():
        sys.path.insert(0, '/tmp/task_torch')
    import torch
from torch import nn

FEATURES = ['oil', 'liquid', 'water_cut', 'pressure', 'injection']


def _metrics(y, p):
    y, p = np.asarray(y, float), np.asarray(p, float)
    if not y.size:
        return {'evaluated_values': 0}
    d = y-p
    return {'MAE': float(np.abs(d).mean()), 'RMSE': float(np.sqrt((d*d).mean())), 'evaluated_values': int(y.size)}


def _artifact(model, **data):
    return {'format': 'geotwin-json-weights-v1', 'official_pretrained': False,
            'weights': {k: v.detach().cpu().tolist() for k, v in model.state_dict().items()}, **data}


def _labels_metrics(labels, scores, threshold):
    labels = np.asarray(labels, int); scores = np.asarray(scores, float)
    p = scores >= threshold
    tp = int(np.sum(p & (labels == 1))); fp = int(np.sum(p & (labels == 0))); fn = int(np.sum(~p & (labels == 1)))
    precision = tp/max(1, tp+fp); recall = tp/max(1, tp+fn)
    out = {'precision': precision, 'recall': recall, 'F1': 2*precision*recall/max(1e-12, precision+recall), 'threshold': float(threshold)}
    if len(set(labels.tolist())) > 1:
        from sklearn.metrics import roc_auc_score
        out['ROC_AUC'] = float(roc_auc_score(labels, scores))
    return out


class RotatE(nn.Module):
    def __init__(self, n_entities, n_relations, dim=12):
        super().__init__(); self.entity = nn.Embedding(n_entities, dim*2); self.phase = nn.Embedding(n_relations, dim)
        nn.init.uniform_(self.entity.weight, -.2, .2); nn.init.uniform_(self.phase.weight, -math.pi, math.pi)
    def forward(self, triples):
        h, t, ph = self.entity(triples[..., 0]), self.entity(triples[..., 2]), self.phase(triples[..., 1])
        hr, hi = h.chunk(2, -1); tr, ti = t.chunk(2, -1)
        return 6-torch.sqrt((hr*ph.cos()-hi*ph.sin()-tr).square()+(hr*ph.sin()+hi*ph.cos()-ti).square()+1e-9).sum(-1)


def _rotate(train, validation, test, inputs, pars):
    if len(train) < 2: raise ValueError('RotatE训练至少需要2条三元组。')
    entities = sorted({str(r[k]) for r in train for k in ['head', 'tail']}); relations = sorted({str(r['relation']) for r in train})
    ei, ri = {v:i for i,v in enumerate(entities)}, {v:i for i,v in enumerate(relations)}
    def encode(rows):
        for r in rows:
            if str(r.get('head')) not in ei or str(r.get('tail')) not in ei or str(r.get('relation')) not in ri:
                raise ValueError('RotatE验证/测试实体与关系必须在训练集出现；请使用实体覆盖划分。')
        return torch.tensor([[ei[str(r['head'])], ri[str(r['relation'])], ei[str(r['tail'])]] for r in rows], dtype=torch.long).reshape(-1,3)
    tr, va, te = map(encode, [train, validation, test])
    validation_known = set(tuple(r) for rows in [tr,va] for r in rows.tolist())
    test_known = validation_known | set(tuple(r) for r in te.tolist())
    def evaluate(m, rows, known):
        ranks=[]
        with torch.no_grad():
            for triple in rows:
                h,r,t=triple.tolist()
                for side in [0,2]:
                    candidates=triple.repeat(len(entities),1); candidates[:,side]=torch.arange(len(entities)); scores=m(candidates).numpy(); target=h if side==0 else t
                    for j in range(len(entities)):
                        if j!=target and tuple(candidates[j].tolist()) in known: scores[j]=-np.inf
                    ranks.append(1+int((scores>scores[target]).sum()))
        a=np.array(ranks,float)
        return {'filtered_MRR':float(np.mean(1/a)),'Hits@1':float(np.mean(a<=1)),'Hits@10':float(np.mean(a<=10)),'ranking_queries':len(a)} if len(a) else {}
    model=RotatE(len(entities),len(relations)); opt=torch.optim.Adam(model.parameters(),lr=.01); best=-1; saved=None; history=[]; started=time.perf_counter()
    for epoch in range(pars['epochs']):
        loss_sum=0
        for ids in torch.randperm(len(tr)).split(64):
            p=tr[ids]; neg=p[:,None,:].repeat(1,8,1); positions=torch.randint(0,len(entities),(len(p),8)); side=torch.rand(len(p),8)<.5
            neg[:,:,0]=torch.where(side,positions,neg[:,:,0]); neg[:,:,2]=torch.where(~side,positions,neg[:,:,2]); ns=model(neg)
            # Ignore known train positives rather than teaching a known relation to be false.
            train_set=set(tuple(v) for v in tr.tolist()); valid=torch.tensor([[tuple(v) not in train_set for v in row] for row in neg.tolist()])
            negative=(nn.functional.logsigmoid(-ns)*valid).sum()/valid.sum().clamp_min(1)
            loss=-(nn.functional.logsigmoid(model(p)).mean()+negative)/2; opt.zero_grad(); loss.backward(); opt.step(); loss_sum+=float(loss.detach())
        met=evaluate(model,va,validation_known); score=met.get('filtered_MRR',-loss_sum)
        history.append({'epoch':epoch+1,'loss':loss_sum,'validation':met})
        if score>best or saved is None: best=score; saved=copy.deepcopy(model.state_dict())
    model.load_state_dict(saved); training=time.perf_counter()-started; started=time.perf_counter(); results=[]
    with torch.no_grad():
        for r in inputs or test:
            h,rel=str(r.get('head')),str(r.get('relation'))
            if h not in ei or rel not in ri: raise ValueError('推理头实体/关系未在训练词表中出现。')
            if r.get('tail') is not None:
                t=str(r['tail'])
                if t not in ei: raise ValueError('推理尾实体未在训练词表中出现。')
                score=float(model(torch.tensor([[ei[h],ri[rel],ei[t]]]))[0]); results.append({**r,'score':score})
            else:
                ts=torch.tensor([[ei[h],ri[rel],i] for i in range(len(entities))]); scores=model(ts).numpy(); order=np.argsort(-scores)[:10]
                results.append({**r,'candidates':[{'tail':entities[i],'score':float(scores[i])} for i in order]})
    return {'results':results,'metrics':{'validation':evaluate(model,va,validation_known),'test':evaluate(model,te,test_known)},'training_seconds':training,'compute_seconds':time.perf_counter()-started,'history':history,'model_artifact':_artifact(model,entity_ids=entities,relation_ids=relations,dimensions=12),'limitations':['小规模RotatE从头训练；关系分数不证明水力连通或因果效应。','验证排名只过滤训练和验证已知三元组；最终测试排名才加入测试已知三元组。测试数据不影响验证选择或权重。']}


class SpanModel(nn.Module):
    def __init__(self, vocab_size, length=256):
        super().__init__(); self.embedding=nn.Embedding(vocab_size,32,padding_idx=0);self.position=nn.Embedding(length,32)
        self.transformer=nn.TransformerEncoder(nn.TransformerEncoderLayer(32,4,64,.1,batch_first=True),1,enable_nested_tensor=False);self.start=nn.Linear(32,1);self.end=nn.Linear(32,1)
    def forward(self,x,mask):
        z=self.embedding(x)+self.position(torch.arange(x.shape[1])[None]); z=self.transformer(z,src_key_padding_mask=x.eq(0));return self.start(z).squeeze(-1).masked_fill(~mask,-1e4), self.end(z).squeeze(-1).masked_fill(~mask,-1e4)


def _uie(train, validation, test, inputs, pars):
    if len(train)<2: raise ValueError('UIE训练至少需要2条带单个精确span的记录。')
    vocab={c:i+2 for i,c in enumerate(sorted(set(''.join(str(r['prompt'])+'\u241e'+str(r['content']) for r in train))))}; maximum=256
    def encode(rows, required=False):
        xs=[]; masks=[]; starts=[]; ends=[]; labeled=[]; offsets=[]
        for r in rows:
            prefix=str(r['prompt'])+'\u241e'; content=str(r['content']); full=prefix+content
            if not content or len(full)>maximum: raise ValueError('UIE的prompt＋分隔符＋content须为1至256个Unicode字符。')
            spans=r.get('spans',[])
            if isinstance(spans,str):
                import json
                spans=json.loads(spans)
            if required and len(spans)!=1: raise ValueError('精简UIE每个prompt训练样本必须有且仅有1个span；空答案需另扩展模型。')
            if len(spans)>1: raise ValueError('精简UIE每个prompt仅支持1个span。')
            if spans:
                s=spans[0]; a,b=int(s['start']),int(s['end'])
                if not (0<=a<b<=len(content)) or (s.get('text') is not None and s['text']!=content[a:b]): raise ValueError('UIE span采用Unicode字符下标[start,end)，须与原文text一致。')
                starts.append(len(prefix)+a);ends.append(len(prefix)+b-1);labeled.append(True)
            else: starts.append(0);ends.append(0);labeled.append(False)
            offsets.append(len(prefix));ids=[vocab.get(c,1) for c in full];xs.append(ids+[0]*(maximum-len(ids))); masks.append([False]*len(prefix)+[True]*len(content)+[False]*(maximum-len(full)))
        return torch.tensor(xs,dtype=torch.long).reshape(-1,maximum),torch.tensor(masks,dtype=torch.bool).reshape(-1,maximum),torch.tensor(starts),torch.tensor(ends),np.array(labeled),offsets
    tr=encode(train,True);va=encode(validation);te=encode(test)
    model=SpanModel(len(vocab)+2); opt=torch.optim.AdamW(model.parameters(),lr=.002);saved=None;best=math.inf;history=[];started=time.perf_counter()
    def evaluate(rows, encoded):
        if not rows:return {},[]
        x,mask,starts,ends,labeled,offs=encoded; preds=[];loss=[];correct=0
        model.eval()
        with torch.no_grad():
            for ids in torch.arange(len(rows)).split(32):
                a,b=model(x[ids],mask[ids]);si=a.argmax(-1).tolist();ei=b.argmax(-1).tolist()
                for j,idx in enumerate(ids.tolist()):
                    start=max(0,si[j]-offs[idx]); end=min(len(str(rows[idx]['content'])),max(start+1,ei[j]-offs[idx]+1)); is_match=labeled[idx] and si[j]==int(starts[idx]) and ei[j]==int(ends[idx]);correct+=int(is_match)
                    preds.append({'doc_id':rows[idx].get('doc_id'),'prompt':rows[idx]['prompt'],'content':rows[idx]['content'],'prediction':{'start':start,'end':end,'text':str(rows[idx]['content'])[start:end]},'exact_match':bool(is_match) if labeled[idx] else None})
                selected=[j for j,i in enumerate(ids.tolist()) if labeled[i]]
                if selected:
                    target=ids[selected]; loss.append(float(nn.functional.cross_entropy(a[selected],starts[target])+nn.functional.cross_entropy(b[selected],ends[target])))
        n=int(labeled.sum());return ({'exact_span_precision':correct/n,'exact_span_recall':correct/n,'exact_span_F1':correct/n,'labeled_samples':n,'cross_entropy':float(np.mean(loss))} if n else {'labeled_samples':0}),preds
    for epoch in range(pars['epochs']):
        model.train(); losses=[]
        for ids in torch.randperm(len(train)).split(32):
            a,b=model(tr[0][ids],tr[1][ids]); loss=nn.functional.cross_entropy(a,tr[2][ids])+nn.functional.cross_entropy(b,tr[3][ids]);opt.zero_grad();loss.backward();nn.utils.clip_grad_norm_(model.parameters(),2);opt.step();losses.append(float(loss.detach()))
        met,_=evaluate(validation,va);value=met.get('cross_entropy',float(np.mean(losses)));history.append({'epoch':epoch+1,'loss':float(np.mean(losses)),'validation':met})
        if value<best:saved=copy.deepcopy(model.state_dict());best=value
    model.load_state_dict(saved);training=time.perf_counter()-started;started=time.perf_counter();vm,_=evaluate(validation,va);tm,_=evaluate(test,te);_,results=evaluate(inputs or test,encode(inputs) if inputs else te)
    return {'results':results,'metrics':{'validation':vm,'test':tm},'training_seconds':training,'compute_seconds':time.perf_counter()-started,'history':history,'model_artifact':_artifact(model,vocab=vocab,max_length=maximum,architecture='character prompt → 1-layer Transformer(32,4heads) → start/end span heads'),'limitations':['UIE式小型结构复现，非官方UIE权重；每个prompt仅预测一个非空span。','训练字符词表只来自训练集，未见字符映射为UNK。','模板样本指标不能代表实际自由文本报告的抽取效果。']}


class GraphGRU(nn.Module):
    def __init__(self, adjacency, features=5):
        super().__init__(); self.register_buffer('adjacency',torch.tensor(adjacency,dtype=torch.float32));self.encode=nn.Linear(features*3+16,16);self.cell=nn.GRUCell(16,16);self.output=nn.Linear(32,features)
    def direction(self,x,visible,reverse=False):
        b,t,n,c=x.shape;h=x.new_zeros(b,n,16);previous=x.new_zeros(b,n,c);out=[]
        for j in (range(t-1,-1,-1) if reverse else range(t)):
            fill=torch.where(visible[:,j],x[:,j],previous);neighbors=torch.einsum('ij,bjc->bic',self.adjacency,fill);nh=torch.einsum('ij,bjh->bih',self.adjacency,h);z=torch.tanh(self.encode(torch.cat([fill,visible[:,j].float(),neighbors,nh],-1)));h=self.cell(z.reshape(-1,16),h.reshape(-1,16)).reshape(b,n,16);previous=self.output(torch.cat([h,nh],-1));out.append(previous)
        return torch.stack(out[::-1] if reverse else out,1)
    def forward(self,x,visible):return (self.direction(x,visible)+self.direction(x,visible,True))/2


def _finite_number(v):
    if v is None or v=='':return np.nan
    value=float(v)
    return value if math.isfinite(value) else np.nan


def _grin(train,validation,test,inputs,pars):
    wells=sorted({str(r['well_id']) for r in train}); wi={w:i for i,w in enumerate(wells)}
    def grid(rows):
        dates=sorted({str(r['date']) for r in rows}); di={v:i for i,v in enumerate(dates)};arr=np.full((len(dates),len(wells),5),np.nan);keys=set()
        for r in rows:
            w=str(r['well_id']);date=str(r['date'])
            if w not in wi:raise ValueError('GRIN需要同一井网络的时间划分；验证/测试井必须在训练网络出现。')
            if (w,date) in keys:raise ValueError('GRIN同一well_id/date不能重复。')
            keys.add((w,date));arr[di[date],wi[w]]=[_finite_number(r.get(f)) for f in FEATURES]
        return arr,dates
    arrays={};dates={}
    for sp,rows in [('train',train),('validation',validation),('test',test),('input',inputs)]:arrays[sp],dates[sp]=grid(rows)
    if len(arrays['train'])<2:raise ValueError('GRIN训练至少需要两个日期。')
    raw=arrays['train'];seen=np.isfinite(raw)
    count=seen.sum((0,1));mean=np.nansum(raw,(0,1))/np.maximum(count,1);var=np.nansum((raw-mean)**2,(0,1))/np.maximum(count,1);std=np.where(var>1e-8,np.sqrt(var),1)
    if not np.any(seen):raise ValueError('GRIN训练数据没有可用数值。')
    signal=np.nan_to_num((raw-mean)/std).mean(-1)
    if len(wells)>1:
        corr=np.corrcoef(signal.T);adj=np.nan_to_num(np.abs(corr),nan=0.)
    else:adj=np.ones((1,1))
    np.fill_diagonal(adj,1);adj/=adj.sum(1,keepdims=True);model=GraphGRU(adj);opt=torch.optim.Adam(model.parameters(),lr=.003);window=min(14,len(raw));rng=np.random.default_rng(pars['seed']);saved=None;best=math.inf;history=[];started=time.perf_counter()
    def windows(arr):
        return [(start,arr[start:start+window]) for start in range(0,len(arr),window)]
    def evaluate(arr,random_seed,return_all=False):
        model.eval();pred=np.zeros_like(arr);diffs=[];maskall=np.zeros_like(arr,dtype=bool);rg=np.random.default_rng(random_seed)
        with torch.no_grad():
            for start,chunk in windows(arr):
                y=(chunk-mean)/std;known=np.isfinite(y);hold=(rg.random(y.shape)<.2)&known
                if known.any() and not hold.any():hold[tuple(np.argwhere(known)[0])]=True
                vis=known&~hold; x=np.where(vis,y,0);out=model(torch.tensor(x[None],dtype=torch.float32),torch.tensor(vis[None]))[0].numpy();pred[start:start+len(chunk)]=out*std+mean;maskall[start:start+len(chunk)]=hold;diffs.extend((out-y)[hold].tolist())
        d=np.array(diffs);met={'normalized_MAE':float(np.abs(d).mean()),'normalized_RMSE':float(np.sqrt((d*d).mean())),'heldout_cells':len(d)} if len(d) else {'heldout_cells':0}
        # For user missing-value inference, rerun without deliberately hiding known values.
        if return_all:
            with torch.no_grad():
                for start,chunk in windows(arr):
                    y=(chunk-mean)/std;vis=np.isfinite(y);out=model(torch.tensor(np.nan_to_num(y)[None],dtype=torch.float32),torch.tensor(vis[None]))[0].numpy();pred[start:start+len(chunk)]=out*std+mean
        return met,pred,maskall
    for epoch in range(pars['epochs']):
        model.train();losses=[]
        for _,chunk in windows(raw):
            y=(chunk-mean)/std; known=np.isfinite(y);hide=(rng.random(y.shape)<.2)&known
            if not hide.any():
                if not known.any():continue
                hide[tuple(np.argwhere(known)[0])]=True
            vis=known&~hide;truth=torch.tensor(np.nan_to_num(y)[None],dtype=torch.float32);mask=torch.tensor(hide[None]);out=model(torch.tensor(np.where(vis,y,0)[None],dtype=torch.float32),torch.tensor(vis[None]));loss=(out-truth).square()[mask].mean();opt.zero_grad();loss.backward();nn.utils.clip_grad_norm_(model.parameters(),2);opt.step();losses.append(float(loss.detach()))
        vm,_,_=evaluate(arrays['validation'],pars['seed']+1);value=vm.get('normalized_RMSE',float(np.mean(losses)));history.append({'epoch':epoch+1,'loss':float(np.mean(losses)),'validation':vm})
        if value<best:saved=copy.deepcopy(model.state_dict());best=value
    model.load_state_dict(saved);training=time.perf_counter()-started;started=time.perf_counter();vm,_,_=evaluate(arrays['validation'],pars['seed']+1);tm,_,_=evaluate(arrays['test'],pars['seed']+2)
    source='input' if inputs else 'test';arr=arrays[source];_,pred,_=evaluate(arr,pars['seed']+3,True);results=[]
    for j,date in enumerate(dates[source]):
        for w,i in wi.items():
            row={'well_id':w,'date':date,'imputed_features':[]}
            for k,f in enumerate(FEATURES):
                observed=arr[j,i,k]; row[f]=float(observed) if np.isfinite(observed) else float(pred[j,i,k]);row[f+'_prediction']=float(pred[j,i,k])
                if not np.isfinite(observed):row['imputed_features'].append(f)
            row['requires_review']=any(row[f]<0 for f in row['imputed_features']) or ('water_cut' in row['imputed_features'] and row['water_cut']>1);results.append(row)
    return {'results':results,'metrics':{'validation':vm,'test':tm},'training_seconds':training,'compute_seconds':time.perf_counter()-started,'history':history,'model_artifact':_artifact(model,wells=wells,features=FEATURES,mean=mean.tolist(),std=std.tolist(),window=window,architecture='bidirectional mask-aware graph-message GRU(16)'),'limitations':['GRIN精简结构复现；邻接为训练期统计相关，非实测水力连通。','验证/测试MAE仅在固定随机遮蔽的已知观测上计算，真实天然缺失没有真值。','补全值不做强制非负裁剪，越界预测须人工复核。']}


class AssociationLayer(nn.Module):
    def __init__(self,dim=24,heads=2):
        super().__init__();self.heads=heads;self.d=dim//heads;self.qkv=nn.Linear(dim,dim*3);self.sigma=nn.Linear(dim,heads);self.proj=nn.Linear(dim,dim);self.norm=nn.LayerNorm(dim);self.ff=nn.Sequential(nn.Linear(dim,48),nn.GELU(),nn.Linear(48,dim));self.norm2=nn.LayerNorm(dim)
    def forward(self,x):
        b,l,d=x.shape;shape=lambda z:z.reshape(b,l,self.heads,self.d).transpose(1,2);q,k,v=map(shape,self.qkv(x).chunk(3,-1));series=(q@k.transpose(-1,-2)/math.sqrt(self.d)).softmax(-1);sigma=.5+self.sigma(x).sigmoid().transpose(1,2)[...,None]*l/3;distance=(torch.arange(l)[:,None]-torch.arange(l)[None,:]).square();prior=torch.exp(-distance[None,None]/(2*sigma.square()));prior=prior/prior.sum(-1,keepdim=True).clamp_min(1e-8);out=(series@v).transpose(1,2).reshape(b,l,d);z=self.norm(x+self.proj(out));return self.norm2(z+self.ff(z)),series,prior


class AnomalyNet(nn.Module):
    def __init__(self):
        super().__init__();self.embed=nn.Linear(5,24);self.position=nn.Embedding(32,24);self.layer=AssociationLayer();self.out=nn.Linear(24,5)
    def forward(self,x):
        z=self.embed(x)+self.position(torch.arange(x.shape[1])[None]);z,s,p=self.layer(z);return self.out(z),s,p


def _association(s,p):
    a=s.clamp_min(1e-8);b=p.clamp_min(1e-8);return ((a*(a.log()-b.log())).sum(-1)+(b*(b.log()-a.log())).sum(-1)).mean(1)


def _anomaly(train,validation,test,inputs,pars):
    def numeric(rows):return np.array([[_finite_number(r.get(f)) for f in FEATURES] for r in rows],dtype=float).reshape(-1,5)
    tr=numeric(train)
    if len(tr)<4:raise ValueError('Anomaly Transformer训练至少需要4条记录。')
    median=np.array([float(np.nanmedian(tr[:,j])) if np.isfinite(tr[:,j]).any() else 0. for j in range(5)]);filled=np.where(np.isfinite(tr),tr,median);mean=filled.mean(0);std=filled.std(0);std=np.where(std>1e-6,std,1)
    def chunks(rows):
        bywell=defaultdict(list)
        for i,r in enumerate(rows):bywell[str(r['well_id'])].append(i)
        chunks=[]
        for indices in bywell.values():
            indices.sort(key=lambda i:str(rows[i]['date']))
            for k in range(0,len(indices),32):
                ids=indices[k:k+32];x=numeric([rows[i] for i in ids]);chunks.append((ids,torch.tensor(((np.where(np.isfinite(x),x,median)-mean)/std)[None],dtype=torch.float32)))
        return chunks
    sets={sp:chunks(rows) for sp,rows in [('train',train),('validation',validation),('test',test),('input',inputs)]};model=AnomalyNet();opt=torch.optim.AdamW(model.parameters(),lr=.002);history=[];best=math.inf;saved=None;started=time.perf_counter()
    def score(sp):
        n=sum(len(ids) for ids,_ in sets[sp]);scores=np.zeros(n);preds=np.zeros((n,5));model.eval();rec=[]
        with torch.no_grad():
            for ids,x in sets[sp]:
                out,s,p=model(x);err=(out-x).square().mean(-1);disc=_association(s,p);energy=torch.softmax(-disc,-1)*err*x.shape[1];scores[ids]=energy[0].numpy();preds[ids]=out[0].numpy()*std+mean;rec.extend(err[0].tolist())
        return scores,preds,float(np.mean(rec)) if rec else None
    for epoch in range(pars['epochs']):
        model.train();losses=[]
        for _,x in sets['train']:
            out,s,p=model(x);reconstruction=(out-x).square().mean();prior_loss=_association(s.detach(),p).mean();series_loss=_association(s,p.detach()).mean();loss=reconstruction+.01*prior_loss-.01*series_loss;opt.zero_grad();loss.backward();nn.utils.clip_grad_norm_(model.parameters(),3);opt.step();losses.append(float(reconstruction.detach()))
        _,_,vm=score('validation');value=vm if vm is not None else float(np.mean(losses));history.append({'epoch':epoch+1,'train_reconstruction_MSE':float(np.mean(losses)),'validation_reconstruction_MSE':vm})
        if value<best:saved=copy.deepcopy(model.state_dict());best=value
    model.load_state_dict(saved);training=time.perf_counter()-started;started=time.perf_counter();train_scores,_,_=score('train');vs,_,vr=score('validation');ts,_,trr=score('test');threshold=float(np.quantile(train_scores,.95));selection='training_score_95th_percentile'
    def labels(rows):return [int(r.get('label',r.get('anomaly_label'))) for r in rows]
    def has_labels(rows):return bool(rows) and all(r.get('label',r.get('anomaly_label')) not in [None,''] for r in rows)
    if has_labels(validation):
        labs=labels(validation);candidates=np.unique(np.quantile(vs,np.linspace(0,1,41)));threshold=float(max(candidates,key=lambda t:_labels_metrics(labs,vs,t)['F1']));selection='validation_F1'
    metrics={}
    for name,rows,scores,rec in [('validation',validation,vs,vr),('test',test,ts,trr)]:
        metrics[name]={'reconstruction_MSE':rec,'samples':len(rows),'threshold':threshold}
        if has_labels(rows):metrics[name].update(_labels_metrics(labels(rows),scores,threshold))
        else:metrics[name]['label_status']='No complete labels: classification accuracy is not measurable.'
    source='input' if inputs else 'test';rows=inputs or test;scores,preds,_=score(source);results=[{**r,'anomaly_score':float(scores[i]),'anomaly_flag':bool(scores[i]>=threshold),'reconstruction':dict(zip(FEATURES,map(float,preds[i])))} for i,r in enumerate(rows)]
    return {'results':results,'metrics':metrics,'training_seconds':training,'compute_seconds':time.perf_counter()-started,'history':history,'model_artifact':_artifact(model,features=FEATURES,median=median.tolist(),mean=mean.tolist(),std=std.tolist(),threshold=threshold,threshold_selection=selection,window=32,architecture='1-layer association attention(24,2heads)+Gaussian prior+reconstruction'),'limitations':['Anomaly Transformer小型结构复现，非官方预训练权重。','无专家标签仅返回重建误差和异常分数，不虚构F1/ROC-AUC。','阈值仅由验证标签或训练分数选择；测试标签不用于调参。','按井和日期排序的记录窗口；不规则采样需先进行业务重采样。']}


def run_deep(model_id, train, validation, test, input_rows=None, parameters=None):
    parameters=dict(parameters or {});parameters['epochs']=int(parameters.get('epochs',6));parameters['seed']=int(parameters.get('seed',20261031))
    if not 1<=parameters['epochs']<=100:raise ValueError('epochs须在1至100之间。')
    if len(train)>10000:raise ValueError('精简CPU服务训练集上限为10000条；请分批或部署专用训练服务。')
    if not train:raise ValueError('需要训练集；当前服务每次请求从头训练并使用本次权重计算。')
    torch.set_num_threads(2);torch.manual_seed(parameters['seed']);np.random.seed(parameters['seed'])
    funcs={'rotate':_rotate,'uie':_uie,'grin':_grin,'anomaly_transformer':_anomaly}
    if model_id not in funcs:raise ValueError('未知深度模型。')
    return funcs[model_id](train,validation or [],test or [],input_rows or [],parameters)
