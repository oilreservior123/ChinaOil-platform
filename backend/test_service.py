import json,sys,unittest
from pathlib import Path
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.app import app,MODELS

class ServiceTests(unittest.TestCase):
 def setUp(self):self.client=TestClient(app)
 def test_health_contracts(self):
  self.assertEqual(self.client.get('/health').status_code,200)
  self.assertEqual(len(self.client.get('/api/contracts').json()['models']),13)
 def test_bad_request_and_leakage(self):
  self.assertEqual(self.client.post('/api/run',json={'model_id':'unknown'}).status_code,422)
  r={'well_id':'X','depth':1,'GR':80,'RHOB':2.4,'DTC':90}
  res=self.client.post('/api/run',json={'model_id':'isolation_forest','operation':'test','train':[r],'test':[r]})
  self.assertEqual(res.status_code,422);self.assertIn('leakage',res.json()['detail'])
 def test_missing_targets_predict(self):
  import math
  train=[{'well_id':'W1','date':f'2025-01-{i+1:02}','t':i,'oil':100*math.exp(-.02*i)} for i in range(10)]
  pred=[{'well_id':'W1','date':'2025-01-20','t':19}]
  out=self.client.post('/api/run',json={'model_id':'arps','operation':'predict','train':train,'input':pred})
  self.assertEqual(out.status_code,200,out.text);self.assertIn('predicted_oil',out.json()['results'][0]);self.assertGreater(out.json()['calibration_seconds'],0)
 def test_rotate_api_missing_tail_returns_candidates(self):
  base=Path(__file__).resolve().parents[1]/'dist/downloads/model-data/rotate'
  load=lambda p:[json.loads(x) for x in (base/p).read_text().splitlines() if x]
  tr=load('train.jsonl'); row=load('infer.jsonl')[0];row.pop('tail',None)
  out=self.client.post('/api/run',json={'model_id':'rotate','operation':'predict','train':tr,'input':[row],'parameters':{'epochs':1}})
  self.assertEqual(out.status_code,200,out.text);self.assertTrue(out.json()['results'])
 def test_input_does_not_replace_test(self):
  test=[{'well_id':'X','date':'2025-01-02','oil':-10,'liquid':100,'water_cut':.5,'pressure':20,'injection':100}]
  inp=[dict(test[0],date='2025-01-03',oil=50)]
  out=self.client.post('/api/run',json={'model_id':'rules','operation':'test','test':test,'input':inp})
  self.assertEqual(out.status_code,200,out.text);self.assertEqual(out.json()['results'][0]['date'],'2025-01-02')
 def test_crm_state_retains_calendar_date_and_rejects_reversed_partitions(self):
  import numpy as np
  from backend.classical_models import crm_design,run_crm
  matrix,state=crm_design([{'date':'2025-04-11','injector_1':0,'injector_2':0}],10,{'response':[100,100],'date':'2025-01-01'})
  self.assertAlmostEqual(matrix[0,0],100*np.exp(-10),places=10)
  self.assertEqual(state['date'],'2025-04-11')
  train=[{'date':f'2025-01-{i+1:02}','injector_1':100+i,'injector_2':80+i,'liquid':60+i} for i in range(10)]
  with self.assertRaisesRegex(ValueError,'chronological order'):
   run_crm(train,[dict(train[0],date='2024-12-31')],[],[],{},'validate')
  # Replay same interval as held-out test must start before test, not after test's end.
  validation=[dict(train[-1],date='2025-02-01')]
  test=[dict(train[-1],date='2025-03-01'),dict(train[-1],date='2025-03-03')]
  tested=run_crm(train,validation,test,[],{},'test')
  replayed=run_crm(train,validation,test,test,{},'predict')
  self.assertEqual([r['predicted_liquid'] for r in tested['results']],[r['predicted_liquid'] for r in replayed['results']])
 def test_service_all_13_models_real_data(self):
  root=Path(__file__).resolve().parents[1]/'dist/downloads/model-data'
  for mid in MODELS:
   with self.subTest(model=mid):
    d={}
    for key in ['train','validation','test','infer']:
     p=root/mid/(key+'.jsonl');d['input' if key=='infer' else key]=[json.loads(line) for line in p.read_text().splitlines() if line]
    # Real full supplied data, one epoch is enough to verify every codepath.
    out=self.client.post('/api/run',json=dict(model_id=mid,operation='predict',parameters={'epochs':1,'trees':16,'time_steps':6},**d))
    self.assertEqual(out.status_code,200,out.text[:2000]);value=out.json();self.assertTrue(value['results']);self.assertGreater(value['elapsed_seconds'],0)
    if MODELS[mid]['kind']=='trainable':self.assertGreater(value['training_seconds'],0)
    if MODELS[mid]['kind']=='simulation':self.assertIsNone(value['training_seconds'])

if __name__=='__main__':unittest.main()
