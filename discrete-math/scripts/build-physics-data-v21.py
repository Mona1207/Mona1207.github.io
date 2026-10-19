"""Import only the user's 19 numbered questions; retain all other courses."""
from pathlib import Path
import json,shutil,re,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1];D=R/'data'
UPLOAD=Path(__file__).resolve().parents[3]/'upload'
def read(name):return json.loads((D/name).read_text())
def save(name,value):(D/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
EXPECTED={9:[13,14,15,17,28,30],10:[10,15,16,27,28,29],11:[15,16,24,25,27,34,35]}
TOPICS={9:['shm_phase','vertical_spring','shm_phase','contact_loss','shm_energy','shm_energy'],10:['traveling_wave','traveling_wave','traveling_wave','standing_wave','standing_wave','doppler'],11:['double_slit','thin_film','newton_rings','thin_film','single_slit','grating','grating']}
names={9:'九',10:'十',11:'十一'};subjects={9:'振动',10:'波动',11:'光的干涉与衍射'}
book={'id':'PHYS','title':'物理学（下册）精选习题','short_title':'物理学（下册）精选习题','edition':'物理学（下册）· 19 道精选习题','meta':{'source':'user_supplied_images','source_scope':'selected_questions_only','image_count':10,'question_count':19,'numbering_rule':'11-12 表示习题十一第12题','full_textbook_available':False}}
books=[b for b in read('books-v15.json') if b['id']!='PHYS'];books.insert(next((i for i,b in enumerate(books) if b.get('legacy')),len(books)),book);save('books-v15.json',books)
chapters=[]
for n,nums in EXPECTED.items():
 root=f'PH-C{n:02}'
 chapters.extend([{'id':root,'book_id':'PHYS','parent_id':None,'title':f'习题{names[n]} · {subjects[n]}','kind':'chapter','order':n,'origin':'user_selected_exercises','scope_complete':True,'question_count':len(nums)},
 {'id':root+'-S1','book_id':'PHYS','parent_id':root,'title':'关联知识','kind':'section','order':1,'origin':'system_explanation','scope_complete':True}])
knowledge=[];topic_ids={}
for k in read('physics-knowledge-v21.json'):
 kid='PH-K-'+k['key'].replace('_','-');topic_ids[k['key']]=kid
 knowledge.append({'id':kid,'chapter_id':f"PH-C{k['chapter']:02}-S1",'title':k['title'],'kind':'concept','weight':1,'critical':False,'verification':'reviewed','source':{'origin':'system_explanation','basis':'根据用户上传的物理选题补充讲解；非原书逐字转录。'},'content':k['content']})
save('book-PHYS-v15.json',{'book':book,'books':books,'chapters':chapters,'knowledge':knowledge,'dependencies':[],'relations':[],'original_subheadings':[],'questions':[],'links':[]})
source_dir=R/'physics/v21/sources';source_dir.mkdir(parents=True,exist_ok=True)
files={p.name.split('-',1)[1]:p for p in UPLOAD.glob('*-*.png')}
if len(files)!=10:files={p.name:p for p in source_dir.glob('*.png')}
assert len(files)==10,(UPLOAD,len(files))
sources=[]
for n,(name,p) in enumerate(sorted(files.items()),1):
 if p.resolve()!=(source_dir/name).resolve():shutil.copyfile(p,source_dir/name)
 sources.append({'image_number':n,'name':name,'path':'/discrete-math/physics/v21/sources/'+name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
by_name={s['name']:s for s in sources};items=[]
for chapter in EXPECTED:
 entries=read(f'physics-ch{chapter:02}-v21.json')
 assert sorted(int(e['number'].split('-')[1]) for e in entries)==EXPECTED[chapter]
 for entry in entries:
  number=int(entry['number'].split('-')[1]);id=f'SRC-PHYS-E{chapter:03}-{number:03}';assert entry['chapter']==chapter
  topic=TOPICS[chapter][EXPECTED[chapter].index(number)];source_image=by_name[entry['source_image']]
  source={'id':id,'book_id':'PHYS','title':entry['number']+' · 第'+str(number)+'题','kind':'exercise','chapter':chapter,'section_id':f'PH-C{chapter:02}-S1','source_number':number,'group_title':'习题'+names[chapter],'source_type':'uploaded_image','source_image':entry['source_image'],'source_image_url':source_image['path'],'image_number':source_image['image_number'],'source_label':f"习题{names[chapter]} · 第{number}题",'sort_order':chapter*1000+number,'knowledge_ids':[topic_ids[topic]],'segments':[],'answer_segments':[],'boundary_status':'ocr_located'}
  item={k:v for k,v in entry.items() if k not in ['figure_crop','knowledge_key']}
  item.update(source,source=source,status='reviewed',answer_status='reviewed',text_origin='user_supplied_image_ocr',solution_origin='根据上传题图独立核对的补充解答；原图手写结果有误时已订正',review_basis='逐项对照 '+entry['source_image']+' 的印刷题干、题号和必要图形，独立推导并核对初始条件、单位和数值。')
  crop=entry.get('figure_crop')
  if crop:
   crop_name=re.sub(r'^\d{2}-','',Path(crop['file']).name)
   assert crop_name==entry['source_image']
   with Image.open(files[entry['source_image']]) as image:
    box=crop['bbox'];assert len(box)==4 and all(0<=v<=1 for v in box)
    box=[round(box[0]*image.width),round(box[1]*image.height),round(box[2]*image.width),round(box[3]*image.height)]
    assert box[0]<box[2] and box[1]<box[3]
    path=R/f'physics/v21/figures/{entry["number"]}.png';path.parent.mkdir(parents=True,exist_ok=True)
    image.crop(box).save(path)
   item['prompt']+='\n\n![原题 '+entry['number']+' 图](/discrete-math/physics/v21/figures/'+entry['number']+'.png)'
   item['figure_source']={'image':entry['source_image'],'bbox':crop['bbox']}
  items.append(item)
items.sort(key=lambda i:i['sort_order'])
audit={'book':'PHYS','numbered_questions':len(items),'reviewed_questions':len(items),'remaining_questions':0,'source_images':len(sources),'selected_only':True,'numbering_rule':book['meta']['numbering_rule'],'chapters':[{'chapter':n,'title':'习题'+names[n],'numbers':nums,'total':len(nums)} for n,nums in EXPECTED.items()]}
save('exercises-PHYS-v21.json',{'version':21,'book':'PHYS','items':items,'sources':sources,'excluded_ids':[],'audit':audit})
save('physics-audit-v21.json',audit)
assert len(items)==19
print('Imported 19 selected physics questions, 12 knowledge topics, 10 unchanged source images and 5 question figures.')
