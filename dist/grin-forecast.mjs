import {finite} from './algorithms.mjs';
export const GRIN_MARKS={
 observed:{label:'原始观测',color:'#0072B2',marker:'circle',encoding:'蓝色实线 / 圆点'},
 imputed:{label:'GRIN补全候选',color:'#00854A',marker:'square',encoding:'绿色方块'},
 rejected:{label:'拒绝接纳的预测',color:'#C62828',marker:'cross',encoding:'红色叉号'},
 truth:{label:'遮蔽评估真值',color:'#52525B',marker:'diamond',encoding:'深灰菱形'},
 forecast:{label:'未来时序预测',color:'#8E24AA',marker:'triangle',dashed:true,encoding:'紫色虚线 / 三角'},
 missing:{label:'原始缺失位置',color:'#D97706',marker:'band',encoding:'橙色底纹'}
};
export function describeGrinWindow(ex){const match=/^GRIN_TEST:(\d+)$/.exec(ex.window_id??''),offset=match?Number(match[1]):null,start=ex.dates?.[0]??'未知',end=ex.dates?.at(-1)??'未知';return{offset,start,end,records:ex.dates?.length??0,description:`GRIN 表示图循环插补网络；TEST 表示独立测试分区；${offset===null?'此编号未注明记录偏移':`冒号后的 ${offset} 是从0开始的窗口起始记录偏移（测试分区第 ${offset+1} 条记录）`}，不是预测天数、井号或模型版本。当前窗口为 ${start} 至 ${end}，共 ${ex.dates?.length??0} 条日记录。TEST是原GRIN的测试分区，不是附加预测头的独立未来测试集。窗口内进行缺失重建；后续时序预测从 ${end} 的下一日开始。`};}
function solve(matrix,rhs){const a=matrix.map((r,i)=>[...r,rhs[i]]),n=rhs.length;for(let c=0;c<n;c++){let pivot=c;for(let r=c+1;r<n;r++)if(Math.abs(a[r][c])>Math.abs(a[pivot][c]))pivot=r;[a[c],a[pivot]]=[a[pivot],a[c]];if(Math.abs(a[c][c])<1e-12)throw Error('预测头矩阵退化，请选择其他窗口');const scale=a[c][c];for(let j=c;j<=n;j++)a[c][j]/=scale;for(let r=0;r<n;r++)if(r!==c){const v=a[r][c];for(let j=c;j<=n;j++)a[r][j]-=v*a[c][j];}}return a.map(r=>r[n]);}
export function forecastCompletedSeries(rows,{horizon=7,order=3,lambda=10}={}){
 if(!Number.isInteger(horizon)||horizon<1||horizon>30)throw Error('预测天数必须为1至30的整数');
 if(rows.length<8)throw Error('时序预测至少8条连续日记录');
 if(rows.some(r=>!finite(r.output_value)))throw Error('补全后仍有缺失，不能直接训练预测头；请选择已完成补全且适用的变量');
 const dates=rows.map(r=>Date.parse(r.date+'T00:00:00Z'));if(dates.some((t,i)=>!Number.isFinite(t)||(i&&t-dates[i-1]!==864e5)))throw Error('预测输入必须按日期排序且连续，每日一条记录');
 if(!Number.isInteger(order)||order<1||order>Math.min(5,rows.length-4)||!Number.isFinite(lambda)||lambda<=0)throw Error('自回归阶数或正则参数无效');
 const started=performance.now(),values=rows.map(r=>Number(r.output_value)),mean=values.reduce((a,b)=>a+b,0)/values.length,std=Math.sqrt(values.reduce((a,b)=>a+(b-mean)**2,0)/values.length)||1,z=values.map(v=>(v-mean)/std),design=[],targets=[];
 for(let t=order;t<z.length;t++){design.push([1,...Array.from({length:order},(_,j)=>z[t-1-j])]);targets.push(z[t]);}
 const n=order+1,gram=Array.from({length:n},()=>Array(n).fill(0)),rhs=Array(n).fill(0);for(let i=0;i<design.length;i++)for(let j=0;j<n;j++){rhs[j]+=design[i][j]*targets[i];for(let k=0;k<n;k++)gram[j][k]+=design[i][j]*design[i][k];}for(let i=1;i<n;i++)gram[i][i]+=lambda;
 const coefficients=solve(gram,rhs),training_seconds=(performance.now()-started)/1000,history=z.slice(),future=[];for(let i=1;i<=horizon;i++){const y=coefficients[0]+coefficients.slice(1).reduce((sum,b,j)=>sum+b*history[history.length-1-j],0);if(!Number.isFinite(y)||Math.abs(y)>1e9)throw Error('递归预测数值发散，请缩短预测天数或更换窗口');history.push(y);const prediction=y*std+mean;future.push({date:new Date(dates.at(-1)+i*864e5).toISOString().slice(0,10),step:i,prediction,status:prediction<0?'负预测 · 待核查':'未来预测 · 待验证'});}
 return{method:'GRIN completion + causal ridge autoregression',origin:rows.at(-1).date,history_start:rows[0].date,horizon,order,lambda,coefficients,normalization:{mean,std},training_samples:design.length,training_seconds,rows:future,limitations:['GRIN负责窗口内重建；未来值由附加的因果岭回归自回归预测头逐步生成。','只使用截止日及之前的补全候选序列，不读取评估真值或截止日之后的观测。','短窗口研究基线，未经过独立未来区间验证；不将拟合误差称为预测准确率。','预测值不裁剪，负值保留并标为待核查；未建模未来生产制度或措施变化。']};
}
