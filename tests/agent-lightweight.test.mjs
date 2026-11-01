import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {normalizeRows,splitData} from '../dist/agent/core.mjs';
import {trainModel,predictModel} from '../dist/agent/models.mjs';
const read=p=>JSON.parse(fs.readFileSync(new URL('../dist/agent/data/'+p,import.meta.url)));
test('light samples are bounded, identify real sources, and preserve specialty labels',()=>{
 const manifest=read('lightweight.json');
 assert.equal(manifest.length,4);
 for(const entry of manifest){const rows=read(entry.file); assert.equal(rows.length,entry.count);assert.ok(entry.count<entry.source_count);assert.ok(fs.statSync(new URL('../dist/agent/data/'+entry.file,import.meta.url)).size<350000);assert.ok(entry.selection);}
 const events=read('samples/threew.json');assert.ok(new Set(events.map(r=>r.event_code)).size>=5);assert.ok(events.every(r=>r.event_id));
 const esp=read('samples/esp.json');assert.equal(new Set(esp.map(r=>r.fault)).size,5);
});
test('light production samples support actual per-well fitting and held-out prediction',async()=>{
 const rows=normalizeRows(read('samples/volve.json'));
 const [train,val,testRows]=splitData(rows,[70,15,15],'well-time');
 for(const id of ['arps','crm']){const fit=await trainModel(id,train,val);const results=await predictModel(fit,testRows);assert.ok(results.length>20);assert.ok(results.every(r=>Number.isFinite(r.prediction)));}
 for(const part of [train,val,testRows]) for(const well of new Set(part.map(r=>r.well_id))){const a=part.filter(r=>r.well_id===well);assert.ok(a.length>=10);for(let i=1;i<a.length;i++)assert.equal(Date.parse(a[i].date)-Date.parse(a[i-1].date),86400000);}
});
