"""Validate semantic split integrity, upload schemas and artifact hashes."""
import json,pathlib,zipfile,hashlib,csv
ROOT=pathlib.Path(__file__).resolve().parents[1]
b=ROOT/'dist/downloads/model-data';m=json.loads((b/'manifest.json').read_text());cs={x['id']:x for x in json.loads((ROOT/'backend/contracts.json').read_text())['models']}
assert len(m['models'])==13 and m['original_zip_complete_files']==76
for model in m['models']:
 mid=model['id'];files={sp:[json.loads(x) for x in (b/mid/f'{sp}.jsonl').read_text().splitlines()] for sp in ['train','validation','test','infer']}
 assert model['features']==cs[mid]['features']
 for sp,rows in files.items():
  for i,r in enumerate(rows):
   for f in cs[mid]['features']:
    if sp=='infer' and f.get('target'):continue
    if f.get('required') and f['name'] not in r:raise AssertionError((mid,sp,i,f['name']))
 if mid=='uie':
  assert not({r['doc_id'] for r in files['train']} & {r['doc_id'] for r in files['test']})
  for sp in ['train','validation','test']:
   for r in files[sp]:
    assert len(r['spans'])==1
    assert len(r['prompt'])+len(r['content'])<255
    for s in r['spans']:assert r['content'][s['start']:s['end']]==s['text']
 if mid=='rotate':
  ent={r[k] for r in files['train'] for k in ['head','tail']};rels={r['relation'] for r in files['train']}
  for sp in ['validation','test']:
   for r in files[sp]:assert r['head'] in ent and r['tail'] in ent and r['relation'] in rels
 if mid in ['grin','anomaly_transformer']:
  for sp in ['validation','test']:assert len({r['date'] for r in files[sp]})>=32
 if mid=='isolation_forest':
  assert not({r['well_id'] for r in files['train']} & {r['well_id'] for r in files['test']})
 if mid in ['grin','anomaly_transformer','arps','crm','lag','rules']:
  assert max(r['date'] for r in files['train'])<min(r['date'] for r in files['validation'])
  assert max(r['date'] for r in files['validation'])<min(r['date'] for r in files['test'])
 print(mid,model['counts'],'OK')
for f in m['files']:assert hashlib.sha256((b/f['path']).read_bytes()).hexdigest()==f['sha256']
with zipfile.ZipFile(b/'model_data_kit.zip') as z:assert z.testzip() is None
print('PASS 13 schemas, 76 source mappings, spans, document/time/well splits, graph coverage, hashes and ZIP CRC')
