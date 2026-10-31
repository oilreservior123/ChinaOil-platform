"""Actual fitting and physical calculation; no uploaded files persisted."""
import json, math, subprocess, time
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares, nnls
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score, average_precision_score

def finite(x):
 try:return x is not None and math.isfinite(float(x))
 except (TypeError,ValueError):return False

def regression(y,p):
 y=np.asarray(y,dtype=float);p=np.asarray(p,dtype=float);ok=np.isfinite(y)&np.isfinite(p);y=y[ok];p=p[ok]
 if not len(y):return {'samples':0}
 d=p-y;den=((y-y.mean())**2).sum()
 return {'MAE':float(np.abs(d).mean()),'RMSE':float(np.sqrt((d*d).mean())),'R2':float(1-(d*d).sum()/den) if den>0 else None,'samples':len(y)}

def classification(rows,scores,threshold):
 indices=[i for i,r in enumerate(rows) if r.get('label') in [0,1]]
 if not indices:return {'samples':len(rows),'labeled_samples':0,'note':'No labels supplied: classification metrics unavailable.'}
 y=np.asarray([rows[i]['label'] for i in indices]);s=np.asarray(scores)[indices];p,r,f,_=precision_recall_fscore_support(y,s>=threshold,average='binary',zero_division=0)
 return {'Precision':p,'Recall':r,'F1':f,'ROC_AUC':roc_auc_score(y,s) if len(set(y))>1 else None,'PR_AUC':average_precision_score(y,s) if y.sum()>0 else None,'labeled_samples':len(y),'threshold':threshold}

def selected(operation,validation,test,input_rows):
 return validation if operation=='validate' else test if operation=='test' else input_rows if operation=='predict' else test or validation or input_rows

def run_if(train,val,test,rows,params,operation):
 cols=['GR','RHOB','DTC'];arr=lambda rs:np.array([[float(r[c]) if finite(r.get(c)) else np.nan for c in cols] for r in rs])
 if len(train)<8:raise ValueError('Isolation Forest needs at least 8 training records.')
 x=arr(train)
 if np.any(np.isnan(x).all(0)):raise ValueError('Every feature must have at least one observed training value.')
 start=time.perf_counter();imp=SimpleImputer(strategy='median');scale=RobustScaler();x=scale.fit_transform(imp.fit_transform(x));model=IsolationForest(n_estimators=int(params.get('trees',64)),max_samples=min(256,len(train)),contamination=float(params.get('contamination',.1)),random_state=int(params.get('seed',20261031)),n_jobs=1).fit(x)
 score=lambda rs:-model.decision_function(scale.transform(imp.transform(arr(rs))))
 threshold=0.;history=[]
 if val and all(r.get('label') in [0,1] for r in val) and len(set(r['label'] for r in val))==2:
  s=score(val);trials=np.quantile(s,np.linspace(.1,.99,40));threshold=float(max(trials,key=lambda t:classification(val,s,t)['F1']))
 training=time.perf_counter()-start;compute=time.perf_counter();metrics={sp:classification(rs,score(rs),threshold) for sp,rs in [('validation',val),('test',test)] if rs}
 target=selected(operation,val,test,rows);s=score(target) if target else []
 results=[dict(r,anomaly_score=float(v),predicted_label=int(v>=threshold)) for r,v in zip(target,s)]
 artifact={'type':'sklearn_IsolationForest','features':cols,'imputer':imp.statistics_.tolist(),'center':scale.center_.tolist(),'scale':scale.scale_.tolist(),'threshold':threshold,'trees':len(model.estimators_)}
 return dict(results=results,metrics=metrics,training_seconds=training,compute_seconds=time.perf_counter()-compute,model_artifact=artifact,limitations=['Scores do not establish field root causes. Labels are required for anomaly accuracy metrics.'])

def rate(t,qi,di,b):
 t=np.asarray(t,dtype=float)
 return qi*np.exp(-di*t) if b<1e-5 else qi*np.power(np.maximum(1+b*di*t,1e-9),-1/b)

