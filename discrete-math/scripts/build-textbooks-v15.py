from pathlib import Path
import ast,collections,csv,json,math,re,runpy
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data'
config=runpy.run_path(str(ROOT/'scripts/textbook-config-v15.py'));dm_toc=config['DM_TOC'];dm_map=config['DM_SECTION_MAP']
tree=ast.parse((ROOT/'scripts/build-books-v14.py').read_text());old_toc=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='TOC' for t in n.targets))
TOCS={'DM2T':dm_toc,**old_toc};OFFSET={'DM2T':11,'LA7':4,'PS3':10};PAGES={'DM2T':414,'LA7':176,'PS3':268}
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n')
def load(path):return json.loads(path.read_text())
oldbooks=load(DATA/'books-v14.json');old_dm=load(DATA/'book.json');legacy=oldbooks[0];legacy.update(short_title='离散数学·旧学习指导',title='离散数学·学习指导与习题解析（第2版）·历史记录',legacy=True)
books=[{'id':'DM2T','title':'离散数学（第2版）','short_title':'离散数学','edition':'第2版 · 屈婉玲、耿素云、张立昂','meta':{'pdf_pages':414,'printed_offset':11,'source':'user_supplied','source_scope':'local_pdf_reading'}},*oldbooks[1:],legacy]
# New original textbook structure; no guidebook section numbering is reused as source numbering.
chapters=[]
for n,(title,sections,ex) in enumerate(dm_toc,1):
 cid=f'DM-C{n:02}';end=dm_toc[n][1][0][0]-1 if n<len(dm_toc) else 390
 chapters.append({'id':cid,'book_id':'DM2T','parent_id':None,'title':f'第 {n} 章 {title}','kind':'chapter','order':n,'page':sections[0][0],'end_page':end,'origin':'textbook','scope_complete':False,'source':{'pdf_page':sections[0][0]+11}})
 for j,(page,st) in enumerate(sections,1):chapters.append({'id':f'{cid}-S{j}','book_id':'DM2T','parent_id':cid,'title':f'{n}.{j} {st}','kind':'section','order':j,'page':page,'end_page':(sections[j][0]-1 if j<len(sections) else ex),'origin':'textbook','scope_complete':False,'source':{'pdf_page':page+11}})
 chapters.append({'id':cid+'-EX','book_id':'DM2T','parent_id':cid,'title':f'习题 {n}','kind':'section','order':99,'page':ex,'end_page':end,'origin':'textbook','scope_complete':False,'source':{'pdf_page':ex+11}})
for i,(title,page) in enumerate([('名词与术语索引',391),('符号注释',400),('参考文献',403)],1):chapters.append({'id':f'DM-APP{i:02}','book_id':'DM2T','parent_id':None,'title':title,'kind':'appendix','order':100+i,'page':page,'end_page':page,'origin':'textbook','scope_complete':False,'source':{'pdf_page':page+11}})
knowledge=old_dm['knowledge']
for k in knowledge:
 n=int(k['id'][4:6]);number=int(k['id'][7:9]);sec=dm_map[n][number-1];page=dm_toc[n-1][1][sec-1][0];k['chapter_id']=f'DM-C{n:02}-S{sec}';k['source']={'printed_page':page,'pdf_page':page+11,'origin':'system_explanation','basis':'按新上传正教材的小节对应主题重新定位；系统讲解不是原文逐字转录。'}
# Fill every original section that previously had no learning point.
for ch in [c for c in chapters if c['kind']=='section' and not c['id'].endswith('EX')]:
 if any(k['chapter_id']==ch['id'] for k in knowledge):continue
 n=int(ch['id'][4:6]);sec=int(ch['id'].split('-S')[1]);kid=f'DM-K{n:02}-S{sec:02}'
 knowledge.append({'id':kid,'chapter_id':ch['id'],'title':ch['title'].split(' ',1)[1],'kind':'concept','weight':1,'critical':False,'verification':'source_scope','source':{'printed_page':ch['page'],'pdf_page':ch['page']+11,'origin':'system_explanation','basis':'新增原书小节节点，原书完整定义、定理及例题可在本节原页中对照。'},'content':{'plain':'沿原书定位定义、定理条件与解法。','definition':'本知识点对应 '+ch['title']+'；完整原文、公式与图表保留在原书本节。','example':'本节原书例题已在下方原题索引关联。','errors':'先确认题目对象、条件与要求；不能把前一小节的定理直接用于本题。','estimated_minutes':12}})
# Prior practice remains supplemental, explicitly separated from the new original text.
qs=[];links=[]
for file in old_dm['question_files']:
 shard=load(DATA/file);qs.extend(shard['questions']);links.extend(shard['links'])
by_id={k['id']:k for k in knowledge};old_links={l['question_id']:l['knowledge_id'] for l in links}
for q in qs:
 k=by_id.get(old_links.get(q['id']));
 if k:q['chapter_id']=k['chapter_id'];q['page']=k['source']['printed_page'];q['meta']['source_pdf_page']=k['source']['pdf_page']
 if q['source_type']=='textbook':q['source_type']='ai_extra';q['meta']['label']='旧学习指导衍生练习 · 非本书原题'
filelist=[]
for start in range(0,len(qs),180):
 name=f'questions-DM2T-v15-{start//180+1:03}.json';chunk=qs[start:start+180];ids={q['id'] for q in chunk};save(DATA/name,{'questions':chunk,'links':[l for l in links if l['question_id'] in ids]});filelist.append(name)
seeds={'DM2T':{'book':books[0],'books':books,'chapters':chapters,'knowledge':knowledge,'dependencies':old_dm['dependencies'],'relations':old_dm['relations'],'original_subheadings':[],'question_files':filelist}}
for bid in ['LA7','PS3']:seeds[bid]=load(DATA/f'book-{bid}.json');seeds[bid]['books']=books
catalog=load(DATA/'textbook-catalog-v14.json');sources={b['id']:b for b in catalog['books']}
sources['DM2T']={'id':'DM2T','title':books[0]['title'],'short_title':'离散数学','edition':books[0]['edition'],'pdf_pages':414,'printed_offset':11,'original_pdf_public':False,'scan_status':'full_book_processed_local_reading','exercise_groups':[{'title':f'习题 {i}','printed_page':ex,'pdf_page':ex+11} for i,(_,_,ex) in enumerate(dm_toc,1)]}
for bid in seeds:
 seeds[bid]['books']=books
 for k in seeds[bid]['knowledge']:k['source']['section_id']=k['chapter_id']
 save(DATA/f'book-{bid}-v15.json',seeds[bid])
save(DATA/'books-v15.json',books);save(DATA/'textbook-catalog-v15.json',{'version':15,'books':list(sources.values())})
print('Structure built:',[(bid,len(b['knowledge'])) for bid,b in seeds.items()])
