"""Merge separately source-checked corrections without treating OCR as reviewed."""
from pathlib import Path
import json,collections
R=Path(__file__).resolve().parents[1];D=R/'data';reports=[]
manifest=json.loads((D/'textbook-assets-v16.json').read_text())
for book in ['DM2T','LA7','PS3']:
 payload=json.loads((D/f'exercises-{book}-v19.json').read_text())
 indexed={i['id']:i for i in payload['items']}
 knowledge={k['id'] for k in json.loads((D/f'book-{book}-v15.json').read_text())['knowledge']}
 patches={};excluded=[]
 for file in sorted(D.glob(f'review-{book}-*-v20.json')):
  for id,patch in json.loads(file.read_text()).items():patches[id]={**patches.get(id,{}),**patch}
 for id,patch in patches.items():
   if patch.get('exclude'):
    indexed.pop(id,None);excluded.append(id);continue
   if id not in indexed:
    assert patch.get('source'),(id,'missing source for added question')
    src=patch['source'];assert src['id']==id and src['book_id']==book
    indexed[id]={'id':id,'title':src['title'],'kind':src['kind'],'source':src,'text_origin':'uploaded_textbook_scan_ocr','source_pages':sorted({s['page'] for s in src['segments']})}
   item=indexed[id];item.update(patch)
   if item.get('figures'):
    import fitz
    figure_links=[]
    book_assets=next(b for b in manifest['books'] if b['id']==book)
    for n,figure in enumerate(item['figures'],1):
     part=next(p for p in book_assets['parts'] if p['start']<=figure['page']<=p['end'])
     bbox=figure['bbox'];assert len(bbox)==4 and all(0<=x<=1 for x in bbox) and bbox[0]<bbox[2] and bbox[1]<bbox[3],(id,'figure rectangle')
     with fitz.open(R/part['file'].replace('/discrete-math/','')) as pdf:
      page=pdf[figure['page']-part['start']];rect=page.rect;clip=fitz.Rect(bbox[0]*rect.width,bbox[1]*rect.height,bbox[2]*rect.width,bbox[3]*rect.height)
      relative=f'figures/v20/{id}-{n}.png';destination=R/relative;destination.parent.mkdir(parents=True,exist_ok=True)
      page.get_pixmap(matrix=fitz.Matrix(2,2),clip=clip).save(destination)
     figure_links.append('!['+figure.get('caption','原书题图 '+str(n))+'](/discrete-math/'+relative+')')
    item['prompt']+='\n\n'+'\n\n'.join(figure_links)
   for n,plot in enumerate(item.get('plots') or [],1):
    import math
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import FontProperties
    x=plot['x'];y=plot['y'];assert len(x)==len(y) and len(x)>1 and all(math.isfinite(v) for v in x+y),(id,'scatter data')
    fig,ax=plt.subplots(figsize=(5.4,3.7),layout='constrained');ax.scatter(x,y,s=30,color='#457c65',zorder=3)
    if 'slope' in plot and 'intercept' in plot:
     span=[min(x),max(x)];ax.plot(span,[plot['intercept']+plot['slope']*v for v in span],color='#e66a4d',linewidth=1.5)
    font_path=Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc');font=FontProperties(fname=str(font_path)) if font_path.exists() else None
    ax.set_xlabel(plot.get('x_label','x'),fontproperties=font);ax.set_ylabel(plot.get('y_label','y'),fontproperties=font);ax.grid(alpha=.2);ax.spines[['top','right']].set_visible(False)
    relative=f'figures/v20/{id}-plot-{n}.png';destination=R/relative;destination.parent.mkdir(parents=True,exist_ok=True);fig.savefig(destination,dpi=160);plt.close(fig)
    field=plot.get('in','solution');assert field in ['prompt','solution'];item[field]+='\n\n!['+plot.get('caption','散点图')+'](/discrete-math/'+relative+')'
   assert item['knowledge_ids'] and set(item['knowledge_ids'])<=knowledge,(id,'unknown knowledge')
   assert item['prompt'] and item['solution'] and item['explanation'],(id,'incomplete correction')
   assert item['status']=='reviewed' and item['answer_status']=='reviewed'
   item['source']['knowledge_ids']=item['knowledge_ids']
   # Corrected source metadata always travels with the same stable id.
   item['source']['id']=id
 # Whole-group entries contain the same checked text as their individual items.
 # They must not silently continue serving the obsolete, damaged OCR page text.
 for group in [i for i in indexed.values() if i['kind']=='exercise_group']:
  number=group['id'].split('-G')[-1]
  children=sorted([i for i in indexed.values() if i['kind']=='exercise' and i['id'].startswith(f'SRC-{book}-E{number}-')],key=lambda i:i['source'].get('source_number',0))
  if not children:continue
  group['prompt']='\n\n'.join('### 第 '+str(i['source']['source_number'])+' 题\n\n'+i['prompt'] for i in children)
  group['solution']='\n\n'.join('### 第 '+str(i['source']['source_number'])+' 题\n\n'+(i.get('solution') or '本题解答待补充。') for i in children)
  group['explanation']=['第 '+str(i['source']['source_number'])+' 题\n\n'+'\n\n'.join(i.get('explanation') or ['讲解待补充。']) for i in children]
  complete=all(i.get('status')=='reviewed' and i.get('answer_status')=='reviewed' for i in children)
  group.update(status='reviewed' if complete else 'partial_review',answer_status='reviewed' if complete else 'partial_review',knowledge_ids=list(dict.fromkeys(k for i in children for k in i['knowledge_ids'])),solution_origin='本组逐题校订解答汇总；各题保留独立来源记录',issues=[] if complete else ['本组仍有题目或解析未校订，见各题说明。'])
 items=sorted(indexed.values(),key=lambda i:(i['source'].get('pdf_page',0),i['source'].get('segments',[{}])[0].get('top',0),i['id']))
 numbered=[i for i in items if i['kind']=='exercise']
 reviewed=[i for i in numbered if i['status']=='reviewed' and i['answer_status']=='reviewed']
 report={'book':book,'numbered_questions':len(numbered),'reviewed_questions':len(reviewed),'remaining_questions':len(numbered)-len(reviewed),'missing_answers':sum(not i.get('solution') for i in numbered),'pending_ids':[i['id'] for i in numbered if i not in reviewed],'chapters':[{'chapter':c,'total':sum(i['source']['chapter']==c for i in numbered),'reviewed':sum(i['source']['chapter']==c for i in reviewed)} for c in sorted({i['source']['chapter'] for i in numbered})]}
 payload.update(version=20,items=items,audit=report,excluded_ids=excluded)
 (D/f'exercises-{book}-v20.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n')
 reports.append(report);print(book,len(reviewed),'/',len(numbered),'source-checked questions and solutions')
(D/'exercise-audit-v20.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
