import {linearModel,intervalAt,t95} from './expert-stats.mjs?v=20261102-expert1';
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
 return {a:my-b*mx,b,n:a.length,uncertainty:linearModel(a.map((r,i)=>({x:xs[i],y:ys[i]})))};
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
 const paired=recent.filter(r=>numeric(r.oil)&&numeric(r.gas)),o=models.oil.uncertainty,g=models.gas.uncertainty,aligned=o&&g&&paired.length===o.n&&paired.length===g.n,cov=aligned?paired.reduce((s,r)=>{const x=day(r.date)-cutoff;return s+(r.oil-o.a-o.b*x)*(r.gas-g.a-g.b*x);},0)/(paired.length-2):null;
 const future=Array.from({length:horizon},(_,i)=>{const t=i+1,row={date:iso(cutoff+t)};for(const k of ['oil','water','gas']){const band=intervalAt(models[k].available?models[k].uncertainty:null,t);row[k]=band.prediction;row[k+'_low95']=band.low95;row[k+'_high95']=band.high95;row[k+'_mean_low95']=band.meanLow95;row[k+'_mean_high95']=band.meanHigh95;row[k+'_confidence']=band.confidence;row[k+'_model']=band.model??'OLS趋势（资料不足）';}const out=ratios(row);out.oil_gas_ratio_low95=null;out.oil_gas_ratio_high95=null;out.oil_gas_ratio_mean_low95=null;out.oil_gas_ratio_mean_high95=null;out.ratio_confidence='无法计算有限比值区间：缺少同窗油气误差协方差、非负边界或分母接近零';if(aligned&&row.gas_low95>0&&row.oil>0&&row.gas>0){const O=row.oil,G=row.gas,h=1/o.n+(t-o.mx)**2/o.sxx,v=Math.max(0,o.s2/G**2+O**2*g.s2/G**4-2*O*cov/G**3),c=t95(o.n-2),pi=c*Math.sqrt(v*(1+h)),ci=c*Math.sqrt(v*h);out.oil_gas_ratio_low95=Math.max(0,out.oil_gas_ratio-pi);out.oil_gas_ratio_high95=out.oil_gas_ratio+pi;out.oil_gas_ratio_mean_low95=Math.max(0,out.oil_gas_ratio-ci);out.oil_gas_ratio_mean_high95=out.oil_gas_ratio+ci;out.ratio_confidence='Delta法条件近似95%区间，计入同窗油气残差协方差；分母远离0、线性及误差假设成立时适用，未保证覆盖';}return out;});
 return {history,future,models,wells,cutoff:iso(cutoff),duration:(performance.now()-started)/1000,horizon};
}
