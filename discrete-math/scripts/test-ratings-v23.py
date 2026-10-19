from pathlib import Path
import json,re,hashlib,runpy,contextlib,io
R=Path(__file__).resolve().parents[1];D=R/'data'
with contextlib.redirect_stdout(io.StringIO()):build=runpy.run_path(str(R/'scripts/build-ratings-v23.py'))
read=lambda f:json.loads((D/f).read_text())
totals=[0,0,0];reviews=json.loads((R/'scripts/ratings-reviewed-v23.json').read_text())
for book in ['DM2T','LA7','PS3','PHYS']:
 data=read(f'ratings-{book}-v23.json');ratings=data['items'];seed=read(f'book-{book}-v15.json');knowledge={k['id']:k for k in seed['knowledge']}
 exercises=read(f'exercises-{book}-v'+('21' if book=='PHYS' else '20')+'.json')['items'];examples=[] if book=='PHYS' else [{**q,'kind':'example'} for q in read(f'examples-{book}-ready-v17.json')['items']]
 singles=examples+[q for q in exercises if q['kind']=='exercise'];groups=[q for q in exercises if q['kind']=='exercise_group']
 assert set(ratings)=={q['id'] for q in singles+groups};totals[0]+=len(singles);totals[1]+=len(groups)
 for q in singles:
  r=ratings[q['id']];assert r['basis']=='content_analysis';assert len(r['dimensions'])==4 and all(type(v)==int and 0<=v<=2 for v in r['dimensions']);assert r['level']==build['level'](r['dimensions']);assert r['evidence'] and r['topics'] and r['recommendation_reasons'];totals[2]+=r['recommended']
  assert 'pass_rate' not in r and 'exam_frequency' not in r
  if q['id'] in reviews:assert r['confidence']=='content_reviewed'
  if book!='PHYS':
   old=build['rating'](q,book,knowledge);verbose={**q,'explanation':['教学解释 '*100]*100};assert build['rating'](verbose,book,knowledge)==old,'teaching verbosity must not change difficulty'
 for kid in knowledge:
  related=[q for q in singles if kid in q['knowledge_ids']]
  if related:assert any(ratings[q['id']]['recommended'] for q in related),(book,kid)
 for q in groups:
  r=ratings[q['id']];children=[v for id,v in ratings.items() if id.startswith(q['id'].replace('-G','-E')+'-')]
  assert 'level' not in r and r['range']==[min(c['level'] for c in children),max(c['level'] for c in children)];assert r['recommended_count']==sum(c['recommended'] for c in children)
 # Every source location that the current textbook presents is accounted for.
 if book!='PHYS':
  sources=[q for f in seed['source_files'] for q in read(f)['items']]
  live={q['id'] for q in sources}|{q['id'] for q in singles};excluded=set(read(f'exercises-{book}-v20.json').get('excluded_ids',[]))
  assert live-excluded<=set(ratings),(book,sorted(live-excluded-set(ratings)))
 cases={q['id']:q for q in singles}
 audit=next(a for a in read('rating-audit-v23.json')['books'] if a['book']==book)
 assert audit['source_hash']==hashlib.sha256(json.dumps(singles,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
assert totals[:2]==[1680,75],totals
dm=read('ratings-DM2T-v23.json')['items'];la=read('ratings-LA7-v23.json')['items'];ps=read('ratings-PS3-v23.json')['items'];ph=read('ratings-PHYS-v23.json')['items']
assert dm['SRC-DM2T-X014-8799']['level']==1
assert dm['SRC-DM2T-E003-001']['level']==2
assert dm['SRC-DM2T-E008-036']['level']==1,'late chapter does not imply high difficulty'
assert dm['SRC-DM2T-E015-010']['level']==4
assert la['SRC-LA7-E004-014']['level']==2,'large numbers and parallel matrices are not automatically advanced'
assert la['SRC-LA7-E005-027']['level']==2
assert la['SRC-LA7-E006-012']['level']==4
assert ps['SRC-PS3-X034-5426']['level']==2
assert ps['SRC-PS3-E039-003']['level']==4
assert ph['SRC-PHYS-E010-010']['level']==2
assert ph['SRC-PHYS-E011-035']['level']==3
print('PASS',totals[0],'individual ratings,',totals[1],'group ranges,',totals[2],'recommendations; complete source coverage, every available knowledge point represented, score/reason consistency, reviewed anchors, and invariance under verbose teaching.')
