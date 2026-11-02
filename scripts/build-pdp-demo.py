"""Generate a clearly-labelled block scenario and public Volve trend case summaries."""
import json,csv,random,math,calendar
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'dist/decision/data';rng=random.Random(20261102)
rows=[];noise=0
for i in range(46):
 y=2023+i//12;m=i%12+1;month=f'{y}-{m:02d}';days=calendar.monthrange(y,m)[1];wells=100 if i<39 else 93;noise=.4*noise+rng.gauss(0,.018);shock=1 if i<39 else .84-.008*(i-39)
 oil=50*math.exp(-.014*i)*days*wells*math.exp(noise)*shock
 rows.append(dict(month=month,oil_tonnes=round(oil,3),active_wells=wells,water_m3=round(200000+i*4500+(max(0,i-38)*3500),3),pressure_mpa=round(24-i*.03-(1.1+max(0,i-39)*.06 if i>=39 else 0),3),injection_m3=round(420000-i*1300-(22000 if i>=39 else 0),3),density_t_per_m3=.85,source='A区块生成月度场景，非新疆现场实测'))
(out/'pdp-monthly.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
with (out/'pdp-monthly.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
public=json.loads((root/'dist/agent/data/samples/volve.json').read_text());cases=[]
def avg(v):return sum(v)/len(v) if v else None
for well in sorted(set(r['well_id'] for r in public)):
 a=sorted([r for r in public if r['well_id']==well],key=lambda r:r['date']);first=a[:30];last=a[-30:];o0=avg([r['oil'] for r in first]);o1=avg([r['oil'] for r in last]);p0=avg([r['pressure'] for r in first if r.get('pressure',0)>0]);p1=avg([r['pressure'] for r in last if r.get('pressure',0)>0]);wc0=100*sum(r['water'] for r in first)/sum(r['liquid'] for r in first);wc1=100*sum(r['water'] for r in last)/sum(r['liquid'] for r in last);h0=avg([r['on_stream_hours'] for r in first if r.get('on_stream_hours') is not None]);h1=avg([r['on_stream_hours'] for r in last if r.get('on_stream_hours') is not None]);cases.append(dict(id='VOLVE-'+well,well=well,start=a[0]['date'],end=a[-1]['date'],source='Volve公开实测抽样：各井首末30日趋势对照',oil_change_pct=100*(o1/o0-1) if o0 else None,water_cut_delta_pp=wc1-wc0,pressure_delta_mpa=p1-p0 if p0 and p1 else None,availability_change_pct=100*(h1/h0-1) if h0 and h1 else None,conclusion='仅证明观测趋势相似；原样本未提供本研究措施因果效果或成功率。',data_path='../agent/data/samples/volve.json'))
(out/'pdp-cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2))
print('monthly records',len(rows),'public trend cases',len(cases))
