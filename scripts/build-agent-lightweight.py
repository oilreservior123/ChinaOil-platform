"""Extract traceable real subsets; run against the full source checkout before packaging."""
import json, math, hashlib
from pathlib import Path
from collections import defaultdict
from datetime import date
P=Path(__file__).resolve().parents[1]/'dist/agent/data'
(P/'samples').mkdir(exist_ok=True)
manifest=[]
def read(name):return json.loads((P/name).read_text())
def valid(r,keys):return all(isinstance(r.get(k),(int,float)) and math.isfinite(r[k]) for k in keys)
def save(id,rows,source,selection):
 raw=json.dumps(rows,ensure_ascii=False,separators=(',',':'))
 (P/f'samples/{id}.json').write_text(raw)
 manifest.append(dict(id=id,file=f'samples/{id}.json',count=len(rows),source_count=len(read(source)),bytes=len(raw.encode()),source_sha256=hashlib.sha256((P/source).read_bytes()).hexdigest(),selection=selection))
# Preserve actual consecutive days and enough held-out windows. Common high-coverage time interval.
a=read('volve.json');groups=defaultdict(list)
for r in a:
 if valid(r,['oil','water','pressure','injection','water_cut']) and all(r[k]>=0 for k in ['oil','water','injection']) and 0<=r['water_cut']<=100:groups[r['well_id']].append(r)
windows={}
for w,rows in groups.items():
 rows.sort(key=lambda r:r['date']);runs=[];run=[]
 for r in rows:
  if run and (date.fromisoformat(r['date'])-date.fromisoformat(run[-1]['date'])).days!=1:runs.append(run);run=[]
  run.append(r)
 runs.append(run);best=max(runs,key=len)
 if len(best)>=120:windows[w]=best[:180]
rows=sorted([r for a in windows.values() for r in a],key=lambda r:(r['date'],r['well_id']))
save('volve',rows,'volve.json','各井最长完整连续日段取前180天，至少120天；保留真实日期与多井关系；仅用于快速流程验证，非全油田代表性评价。')
for id,source,keys,label,cap in [('threew','threew-events.json',['p_mean','p_std','t_mean','t_std','p_delta','t_delta'],'event_code',24),('esp','esp-features.json',['f_low','f_rms','f_near','f_1x','f_2x','f_a','f_b'],'fault',36)]:
 groups=defaultdict(list)
 for r in read(source):
  if valid(r,keys):groups[str(r[label])].append(r)
 rows=[]
 for k,items in sorted(groups.items()):
  n=min(cap,len(items));rows.extend(items[round(i*(len(items)-1)/max(1,n-1))] for i in range(n))
 save(id,rows,source,f'按真实{label}类别均匀间隔抽取，每类最多{cap}条；保留事件/样本标识；小样本及随机划分只用于快速验证。')
groups=defaultdict(list)
for r in read('dst.json'):
 if valid(r,['log_horner','pressure','time_min']):groups[r['test_id']].append(r)
rows=[]
for key,items in sorted(groups.items(),key=lambda x:(-len(x[1]),x[0]))[:4]:
 items.sort(key=lambda r:r['time_min']);n=min(60,len(items));rows.extend(items[round(i*(len(items)-1)/(n-1))] for i in range(n))
save('dst',rows,'dst.json','选择观测数最多的4段测试，每段均匀抽取最多60个原始观测；径向流解释段仍需人工筛选。')
(P/'lightweight.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
for e in manifest:print(e['id'],e['count'],e['bytes'])
