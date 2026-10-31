"""Run: python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000."""
from __future__ import annotations
import json, math, os, secrets, threading, time
from datetime import date
from pathlib import Path
from typing import Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from .classical_models import run_if,run_arps,run_crm,run_dfn,run_edfm,selected
from .auxiliary_models import run_aux

CONTRACTS=json.loads(Path(__file__).with_name('contracts.json').read_text())
MODELS={m['id']:m for m in CONTRACTS['models']}
# Set explicit GitHub Pages origin when deploying. A wildcard is deliberately not used.
ORIGINS=os.getenv('GEOTWIN_ALLOWED_ORIGINS','http://localhost:4173,http://127.0.0.1:4173,http://localhost:8000,http://127.0.0.1:8000,http://terminal.local:4173,https://chinaoil-geotwin-20261031.redcrown2.chatgpt.site').split(',')
API_TOKEN=os.getenv('GEOTWIN_API_TOKEN','')
LOCK=threading.Lock()
app=FastAPI(title='ChinaOil GeoTwin training and calculation API',version='2.0.0',docs_url='/docs')
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in ORIGINS if x.strip()],allow_methods=['GET','POST'],allow_headers=['Content-Type','Authorization','X-API-Key'],allow_credentials=False)

class RunRequest(BaseModel):
 model_config=ConfigDict(extra='forbid')
 model_id:str
 operation:str='predict'
 train:list[dict[str,Any]]=Field(default_factory=list)
 validation:list[dict[str,Any]]=Field(default_factory=list)
 test:list[dict[str,Any]]=Field(default_factory=list)
 input:list[dict[str,Any]]=Field(default_factory=list)
 parameters:dict[str,Any]=Field(default_factory=dict)

@app.middleware('http')
async def limits(request:Request,call_next):
 size=request.headers.get('content-length')
 if size and int(size)>30_000_000:
  from fastapi.responses import JSONResponse
  return JSONResponse({'detail':'Request exceeds 30 MB; use a representative sample or a dedicated training cluster.'},status_code=413)
 return await call_next(request)

def authenticate(request):
 if API_TOKEN:
  given=request.headers.get('x-api-key','') or request.headers.get('authorization','').removeprefix('Bearer ')
  if not secrets.compare_digest(given,API_TOKEN):raise HTTPException(401,'Invalid API key')

@app.get('/health')
def health():return {'status':'ok','service':'ChinaOil GeoTwin','models':list(MODELS),'version':'2.0.0','data_retention':'none','supported_operations':['train','validate','test','predict']}

@app.get('/api/contracts')
def contracts():return CONTRACTS

def check_rows(model_id,rows,role):
 model=MODELS[model_id]
 for i,row in enumerate(rows):
  if not isinstance(row,dict):raise ValueError(f'{role}[{i}] must be an object.')
  for f in model['features']:
   name=f['name'];is_input=role=='input';value=row.get(name)
   if f.get('target') and is_input:continue
   if name not in row or value in [None,'']:
    if f.get('nullable') and name in row:continue
    if f.get('required'):raise ValueError(f'{role}[{i}].{name} is required.')
    continue
   typ=f['type']
   if typ=='number' or typ=='integer':
    if isinstance(value,bool):raise ValueError(f'{role}[{i}].{name} must be numeric.')
    try:number=float(value)
    except (TypeError,ValueError):raise ValueError(f'{role}[{i}].{name} must be numeric.')
    if not math.isfinite(number):raise ValueError(f'{role}[{i}].{name} must be finite or null when allowed.')
    if typ=='integer' and int(number)!=number:raise ValueError(f'{role}[{i}].{name} must be integer.')
    row[name]=int(number) if typ=='integer' else number
    if name=='label' and number not in [0,1]:raise ValueError(f'{role}[{i}].label must be 0 or 1.')
   elif typ=='array' and not isinstance(value,list):raise ValueError(f'{role}[{i}].{name} must be an array.')
   elif typ=='date':
    try:date.fromisoformat(value)
    except (TypeError,ValueError):raise ValueError(f'{role}[{i}].{name} must be YYYY-MM-DD.')
   elif typ=='string' and not isinstance(value,str):raise ValueError(f'{role}[{i}].{name} must be a string.')