def run_arps(train,val,test,rows,params,operation):
 if len(train)<6:raise ValueError('Arps needs 6 positive-rate training observations at minimum.')
 wells={r.get('well_id') for r in train+val+test+rows}
 if len(wells)>1:raise ValueError('Arps run accepts one well only; select and split a single stable production window.')
 for r in train+val+test+rows:
  if not finite(r.get('t')):raise ValueError('Arps requires numeric elapsed day t.')
  if r in train and (not finite(r.get('oil')) or float(r['oil'])<=0):raise ValueError('Arps training rates must be positive.')
 start=time.perf_counter();t=np.array([r['t'] for r in train],float);y=np.array([r['oil'] for r in train],float);candidates=[]
 for b in [0,.1,.3,.5,.7,1.]:
  fit=least_squares(lambda z:np.log(np.maximum(rate(t,z[0],z[1],b),1e-9))-np.log(y),[max(y),.01],bounds=([1e-8,1e-8],[max(y)*100,5]))
  q,d=fit.x
  v=regression([r['oil'] for r in val],[rate(r['t'],q,d,b) for r in val])['RMSE'] if val else np.sqrt(np.mean((rate(t,q,d,b)-y)**2))
  candidates.append((v,q,d,b))
 _,q,d,b=min(candidates);training=time.perf_counter()-start;compute=time.perf_counter();target=selected(operation,val,test,rows);metrics={s:regression([r.get('oil',np.nan) for r in rs],[rate(r['t'],q,d,b) for r in rs]) for s,rs in [('validation',val),('test',test)] if rs}
 return dict(results=[dict(r,predicted_oil=float(rate(r['t'],q,d,b))) for r in target],metrics=metrics,training_seconds=training,compute_seconds=time.perf_counter()-compute,model_artifact={'qi':q,'Di_per_day':d,'b':b},limitations=['Only stable operating conditions and an applicable decline regime support engineering interpretation. Calibration duration is not neural training duration.'])

def crm_design(rows,tau,initial=None,initial_date=None):
 from datetime import date
 x=np.array([[r['injector_1'],r['injector_2']] for r in rows],float).reshape(-1,2);out=np.zeros_like(x)
 if isinstance(initial,dict):
  prev=np.asarray(initial['response'],float).copy();initial_date=initial.get('date')
 else:prev=np.zeros(2) if initial is None else np.asarray(initial,float).copy()
 last_date=date.fromisoformat(initial_date) if isinstance(initial_date,str) else initial_date
 for i,r in enumerate(rows):
  day=date.fromisoformat(r['date'])
  if last_date is not None and day<=last_date:raise ValueError('CRM current date must follow the previous response-state date.')
  dt=(day-last_date).days if last_date is not None else 1
  alpha=np.exp(-dt/tau);prev=alpha*prev+(1-alpha)*x[i];out[i]=prev;last_date=day
 state={'response':prev.tolist(),'date':last_date.isoformat() if last_date else None}
 return np.column_stack([out,np.ones(len(out))]),state

