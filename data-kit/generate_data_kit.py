"""Reproducible upload-ready samples. No site uploads or credentials are read."""
from pathlib import Path
import csv, json, math, random, hashlib, zipfile, argparse, shutil, copy
from datetime import date,timedelta
SEED=20261031
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'dist/downloads/model-data'
rng=random.Random(SEED)

def readcsv(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_json(p,obj):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def write_records(p,rows,fmt='jsonl'):
 p.parent.mkdir(parents=True,exist_ok=True)
 if fmt=='jsonl':p.write_text('\n'.join(json.dumps(r,ensure_ascii=False,allow_nan=False) for r in rows)+'\n',encoding='utf-8')
 else:
  fields=list(dict.fromkeys(k for r in rows for k in r))
  with p.open('w',encoding='utf-8-sig',newline='') as f:
   w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def mapping(path):
 d=path.parts[0];n=path.name
 if d=='00_sources':
  if n.endswith('xlsx'):return 'grin;anomaly_transformer;arps;crm;lag;rules','公开原始生产观测','原始体积、压力、日期、井号','源文件；先经单位/停井/缺失检查再转成长表，不能直接当统一模型上传格式'
  return '全部模型（来源与许可）','来源/许可元数据','URL、许可、校验值','非训练样本，保留归属与许可'
 if d=='01_well_logs':
  if 'spike' in n:return 'isolation_forest;rules','公开观测＋人工注入异常/标签','GR、RHOB、DTC、spike标签','仅用于受控异常检测评价，不等于现场专家确认异常'
  if 'mask' in n:return 'grin（需按深度序列适配）；isolation_forest（质控）','公开观测＋人工遮蔽/目标','GR、RHOB、DTC、mask位置','目标值仅在测评中使用，禁止作为输入特征；现网页GRIN适配器使用生产时间序列'
  if n=='well_split.csv':return 'isolation_forest;grin','划分元数据','井号、split','按整井隔离，非训练特征'
  return 'isolation_forest;rules;entity_align;hierarchy','公开抽样观测','井号、深度、GR、RHOB、DTC、地层','部分测井为空；测试集不参与填补器/标准化拟合'
 if d=='02_production':return 'grin;anomaly_transformer;arps;crm;lag;rules','公开生产观测及派生特征','date、well_id、oil/water/injection、pressure、water_cut','NPZ是已构造张量，上传入口用转换后的CSV/JSONL；不同井/流动角色不能直接混合；CRM需注采日期对齐；Arps需稳定制度筛选'
 if d=='03_extraction':
  if 'retrieval' in n:return 'entity_align;语义检索（非训练神经向量模型）','表格事实转中文模板＋检索基准','doc_id、content、查询、相关性标注','非人工撰写油藏报告；qrels仅测评'
  return 'uie;entity_align','真实表格事实生成中文模板/实体跨度标注','doc_id、content、prompt、result_list/start/end','非原始报告人工标注；同doc_id全部prompt必须在同分区；模板化数据泛化有限'
 if d=='04_graph':
  if n.startswith('rotate_'):return 'rotate','公开井层事实构造三元组','head、relation、tail（TSV无表头）','使用三元组预划分；验证/测试端点须在训练词表；已知真关系只用于filtered测评'
  if n=='event_graph.json':return 'rules;历史异常检索','公开动态规则生成候选事件图','井、日期、模式、证据','候选异常非专家确诊，非因果标签'
  if n=='link_prediction_protocol.json':return 'rotate','评价协议','过滤排名与划分规则','非训练数据'
  return 'rotate;hierarchy;entity_align','公开数据构造关联图','节点、边、类型、来源','完整图包含验证/测试边，不能整图当训练集'
 if d=='05_simulation':return 'edfm（几何/参数参考）；未来Darcy代理模型','公开SPE算例/生成Darcy解','SPE网格/渗透率；NPZ压力/边界/残差','原SPE deck与Darcy NPZ不能直接当当前紧凑EDFM输入；必须转换单位和参数，Darcy不是EDFM多相真值'
 if d=='06_fractures':return 'dfn;edfm','公开裂缝几何基准（非现场观测）','裂缝端点、方向、长度/平面','缺少现场应力、开度、导流校准；需补充假设参数并明确生成'
 if d=='07_diagnosis':return 'rules;anomaly_transformer（辅助筛查）；lag','公开观测派生/规则生成候选','油量变化、含水变化、压力变化、候选规则','规则结果不是监督学习专家金标准；不得用候选标签声称现场异常准确率'
 if d=='08_platform':return '平台接口演示（非训练样本）','接口响应/配置示例','主数据、图谱、诊断、工作流注册','不是模型训练数据；可用于接口联调'
 return '全部模型（说明元数据）','说明/校验','数据字典、使用说明、哈希','非训练数据'

def source_inventory(src):
 entries=[]
 for p in sorted(src.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(src);models,nature,features,limits=mapping(rel)
  entries.append({'原ZIP内路径':str(rel),'适用模型':models,'数据性质':nature,'特征或内容':features,'限制与使用注意':limits,'字节数':p.stat().st_size,'SHA256':hashlib.sha256(p.read_bytes()).hexdigest()})
 write_records(OUT/'original_zip_model_mapping.csv',entries,'csv')
 return entries

def partitions(rows,policy='time',group='well_id'):
 if policy=='group':
  groups=list(dict.fromkeys(r[group] for r in rows));rng.shuffle(groups);n=len(groups);a=max(1,int(n*.7));b=max(a+1,int(n*.85));sets={'train':set(groups[:a]),'validation':set(groups[a:b]),'test':set(groups[b:])};return {sp:[r for r in rows if r[group] in keys] for sp,keys in sets.items()}
 if policy=='doc':
  ids=list(dict.fromkeys(r['doc_id'] for r in rows));rng.shuffle(ids);n=len(ids);a=int(n*.7);b=int(n*.85);sets={'train':set(ids[:a]),'validation':set(ids[a:b]),'test':set(ids[b:])};return {sp:[r for r in rows if r['doc_id'] in keys] for sp,keys in sets.items()}
 groups={}
 for r in rows:groups.setdefault(r.get(group,'ALL'),[]).append(r)
 out={k:[] for k in ['train','validation','test']}
 for vals in groups.values():
  vals.sort(key=lambda r:(r.get('date',''),r.get('t',0)));a=int(len(vals)*.7);b=int(len(vals)*.85)
  for sp,v in zip(out,[vals[:a],vals[a:b],vals[b:]]):out[sp]+=v
 return out

# Generation functions are kept explicit: generated examples never silently masquerade as field data.
def generate_sequences():
 rows=[]
 for w in range(6):
  for t in range(240):
   inj=130+28*math.sin(t/12+w);oil=(110+8*w)*math.exp(-t*.003);wc=min(.86,.18+.0025*t+.02*math.sin(t/20));liquid=oil/(1-wc);pressure=24-.014*t+.1*math.sin(t/9);label=0
   if t%53 in (31,32,33):oil*=.48;liquid=oil/(1-wc);pressure-=3;label=1
   rows.append({'well_id':f'DEMO:W{w+1:02}','date':str(date(2025,1,1)+timedelta(days=t)),'oil':round(oil,5),'liquid':round(liquid,5),'water_cut':round(wc,6),'pressure':round(pressure,5),'injection':round(inj,5),'label':label})
 return rows

def generate(src):
 OUT.mkdir(parents=True,exist_ok=True);inventory=source_inventory(src);seq=generate_sequences();data={};meta={}
 # FORCE public records converted to exact upload feature names, whole well split retained.
 ifs={}
 for sp in ['train','validation','test']:
  rr=[]
  for row in readcsv(src/f'01_well_logs/{sp}.csv'):
   try: vals=[float(row[k]) for k in ['GR','RHOB','DTC']]
   except (ValueError,TypeError):continue
   if not all(math.isfinite(x) for x in vals):continue
   rr.append({'well_id':row['well_id'],'depth':float(row['DEPTH_MD']),'GR':vals[0],'RHOB':vals[1],'DTC':vals[2]})
   if len(rr)>=600:break
  if sp!='train':
   for i,r in enumerate(rr):
    r['label']=int(i%13==0)
    if r['label']:r['GR']+=500;r['RHOB']+=1.8
  ifs[sp]=rr
 data['isolation_forest']=ifs;meta['isolation_forest']={'nature':'FORCE公开观测转换；验证/测试每13条注入一次异常以提供受控标签','policy':'沿用原整井隔离；每分区最多600个完整特征记录','source':'01_well_logs/{train,validation,test}.csv'}
 # Shared generated sequence dimensions, each partition sliced by date inside each well.
 for mid in ['grin','anomaly_transformer','rules']:
  data[mid]=partitions(copy.deepcopy(seq));meta[mid]={'nature':'固定随机种子、解析信号生成数据；非现场观测','policy':'每井前70%日期训练/中15%验证/后15%测试；推理样例保留同一数据字典','source':'generate_sequences()'}
 for sp in data['grin']:
  for i,r in enumerate(data['grin'][sp]):
   r.pop('label',None)
   if i%17==6:r['oil']=None
 arps=[]
 for t in range(240):arps.append({'well_id':'DEMO:ARPS:01','date':str(date(2024,1,1)+timedelta(days=t)),'t':t,'oil':round(160/(1+.6*.008*t)**(1/.6),6)})
 data['arps']=partitions(arps);meta['arps']={'nature':'生成解析Arps曲线，qi=160,Di=0.008,b=0.6','policy':'按时间70/15/15，单井稳定制度理想基准','source':'解析式，不代表现场可预测性'}
 crm=[];q=0.
 for t in range(240):
  i1=100+30*math.sin(t/9)+rng.gauss(0,4);i2=80+25*math.sin(t/17+1)+rng.gauss(0,4);q=math.exp(-1/12)*q+(1-math.exp(-1/12))*(.65*i1+.25*i2)+rng.gauss(0,.15);crm.append({'date':str(date(2024,1,1)+timedelta(days=t)),'injector_1':round(i1,5),'injector_2':round(i2,5),'liquid':round(q,5)})
 data['crm']=partitions(crm);meta['crm']={'nature':'生成已知CRM响应，tau=12d、权重0.65/0.25','policy':'按时间70/15/15；验证选择tau，测试只评价','source':'一阶解析离散机制，不代表真实井间连通'}
 # Real graph triples keep source split; small 591-record corpus suitable for compact run.
 data['rotate']={}
 for sp in ['train','validation','test']:
  data['rotate'][sp]=[dict(zip(['head','relation','tail'],line.split('\t'))) for line in (src/f'04_graph/rotate_{sp}.tsv').read_text().splitlines() if line.strip()]
 meta['rotate']={'nature':'公开FORCE井层事实构建三元组','policy':'沿用原始三元组划分；训练实体与关系覆盖验证/测试','source':'04_graph/rotate_{split}.tsv'}
 # Preserve document-group isolation while converting original prompt span key.
 data['uie']={}
 for sp in ['train','validation','test']:
  rr=[json.loads(x) for x in (src/f'03_extraction/{sp}_prompt_spans.jsonl').read_text().splitlines() if x.strip()];ids=[]
  for x in rr:
   if x['doc_id'] not in ids:ids.append(x['doc_id'])
  selected=set(ids[:24 if sp=='train' else 5]);data['uie'][sp]=[{'doc_id':r['doc_id'],'content':r['content'],'prompt':r['prompt'],'spans':r['result_list']} for r in rr if r['doc_id'] in selected]
 meta['uie']={'nature':'Volve真实表格事实生成中文模板及精确跨度标注，非人工原报告','policy':'沿用按doc_id分组划分；训练24篇、验证/测试各5篇文档，每文档多个prompt','source':'03_extraction/{split}_prompt_spans.jsonl'}
 # DFN uses public geometry; added stress/opening values are generated assumptions.
 fractures=readcsv(src/'06_fractures/segments_2d.csv');dfn=[]
 for c in range(12):
  for r in fractures:
   dfn.append({'case_id':f'DEMO:DFN:{c+1:02}','x1':float(r['x1']),'y1':float(r['y1']),'x2':float(r['x2']),'y2':float(r['y2']),'aperture_mm':round(.3+.04*c,3),'stress_direction_deg':c*15,'stress_ratio':round(.5+.03*c,3)})
 data['dfn']=partitions(dfn,'group','case_id');meta['dfn']={'nature':'公开PorePy二维几何＋生成应力/开度假设','policy':'12个完整工况8/2/2隔离；机理模型无需训练','source':'06_fractures/segments_2d.csv；应力与开度非现场实测'}
 edfm=[{'case_id':f'DEMO:EDFM:{c+1:02}','aperture_mm':round(.3+.05*c,2),'pressure_drop_mpa':round(2+.3*c,2),'duration_days':15+5*c} for c in range(12)]
 data['edfm']=partitions(edfm,'group','case_id');meta['edfm']={'nature':'生成工况参数；底层使用公开基准几何','policy':'完整工况8/2/2；直接机理求解，无训练真值','source':'机理求解输入参数，不可作为神经网络监督目标'}
 # Dictionary alignment corpus: held-out aliases share known canonical entities, no factual field claims.
 aliases={'train':[],'validation':[],'test':[]}
 for i in range(30):
  canonical=f'DEMO-W{i+1:03}';variants=[canonical,canonical.lower(),canonical.replace('-','_'),canonical.replace('-',' '),' '+canonical+' ',canonical.replace('W','w')]
  for j,alias in enumerate(variants):
   sp='train' if j<4 else 'validation' if j==4 else 'test';aliases[sp].append({'entity_id':f'DEMO:ENTITY:{i+1:03}','alias':alias,'canonical':canonical,'type':'well'})
 data['entity_align']=aliases;meta['entity_align']={'nature':'生成实体别名词典与同一实体的未见格式变体','policy':'别名记录4/1/1；canonical实体训练已见，不代表未知实体发现能力','source':'生成格式规范化测试'}
 lag=[]
 for t in range(240):
  injection=100+25*math.sin(t/9)+15*math.cos(t/17);previous=max(0,t-7);production=60+.7*(100+25*math.sin(previous/9)+15*math.cos(previous/17))
  lag.append({'date':str(date(2024,1,1)+timedelta(days=t)),'injection':round(injection,6),'production':round(production,6)})
 data['lag']=partitions(lag);meta['lag']={'nature':'生成已知7日时滞信号','policy':'按时间70/15/15；训练估计时滞，测试外推评价（相关不等于因果连通）','source':'解析信号，不是实际注采响应'}
 hierarchy=[]
 for w in range(20):
  for l in range(2):hierarchy.append({'well_id':f'DEMO:W{w+1:02}','layer_id':f'DEMO:L{l+1:02}','group_id':f'DEMO:G{w//5+1:02}','block_id':f'DEMO:B{w//10+1:02}','valid_from':'2025-01-01','valid_to':'2025-12-31'})
 data['hierarchy']=partitions(hierarchy,'group','well_id');meta['hierarchy']={'nature':'完整生成井—层—井组—区块映射','policy':'按整井14/3/3划分，确定性建图无需模型训练','source':'不代表Volve真实地层/区块/注采边界'}
 contracts=json.loads((BASE/'backend/contracts.json').read_text()) if (BASE/'backend/contracts.json').exists() else {}
 return data,meta,inventory,contracts

def finalize(data,meta,inventory,contracts):
 catalog={m['id']:m for m in contracts.get('models',[])};manifest={'version':'2026-10-31','seed':SEED,'original_zip_complete_files':len(inventory),'original_zip_note':'上传ZIP尾部缺失，仅使用76个CRC与长度验证通过的完整文件；残缺预览PNG不入包。','models':[],'files':[]}
 for mid,splits in data.items():
  overall=[r for sp in ['train','validation','test'] for r in splits[sp]]
  infer=copy.deepcopy(splits['test'])
  for r in infer:
   r.pop('label',None)
   if mid=='uie':r.pop('spans',None)
  if mid in ['dfn','edfm']:infer=[r for r in infer if r.get('case_id')==infer[0].get('case_id')]
  sample_splits={**splits,'overall':overall,'infer':infer}
  for sp,rows in sample_splits.items():
   write_records(OUT/mid/f'{sp}.jsonl',rows)
   if mid!='uie':write_records(OUT/mid/f'{sp}.csv',rows,'csv')
  n=sum(map(len,splits.values()));counts={sp:len(r) for sp,r in splits.items()};c=catalog.get(mid,{})
  info={'id':mid,'name':c.get('name',mid),'nature':meta[mid]['nature'],'split_policy':meta[mid]['policy'],'source':meta[mid]['source'],'counts':counts,'record_ratios':{sp:round(v/n,6) for sp,v in counts.items()},'recommended_ratio':[70,15,15],'format':'JSONL (one record per line)'+(' / CSV' if mid!='uie' else ''),'features':c.get('features',[]),'files':{sp:f'{mid}/{sp}.jsonl' for sp in sample_splits}}
  manifest['models'].append(info)
  readme=f"# {info['name']} 数据说明\n\n数据性质：{info['nature']}。\n\n来源：{info['source']}。\n\n划分：{info['split_policy']}。实际记录数：训练 {counts['train']}、验证 {counts['validation']}、测试 {counts['test']}；比例随分组粒度可能偏离70/15/15。\n\n- train：仅用于拟合/词表/标准化。\n- validation：选择超参数/阈值，不能合并进测试。\n- test：独立最终评价；机理/规则模型为工况或一致性比较，无需学习。\n- overall：上述三部分合并，用于平台重新划分；重分后不能与旧指标混用。\n- infer：计算输入，UIE不带spans，异常检测不带label；此演示复用测试输入，不能另称新独立测试集。\n\n"
  readme+='字段：\n\n|字段|类型|单位|要求|说明|\n|---|---|---|---|---|\n'
  for f in c.get('features',[]):readme+=f"|{f['name']}|{f['type']}|{f.get('unit','')}|{'必有字段' if f.get('required') else '可选/按任务'}|{f.get('description','')}|\n"
  readme+='\n输入样例（只展示前2条，实际训练请上传完整文件）：\n\n```json\n'+json.dumps(splits['train'][:2],ensure_ascii=False,indent=2)+'\n```\n'
  (OUT/mid/'README.md').write_text(readme,encoding='utf-8')
 source_md=['# 原ZIP逐文件—模型对应清单','','公开观测、人工注入标签、模板语料、生成机理算例已分开说明。没有现场专家异常金标准；候选事件不等于异常确诊。','','|原ZIP内路径|可用于模型|性质|使用注意|','|---|---|---|---|']
 for r in inventory:source_md.append('|'+ '|'.join(str(r[k]).replace('|','/') for k in ['原ZIP内路径','适用模型','数据性质','限制与使用注意'])+'|')
 (OUT/'original_zip_model_mapping.md').write_text('\n'.join(source_md)+'\n',encoding='utf-8')
 readme="""# ChinaOil 模型训练、验证、测试与计算数据包

本包为可上传接口的数据资产，不是全部模型已达到现场应用精度的证明。所有生成对象使用 DEMO 命名。固定随机种子：20261031。原ZIP数据可在平台另外下载 public_training_data.zip，本包提供统一接口格式的转换与补充生成样例。

## 文件与用途

每个模型目录含 train.jsonl、validation.jsonl、test.jsonl、overall.jsonl、infer.jsonl；除UIE还提供同内容CSV。每个目录README给出字段、类型、单位、来源、记录数、比例、输入样例。manifest.json提供数据字典、真实记录比例与所有文件SHA256。original_zip_model_mapping.csv / .md逐项列出原ZIP全部76个完整文件的用途。

|模型|提供的数据性质|建议划分与约束|
|---|---|---|
|Isolation Forest|FORCE公开测井完整特征转换；验证/测试人工注入尖峰|沿用整井分区；非注入行不等于专家确认正常|
|GRIN精简结构|生成6井×240日动态，插入显式null缺口|时间顺序70/15/15；训练期统计邻接；遮蔽重建评价|
|Anomaly Transformer精简结构|生成6井×240日动态、受控降产/降压标签|时间顺序70/15/15；test标签不进入拟合|
|UIE式精简结构|真实Volve表格事实转中文模板/精确跨度|按文档隔离，216/45/45记录；非原报告人工标注|
|RotatE|FORCE真实井层事实转三元组|沿用444/73/74三元组；训练词表覆盖所有端点|
|Arps|已知解析参数理想曲线|时间168/36/36；仅稳定制度条件校验|
|CRM|已知响应时间12日和权重0.65/0.25生成序列|时间168/36/36；不能证明现场连通性|
|DFN|公开裂缝端点＋生成应力和开度|完整工况8/2/2；是几何求解，非训练样本标签|
|EDFM|生成开度/压差/时长工况|完整工况8/2/2；直接机理求解，无监督真值|
|实体对齐|生成词典/格式变体|canonical已见、别名4/1/1；非未知实体发现测试|
|时滞关联|生成已知7日时滞信号|时间168/36/36；相关不等于因果|
|层级主数据|生成20井—两层—井组—区块映射|整井14/3/3；非真实地质归属|
|专业规则|生成动态与注入异常|时间70/15/15；规则无需训练，标签是受控生成|

## 上传及计算

1. 平台模型工作台选择模型，阅读字段说明和模型结构图。
2. 分别上传 train / validation / test，或上传 overall 后设置比例重新划分。
3. 推荐比例70/15/15。测井推荐整井隔离，UIE按文档隔离，时间序列按日期排序且同日跨井成组，DFN/EDFM按完整工况分组。随机划分只用于IID假设下的实验；不能打散滑动窗口或把同文档泄漏到不同分区。
4. 配置独立Python计算服务URL，训练或校准后查看实际耗时、验证/测试指标。
5. 上传 infer 运行计算，下载结果；源数据不会自动变成现场结论。

## 特征及单位

生产油量、液量、注水采用日均标准体积Sm³/d；含水water_cut为0–1；pressure为MPa。原ZIP Volve压力保留源口径，转换时必须显式确认单位（不得直接当MPa）。真实日累计体积转日均时须区分日历日与开井时长。UIE使用Unicode字符索引，start包含、end不包含；text须与content[start:end]严格相等。标签、真值与mask目标不作模型输入特征。

## 来源、许可及局限

- 原ZIP的00_sources与docs/SOURCES.md记录Volve、FORCE、OPM/SPE、PorePy来源；随包保留 SOURCES.md 和可得许可文本。
- FORCE/Volve为公开数据；UIE是公开事实模板，非真实中文现场报告。公开裂缝为几何基准而非真实油藏裂缝预测真值。
- 原上传ZIP尾部不完整，仅76个CRC、长度验证通过的文件进入逐文件映射，残缺PNG未使用。
- 训练服务是科研演示实现，深度模型是精简结构复现，不是官方预训练权重。实际训练时长取决于设备、样本量、epochs，不预填虚构耗时。
- 生成标签仅验证可控机制；不能将本包高指标宣传为现场性能。Arps、CRM、DFN、EDFM需专业适用性及现场校准。

## 重现

在仓库根目录运行 `python data-kit/generate_data_kit.py --source /path/to/CRC-verified/reservoir_public_demo`。仅用Python标准库，不读取用户上传内容或密钥。
"""
 (OUT/'README.md').write_text(readme,encoding='utf-8')
 for fname in ['SOURCES.md']:
  shutil.copyfile(SOURCE_ROOT/'docs'/fname,OUT/fname)
 for name in ['odbl-10.txt','dbcl-10.txt','porepy_LICENSE.md']:
  shutil.copyfile(SOURCE_ROOT/'00_sources'/name,OUT/name)
 shutil.copyfile(Path(__file__),OUT/'generate_data_kit.py')
 for p in sorted(OUT.rglob('*')):
  if p.is_file() and p.name not in ['manifest.json','model_data_kit.zip','_draft_data.json']:
   manifest['files'].append({'path':str(p.relative_to(OUT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 write_json(OUT/'manifest.json',manifest)
 draft=OUT/'_draft_data.json'
 if draft.exists():draft.unlink()
 with zipfile.ZipFile(OUT/'model_data_kit.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(OUT.rglob('*')):
   if p.is_file() and p.name!='model_data_kit.zip':z.write(p,p.relative_to(OUT))
 print('Wrote',len(manifest['models']),'models,',len(inventory),'original mappings;',len(manifest['files']),'files')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=Path('/workspace/scratch/871dad45c098/staging/recovered_data/reservoir_public_demo'));args=p.parse_args()
 SOURCE_ROOT=args.source
 data,meta,inventory,contracts=generate(args.source)
 finalize(data,meta,inventory,contracts)
