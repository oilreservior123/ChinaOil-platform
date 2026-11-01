"""Reproducible synthetic scenarios, never presented as field measurements."""
import json,csv,math,random
from pathlib import Path
from datetime import date,timedelta
out=Path(__file__).resolve().parents[1]/'dist/decision/data';out.mkdir(parents=True,exist_ok=True)
rng=random.Random(20261101)
def save(name,rows):
 (out/(name+'.json')).write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':')))
 if rows:
  with (out/(name+'.csv')).open('w',newline='',encoding='utf-8-sig') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
prod=[];inj=[];layers=[];profiles=[];measures=[];evolution=[];cases=[]
I1=[];I2=[]
for d in range(180):
 dt=str(date(2025,1,1)+timedelta(days=d));I1.append(460+90*math.sin(d*.27)+rng.gauss(0,25));I2.append(390+80*math.cos(d*.19)+rng.gauss(0,22))
 for i,arr in enumerate([I1,I2]):inj.append(dict(date=dt,well_id='I-0'+str(i+1),injection=round(arr[-1],3),pressure=round(18+.001*d,4),source='合成注水响应场景'))
 for j in range(3):
  lag=3+j*2;local=.25*I1[max(0,d-lag)]+.17*I2[max(0,d-lag-1)];liq=220+j*30+.35*local+rng.gauss(0,2);wc=min(88,35+j*12+d*.08);oil=liq*(1-wc/100);pressure=23-j*.4-.006*d+.0006*local
  prod.append(dict(well_id='P-0'+str(j+1),date=dt,oil=round(oil,3),water=round(liq-oil,3),liquid=round(liq,3),gas=round(oil*80,3),pressure=round(pressure,4),injection=round(local,3),water_cut=round(wc,3),x=round((j+1)/4,3),t=round(d/179,4),Bo=1.15,Bw=1.02,label=int(d%50 in range(30,35)),root_cause='供液不足' if d%50 in range(30,35) else '正常',source='合成井组场景，非实测'))
for j in range(3):
 for l in range(3):
  layers.append(dict(well_id='P-0'+str(j+1),layer='L'+str(l+1),permeability=round(80+l*100+j*15,2),thickness=5+l*2,porosity=.18+l*.02,saturation=.6-l*.06,connectivity=.75-l*.18,water_cut=35+l*20,pressure=22-l*.4,fracture=31,injectivity=18+l*8,min=10,max=300,weight=3-l,source='合成小层属性'))
  for t in range(20):profiles.append(dict(well_id='P-0'+str(j+1),sample_id=str(l)+'-'+str(t),date=str(date(2025,1,1)+timedelta(days=t*7)),layer='L'+str(l+1),permeability=80+l*100+j*15,thickness=5+l*2,porosity=.18+l*.02,connectivity=.75-l*.18,water_cut=35+l*20,fraction=round([.25,.4,.35][l]+rng.gauss(0,.015),4),source='合成剖面监督样本，未提供实测剖面'))
for n in range(90):
 k=80+n%5*50;h=5+n%4;wc=30+n%50;kind=['酸化','堵水','调参'][n%3];gain=max(0,18+.07*k+2*h-.25*wc+rng.gauss(0,3))
 measures.append(dict(well_id='CASE-'+str(n),sample_id=str(n),date=str(date(2023,1,1)+timedelta(days=n*5)),permeability=k,thickness=h,water_cut=wc,measure_code=n%3,measure_type=kind,incremental=round(gain,3),cost=50000+n%4*10000,source='合成措施训练样本，非现场增油效果'))
for n in range(180):
 d=n+1;base=110*math.exp(-.001*d);oil=base+25*math.exp(-.008*d)+rng.gauss(0,1)
 cases.append(dict(well_id='P-01',date=str(date(2025,7,1)+timedelta(days=n)),oil=round(oil,3),baseline=round(base,3),source='合成措施后跟踪及已知反事实基线'))
for phase in range(12):
 for j in range(3):
  e=phase*.5;k=80+j*180
  evolution.append(dict(well_id='P-0'+str(j+1),sample_id=str(phase),date=str(date(2024+phase//12,phase%12+1,1)),exposure=e,permeability=round(k*(1+.1*math.log1p(e)),3),porosity=.18+.002*e,viscosity=round(3*(1+.04*e),3),residualOil=round(.28-.01*e,3),source='合成阶段物性，变化系数未现场标定'))
for name,rows in [('production',prod),('injection',inj),('layers',layers),('profiles',profiles),('measures',measures),('followup',cases),('evolution',evolution)]:save(name,rows)
knowledge=[
 dict(id='K01',anomaly='产油下降且压力下降',cause='能量不足候选',measure='复核压力与注采资料，按层补充注水',condition='排除停井、计量变化；地下体积注采比偏低',evidence='PPT35、39、41页',success=None),
 dict(id='K02',anomaly='含水上升且注采响应强',cause='水窜候选',measure='示踪剂与剖面验证后评估堵水或调剖',condition='优势通道有独立证据，满足施工与地层条件',evidence='PPT33、37、40页',success=None),
 dict(id='K03',anomaly='注入压力上升且吸水能力下降',cause='近井堵塞候选',measure='复核水质、洗井，评估解堵或酸化',condition='排除仪表故障；具备配伍性和伤害诊断',evidence='PPT32–34页',success=None),
 dict(id='K04',anomaly='高含水层产液强度偏高',cause='无效水循环候选',measure='在产油、设备及地面处理约束内调整分层产液',condition='具备分层产液与含水测试',evidence='PPT38–40页',success=None),
 dict(id='K05',anomaly='预测与实际持续偏离',cause='参数或工况漂移候选',measure='复核当前阶段物性并触发重训审核',condition='措施偏差>25%；劈分偏差>15%；注采响应偏差>20%',evidence='PPT34、38、39、45–47页',success=None)
]
(out/'knowledge.json').write_text(json.dumps(knowledge,ensure_ascii=False,indent=2))
tracer=[]
for i in range(1,101):
 t=i*.2;L=100;v=12;D=20;c=10/math.sqrt(4*math.pi*D*t)*math.exp(-(L-v*t)**2/(4*D*t))
 tracer.append(dict(well_id='I-01→P-01',sample_id=str(i),time_days=t,distance_m=L,concentration=c,source='一维方程合成示踪剂，非实测'))
save('tracer',tracer)
print({p.name:p.stat().st_size for p in out.glob('*.json')})
