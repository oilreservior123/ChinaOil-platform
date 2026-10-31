import unittest
import math
from deep_models import run_deep

class DeepModelsTest(unittest.TestCase):
 def test_rotate_real_fit_and_unseen_rejection(self):
  records=[{'head':'A','relation':'flows','tail':'B'},{'head':'B','relation':'flows','tail':'C'},{'head':'C','relation':'flows','tail':'A'}]
  out=run_deep('rotate',records,records[:1],records[1:2],[{'head':'A','relation':'flows'}],{'epochs':1})
  self.assertEqual(len(out['results'][0]['candidates']),3)
  self.assertGreater(out['training_seconds'],0)
  self.assertIn('filtered_MRR',out['metrics']['test'])
  with self.assertRaises(ValueError):run_deep('rotate',records,[{'head':'X','relation':'flows','tail':'A'}],[],parameters={'epochs':1})
 def test_uie_unicode_span_and_unlabeled_input(self):
  records=[{'doc_id':str(i),'content':f'井号为A{i}。','prompt':'井号','spans':[{'start':3,'end':5,'text':f'A{i}'}]} for i in range(4)]
  out=run_deep('uie',records[:2],records[2:3],records[3:],[{'doc_id':'new','content':'井号为Z9。','prompt':'井号'}],{'epochs':1})
  p=out['results'][0]['prediction'];self.assertEqual(p['text'],'井号为Z9。'[p['start']:p['end']]);self.assertIn('exact_span_F1',out['metrics']['test'])
 def make_rows(self,offset=0):
  return [{'well_id':w,'date':f'2020-01-{i+offset:02d}','oil':100-i,'liquid':130+i,'water_cut':.2+i*.01,'pressure':200-i,'injection':110+i} for i in range(1,9) for w in ['A','B']]
 def test_grin_mask_metrics_and_missing_inference(self):
  tr=self.make_rows();va=self.make_rows(8);te=self.make_rows(16);inp=[dict(te[0]),dict(te[1])];inp[0]['oil']=None
  out=run_deep('grin',tr,va,te,inp,{'epochs':1})
  r=next(r for r in out['results'] if r['well_id']=='A');self.assertIn('oil',r['imputed_features']);self.assertTrue(math.isfinite(r['oil']));self.assertGreater(out['metrics']['test']['heldout_cells'],0)
  # Test values never alter train normalization.
  te[0]['oil']=1e9
  changed=run_deep('grin',tr,va,te,inp,{'epochs':1})
  self.assertEqual(out['model_artifact']['mean'],changed['model_artifact']['mean'])
 def test_anomaly_labels_optional_and_actual_timing(self):
  tr=self.make_rows();va=self.make_rows(8);te=self.make_rows(16)
  out=run_deep('anomaly_transformer',tr,va,te,parameters={'epochs':1})
  self.assertEqual(len(out['results']),len(te));self.assertNotIn('F1',out['metrics']['test']);self.assertGreater(out['training_seconds'],0)
  for i,r in enumerate(va):r['label']=int(i>12)
  for i,r in enumerate(te):r['label']=int(i>12)
  out=run_deep('anomaly_transformer',tr,va,te,parameters={'epochs':1})
  self.assertIn('F1',out['metrics']['test']);self.assertEqual(out['model_artifact']['threshold_selection'],'validation_F1')
 def test_test_data_never_changes_train_weights_or_selection(self):
  triples=[{'head':'A','relation':'r','tail':'B'},{'head':'B','relation':'r','tail':'C'},{'head':'C','relation':'r','tail':'A'}]
  va=[{'head':'A','relation':'r','tail':'C'}]
  altered=[{'head':h,'relation':'r','tail':t} for h in ['A','B','C'] for t in ['A','B','C']]
  a=run_deep('rotate',triples,va,[],parameters={'epochs':8,'seed':2})
  b=run_deep('rotate',triples,va,altered,parameters={'epochs':8,'seed':2})
  self.assertEqual(a['model_artifact'],b['model_artifact']);self.assertEqual(a['history'],b['history']);self.assertEqual(a['metrics']['validation'],b['metrics']['validation'])
  for mid in ['grin','anomaly_transformer']:
   tr=self.make_rows();validation=self.make_rows(8);test=self.make_rows(16)
   changed=[dict(r,oil=1e6,pressure=1e5,label=1) for r in test]
   a=run_deep(mid,tr,validation,test,parameters={'epochs':2})
   b=run_deep(mid,tr,validation,changed,parameters={'epochs':2})
   self.assertEqual(a['model_artifact'],b['model_artifact'],mid);self.assertEqual(a['history'],b['history'],mid)
  rows=[{'doc_id':str(i),'content':f'井号为A{i}。','prompt':'井号','spans':[{'start':3,'end':5,'text':f'A{i}'}]} for i in range(4)]
  a=run_deep('uie',rows[:2],rows[2:3],rows[3:],parameters={'epochs':2})
  changed=[{'doc_id':'changed','content':'未知井的文本Z999。','prompt':'井号','spans':[{'start':0,'end':3,'text':'未知井'}]}]
  b=run_deep('uie',rows[:2],rows[2:3],changed,parameters={'epochs':2})
  self.assertEqual(a['model_artifact'],b['model_artifact']);self.assertEqual(a['history'],b['history'])
 def test_epoch_limit(self):
  with self.assertRaises(ValueError):run_deep('uie',[{}],[],[],parameters={'epochs':101})

if __name__=='__main__':unittest.main()
