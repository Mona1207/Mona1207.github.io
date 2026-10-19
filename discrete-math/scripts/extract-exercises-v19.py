"""Read OCR line checkpoints and retain provenance, uncertainty and stable source IDs.
No item is promoted to reviewed automatically. Mathematical correction lives in a
separate reviewed JSON file; missing solutions are never filled with generic tips.
"""
from pathlib import Path
import argparse,json,re,collections
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data'
p=argparse.ArgumentParser();p.add_argument('--ocr-directory',type=Path,required=True);args=p.parse_args();OCR=args.ocr_directory

def clean(t):
 t=re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])','',t)
 t=re.sub(r'\s+([，。；：？！])',r'\1',t)
 return t.strip()
def line_text(l):return clean(l['text'])
def pos(l):return l['page']+l['y']
def read_lines(b):
 return [{**l,'page':int(f.stem)} for f in sorted((OCR/b).glob('[0-9]*.json')) for l in json.loads(f.read_text())['lines'] if .045<l['y']<.963 and not re.search(r'公众号|pdf2book|电子书|旗胜考研|第\s*\d+\s*章|^\s*\d{1,3}\s*$',l['text'])]
def source_segments(a,z):
 p1,p2=int(a),int(z);return [{'page':p,'top':round(a-p if p==p1 else .055,5),'bottom':round(z-p if p==p2 else .963,5)} for p in range(p1,p2+1) if (z-p if p==p2 else .963)>(a-p if p==p1 else .055)]
def extract(lines,segments):return '\n'.join(line_text(l) for seg in segments for l in lines if l['page']==seg['page'] and seg['top']-.004<=l['y']<seg['bottom']-.002)
# Directly inspected chapter headings in the uploaded LA7 answer appendix.
LA_HEADS=[(164,.0),(164,.735),(167,.0),(169,.596),(171,.384),(174,.647),(176,.0)]

def answer_key(lines):
 out={}
 for group in range(1,7):
  a=LA_HEADS[group-1][0]+LA_HEADS[group-1][1];z=LA_HEADS[group][0]+LA_HEADS[group][1];scope=[l for l in lines if a<pos(l)<z];starts=[];last=0
  for l in scope:
   m=re.match(r'^(\d{1,2})\s*[.．、]\s*',l['text'])
   if m and l['x']<.23 and int(m[1])>last:
    starts.append((l,int(m[1])));last=int(m[1])
  for i,(l,n) in enumerate(starts):
   end=pos(starts[i+1][0])-.001 if i+1<len(starts) else z
   text='\n'.join(line_text(x) for x in scope if pos(l)<=pos(x)<end and not re.search(r'习\s*题',x['text']))
   out[(group,n)]={'text':text,'pages':sorted({x['page'] for x in scope if pos(l)<=pos(x)<end})}
 return out
