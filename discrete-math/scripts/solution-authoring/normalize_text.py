"""Repair an extra JSON-escaping layer in legacy OCR math fields, never numerical content."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def normalize(s):
 if not isinstance(s,str):return s
 # A doubled command (\\\\begin, \\\\frac...) identifies the legacy layer.
 commands=r'begin|end|frac|dfrac|tfrac|sqrt|lambda|alpha|beta|gamma|theta|pi|sum|prod|land|lor|neg|leftrightarrow|Leftrightarrow|rightarrow|infty|mathrm|mathbb|operatorname|boxed|ldots|cdots'
 legacy=bool(re.search(r'(?<!\\)\\\\(?:'+commands+r')\b',s))
 if legacy:
  s=re.sub(r'\\+',lambda m:'\\'*((len(m[0])+1)//2),s)
 # A serialized line-break must end before the next TeX command letter.
 # Thus \\n is decoded while \\neg, \\nu and \\nabla remain untouched.
 parts=re.split(r'(\$\$[\s\S]*?\$\$|(?<!\$)\$(?!\$)[^$]*?\$(?!\$))',s)
 for i in range(0,len(parts),2):
  parts[i]=re.sub(r'(?<!\\)\\n','\n',parts[i])
 s=''.join(parts)
 return s

def main():
 changes=[]
 for book in ['DM2T','LA7','PS3','PHYS']:
  files=[f'exercises-{book}-'+('v29' if book=='PHYS' else 'v20')+'.json']
  if book!='PHYS':files.append(f'examples-{book}-ready-v17.json')
  for fn in files:
   p=ROOT/'data'/fn;d=json.loads(p.read_text())
   for item in d['items']:
    touched=[]
    for key in ['prompt','solution','explanation','common_mistakes']:
     old=item.get(key)
     new=[normalize(x) for x in old] if isinstance(old,list) else normalize(old)
     if new!=old:item[key]=new;touched.append(key)
    if touched:
     item['text_normalization']={'removed_extra_escape_layer':True,'fields':touched,'question_values_unchanged':True}
     changes.append({'id':item['id'],'fields':touched})
   p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'normalized_items_including_group_pages':len(changes),'fields':sum(len(x['fields']) for x in changes)}))
 (ROOT/'data'/'text-normalization-audit.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
