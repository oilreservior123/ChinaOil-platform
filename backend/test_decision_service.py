import importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('decision_service',Path(__file__).with_name('decision_service.py'))
try:
 service=importlib.util.module_from_spec(spec);spec.loader.exec_module(service)
except FileNotFoundError:
 service=None
class DecisionServiceTests(unittest.TestCase):
 def test_auth_requires_configured_strong_token(self):
  self.assertIsNotNone(service)
  self.assertFalse(service.authorized('Bearer abc',''))
  self.assertFalse(service.authorized('Bearer abc','abc'))
  self.assertTrue(service.authorized('Bearer abcdefghijklmnop','abcdefghijklmnop'))
  self.assertFalse(service.authorized('Bearer bad','abcdefghijklmnop'))
 def test_upstream_messages_require_evidence_and_preserve_source(self):
  self.assertIsNotNone(service)
  m=service.build_messages({'question':'分析当前生产','evidence':{'source':'synthetic','tools':{}}})
  self.assertIn('synthetic',m[1]['content']);self.assertIn('不可信',m[0]['content'])
  with self.assertRaises(ValueError):service.build_messages({'question':'','evidence':{}})
 def test_model_input_rejects_nonfinite_and_target_leakage(self):
  self.assertIsNotNone(service)
  keys=['lag_oil','lag_water','lag_pressure','lag_injection','lag_water_cut']
  row={k:1 for k in keys};row['oil']=2
  x,y=service.matrix([row],True);self.assertEqual(len(x[0]),5);self.assertEqual(y,[2])
  row['lag_oil']=float('nan')
  with self.assertRaises(ValueError):service.matrix([row],True)
if __name__=='__main__':unittest.main()
