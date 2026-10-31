import math,re,time
from difflib import SequenceMatcher
import numpy as np

def normalize(s):return re.sub(r'[\s_\-－—]','',str(s)).casefold()

def run_aux(model_id,train,validation,test,input_rows,parameters,operation):
 start=time.perf_counter();rows=validation if operation=='validate' else test if operation=='test' else input_rows if operation=='predict' else test or validation or input_rows or train;metrics={};results=[]
 if model_id=='entity_align':
  vocab=train;threshold=float(parameters.get('threshold',.8));correct=0;labeled=0
  if not vocab:raise ValueError('Entity alignment requires training dictionary rows.')
  for r in rows:
   candidates=[(1. if normalize(r.get('alias','')) in [normalize(a.get('alias','')),normalize(a.get('canonical',''))] else SequenceMatcher(None,normalize(r.get('alias','')),normalize(a.get('alias',''))).ratio(),a) for a in vocab if not r.get('type') or a.get('type')==r.get('type')]
   score,a=max(candidates,key=lambda t:t[0]) if candidates else (0,{})
   prediction=a.get('canonical') if score>=threshold else None
   results.append(dict(r,predicted_canonical=prediction,alignment_score=score,manual_review=prediction is None))
   if r.get('canonical'):labeled+=1;correct+=prediction==r['canonical']
  metrics={'evaluation':{'accuracy':correct/labeled if labeled else None,'labeled_samples':labeled,'dictionary_entries':len(vocab)}}
 elif model_id=='lag':
  from datetime import date,timedelta
  if len(rows)<5:raise ValueError('Lag analysis needs at least 5 dated observations.')
  byday={date.fromisoformat(r['date']):r for r in rows};maxlag=min(int(parameters.get('max_lag_days',30)),90)
  for lag in range(maxlag+1):
   pairs=[(float(r['injection']),float(byday[d+timedelta(days=lag)]['production'])) for d,r in byday.items() if d+timedelta(days=lag) in byday and r.get('injection') is not None and byday[d+timedelta(days=lag)].get('production') is not None]
   corr=None
   if len(pairs)>=4:
    a,b=np.array(pairs).T
    if np.std(a)>0 and np.std(b)>0:corr=float(np.corrcoef(a,b)[0,1])
   results.append({'lag_days':lag,'Pearson_r':corr,'aligned_pairs':len(pairs)})
  available=[r for r in results if r['Pearson_r'] is not None];best=max(available,key=lambda r:abs(r['Pearson_r'])) if available else None;metrics={'calculation':{'max_absolute_correlation_lag_days':best['lag_days'] if best else None,'correlation':best['Pearson_r'] if best else None}}
 elif model_id=='hierarchy':
  seen={};issues=[];history={}
  for i,r in enumerate(rows):
   key=(r['well_id'],r['layer_id'],r['valid_from'],r['valid_to']);signature=(r['group_id'],r['block_id'])
   if key in seen and seen[key]!=signature:issues.append({'row':i,'issue':'Conflicting membership for same well-layer validity interval.'})
   obj=(r['well_id'],r['layer_id'])
   for earlier,j in history.get(obj,[]):
    overlap=max(str(r['valid_from']),str(earlier['valid_from']))<=min(str(r['valid_to']),str(earlier['valid_to']))
    if overlap and signature!=(earlier['group_id'],earlier['block_id']):issues.append({'row':i,'conflict_with_row':j,'issue':'Overlapping validity intervals with different group/block memberships.'})
   history.setdefault(obj,[]).append((r,i))
   if str(r['valid_from'])>str(r['valid_to']):issues.append({'row':i,'issue':'valid_from after valid_to'})
   seen[key]=signature;results.append(dict(r,path=[r['block_id'],r['group_id'],r['well_id'],r['layer_id']]))
  metrics={'calculation':{'records':len(rows),'unique_wells':len({r['well_id'] for r in rows}),'conflicts':len(issues)}};return dict(results=results,issues=issues,metrics=metrics,training_seconds=None,compute_seconds=time.perf_counter()-start,limitations=['Provided hierarchy memberships are not inferred hydraulic connectivity.'])
 elif model_id=='rules':
  for r in rows:
   issues=[]
   for k in ['oil','liquid','pressure','injection']:
    if r.get(k) is not None and float(r[k])<0:issues.append({'field':k,'rule':'negative_physical_value','level':'L0'})
   if r.get('water_cut') is not None and not 0<=float(r['water_cut'])<=1:issues.append({'field':'water_cut','rule':'fraction_out_of_range','level':'L0'})
   if r.get('oil') is not None and r.get('liquid') is not None and float(r['oil'])>float(r['liquid']):issues.append({'field':'oil','rule':'oil_exceeds_liquid','level':'L1'})
   if all(r.get(k) is not None for k in ['oil','liquid','water_cut']) and float(r['liquid'])>0:
    expected=1-float(r['oil'])/float(r['liquid'])
    if abs(expected-float(r['water_cut']))>float(parameters.get('water_cut_tolerance',.05)):issues.append({'field':'water_cut','rule':'oil_liquid_water_cut_inconsistent','level':'L1'})
   results.append(dict(r,issues=issues,predicted_label=int(bool(issues))))
  metrics={'calculation':{'records':len(rows),'flagged':sum(r['predicted_label'] for r in results),'L0_blocked':sum(any(x['level']=='L0' for x in r['issues']) for r in results)}}
 else:raise ValueError('Unsupported auxiliary model')
 return dict(results=results,metrics=metrics,training_seconds=None,compute_seconds=time.perf_counter()-start,limitations=['Deterministic dictionary/rule/statistical calculation: no neural training. Correlation alone does not establish causality.'])
