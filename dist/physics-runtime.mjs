/** Compact, actually-computed EDFM-style two-phase demo. See physics-assets.json assumptions. */
const DAY = 86400, SWC = .15, MAXSW = .85;
const dot=(a,b)=>{let s=0;for(let i=0;i<a.length;i++)s+=a[i]*b[i];return s};
function fluid(s) {const e=Math.max(0,Math.min(1,(s-SWC)/.7)),w=e*e/.001,o=(1-e)*(1-e)/.003;return {mobility:w+o,fw:w/(w+o)}}
function pcg(diag, links, b, initial, maxIter=1600) {
  const n=b.length,x=Float64Array.from(initial||new Float64Array(n));
  const mv=v=>{const y=Float64Array.from(v,(z,i)=>z*diag[i]);for(const [i,j,c] of links){y[i]-=c*v[j];y[j]-=c*v[i]}return y};
  let ax=mv(x),r=Float64Array.from(b,(z,i)=>z-ax[i]),z=Float64Array.from(r,(v,i)=>v/diag[i]),p=Float64Array.from(z),rz=dot(r,z),target=Math.max(dot(b,b),1e-30)*1e-22,it=0;
  for(;it<maxIter && dot(r,r)>target;it++) {
    const ap=mv(p),den=dot(p,ap);if(!(den>0))break;const alpha=rz/den;
    for(let i=0;i<n;i++){x[i]+=alpha*p[i];r[i]-=alpha*ap[i]}
    z=Float64Array.from(r,(v,i)=>v/diag[i]);const next=dot(r,z),beta=next/rz;
    for(let i=0;i<n;i++)p[i]=z[i]+beta*p[i];rz=next;
  }
  const rem=mv(x);let err=0;for(let i=0;i<n;i++)err=Math.max(err,Math.abs(rem[i]-b[i]));return {x,iterations:it,residual:err};
}
function solvePressure(sw,g,apertureMm,dropMPa,warm) {
  const n=sw.length,base=g.reference_aperture_mm,ratio=apertureMm/base,mob=Float64Array.from(sw,s=>fluid(s).mobility),ei=g.edge_i,ej=g.edge_j;
  const conduct=Float64Array.from(g.transmissibility_base_m3,(t,e)=>t*Math.pow(ratio,g.edge_aperture_power[e])*2*mob[ei[e]]*mob[ej[e]]/(mob[ei[e]]+mob[ej[e]]));
  const fixed=new Map([...g.left_cells.map(x=>[x,1]),...g.right_cells.map(x=>[x,0])]);const free=[],index=new Int32Array(n).fill(-1);for(let i=0;i<n;i++)if(!fixed.has(i)){index[i]=free.length;free.push(i)}
  const diag=new Float64Array(free.length),rhs=new Float64Array(free.length),links=[];
  for(let e=0;e<ei.length;e++){const i=ei[e],j=ej[e],a=index[i],b=index[j],c=conduct[e];if(a>=0){diag[a]+=c;if(b<0)rhs[a]+=c*fixed.get(j)}if(b>=0){diag[b]+=c;if(a<0)rhs[b]+=c*fixed.get(i)}if(a>=0&&b>=0)links.push([a,b,c])}
  const init=free.map(i=>warm?warm[i]:1-(g.node_centers[i][0]/g.width_m));const sol=pcg(diag,links,rhs,init);const u=new Float64Array(n);for(const [i,value]of fixed)u[i]=value;for(let i=0;i<free.length;i++)u[free[i]]=sol.x[i];
  const flux=new Float64Array(ei.length),balance=new Float64Array(n);let qmax=0;
  for(let e=0;e<ei.length;e++){const q=conduct[e]*dropMPa*1e6*(u[ei[e]]-u[ej[e]]);flux[e]=q;balance[ei[e]]+=q;balance[ej[e]]-=q;qmax=Math.max(qmax,Math.abs(q))}
  let res=0;for(const i of free)res=Math.max(res,Math.abs(balance[i]));const source=Float64Array.from(balance,(q,i)=>fixed.has(i)?q:0);
  return {u,pressureMPa:Float64Array.from(u,v=>25+dropMPa*v),flux,source,relativeResidual:res/Math.max(qmax,1e-30),cgIterations:sol.iterations};
}
function solveTransport(old,dt,pv,g,flow) {
  const n=old.length,upstream=Array.from({length:n},()=>[]),out=new Float64Array(n),inj=new Float64Array(n);
  for(let e=0;e<g.edge_i.length;e++){const q=flow.flux[e],up=q>=0?g.edge_i[e]:g.edge_j[e],down=q>=0?g.edge_j[e]:g.edge_i[e],abs=Math.abs(q);out[up]+=abs;upstream[down].push([up,abs])}
  for(let i=0;i<n;i++){inj[i]=Math.max(0,flow.source[i]);out[i]+=Math.max(0,-flow.source[i])}
  // Scalar-pressure fluxes form a DAG (strictly decreasing potential). Thus
  // fully implicit upstream transport is solved by monotone scalar roots.
  const order=Array.from({length:n},(_,i)=>i).sort((a,b)=>flow.u[b]-flow.u[a]),s=Float64Array.from(old),fw=new Float64Array(n);let residual=0;
  for(const i of order){let input=inj[i];for(const [j,q]of upstream[i])input+=q*fw[j];const capacity=pv[i]/dt;
    let low=SWC,high=MAXSW;for(let k=0;k<48;k++){const mid=(low+high)/2,r=capacity*(mid-old[i])+out[i]*fluid(mid).fw-input;if(r>0)high=mid;else low=mid}s[i]=(low+high)/2;fw[i]=fluid(s[i]).fw;residual=Math.max(residual,Math.abs(capacity*(s[i]-old[i])+out[i]*fw[i]-input));
  }
  return {s,fw,residual};
}
export async function simulateEDFM(graph, options={}, onProgress=null) {
  const apertureMm=Number(options.apertureMm??.5),pressureDropMPa=Number(options.pressureDropMPa??5),durationDays=Number(options.durationDays??180),requestedSteps=Number(options.timeSteps??30);
  if(!Number.isFinite(requestedSteps))throw new Error('Finite time step count required');
  const timeSteps=Math.max(6,Math.min(120,Math.round(requestedSteps)));
  if(!(apertureMm>=.05&&apertureMm<=2&&pressureDropMPa>=.1&&pressureDropMPa<=15&&durationDays>0&&durationDays<=365))throw new Error('EDFM demonstration parameter outside supported bounds');
  const g=graph,n=g.node_centers.length,pv=Float64Array.from(g.pore_volume_base_m3,(v,i)=>v*(i<g.matrix_count?1:apertureMm/g.reference_aperture_mm)),initial=new Float64Array(n).fill(.17);let s=Float64Array.from(initial),warm=null,totalIn=0,totalOut=0,maxResidual=0,maxTransport=0,cgMax=0;
  const dt=durationDays*DAY/timeSteps,curve=[],snapshots=[];const makeSnap=(day,f)=>({day,matrix_pressure_mpa:Array.from({length:g.ny},(_,j)=>Array.from(f.pressureMPa.slice(j*g.nx,(j+1)*g.nx))),matrix_water_saturation:Array.from({length:g.ny},(_,j)=>Array.from(s.slice(j*g.nx,(j+1)*g.nx))),fracture_pressure_mpa:Array.from(f.pressureMPa.slice(g.matrix_count)),fracture_water_saturation:Array.from(s.slice(g.matrix_count))});
  let flow=solvePressure(s,g,apertureMm,pressureDropMPa,warm);snapshots.push(makeSnap(0,flow));
  for(let step=0;step<timeSteps;step++) {
    flow=solvePressure(s,g,apertureMm,pressureDropMPa,warm);warm=flow.u;maxResidual=Math.max(maxResidual,flow.relativeResidual);cgMax=Math.max(cgMax,flow.cgIterations);
    const transport=solveTransport(s,dt,pv,g,flow);s=transport.s;maxTransport=Math.max(maxTransport,transport.residual);let qi=0,qw=0,ql=0;
    for(let i=0;i<n;i++){qi+=Math.max(0,flow.source[i]);const prod=Math.max(0,-flow.source[i]);ql+=prod;qw+=prod*transport.fw[i]}
    totalIn+=qi*dt;totalOut+=qw*dt;const day=(step+1)*durationDays/timeSteps;
    curve.push({day,oil_m3_day:(ql-qw)*DAY,water_m3_day:qw*DAY,liquid_m3_day:ql*DAY,injected_water_m3_day:qi*DAY,water_cut:qw/Math.max(ql,1e-30)});
    if((step+1)%Math.max(1,Math.round(timeSteps/6))===0||step===timeSteps-1){const f=solvePressure(s,g,apertureMm,pressureDropMPa,warm);snapshots.push(makeSnap(day,f))}
    if(onProgress){onProgress({progress:(step+1)/timeSteps,day,production:curve.at(-1)});await new Promise(resolve=>setTimeout(resolve,0))}
  }
  const stored=dot(pv,Float64Array.from(s,(v,i)=>v-initial[i])),closure=stored-(totalIn-totalOut);
  return {model:'2D compact EDFM oil/water live browser solve',provenance:'actually_computed_browser_generated_scenario_not_field_measurement',parameters:{aperture_mm:apertureMm,pressure_drop_mpa:pressureDropMPa,duration_days:durationDays},snapshots,production_curve:curve,metrics:{pressure_relative_residual_max:maxResidual,water_mass_balance_relative_error:Math.abs(closure)/Math.max(totalIn,1),water_mass_balance_absolute_m3:closure,cumulative_injected_water_m3:totalIn,cumulative_produced_water_m3:totalOut,domain_water_storage_change_m3:stored,transport_residual_max_m3_s:maxTransport,pressure_CG_iterations_max:cgMax,accepted_time_steps:timeSteps},limitations:g.limitations};
}
