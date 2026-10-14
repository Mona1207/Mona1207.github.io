"""Index source locations. Never promote unverified OCR formulas into graded text.
The viewer renders the user's original PDF locally, preserving every symbol.
"""
from pathlib import Path
import argparse,ast,collections,csv,json,re,runpy
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data'
parser=argparse.ArgumentParser();parser.add_argument('--ocr-directory',type=Path,required=True);OCR=parser.parse_args().ocr_directory
config=runpy.run_path(str(ROOT/'scripts/textbook-config-v15.py'));tree=ast.parse((ROOT/'scripts/build-books-v14.py').read_text());ot=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='TOC' for t in n.targets));TOCS={'DM2T':config['DM_TOC'],**ot};OFF={'DM2T':11,'LA7':4,'PS3':10};TOTAL={'DM2T':414,'LA7':176,'PS3':268}
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n')
def read_lines(bid,p):
 rows=list(csv.DictReader((OCR/bid/f'{p:03}.tsv').open(),delimiter='\t',quoting=csv.QUOTE_NONE));page=rows[0];h=int(page['height']);w=int(page['width']);groups={}
 for r in rows:
  if r.get('level')=='5' and r.get('text','').strip():groups.setdefault((r['block_num'],r['par_num'],r['line_num']),[]).append(r)
 out=[]
 for words in groups.values():
  t=''.join(r['text'] for r in words);x=min(int(r['left']) for r in words)/w;y=min(int(r['top']) for r in words)/h;bottom=max(int(r['top'])+int(r['height']) for r in words)/h
  out.append({'text':t,'spaced':' '.join(r['text'] for r in words),'x':x,'y':y,'bottom':bottom,'p':p,'conf':round(sum(float(r['conf']) for r in words)/len(words),1)})
 return sorted(out,key=lambda x:(x['y'],x['x']))
def pos(r):return r['p']+r['y']
def segments(start,end):
 p1=int(start);p2=int(end);y1=start-p1;y2=end-p2;return [{'page':p,'top':round(y1 if p==p1 else .055,4),'bottom':round(y2 if p==p2 else .965,4)} for p in range(p1,p2+1) if (y2 if p==p2 else .965)>(y1 if p==p1 else .055)+.005]
def chapter(bid,p):
 printed=p-OFF[bid];return max((i for i,(_,s,_) in enumerate(TOCS[bid],1) if s[0][0]<=printed),default=1)
def section_id(bid,p):
 n=chapter(bid,p);printed=p-OFF[bid];sections=TOCS[bid][n-1][1];j=max((j for j,(p,_) in enumerate(sections,1) if p<=printed),default=1);prefix='DM' if bid=='DM2T' else 'LA' if bid=='LA7' else 'PS';return f'{prefix}-C{n:02}-S{j}'
