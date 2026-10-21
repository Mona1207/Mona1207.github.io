"""Add source-located teaching sequences without changing any historical IDs."""
from pathlib import Path
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[1]
guides={}
for line in (ROOT/'scripts/lesson-guide-v32.txt').read_text().splitlines():
    if not line or line.startswith('#'):continue
    key,question,walkthrough=line.split('|')
    assert key not in guides,key
    guides[key]={'question':question,'walkthrough':walkthrough,'basis':'教材对应小节导学与独立讲解；非逐字转录'}
stats=[]
for book in ['DM2T','LA7','PS3','PHYS','DM2']:
    path=ROOT/'data'/('book.json' if book=='DM2' else f'book-{book}-v15.json')
    data=json.loads(path.read_text())
    for point in data['knowledge']:
        key=point['id']
        if book=='DM2':
            target=next((v for k,v in guides.items() if k==key),None)
        else:target=guides[key]
        if target:point['content']['lesson_guide']=target
        point['content']['content_version']=32
        if book=='PHYS':
            page=point['source']['printed_page']
            point['content']['lesson_source_image']=f'/discrete-math/physics/v32/lesson-pages/p{page}.webp'
        elif book!='DM2':
            page=point['source']['pdf_page']
            point['content']['lesson_source_image']=f'/discrete-math/textbooks/v32/lesson-pages/{book}-p{page}.webp'
        # Source-book examples precede supplementary exercises in the guided page.
        point['content']['worked_examples']=sorted(point['content'].get('worked_examples',[]),key=lambda x:0 if re.search('教材|用户提供',x.get('label','')) and not re.search('非教材|非本书原题|系统补充|改编',x.get('label','')) else 1)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    stats.append({'book':book,'topics':len(data['knowledge']),'guides':sum('lesson_guide' in k['content'] for k in data['knowledge'])})
assert len(guides)==233,len(guides)
audit={'version':32,'topics':stats,'original_examples_first':True,'source_policy':'保留教材页码定位；导学和推导独立撰写，教材例题与补充例题分别标识。物理仅提供知识点定位页图像，不上传整本PDF。'}
(ROOT/'data/lessons-audit-v32.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
print(stats)
