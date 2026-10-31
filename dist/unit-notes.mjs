import{esc}from'./ui.mjs';
export const UNIT_NOTES={
 'Sm³/d':'标准立方米/日','Sm3/d':'标准立方米/日','Sm³/day':'标准立方米/日','Sm3/day':'标准立方米/日','Sm³/h':'标准立方米/小时','Sm3/h':'标准立方米/小时','Sm³':'标准立方米','Sm3':'标准立方米',
 'm³/d':'立方米/日','m3/d':'立方米/日','m³/day':'立方米/日','m3/day':'立方米/日','m³/s':'立方米/秒','m3/s':'立方米/秒','m³':'立方米','m3':'立方米','m²':'平方米','m2':'平方米',
 'g/cm³':'克/立方厘米','g/cm3':'克/立方厘米','kg/m³':'千克/立方米','kg/m3':'千克/立方米','µs/ft':'微秒/英尺','μs/ft':'微秒/英尺','us/ft':'微秒/英尺',
 'mPa·s':'毫帕·秒','Pa·s':'帕·秒','mPa.s':'毫帕·秒','Pa.s':'帕·秒','cP':'厘泊','mD':'毫达西','MPa':'兆帕','kPa':'千帕','Pa':'帕','bar':'巴','psi':'磅/平方英寸',
 'km':'千米','cm':'厘米','mm':'毫米','µm':'微米','μm':'微米','ft':'英尺','m':'米','ms':'毫秒','µs':'微秒','μs':'微秒','s':'秒','h':'小时','hr':'小时','hrs':'小时','d':'日','day':'日','days':'日',
 '°C':'摄氏度','deg':'度','rad':'弧度','°':'度','%':'百分比','ppm':'百万分之一','fraction':'比例，0至1，无量纲','API':'自然伽马测井刻度'
};
const escapeRegex=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
const candidates=Object.keys(UNIT_NOTES).filter(x=>!['API','%','°'].includes(x)).sort((a,b)=>b.length-a.length);
const combined=new RegExp(`(?<![A-Za-z_µμ])(${candidates.map(escapeRegex).join('|')})(?![A-Za-z_³0-9])`,'g');
const fieldUnits=[[/_m3_day$/,'立方米/日'],[/_sm3$/,'标准立方米'],[/_mpa$/i,'兆帕'],[/_mm$/,'毫米'],[/_m$/,'米'],[/_deg$/,'度'],[/_days$/,'日'],[/_seconds$/,'秒']];
export function unitNote(unit){let key=String(unit??'').trim().replace(/\s*\/\s*/g,'/');return UNIT_NOTES[key]??null;}
export function annotateUnitText(value,{allowAPI=false}={}){let text=String(value??'');if(!text.trim())return text;
 text=text.replace(combined,(match,key,offset,whole)=>{const before=whole.slice(0,offset),after=whole.slice(offset+match.length);if(after.trimStart().startsWith('（'+UNIT_NOTES[key]+'）'))return match;if(['m','s','h','d'].includes(key)&&!/^\s*[mshd]\s*$/.test(whole)&&!/(?:[\d.]\s*|[/·]\s*|(?:测深|深度|长度|厚度|距离|宽度|高度|时间|时长|间隔|单位)[:：]?\s*)$/.test(before))return match;return match+'（'+UNIT_NOTES[key]+'）'});
 if((allowAPI||text.trim()==='API'||/^GR\s*[/（(]\s*API\b/.test(text))&&!text.includes('API（'))text=text.replace(/\bAPI\b(?!请求|接口|文档|文档)/g,'API（'+UNIT_NOTES.API+'）');
 if(/^[A-Za-z][A-Za-z0-9_]*$/.test(text)){for(const[re,note]of fieldUnits)if(re.test(text)){text+='（'+note+'）';break}}
 return text;
}
export function unitLabel(unit){const note=unitNote(unit);return note?`${unit}（${note}）`:annotateUnitText(unit);}
export function annotateUnits(root){if(!root?.ownerDocument)return;const walker=root.ownerDocument.createTreeWalker(root,4);const changes=[];let node;while(node=walker.nextNode()){const p=node.parentElement;if(!p||p.closest('script,style,pre,code,input,textarea,a,[data-unit-legend],.math-equation,.theory-architecture,.brand,.eyebrow'))continue;const old=node.nodeValue;if(!old||old.length>1800)continue;const value=annotateUnitText(old);if(value!==old)changes.push([node,value])}for(const[n,t]of changes)n.nodeValue=t;}
export function observeUnitNotes(root){let observer,queued=false;const refresh=()=>{queued=false;observer.disconnect();annotateUnits(root);observer.observe(root,{subtree:true,childList:true,characterData:true})};observer=new MutationObserver(()=>{if(!queued){queued=true;queueMicrotask(refresh)}});refresh();return()=>observer.disconnect();}
export function renderUnitLegend(){const preferred=['Sm³/d','Sm³','m³/d','m³/s','m³','MPa','Pa','bar','psi','m','mm','ft','g/cm³','µs/ft','mD','cP','Pa·s','s','h','d','°','fraction','API'];return`<details class="unit-legend" data-unit-legend><summary>计量单位中文释义 · 点击查看完整对照</summary><p>界面保留原计量符号并添加中文注释；这不是数值换算。原压力口径未核定时，继续显示“源单位未核定”，不擅自改为兆帕。标识、数据字段名和导出文件保持原始格式。</p><div class="unit-legend-grid">${preferred.map(k=>`<div><code>${esc(k)}</code><span>${esc(UNIT_NOTES[k])}</span></div>`).join('')}</div><p>API在自然伽马测井中是约定刻度；“API接口”中的API表示应用程序编程接口，不是计量单位。标准立方米与实际立方米的条件不同，不能直接混用。黏度换算：1 cP（厘泊）= 1 mPa·s（毫帕·秒）。</p></details>`}
