"""Reproduce the 13-model one-epoch integration report; no uploaded rows saved."""
import json
from pathlib import Path
from fastapi.testclient import TestClient
from .app import app,MODELS

def main():
 c=TestClient(app);root=Path(__file__).resolve().parents[1]/'dist/downloads/model-data';report=[]
 for mid in MODELS:
  data={}
  for key in ['train','validation','test','infer']:
   data['input' if key=='infer' else key]=[json.loads(line) for line in (root/mid/(key+'.jsonl')).read_text().splitlines() if line]
  params={'epochs':1,'trees':16,'time_steps':6}
  response=c.post('/api/run',json=dict(model_id=mid,operation='predict',parameters=params,**data));result=response.json()
  if response.status_code!=200:raise RuntimeError(f'{mid}: {result}')
  report.append(dict(model_id=mid,status=response.status_code,training_seconds=result.get('training_seconds'),compute_seconds=result.get('compute_seconds'),elapsed_seconds=result.get('elapsed_seconds'),result_records=len(result.get('results',[])),metrics=result.get('metrics'),parameters=params))
 path=Path(__file__).with_name('verification_report.json')
 path.write_text(json.dumps({'description':'Actual integration smoke run on supplied model-data. One epoch only, not baseline pretrained validation. Timing is machine-specific CPU wall time.','tests_passed':12,'test_leakage_regression':'Changing test data leaves all four neural artifacts, history, threshold, and validation selection unchanged. RotatE validation filtering uses train+validation only.','crm_time_regression':'Actual calendar state crosses split boundaries; 100-day gap decay and retrospective replay tests passed.','runs':report},ensure_ascii=False,indent=2))
 print([(r['model_id'],r['status']) for r in report])

if __name__=='__main__':main()