def disjoint(model_id,partitions):
 fields={'isolation_forest':['well_id','depth'],'rotate':['head','relation','tail'],'grin':['well_id','date'],'anomaly_transformer':['well_id','date'],'uie':['doc_id','prompt'],'arps':['well_id','date'],'crm':['date'],'lag':['date'],'hierarchy':['well_id','layer_id','valid_from','valid_to']}.get(model_id)
 if not fields:return
 seen={}
 for split,rows in partitions.items():
  local=set()
  for row in rows:
   key=tuple(str(row.get(k)) for k in fields)
   if key in local:raise ValueError(f'Duplicate identity within {split}: {key}.')
   if key in seen:raise ValueError(f'Data leakage: identity appears in {seen[key]} and {split}: {key}.')
   local.add(key);seen[key]=split

def clean(value):
 if isinstance(value,dict):return {str(k):clean(v) for k,v in value.items()}
 if isinstance(value,(list,tuple)):return [clean(v) for v in value]
 if hasattr(value,'item'):value=value.item()
 if isinstance(value,float) and not math.isfinite(value):return None
 return value

@app.post('/api/run')
def run(payload:RunRequest,request:Request):
 authenticate(request)
 if payload.model_id not in MODELS:raise HTTPException(422,'Unknown model_id')
 if payload.operation not in ['train','validate','test','predict']:raise HTTPException(422,'operation must be train / validate / test / predict')
 params=payload.parameters
 try:
  epochs=int(params.get('epochs',6))
  if not 1<=epochs<=100:raise ValueError('epochs must be 1–100.')
  if int(params.get('trees',64)) not in range(8,257):raise ValueError('trees must be 8–256.')
  contamination=float(params.get('contamination',.1))
  if not 0<contamination<=.5:raise ValueError('contamination must be in (0,.5].')
  params['epochs']=epochs
  count=sum(len(x) for x in [payload.train,payload.validation,payload.test,payload.input])
  if count>100000:raise ValueError('Combined row limit is 100000 for this compact service.')
  for role in ['train','validation','test','input']:check_rows(payload.model_id,getattr(payload,role),role)
  disjoint(payload.model_id,{k:getattr(payload,k) for k in ['train','validation','test']})
  if payload.operation=='validate' and not payload.validation:raise ValueError('Validation operation requires validation data.')
  if payload.operation=='test' and not payload.test:raise ValueError('Test operation requires test data.')
  if payload.operation=='predict' and not payload.input:raise ValueError('Prediction operation requires input data.')
  if MODELS[payload.model_id]['kind'] in ['trainable','calibration'] and not payload.train:raise ValueError('This operation requires train data; every run fits current train data from scratch.')
 except (TypeError,ValueError) as e:raise HTTPException(422,str(e))
 if not LOCK.acquire(blocking=False):raise HTTPException(409,'Another run is active; wait until it completes.')
 start=time.perf_counter()
 try:
  tr,va,te,inp=payload.train,payload.validation,payload.test,payload.input
  mid=payload.model_id;operation=payload.operation
  if mid in ['rotate','grin','uie','anomaly_transformer']:
   from .deep_models import run_deep
   results=run_deep(mid,tr,va,te,selected(operation,va,te,inp),params)
  elif mid=='isolation_forest':results=run_if(tr,va,te,inp,params,operation)
  elif mid=='arps':results=run_arps(tr,va,te,inp,params,operation)
  elif mid=='crm':results=run_crm(tr,va,te,inp,params,operation)
  elif mid=='dfn':results=run_dfn(selected(operation,va,te,inp) or tr)
  elif mid=='edfm':results=run_edfm(selected(operation,va,te,inp) or tr,params)
  else:results=run_aux(mid,tr,va,te,inp,params,operation)
  results.update(model_id=mid,operation=operation,kind=MODELS[mid]['kind'],elapsed_seconds=time.perf_counter()-start,split_counts={k:len(getattr(payload,k)) for k in ['train','validation','test','input']},run_policy='Each request independently fits train and selects on validation; test never updates weights or thresholds. No uploaded rows or model weights are stored on disk.',training_time_label='training_seconds' if MODELS[mid]['kind']=='trainable' else 'calibration_seconds' if MODELS[mid]['kind']=='calibration' else 'not_applicable')
  if MODELS[mid]['kind']=='calibration':results['calibration_seconds']=results['training_seconds']
  return clean(results)
 except (ValueError,KeyError,TypeError) as e:raise HTTPException(422,str(e))
 except Exception as e:raise HTTPException(500,f'Calculation failed: {type(e).__name__}: {str(e)[:300]}')
 finally:LOCK.release()
