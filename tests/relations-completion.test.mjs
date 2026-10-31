import test from 'node:test';
import assert from 'node:assert/strict';
import * as a from '../dist/algorithms.mjs';
test('entity relations keep direction, evidence and the actual endpoints',()=>{
 assert.equal(typeof a.entityRelations,'function');
 const graph={nodes:[{id:'a',label:'A井'},{id:'b',label:'B层'},{id:'c',label:'C区'}],edges:[{source_id:'a',target_id:'b',relation:'INTERSECTS_FORMATION',source_dataset:'FORCE',properties:{depth:23}},{source_id:'c',target_id:'a',relation:'BELONGS_TO_FIELD'},{source_id:'b',target_id:'c',relation:'OTHER'}]};
 const rows=a.entityRelations(graph,'a');assert.equal(rows.length,2);assert.equal(rows[0].source.label,'A井');assert.equal(rows[0].target.label,'B层');assert.equal(rows[0].direction,'outgoing');assert.equal(rows[1].direction,'incoming');assert.equal(rows[0].properties.depth,23);assert.equal(rows[0].relation_label,'穿过地层');assert.deepEqual(a.entityRelations(graph,'unknown'),[]);
});
const ex=()=>({window_id:'W0',dates:['2020-01-01','2020-01-02','2020-01-03','2020-01-04','2020-01-05','2020-01-06','2020-01-07','2020-01-08','2020-01-09'],well_ids:['A'],feature_names:['oil_volume_sm3'],input:[[[10]],[[null]],[[12]],[[null]],[[13]],[[null]],[[null]],[[null]],[[null]]],prediction:[[[99]],[[11]],[[99]],[[-2]],[[99]],[[16]],[[17]],[[18]],[[19]]],target_observed:[[[10]],[[10.8]],[[12]],[[null]],[[13]],[[null]],[[null]],[[null]],[[null]]],holdout_mask:[[[false]],[[true]],[[false]],[[false]],[[false]],[[false]],[[false]],[[false]],[[false]]]});
test('GRIN completion fills valid short gaps, keeps observations and reports rejected predictions',()=>{
 assert.equal(typeof a.grinCompletion,'function');const e=ex(),r=a.grinCompletion(e,'A',0);assert.equal(r.rows[0].output_value,10);assert.equal(r.rows[1].output_value,11);assert.equal(r.rows[1].prediction,11);assert.equal(r.rows[3].prediction,-2);assert.equal(r.rows[3].output_value,null);assert.equal(r.rows[5].output_value,null);assert.equal(r.filled,1);assert.equal(r.pending,5);assert.equal(e.input[1][0][0],null);
 const changed=ex();changed.target_observed[1][0][0]=9999;assert.deepEqual(a.grinCompletion(changed,'A',0).rows.map(x=>x.output_value),r.rows.map(x=>x.output_value));
});
test('GRIN completes natural short gaps but never fills an unsupported all-missing variable',()=>{
 assert.equal(typeof a.grinCompletion,'function');let e=ex();e.prediction[3][0][0]=12.5;const r=a.grinCompletion(e,'A',0);assert.equal(r.rows[3].output_value,12.5);assert.equal(r.rows[3].target,null);e.input=e.input.map(()=>[[null]]);const empty=a.grinCompletion(e,'A',0);assert.equal(empty.filled,0);assert.ok(empty.rows.every(x=>x.output_value===null));
});
