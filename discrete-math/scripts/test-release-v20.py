from pathlib import Path
import json,re
from PIL import Image
R=Path(__file__).resolve().parents[1];D=R/'data';reports=json.loads((D/'exercise-audit-v20.json').read_text());seen=set();figures=set();total=0
for report in reports:
 assert report['remaining_questions']==0,(report['book'],report['pending_ids'])
 payload=json.loads((D/f"exercises-{report['book']}-v20.json").read_text());assert payload['version']==20
 numbered={};points={k['id'] for k in json.loads((D/f"book-{report['book']}-v15.json").read_text())['knowledge']}
 for item in payload['items']:
  assert item['id'] not in seen,item['id'];seen.add(item['id'])
  assert item['status']=='reviewed' and item['answer_status']=='reviewed',item['id']
  assert isinstance(item['prompt'],str) and item['prompt'].strip(),item['id']
  assert isinstance(item['solution'],str) and item['solution'].strip(),item['id']
  assert item['explanation'] and all(isinstance(s,str) and s.strip() for s in item['explanation']),item['id']
  assert set(item['knowledge_ids'])<=points,item['id']
  if item['kind']=='exercise':
   total+=1;src=item['source'];assert src['id']==item['id'] and src['book_id']==report['book'] and src['kind']=='exercise',item['id'];assert src['segments'],item['id']
   group=item['id'].split('-E')[1].split('-')[0];numbered.setdefault(group,set()).add(src['source_number'])
  for image in re.findall(r'!\[[^\]]*\]\((/discrete-math/[^)]+)\)',item['prompt']+'\n'+item['solution']):
   path=R/image.removeprefix('/discrete-math/');assert path.is_file(),(item['id'],image);figures.add(path)
 for group,numbers in numbered.items():assert numbers==set(range(1,max(numbers)+1)),(report['book'],group,'numbering gap')
for path in figures:
 with Image.open(path) as im:im.verify()
index=(R/'index.html').read_text();assert 'app-ui-v20.js?v=20' in index;assert 'reader-stable-v19.css' in index;assert 'textbook-workspace-v20' in index
for filename in ['app-ui-v20.js','client-v20.js','pages-worker-v20.js','ui-v19.css','ui-v20.css','reader-stable-v19.css','pdfjs-v15/pdf.reader-worker-v19.mjs']:assert (R/'assets'/filename).is_file(),filename
print(f'PASS release: {total} numbered exercises with checked prompts, solutions and explanations; {len(figures)} valid figure assets; contiguous source numbering and all v20 entry assets.')
