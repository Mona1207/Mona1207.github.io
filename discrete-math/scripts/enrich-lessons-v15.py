from pathlib import Path
import collections,json,runpy,re
R=Path(__file__).resolve().parents[1];D=R/'data';notes=runpy.run_path(str(R/'scripts/lecture-notes-v15.py'));NEW=notes['NEW'];GUIDES=notes['GUIDES'];DETAILS=runpy.run_path(str(R/'scripts/exam-details-v15.py'))['DETAILS']
GROUPS=json.loads(re.search(r'const groups=(\{.*\});', (R/'assets/practice-groups-v13.js').read_text()).group(1))
for bid in ['DM2T','LA7','PS3']:
 b=json.loads((D/f'book-{bid}-v15.json').read_text());qs=[];links=[]
 for file in b['question_files']:
  shard=json.loads((D/file).read_text());qs.extend(shard['questions']);links.extend(shard['links'])
 qmap={q['id']:q for q in qs};linked=collections.defaultdict(list)
 for l in links:linked[l['knowledge_id']].append(qmap[l['question_id']])
 for k in b['knowledge']:
  c=k['content'];chapter=int(k['chapter_id'].split('-C')[1].split('-')[0]);conditions,method=GUIDES[bid][chapter]
  if k['title'] in NEW:
   definition,extra,steps,example,errors=NEW[k['title']];c.update(definition=definition,plain=definition.split('。')[0]+'。',example=example,errors=errors,confusions=errors,conditions=extra,method=steps,reason='把定义中的存在性、任意性与附加条件逐项落实，再按本页步骤检验。');k['verification']='reviewed_math'
  else:
   c['conditions']=conditions;c['method']=method
  seen=set();cases=[]
  for q in linked[k['id']]:
   family=GROUPS.get(q['id']) or q['meta'].get('practice_group') or q['meta'].get('family_id') or q['id']
   if family in seen or q['verification']!='verified':continue
   seen.add(family);cases.append({'title':re.sub(r'^(?:DM|LA|PS)-K\d+-\d+-','',family),'question_id':q['id'],'prompt':q['prompt'],'answer':q['answer']['text'],'steps':q['explanation']['steps'],'label':q['meta'].get('label','系统补充示例')})
  # Full range of distinct existing exam methods is available, without number-only duplicates.
  c['exam_cases']=cases;c['exam_methods']=[x['title'] for x in cases]
  c['reason']=c.get('reason','')
  if c['reason'].startswith('从定义逐项检查条件') or not c['reason']:c['reason']='\n\n'.join('【'+v['title']+'】\n'+'\n'.join(v['steps']) for v in cases[:2]) or c['example']
  c['exam_checklist']=['能否不看解析复述定义及其适用条件？','能否判断题目中的每个已知条件用于哪一步？','能否给出不满足条件时的反例或说明？','能否把结果代回定义、原式、概率归一化或边数约束？']
  c['theory']=DETAILS.get(k['id'],c['definition']+'\n\n'+c['conditions']+'\n\n'+c['method'])
  c['estimated_minutes']=max(12,min(35,10+len(cases)*2));c['content_version']=15
 (D/f'book-{bid}-v15.json').write_text(json.dumps(b,ensure_ascii=False,separators=(',',':'))+'\n');print(bid,'enriched',len(b['knowledge']),'points;',sum(len(k['content']['exam_cases']) for k in b['knowledge']),'distinct worked methods')