reports=[]
for book in ['DM2T','LA7','PS3']:
 all_items=[i for f in sorted(DATA.glob(f'originals-{book}-v15-*.json')) for i in json.loads(f.read_text())['items']];sources=[i for i in all_items if i['kind']!='example'];lines=read_lines(book);seed=json.loads((DATA/f'book-{book}-v15.json').read_text());points=seed['knowledge'];keys=answer_key(lines) if book=='LA7' else {};items=[]
 groups=[i for i in sources if i['kind']=='exercise_group'];bygroup=collections.defaultdict(list)
 for source in sources:
  if source['kind']=='exercise':bygroup[int(source['id'].split('-E')[1].split('-')[0])].append(source)
 for gi,g in enumerate(groups,1):
  group_lines=[l for l in lines if any(l['page']==s['page'] and s['top']-.004<=l['y']<s['bottom']-.002 for s in g['segments'])];located={}
  # Re-find the starts near the previous coordinates. This also repairs an item
  # whose crop began with the previous exercise's final line.
  for src in bygroup[gi]:
   candidates=[l for l in group_lines if l['x']<.29 and re.match(r'^\s*'+str(src['source_number'])+r'\s*[.．、]\s*(?!\d)',l['text'])]
   if candidates:located[src['source_number']]=min(candidates,key=lambda l:abs(pos(l)-(src['segments'][0]['page']+src['segments'][0]['top'])))
   else:located[src['source_number']]={'page':src['segments'][0]['page'],'y':src['segments'][0]['top']+.004}
  # Fill numbering gaps only when a Chinese problem sentence follows the number.
  maximum=max(located,default=0)
  for l in group_lines:
   m=re.match(r'^(\d{1,3})\s*[.．、]\s*([^\d].*)',l['text'])
   if not m or l['x']>.27 or not re.search(r'[\u4e00-\u9fff]',m[2]):continue
   n=int(m[1])
   if 0<n<=maximum+1 and n not in located:located[n]=l
  ordered=sorted(located.items(),key=lambda t:pos(t[1]));old={s['source_number']:s for s in bygroup[gi]}
  for j,(number,start) in enumerate(ordered):
   end=pos(ordered[j+1][1])-.002 if j+1<len(ordered) else g['segments'][-1]['page']+g['segments'][-1]['bottom']
   if end<=pos(start):continue
   src=dict(old.get(number) or {**g,'id':f'SRC-{book}-E{gi:03}-{number:03}','kind':'exercise','title':g['title'].replace(' · 完整原页','')+f' · 第 {number} 题','source_number':number,'group_title':g['title'].replace(' · 完整原页',''),'boundary_status':'number_gap_review','printed_page':start['page']-{'DM2T':11,'LA7':4,'PS3':10}[book],'pdf_page':start['page']})
   src['segments']=source_segments(pos(start)-.004,end)
   text=extract(lines,src['segments']);issues=['自动OCR转写；矩阵、分式、上下标、图形及题目边界尚待逐项校订。']
   if not text:issues.append('此题未取得可靠OCR文字。')
   # Correct PS3 section shifts caused by matching the group heading to the next
   # section on a shared page. Other books keep their stable association for now.
   if book=='PS3':
    m=re.search(r'习题\s*(\d+)\.(\d+)',src['group_title'])
    if m:
     sid=f'PS-C{int(m[1]):02}-S{int(m[2])}';pool=[k for k in points if k['chapter_id']==sid]
     if pool:src['section_id']=sid;src['knowledge_ids']=[k['id'] for k in pool]
   ans=keys.get((gi,number));entry={k:src[k] for k in ['id','title','kind','knowledge_ids']};entry.update(source=src,prompt=text,solution=ans['text'] if ans else '',explanation=[],status='ocr_needs_review',answer_status='ocr_needs_review' if ans else 'missing',issues=issues,source_pages=sorted({s['page'] for s in src['segments']}),answer_pages=ans['pages'] if ans else [],text_origin='uploaded_textbook_scan_ocr',solution_origin='原书书后部分参考答案 · OCR转写' if ans else '当前尚无可用的完整文字解答')
   items.append(entry)
  group_prompt=extract(lines,g['segments']);items.append({**{k:g[k] for k in ['id','title','kind','knowledge_ids']},'title':g['title'].replace('完整原页','整组文字'),'source':{**g,'title':g['title'].replace('完整原页','整组文字')},'prompt':group_prompt,'solution':'','explanation':[],'status':'ocr_needs_review','answer_status':'missing','issues':['整组习题OCR文字；部分数学符号、图形及子题边界待校订。'],'source_pages':sorted({s['page'] for s in g['segments']}),'text_origin':'uploaded_textbook_scan_ocr','solution_origin':'请进入各题查看已整理的解答'})
 corrections_file=DATA/f'exercises-{book}-reviewed-v19.json';corrections=json.loads(corrections_file.read_text()) if corrections_file.exists() else {}
 for item in items:
  if item['id'] in corrections:item.update(corrections[item['id']])
  item['source']['knowledge_ids']=item['knowledge_ids']
 report={'book':book,'indexed_numbered_before':len([i for i in sources if i['kind']=='exercise']),'ocr_numbered':sum(i['kind']=='exercise' for i in items),'ocr_groups':len(groups),'ocr_pages':len({p for i in items for p in i['source_pages']}),'reviewed_prompts':sum(i['status']=='reviewed' for i in items),'reviewed_answers':sum(i['answer_status']=='reviewed' for i in items),'ocr_answer_drafts':sum(i['answer_status']=='ocr_needs_review' for i in items),'missing_answers':sum(i['kind']=='exercise' and not i['solution'] for i in items),'empty_prompts':[i['id'] for i in items if not i['prompt']], 'statement':'OCR覆盖已定位的习题及整组入口；OCR初稿不等于数学内容已校订，无完整答案的题明确留空，不宣称全书解析已完成。'}
 payload={'version':19,'book_id':book,'audit':report,'items':items};(DATA/f'exercises-{book}-v19.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n');reports.append(report);print(json.dumps(report,ensure_ascii=False))
(DATA/'exercise-audit-v19.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
