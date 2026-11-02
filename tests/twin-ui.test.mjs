import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
test('all seven views render production data, scientific notes and model controls',async()=>{
 const box={innerHTML:''},toast={textContent:'',classList:{add(){},remove(){}}},listeners={};
 globalThis.document={querySelector:s=>s==='#app'?box:s==='#toast'?toast:null,querySelectorAll:()=>[],getElementById:()=>null};
 globalThis.window={addEventListener:(name,fn)=>listeners[name]=fn,scrollTo(){}};
 globalThis.location={hash:''};
 globalThis.fetch=async path=>({ok:true,text:()=>readFile(new URL('../dist/twin/'+path,import.meta.url),'utf8')});
 await import('../dist/twin/app.mjs');
 for(let i=0;i<100&&!box.innerHTML.includes('180 条记录');i++)await new Promise(r=>setTimeout(r,5));
 assert.match(box.innerHTML,/180 条记录/);
 for(const [view,expected] of [['overview','体'],['schemes','方案对比'],['forecast','日产气'],['optimise','Pareto'],['evaluate','窗口增量净现值'],['models','动态监测JSON数组'],['report','本地计算依据报告']]){
  location.hash='#'+view;listeners.hashchange();assert.match(box.innerHTML,new RegExp(expected));assert.doesNotMatch(box.innerHTML,/<div class="error-banner">/);
  if(view==='forecast'){assert.equal((box.innerHTML.match(/· 历史与预测/g)||[]).length,5);assert.match(box.innerHTML,/水量÷|油量÷水量/);}
  if(view==='models'){assert.match(box.innerHTML,/训练126 \/ 验证27 \/ 测试27/);assert.match(box.innerHTML,/Ridge-AR/);assert.match(box.innerHTML,/GA · 离散/);}
 }
});