cn='一二三四五六七八九十'
summary=[]
for bid in ['DM2T','LA7','PS3']:
 seed=json.loads((DATA/f'book-{bid}-v15.json').read_text());cat=next(b for b in json.loads((DATA/'textbook-catalog-v15.json').read_text())['books'] if b['id']==bid)
 lines=[line for p in range(1,TOTAL[bid]+1) for line in read_lines(bid,p)];body=[l for l in lines if .055<l['y']<.965 and l['p']>=TOCS[bid][0][1][0][0]+OFF[bid]];boundaries=[]
 for l in body:
  text=l['text'].lstrip('*“”"')
  if re.match(r'^(?:[§$]\s*[0-9]+|第[一二三四五六七八九十百0-9]+[章节]|[0-9]+\.[0-9]+[^0-9])',text) and l['x']<.3:boundaries.append(pos(l))
 exstarts=[]
 for l in body:
  raw=l.get('spaced',l['text']).lstrip('*“”" ')
  raw=re.sub(r'^[Ee][^例]{0,30}(?=例)','',raw)
  raw=re.sub(r'^例\s*S\s*\$(?=\s*[.．])','例5',raw)
  raw=re.sub(r'^例\s*[S$](?=\s*[.．])','例5',raw)
  if bid=='DM2T':raw=re.sub(r'^例\s*%(?=\s*[.．])','例9',raw);raw=re.sub(r'^(例\s*9)\s*%',r'\1',raw)
  raw=re.sub(r'^(例\s*\d+[.．]\d*)S',r'\g<1>5',raw)
  raw=re.sub(r'^例\s*[工I](?=\s|[.．])','例1',raw)
  match=re.match(r'^例\s*(\d+(?:\s*[.．·]\s*\d+){0,2})(?!\d)',raw)
  if not match or l['x']>=.35:continue
  tail=re.sub(r'\s+','',raw[match.end():])
  if re.match(r'^(?:说明(?:[，,]|在)|中的|告诉我们|与[0-9]|利用.*求解过|和例|都是|是一种|的结果|可以推广|、例|的数据|[，,]作为)',tail):continue
  exstarts.append((l,re.sub(r'\s+','',match.group(1))))
 # Directly inspected locations repair labels missed by both line grouping and OCR.
 corrections={'DM2T':[(104,.4911,'6.1'),(390,.3004,'19.7')], 'LA7':[(44,.5526,'11'),(53,.4217,'18'),(100,.1451,'12'),(133,.292,'12'),(139,.434,'15')], 'PS3':[(21,.1756,'5'),(140,.4185,'5')]}
 for p,y,number in corrections[bid]:
  nearby=[j for j,(l,_) in enumerate(exstarts) if l['p']==p and abs(l['y']-y)<.035]
  if nearby:
   for j in nearby:exstarts[j]=(exstarts[j][0],number)
  else:
   nearest=min((l for l in body if l['p']==p),key=lambda l:abs(l['y']-y))
   exstarts.append(({**nearest,'y':y},number))
 exstarts.sort(key=lambda x:pos(x[0]))
 seen_examples=set();unique_examples=[]
 for l,num in exstarts:
  key=(l['p'],num)
  if key not in seen_examples:unique_examples.append((l,num));seen_examples.add(key)
 exstarts=unique_examples
 # Match known exercise-group pages to actual source headings; preserve uncertainty flags.
 groups=[]
 for g in cat['exercise_groups']:
  if '参考答案' in g['title']:continue
  page=g['pdf_page'];candidates=[l for l in body if l['p']==page and ('习题' in l['text'] or '综合' in l['text']) and len(l['text'])<45]
  if '综合' in g['title']:candidates=[l for l in candidates if '综合' in l['text']]
  elif bid=='PS3':
   nums=re.findall(r'\d+',g['title']);candidates=[l for l in candidates if re.findall(r'\d+',l['text'].replace('$','5').replace('S','5').replace('工','1'))[:2]==nums[:2]]
  head=candidates[0] if candidates else {'p':page,'y':.06,'bottom':.06,'text':g['title'],'x':0,'conf':0}
  n=chapter(bid,page);end=(TOCS[bid][n][1][0][0]+OFF[bid]-.04) if n<len(TOCS[bid]) else (391+11 if bid=='DM2T' else 164 if bid=='LA7' else 221)
  if bid=='PS3':
   later=[pos(l) for l in body if pos(l)>pos(head)+.04 and re.match(r'^第[一二三四五六七八九十]+[节章]',l['text'])]
   if later:end=min(end,min(later))
  if bid=='PS3' and '综合' not in g['title']:
   number=re.findall(r'\d+',g['title']);section=int(number[1]) if len(number)>1 else None
   if section and section<len(TOCS[bid][n-1][1]):
    nextpage=TOCS[bid][n-1][1][section][0]+OFF[bid];heads=[pos(l) for l in body if l['p']==nextpage and pos(l)>pos(head) and re.match(r'^第[一二三四五六七八九十]+节',l['text'])]
    cap=min(heads) if heads else nextpage+.055
    if cap>pos(head):end=min(end,cap)
  groups.append({'title':g['title'],'start':pos(head),'end':end,'heading_checked':bool(candidates),'chapter':n,'p':page})
 # A later exercise group also ends the previous group (e.g. section exercises / comprehensive exercises).
 groups.sort(key=lambda g:g['start'])
 for i,g in enumerate(groups[:-1]):g['end']=min(g['end'],groups[i+1]['start'])
 for ch in seed['chapters']:
  if ch['kind']=='appendix':
   p=ch['page']+OFF[bid];heads=[pos(l) for l in body if l['p']==p and (ch['title'][-4:] in l['text'] or l['text'].startswith('附表'))]
   boundaries.append(min(heads) if heads else p+.055)
 items=[]
 for gi,g in enumerate(groups):
  candidates=[];expected=1
  for l in body:
   if not(g['start']<pos(l)<g['end']) or l['x']>.28:continue
   t=l['text'].lstrip('*＊“”\"');t=re.sub(r'^([Il工])(?=[.．、,，])','1',t);m=re.match(r'^(\d{1,3})[.．、,，](?!\d)',t) or re.match(r'^(\d{1,3})(?=[\u4e00-\u9fff])',t)
   if not m:continue
   num=int(m.group(1))
   if num<expected or num>expected+15 or not re.search(r'[\u4e00-\u9fff]',l['text']):continue
   candidates.append((l,num,expected!=num));expected=num+1
  if candidates:
   nums=[v[1] for v in candidates];missing=len(set(range(1,max(nums)+1))-set(nums))
   if missing>max(4,len(nums)*.45):candidates=[]
  # Every group retains a complete-page entry so uncertain OCR numbering never hides a question.
  items.append({'id':f'SRC-{bid}-G{gi+1:03}','book_id':bid,'kind':'exercise_group','title':g['title']+' · 完整原页','chapter':g['chapter'],'section_id':section_id(bid,g['p']),'printed_page':g['p']-OFF[bid],'pdf_page':g['p'],'segments':segments(g['start'],g['end']),'answer_segments':[],'boundary_status':'group_page_reference' if candidates else 'group_page_review','mapping_basis':'原书习题组所在章；待逐题细分','keywords':[]})
  if not candidates:continue
  for i,(l,num,gap) in enumerate(candidates):
   end=pos(candidates[i+1][0])-.004 if i+1<len(candidates) else g['end']-.004;text=''.join(x['text'] for x in body if pos(l)<=pos(x)<end)
   items.append({'id':f'SRC-{bid}-E{gi+1:03}-{num:03}','book_id':bid,'kind':'exercise','title':g['title']+f' · 第 {num} 题','chapter':g['chapter'],'section_id':section_id(bid,l['p']),'printed_page':l['p']-OFF[bid],'pdf_page':l['p'],'segments':segments(pos(l)-.004,end),'answer_segments':[],'boundary_status':'number_gap_review' if gap else 'ocr_located','source_number':num,'group_title':g['title'],'mapping_basis':'原书所在小节及题面关键词；边界可回看前后页核对','_text':text,'context_needed':bool(re.search(r'上题|前题|例\d|续\)|续）|如图|图\d',text))})
 for i,(l,number) in enumerate(exstarts):
  start=pos(l)-.004;next_example=pos(exstarts[i+1][0])-.004 if i+1<len(exstarts) else TOTAL[bid]+.96
  caps=[b for b in boundaries if b>start+.03]+[g['start'] for g in groups if g['start']>start+.03];end=min([next_example,*caps]) if caps else next_example
  # Never let a section heading detection create an empty example.
  answer=next((pos(x)-.003 for x in body if start+.005<pos(x)<end and re.match(r'^(?:解|证明|证)(?:$|[”"，:：\s\u4e00-\u9fff0-9A-Za-z(（])',x['text'])),None)
  text=''.join(x['text'] for x in body if start<=pos(x)<(answer or end))
  items.append({'id':f'SRC-{bid}-X{l["p"]:03}-{round(l["y"]*10000):04}','book_id':bid,'kind':'example','title':('辅助材料 · ' if bid=='PS3' and l['p']>=221 else '')+'例 '+number,'source_scope':'appendix' if bid=='PS3' and l['p']>=221 else 'chapter','chapter':0 if bid=='PS3' and l['p']>=221 else chapter(bid,l['p']),'section_id':section_id(bid,l['p']),'printed_page':l['p']-OFF[bid],'pdf_page':l['p'],'segments':segments(start,answer or end),'answer_segments':segments(answer,end) if answer else [],'boundary_status':'ocr_located' if answer else 'example_answer_boundary_review','mapping_basis':'原书例题所在小节','_text':text,'context_needed':bool(re.search(r'上例|前例|例\d|续\)|续）|如图',text))})
 # Scope preservation: all exercise groups are present even when numbering needs human checking.
 points=seed['knowledge']
 for item in items:
  chapter_prefix=('DM' if bid=='DM2T' else 'LA' if bid=='LA7' else 'PS')+f'-C{item["chapter"]:02}'
  pool=[k for k in points if k['chapter_id']==item['section_id']] if item['kind']=='example' or bid=='PS3' and '综合' not in item.get('group_title','') else []
  if item.get('source_scope')=='appendix':pool=points
  if not pool:pool=[k for k in points if k['chapter_id'].startswith(chapter_prefix)]
  text=item.pop('_text','');rank=[]
  for k in pool:
   terms=[t for t in re.split(r'[、，与及和的\s]',k['title']) if len(t)>1];score=sum(len(t)*text.count(t) for t in terms);rank.append((score,k))
  rank.sort(key=lambda p:p[0],reverse=True);positive=[k['id'] for score,k in rank if score>0];item['knowledge_ids']=positive[:4] if positive else [k['id'] for _,k in (rank if item['kind']=='exercise_group' else rank[:4])];item['mapping_status']='section_and_keywords' if positive else 'section_scope'
  item['verification']='source_location';item['scoring']='reference_only';item['counted_as_mastery']=False
 items.sort(key=lambda x:(x['pdf_page'],x['segments'][0]['top'] if x['segments'] else 0))
 for k in points:k['source_item_ids']=[i['id'] for i in items if k['id'] in i['knowledge_ids']]
 files=[]
 for n in range(0,len(items),180):name=f'originals-{bid}-v15-{n//180+1:03}.json';save(DATA/name,{'items':items[n:n+180]});files.append(name)
 report={'book_id':bid,'pdf_pages_processed':TOTAL[bid],'example_locations':sum(i['kind']=='example' for i in items),'exercise_locations':sum(i['kind']=='exercise' for i in items),'exercise_groups_expected':len(groups),'exercise_groups_indexed':len(groups),'numbering_or_boundary_review':sum(i['boundary_status'] not in ['ocr_located','group_page_reference'] for i in items),'coverage_statement':'全书逐页扫描并保留本机原页；编号和切分为OCR定位，未宣称全部逐题人工核验。','ungraded_originals':len(items),'graded_originals':0,'full_group_entries':sum(i['kind']=='exercise_group' for i in items),'files':files}
 summary.append(report);seed['source_files']=files;seed['source_audit']=report;save(DATA/f'book-{bid}-v15.json',seed);print(report,flush=True)
save(DATA/'source-audit-v15.json',{'version':15,'books':summary})
