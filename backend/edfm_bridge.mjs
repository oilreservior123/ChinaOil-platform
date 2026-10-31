import fs from 'node:fs';
import {simulateEDFM} from '../dist/physics-runtime.mjs';
const graph=JSON.parse(fs.readFileSync(new URL('../dist/assets/physics-runtime-input.json',import.meta.url),'utf8'));
const payload=JSON.parse(fs.readFileSync(0,'utf8'));const results=[];
for(const r of payload.rows){const value=await simulateEDFM(graph,{apertureMm:Number(r.aperture_mm),pressureDropMPa:Number(r.pressure_drop_mpa),durationDays:Number(r.duration_days),timeSteps:Math.max(6,Math.min(60,Number(payload.parameters.time_steps??24)))});results.push({case_id:r.case_id,...value})}
console.log(JSON.stringify({results,metrics:{cases:results.map(r=>({case_id:r.case_id,...r.metrics}))},model_artifact:{type:'compact_EDFM_2D_physical_solver',matrix_cells:120,fracture_unknowns:276},limitations:['Uses the shipped public benchmark geometry; uploaded rows change scenarios, not field geometry. No neural training is required.']}));