def run_crm(train,val,test,rows,params,operation):
 if len(train)<8:raise ValueError('CRM needs at least 8 chronological training observations.')
 for rs in [train,val,test,rows]:
  if any(rs[i]['date']>=rs[i+1]['date'] for i in range(len(rs)-1)):raise ValueError('CRM records must have unique dates in ascending order.')
 last=None
 for name,rs in [('train',train),('validation',val),('test',test)]:
  if rs and last is not None and rs[0]['date']<=last:raise ValueError('CRM train/validation/test partitions must follow chronological order without overlap.')
  if rs:last=rs[-1]['date']
 start=time.perf_counter();candidates=[]
 for tau in [1,2,4,8,12,20,30,60,120]:
  X,end=crm_design(train,tau);w,_=nnls(X,np.array([r['liquid'] for r in train],float));V,_=crm_design(val,tau,end) if val else (X,end);y=[r['liquid'] for r in val] if val else [r['liquid'] for r in train];err=regression(y,V@w)['RMSE'];candidates.append((err,tau,w,end))
 _,tau,w,end=min(candidates,key=lambda c:c[0]);training=time.perf_counter()-start;compute=time.perf_counter();validation_x,vend=crm_design(val,tau,end) if val else (np.zeros((0,3)),end);test_x,_=crm_design(test,tau,vend) if test else (np.zeros((0,3)),vend);metrics={}
 if val:metrics['validation']=regression([r['liquid'] for r in val],validation_x@w)
 if test:metrics['test']=regression([r['liquid'] for r in test],test_x@w)
 target=selected(operation,val,test,rows)
 if target is val:pred=validation_x@w
 elif target is test:pred=test_x@w
 else:
  # Supports both future prediction and retrospective replay without reading future injection history.
  context=sorted([r for r in train+val+test if target and r['date']<target[0]['date']],key=lambda r:r['date'])
  _,state=crm_design(context,tau) if context else (None,None)
  xx,_=crm_design(target,tau,state);pred=xx@w
 return dict(results=[dict(r,predicted_liquid=float(v)) for r,v in zip(target,pred)],metrics=metrics,training_seconds=training,compute_seconds=time.perf_counter()-compute,model_artifact={'tau_days':tau,'nonnegative_weights':w[:2].tolist(),'baseline':w[2],'state_policy':'Response state carries its last calendar date. Validation follows train; test follows validation. Input replay uses only injection history strictly before its first date, never later observations.'},limitations=['Weights are response-fit parameters, not proven hydraulic connectivity. Uniform volume/PVT conventions must be checked.','Calendar gaps propagate with actual elapsed days; first-ever observation initializes from zero with one-day step.'])

def intersection(a,b):
 p=np.array([a['x1'],a['y1']],float);r=np.array([a['x2']-a['x1'],a['y2']-a['y1']],float);q=np.array([b['x1'],b['y1']],float);s=np.array([b['x2']-b['x1'],b['y2']-b['y1']],float);cross=lambda u,v:u[0]*v[1]-u[1]*v[0];den=cross(r,s)
 if abs(den)<1e-10:return False
 return 0<=cross(q-p,s)/den<=1 and 0<=cross(q-p,r)/den<=1

def run_dfn(rows):
 start=time.perf_counter();results=[]
 for r in rows:
  dx=float(r['x2'])-float(r['x1']);dy=float(r['y2'])-float(r['y1']);length=math.hypot(dx,dy)
  if length<=0:raise ValueError('DFN segments require distinct endpoints.')
  ratio=float(r['stress_ratio']);ap=float(r['aperture_mm'])
  if not 0<=ratio<=1 or ap<=0:raise ValueError('DFN stress_ratio must be in [0,1], aperture must be positive.')
  angle=math.atan2(dy,dx);delta=angle-math.radians(float(r['stress_direction_deg']));weight=ratio+(1-ratio)*math.cos(delta)**2
  results.append(dict(r,length_m=length,orientation_deg=math.degrees(angle),stress_weight=weight,effective_aperture_mm=ap*weight))
 groups={}
 for r in rows:groups.setdefault(r['case_id'],[]).append(r)
 count=sum(intersection(a,b) for rs in groups.values() for i,a in enumerate(rs) for b in rs[i+1:])
 return dict(results=results,metrics={'calculation':{'fracture_count':len(rows),'intersection_count':count,'total_length_m':sum(r['length_m'] for r in results)}},training_seconds=None,compute_seconds=time.perf_counter()-start,model_artifact={'type':'stress_direction_weighted_DFN_geometry'},limitations=['Generated stress-direction aperture weighting is a declared geometric assumption, not a calibrated coupled geomechanics solver.'])

def run_edfm(rows,params):
 if len(rows)>12:raise ValueError('EDFM accepts at most 12 cases per request.')
 start=time.perf_counter();root=Path(__file__).resolve().parent
 proc=subprocess.run(['node',str(root/'edfm_bridge.mjs')],input=json.dumps({'rows':rows,'parameters':params}),text=True,capture_output=True,timeout=120,check=False)
 if proc.returncode:raise ValueError('EDFM solver failed: '+proc.stderr[-500:])
 out=json.loads(proc.stdout);out.update(training_seconds=None,compute_seconds=time.perf_counter()-start);return out
