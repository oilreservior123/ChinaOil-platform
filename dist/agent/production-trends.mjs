// Short-horizon descriptive baseline; never uses observations beyond the displayed cutoff.
const DAY=86400000;
const numeric=v=>(typeof v==='number'||typeof v==='string')&&String(v).trim()!==''&&Number.isFinite(Number(v))&&Number(v)>=0;
const day=s=>Date.parse(s)/DAY;
const iso=n=>new Date(n*DAY).toISOString().slice(0,10);
const ratio=(a,b)=>a!==null&&b!==null&&b>0?a/b:null;
const ratios=r=>({...r,oil_gas_ratio:ratio(r.oil,r.gas),gas_oil_ratio:ratio(r.gas,r.oil)});
function fit(points,key,origin){
 const a=points.filter(r=>numeric(r[key]));if(a.length<14)return null;
 const xs=a.map(r=>day(r.date)-origin),ys=a.map(r=>Number(r[key])),mx=xs.reduce((a,b)=>a+b,0)/a.length,my=ys.reduce((a,b)=>a+b,0)/a.length;
 const den=xs.reduce((s,x)=>s+(x-mx)**2,0),b=den?xs.reduce((s,x,i)=>s+(x-mx)*(ys[i]-my),0)/den:0;
 return {a:my-b*mx,b,n:a.length};
}
const predict=(model,t)=>model?Math.max(0,model.a+model.b*t):null;
export function productionTrends(rows,horizon=7){
 const started=performance.now();horizon=[7,14,30].includes(Number(horizon))?Number(horizon):7;
 const input=rows.filter(r=>r.well_id&&typeof r.date==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(r.date)&&Number.isFinite(day(r.date)));
 if(!input.length)return {history:[],future:[],models:{},wells:[],cutoff:null,duration:0};
 const cutoff=Math.max(...input.map(r=>day(r.date))),start=cutoff-29;
 const wells=[...new Set(input.filter(r=>day(r.date)>=start).map(r=>r.well_id))];
 const byDate=new Map();for(const r of input){if(!wells.includes(r.well_id)||day(r.date)<cutoff-89)continue;if(!byDate.has(r.date))byDate.set(r.date,[]);byDate.get(r.date).push(r);}
 const history=[];for(let d=cutoff-89;d<=cutoff;d++){
  const rs=byDate.get(iso(d))??[],complete=rs.length===wells.length&&new Set(rs.map(r=>r.well_id)).size===wells.length;
  const point={date:iso(d),well_count:rs.length};for(const k of ['oil','water','gas'])point[k]=complete&&rs.every(r=>numeric(r[k]))?rs.reduce((s,r)=>s+Number(r[k]),0):null;
  history.push(ratios(point));
 }
 const recent=history.filter(r=>day(r.date)>=start),models={};
 for(const key of ['oil','water','gas']){
  const model=recent.at(-1)[key]!==null?fit(recent,key,cutoff):null;
  const training=recent.filter(r=>day(r.date)<=cutoff-7),validation=recent.filter(r=>day(r.date)>cutoff-7&&r[key]!==null),heldFit=fit(training,key,cutoff);
  let metrics=null;if(heldFit&&validation.length>=4){const errors=validation.map(r=>predict(heldFit,day(r.date)-cutoff)-r[key]);metrics={N:errors.length,MAE:errors.reduce((s,x)=>s+Math.abs(x),0)/errors.length,RMSE:Math.sqrt(errors.reduce((s,x)=>s+x*x,0)/errors.length)};}
  models[key]={...model,available:!!model,validation:metrics,reason:model?'近期30天非负线性趋势基线':recent.at(-1)[key]===null?'截止日资料缺失或井覆盖不完整':'近30天有效日少于14天'};
 }
 const future=Array.from({length:horizon},(_,i)=>ratios({date:iso(cutoff+i+1),oil:predict(models.oil.available?models.oil:null,i+1),water:predict(models.water.available?models.water:null,i+1),gas:predict(models.gas.available?models.gas:null,i+1)}));
 return {history,future,models,wells,cutoff:iso(cutoff),duration:(performance.now()-started)/1000,horizon};
}
