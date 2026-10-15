"""Extract LA7 examples as editable OCR text; preserve explicitly reviewed corrections.
No source images are emitted in the published data. OCR text is never labelled
reviewed automatically. Source page coordinates remain in v15 originals.
"""
from pathlib import Path
import csv, json, re, argparse
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--ocr-directory',type=Path,default=ROOT.parents[1]/'tmp/v15/ocr/LA7');args=p.parse_args()
DEST=ROOT/'data/examples-LA7-v17.json'
old={i['id']:i for i in json.loads(DEST.read_text()).get('items',[])} if DEST.exists() else {}
originals=sum([json.loads(f.read_text())['items'] for f in sorted((ROOT/'data').glob('originals-LA7-v15-*.json'))],[])
items=[];cache={}
def lines(page):
 if page in cache:return cache[page]
 with (args.ocr_directory/f'{page:03}.tsv').open() as f:rows=list(csv.DictReader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
 h=int(rows[0]['height']);group={}
 for w in rows:
  if w['level']=='5' and w.get('text','').strip():group.setdefault((w['block_num'],w['par_num'],w['line_num']),[]).append(w)
 result=[]
 for words in group.values():
  y=min(int(w['top']) for w in words)/h;b=max(int(w['top'])+int(w['height']) for w in words)/h
  words.sort(key=lambda w:int(w['left']))
  t=' '.join(w['text'] for w in words)
  if re.search(r'公众号|pdf2book|考研电子书|www\.|旗胜考研',t):
   t=re.sub(r'公众号.*|考研电子书.*|www\..*','',t).strip()
  if t:result.append((y,b,t))
 result.sort();cache[page]=result;return result

def extract(segments):
 pieces=[]
 for seg in segments:
  text='\n'.join(t for y,b,t in lines(seg['page']) if y>=seg['top']-.004 and y<seg['bottom']-.002)
  if text:pieces.append(text)
 return '\n\n'.join(pieces)
for src in originals:
 if src['kind']!='example':continue
 if src['id'] in old and old[src['id']]['status']=='reviewed':items.append(old[src['id']]);continue
 prompt=extract(src['segments']);solution=extract(src['answer_segments']);issues=['自动OCR初稿；矩阵、上下标、正负号和分数尚未逐式核对，不可作为已校订答案。']
 if not solution:
  # Several source examples explain the result in the same paragraph and have no 解 heading.
  split=re.search(r'(?m)^\s*(?:解|证明|证)\s*(?:\n|[由因设按对令把将取])',prompt)
  if split:prompt,solution=prompt[:split.start()].strip(),prompt[split.start():].strip()
  else:issues.append('题干与解答边界尚待人工划分；不能据此认定原书无解答。')
 if src['answer_segments'] and len(src['answer_segments'])>=3:issues.append('跨页解答的终点需复核，OCR段可能混入后续正文。')
 i={k:src[k] for k in ['id','title','chapter','section_id','knowledge_ids','printed_page']}
 i.update(prompt=prompt,solution=solution,explanation=[],status='ocr_needs_review',issues=issues,source_pages=sorted({s['page'] for s in src['segments']+src['answer_segments']}),text_origin='OCR文字初稿；非PDF或图片替代')
 items.append(i)
result={'version':17,'book_id':'LA7','coverage':{'indexed_examples':len(items),'reviewed_examples':sum(i['status']=='reviewed' for i in items),'ocr_needs_review':sum(i['status']!='reviewed' for i in items),'statement':'覆盖已定位的全部例题；不将OCR初稿冒充逐题校订，未证明定位扫描绝无漏检。'},'items':items}
DEST.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result['coverage'],ensure_ascii=False))
