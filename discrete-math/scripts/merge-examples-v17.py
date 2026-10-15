"""Combine independently checked chapters without overwriting OCR/review inputs."""
from pathlib import Path
import json,collections
R=Path(__file__).resolve().parents[1]/'data'
for book in ['DM2T','LA7','PS3']:
    base=json.loads((R/f'examples-{book}-v17.json').read_text())
    items={i['id']:i for i in base['items']}
    for source in sorted(R.glob(f'examples-{book}-*-v17.json')):
        if source.name.endswith('-ready-v17.json'):continue
        for patch in json.loads(source.read_text())['items']:
            if patch['status']=='reviewed' or items.get(patch['id'],{}).get('status')!='reviewed':
                items[patch['id']]={**items.get(patch['id'],{}),**patch}
    mapping_path=R/'example-knowledge-v17.json'
    if mapping_path.exists():
        mapping=json.loads(mapping_path.read_text()).get('books',{}).get(book,{})
        valid={k['id'] for k in json.loads((R/f'book-{book}-v15.json').read_text())['knowledge']}
        for id,points in mapping.items():
            assert points and all(p in valid for p in points),(book,id,points)
            if id in items:
                items[id]['knowledge_ids']=points
                items[id]['mapping_basis']='按本例题的题干、原书解答及实际主题校订知识点关联。'
    ordered=sorted(items.values(),key=lambda i:(i['source_pages'][0],i['id']))
    counts=collections.Counter(i['status'] for i in ordered)
    output={'version':17,'book_id':book,'items':ordered,'audit':{'total':len(ordered),'reviewed':counts['reviewed'],'needs_review':len(ordered)-counts['reviewed'],'statement':'文字题干、解答与本题讲解按原页核对；个别原书疑点单独注明。未校订OCR不作为可靠答案。'}}
    target=R/f'examples-{book}-ready-v17.json';temporary=target.with_suffix('.building');temporary.write_text(json.dumps(output,ensure_ascii=False,separators=(',',':'))+'\n');temporary.replace(target)
    print(book,len(ordered),dict(counts))
