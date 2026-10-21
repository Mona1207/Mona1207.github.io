"""Render only knowledge-location pages, with explicit source-page hashes."""
from pathlib import Path
import json,hashlib,sys
import fitz
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'data/textbook-assets-v16.json').read_text())
audit=json.loads((ROOT/'data/lessons-audit-v32.json').read_text())
sources={}
def render(doc,index,dest):
    pix=doc[index].get_pixmap(matrix=fitz.Matrix(1.8,1.8))
    image=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
    image.thumbnail((1100,1600));dest.parent.mkdir(parents=True,exist_ok=True)
    image.save(dest,'WEBP',quality=82,method=4)
    return {'file':'/discrete-math/'+str(dest.relative_to(ROOT)),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'bytes':dest.stat().st_size}
for book in ['DM2T','LA7','PS3','PHYS']:
    data=json.loads((ROOT/f'data/book-{book}-v15.json').read_text())
    points={k['source']['pdf_page']:k['source'] for k in data['knowledge']}
    entries=[];docs={}
    for pdf_page,location in sorted(points.items()):
        if book=='PHYS':
            path=Path(sys.argv[1]);index=pdf_page-1;dest=ROOT/f'physics/v32/lesson-pages/p{location["printed_page"]}.webp'
        else:
            spec=next(b for b in manifest['books'] if b['id']==book)
            part=next(p for p in spec['parts'] if p['start']<=pdf_page<=p['end'])
            path=ROOT/part['file'].replace('/discrete-math/','');index=pdf_page-part['start'];dest=ROOT/f'textbooks/v32/lesson-pages/{book}-p{pdf_page}.webp'
        if str(path) not in docs:docs[str(path)]=fitz.open(path)
        doc=docs[str(path)]
        assert 0<=index<len(doc),(book,pdf_page)
        entries.append({**render(doc,index,dest),'pdf_page':pdf_page,'printed_page':location['printed_page']})
    for doc in docs.values():doc.close()
    sources[book]={'pages':entries,'scope':'知识点教材定位页节选，非逐字转录讲义'}
    if book=='PHYS':sources[book]['pdf_sha256']=hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest()
audit['source_pages']=sources;audit['physics_source']=sources['PHYS']
(ROOT/'data/lessons-audit-v32.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
print({book:{'pages':len(v['pages']),'bytes':sum(p['bytes'] for p in v['pages'])} for book,v in sources.items()})
