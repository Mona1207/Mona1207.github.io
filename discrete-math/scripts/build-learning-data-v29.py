"""Expand the existing textbooks in place; keep every historical knowledge/question ID."""
import json,re,runpy,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data'
def read(file):return json.loads((DATA/file).read_text())
def write(file,value):(DATA/file).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
old=read('book-PHYS-v15.json');old_by_id={k['id']:k for k in old['knowledge']}
primary={'9-1':'shm-phase','9-4':'shm-energy','10-2':'traveling-wave','10-5':'standing-wave','10-6':'doppler','11-2':'double-slit','11-3':'thin-film','11-6':'single-slit','11-8':'grating'}
topics={};chapters=[];knowledge=[];names={9:'九',10:'十',11:'十一',12:'十二',13:'十三',14:'十四',15:'十五',16:'十六'}
titles={9:'振动',10:'波动',11:'光学',12:'气体动理论',13:'热力学基础',14:'相对论',15:'量子物理',16:'原子核与粒子物理简介'}
starts={9:1,10:44,11:96,12:185,13:227,14:281,15:323,16:421}
diagram_map={'9-1':'shm','9-2':'phasor','9-3':'pendulum','9-4':'energy','9-6':'resonance','10-1':'wave','10-2':'wave','10-4':'double-slit','10-5':'standing','11-1':'double-slit','11-2':'double-slit','11-3':'thin-film','11-4':'newton','11-5':'single-slit','11-6':'single-slit','11-7':'single-slit','11-8':'single-slit','11-9':'polarization','11-12':'polarization','12-1':'ideal-gas','12-2':'ideal-gas','12-3':'ideal-gas','12-4':'distribution','12-6':'distribution','13-1':'pv','13-2':'heat-engine','13-5':'heat-engine','13-6':'heat-engine','14-3':'light-clock','14-4':'light-clock','15-2':'levels','15-4':'levels','15-5':'levels','15-8':'tunnel','15-14':'tunnel','16-1':'decay'}
conditions={'9-1':'理想弹簧、无耗散，回复力在线性范围内；位移从平衡位置量起，三角函数角度采用弧度。','9-3':'小角度摆动，忽略空气阻力及轴摩擦；重力场近似均匀，转轴固定。','9-4':'理想简谐振动、无外力做净功及耗散；若有碰撞、阻尼或驱动力，要重新核对能量收支。','9-7':'理想集总参数 LC 回路；忽略电阻、辐射和电容电感参数随时间变化。','10-2':'介质均匀、线性，讨论稳定平面简谐行波；波函数在波已传播到的范围内成立。','10-5':'两波同频、等幅、反向传播，端点条件固定；实际阻尼和驱动决定稳态可维持的幅度。','10-6':'经典声波、介质静止且波源与接收者沿连线运动，未进入激波情形；所有速度相对介质。','11-2':'相干、近轴、小角度，缝屏距远大于缝距；更大角度须保留精确几何关系。','11-3':'薄膜近似平行且透明；半波损失按两界面折射率顺序分别判断；波长符号取真空或空气值并统一。','11-6':'单缝均匀照明、远场观察；小角度屏距公式和旁极大半波带法均为近似，暗纹角条件更一般。','11-8':'理想等间距透射光栅；正入射公式与斜入射公式应区分，缺级还需知道单缝宽度。','11-9':'理想偏振片和准单色光；自然光通过首片减半，之后的入射偏振态须逐片更新。','12-1':'处于平衡态的稀薄理想气体；使用绝对压强与热力学温度，质量和物质的量不可混淆。','12-5':'经典平衡条件，分子自由度在该温度范围有效；刚性双原子近似忽略振动自由度。','12-6':'麦克斯韦分布适用于经典、非相对论、稀薄平衡气体；题设另给分布时应按题设积分。','12-8':'稀薄气体的硬球碰撞模型，有效分子直径近似不变；区分定压与定容升温。','13-3':'一定量理想气体，摩尔热容在温区内近似常量；只计体积功。','13-4':'等温计算取理想气体；绝热幂律限于准静态可逆且热容比近似恒定的过程。','13-5':'每个循环回到同一状态；效率分母为从外界吸收的正热量之和，需明确是否有回热器。','13-7':'熵是平衡态函数；不可逆过程通过同端点的假想可逆路径计算，熵增判据用于孤立系统总熵。','14-3':'惯性系、标准配置，坐标轴平行，原点在零时刻重合；相对速度大小小于真空光速。','14-4':'长度指同一测量系同时记录两端的位置差；时间延缓式要求先认出固有时间。','14-6':'自由粒子使用不变静止质量；系统反应须同时守恒总能量和总动量。','15-4':'氢原子或适当修正后的类氢体系；玻尔轨道是历史模型，现代描述为量子态。','15-8':'所给薛定谔方程为非相对论、一维、定态形式；概率须归一化并满足边界条件。'}
symbols={9:r'$x$：位移（米）；$A$：振幅（米）；$\omega$：角频率（弧度每秒）；$T$：周期（秒）；$\varphi$：初相（弧度）。',10:r'$u$：波速（米每秒）；$\lambda$：波长（米）；$\nu$：频率（赫兹）；$k$：波数（每米）；$y$：质点位移（米）。',11:r'$\lambda$：真空或空气波长（米）；$n$：折射率（无量纲）；$e$：膜厚（米）；$I$：光强；$\theta$：由相应法线量取的角度。',12:r'$N$：分子总数；$n_N=N/V$：数密度（每立方米）；$n_{\mathrm{mol}}$：物质的量（摩尔）；$m$：单分子质量（千克）；$M$：摩尔质量（千克每摩尔）；$k=1.380649\times10^{-23}\,\mathrm{J/K}$。',13:r'$Q$：系统吸热为正；$W$：系统对外做功为正；$U$：内能（焦耳）；$S$：熵（焦耳每开尔文）；$C_V,C_p$：摩尔热容；$T$：开尔文温度。',14:r'$c$：真空光速；$v$：参考系或物体的相应速度；$\gamma=(1-v^2/c^2)^{-1/2}$；$m_0$：静止质量；$E$：总能量；$K$：动能。',15:r'$h$：普朗克常量；$\hbar=h/(2\pi)$；$\nu$：频率；$E$：能量；$\psi$：波函数；$\lvert\psi\rvert^2$：概率密度；$1\,\mathrm{eV}=1.602176634\times10^{-19}\,\mathrm J$。',16:r'$A$：质量数或衰变活度，依上下文区分；$Z$：质子数；$N$：中子数或未衰变核数，依上下文区分；$\lambda$：衰变常量；$T_{1/2}$：半衰期。'}
for ch in titles:chapters.append({'id':f'PH-C{ch:02}','book_id':'PHYS','parent_id':None,'title':f'第{names[ch]}章 · {titles[ch]}','kind':'chapter','order':ch,'origin':'textbook_toc','source':{'printed_page':starts[ch],'pdf_page':starts[ch]+15}})
for line in (ROOT/'scripts/physics-lessons-v29.txt').read_text().splitlines():
 if not line or line.startswith('#'):continue
 number,page,title,definition,theory,reason,example,errors=line.split('|');ch,sec=map(int,number.split('-'));page=int(page)
 section=f'PH-C{ch:02}-S{sec}';chapters.append({'id':section,'book_id':'PHYS','parent_id':f'PH-C{ch:02}','title':number+' '+title,'kind':'section','order':sec,'origin':'textbook_toc','source':{'printed_page':page,'pdf_page':page+15}})
 kid='PH-K-'+primary[number] if number in primary else 'PH-K-'+number;topics[number]=kid
 content={'plain':definition,'definition':definition,'theory':theory,'method':reason,'reason':example,'example':example,'errors':errors,'confusions':'','conditions':conditions.get(number,'先核对本节明确的物理模型与过程约束；定量计算统一单位，不能将某一种条件下的结论推广为无条件规律。'),'symbols':symbols[ch],'estimated_minutes':18,'content_version':29,'check':'把结果的单位和正负号代回题意；检查零速度、零温差、小角度或低速等本题适用的极限。用公式之前，应能说明每个量代表什么。'}
 if number in diagram_map:content['theory']+='\n\n![本节讲解示意图：'+title+'](/discrete-math/physics/v29/diagrams/'+diagram_map[number]+'.svg)'
 knowledge.append({'id':kid,'chapter_id':section,'title':title,'kind':'concept','weight':1,'critical':ch in [11,12,13,14],'verification':'reviewed','source':{'printed_page':page,'pdf_page':page+15,'origin':'textbook_based_system_explanation','basis':'目录与知识主题依据用户上传的第七版下册；本页公式推导、例子与图示为学习补充。'},'content':content})
# Preserve the three old, more focused topics which are not whole textbook sections.
for oldid,lesson,diagram in [('PH-K-vertical-spring','9-1','shm'),('PH-K-contact-loss','9-1','shm'),('PH-K-newton-rings','11-4','newton')]:
 k=old_by_id[oldid];k['content']['theory']=re.sub(r'\n\n!\[相关图示\]\([^)]*\)', '', k['content']['theory']);k['chapter_id']=next(x['chapter_id'] for x in knowledge if x['id']==topics[lesson]);k['source']={'origin':'textbook_based_system_explanation','printed_page':1 if lesson=='9-1' else 114,'pdf_page':16 if lesson=='9-1' else 129};k['content']['theory']+='\n\n![相关图示](/discrete-math/physics/v29/diagrams/'+diagram+'.svg)';k['content']['content_version']=29;knowledge.append(k)
assert len(knowledge)==78,len(knowledge)
book={**old['book'],'title':'物理学（第七版）下册','short_title':'物理学（下册）','edition':'第七版 · 第九至十六章','meta':{'source':'user_uploaded_pdf_and_selected_images','full_textbook_available':True,'knowledge_sections':75,'knowledge_topics':78,'numbering_rule':'11-12 表示习题十一第12题','source_note':'上传扫描包含正文第1—437页；目录列出的书后答案与索引页未包含，解析由系统独立编写。'}}
old_items=read('exercises-PHYS-v21.json');items=old_items['items'];new=runpy.run_path(str(ROOT/'scripts/physics-questions-v29.py'))['ITEMS'];seen={i['number'] for i in items}
for row in new:
 assert row['number'] not in seen,row['number'];seen.add(row['number']);ch,num=map(int,row['number'].split('-'));kid=topics[row['lesson']];section=next(k['chapter_id'] for k in knowledge if k['id']==kid);id=f'SRC-PHYS-E{ch:03}-{num:03}';page=row['printed_page'];pdf=page+15
 source={'id':id,'book_id':'PHYS','title':row['number']+' · '+('选择题' if row['choice_answer'] else f'第{num}题'),'kind':'exercise','chapter':ch,'section_id':section,'source_number':num,'group_title':'习题'+names[ch],'source_type':'uploaded_textbook_pdf','source_label':f'习题{names[ch]} · 第{num}题 · 教材第{page}页','sort_order':ch*1000+num,'knowledge_ids':[kid],'segments':[],'answer_segments':[],'boundary_status':'ocr_located','pdf_page':pdf,'printed_page':page,'image_number':pdf,'source_image':f'textbook-page-{page}.jpg','source_image_url':f'/discrete-math/physics/v29/sources/p{page}.jpg'}
 prompt=row['prompt']
 if row['figure']:prompt+='\n\n![教材原题 '+row['number']+' 图](/discrete-math/physics/v29/figures/'+row['number']+'.png)'
 items.append({**source,'number':row['number'],'source':source.copy(),'prompt':prompt,'solution':row['solution'],'explanation':row['explanation'],'issues':row['issues'],'question_type':'choice' if row['choice_answer'] else 'calculation','choice_answer':row['choice_answer'],'options':row['options'],'status':'reviewed','answer_status':'reviewed','text_origin':'user_uploaded_textbook_ocr_reviewed','solution_origin':'依据上传教材题干独立推导的学习解析','review_basis':'对照教材印刷题干、题号、单位与题图校订；解析独立计算，未冒充书后答案。'})
items.sort(key=lambda i:i['sort_order'])
# Update old source section paths, keeping their IDs and all user-record keys intact.
knowledge_lookup={k['id']:k for k in knowledge}
for item in items:
 item['section_id']=knowledge_lookup[item['knowledge_ids'][0]]['chapter_id'];item['source']['section_id']=item['section_id']
for ch in chapters:
 ch['question_count']=sum(1 for i in items if i['chapter']==int(ch['id'][4:6])) if not ch['parent_id'] else sum(i['section_id']==ch['id'] for i in items)
book['meta']['question_count']=len(items)
books=read('books-v15.json');books=[book if b['id']=='PHYS' else b for b in books];write('books-v15.json',books)
for k in knowledge:
 related=[q for q in items if k['id'] in q['knowledge_ids']]
 k['content']['worked_examples']=[{'title':q['number']+' · 教材习题讲解','prompt':q['prompt'],'answer':q['solution'],'steps':q['explanation'],'label':'用户提供教材题干 · 解析为独立编写'} for q in related[:2]]
write('book-PHYS-v15.json',{**old,'book':book,'books':books,'chapters':chapters,'knowledge':knowledge})
requested={11:[15,16,24,25,27,34,35,38],12:[10,19,20,22,25,27],13:[22,24,27,29,32,38],14:[17,23,24,27,28,29]}
for ch,nums in requested.items():assert all(f'{ch}-{n}' in seen for n in nums)
audit={'version':29,'book':'PHYS','questions':len(items),'preserved_question_ids':len(old_items['items'])-len(new),'added_questions':len(new),'choice_questions':sum(bool(i.get('choice_answer')) for i in items),'requested_numbers':requested,'reviewed_questions':len(items),'chapters':8,'textbook_sections':75,'knowledge_topics':78,'original_pdf_sha256':'','source_pages':sorted({i['printed_page'] for i in items if i.get('text_origin')=='user_uploaded_textbook_ocr_reviewed'}),'notes':['保留全部旧题ID与学习记录键。','第11-27、11-34、11-35等原题条件及解释按旧版校核结果保留，不擅自补成唯一解。','教材扫描没有书后答案和索引页，解析为独立编写。']}
write('exercises-PHYS-v29.json',{'version':29,'book':'PHYS','items':items,'sources':old_items.get('sources',[]),'excluded_ids':[],'audit':audit})
write('physics-audit-v29.json',audit)
# Give new questions content-based, explicitly provisional ratings so filters include them.
ratings=read('ratings-PHYS-v23.json')
ratingmap=ratings['items'];template=next(iter(ratingmap.values()))
for i in items:
 if i['id'] in ratingmap:continue
 r=json.loads(json.dumps(template));r.update({'topics':[knowledge_lookup[k]['title'] for k in i['knowledge_ids']],'level':1 if i.get('choice_answer') else 3,'recommended':True,'evidence':['根据本题所需的定义辨析、公式步骤与运算量进行内容分析暂评；不代表用户实际掌握情况。'],'recommendation_reasons':['本次新增的教材选择题或用户指定题，建议完成。']});ratingmap[i['id']]=r
write('ratings-PHYS-v23.json',ratings)
# Reveal the existing worked derivations instead of hiding them behind the old short theory summary.
total=0;worked=0
for filename,readyfile in [('book-DM2T-v15.json','examples-DM2T-ready-v17.json'),('book-LA7-v15.json','examples-LA7-ready-v17.json'),('book-PS3-v15.json','examples-PS3-ready-v17.json'),('book.json',None)]:
 d=read(filename);examples=read(readyfile)['items'] if readyfile else [];byid={ex['id']:ex for ex in examples}
 for k in d['knowledge']:
  c=k.get('content',{});cases=list(c.get('exam_cases',[])[:3]);seen_prompts={x.get('prompt') for x in cases}
  candidates=[byid[id] for id in k.get('source_item_ids',[]) if id in byid]
  if not candidates:candidates=[ex for ex in examples if k['id'] in ex.get('knowledge_ids',[])]
  for ex in candidates[:2]:
   if ex.get('status')!='reviewed':continue
   prompt=ex.get('prompt','');prompt='\n\n'.join(prompt) if isinstance(prompt,list) else prompt
   if prompt in seen_prompts:continue
   answer=ex.get('solution','');answer='\n\n'.join(answer) if isinstance(answer,list) else answer
   cases.append({'title':ex.get('title','教材例题'),'prompt':prompt,'answer':answer,'steps':ex.get('explanation',[]),'label':'教材例题转写 · 分步讲解为学习补充'});seen_prompts.add(prompt)
  c['worked_examples']=cases;c['content_version']=29
  if cases:worked+=1
  # Attach a relevant structural diagram without replacing mathematical prose.
  title=k['title'];dia=None
  if re.search('集合运算|事件运算|样本空间',title):dia='venn'
  elif re.search('关系矩阵|关系图',title):dia='relation'
  elif re.search('内积|正交与标准|线性组合',title):dia='vector'
  elif re.search('正态分布|中心极限',title):dia='normal'
  if dia and '/physics/v29/diagrams/' not in c.get('theory',''):c['theory']=c.get('theory','')+'\n\n![知识图示](/discrete-math/physics/v29/diagrams/'+dia+'.svg)'
  total+=1
 write(filename,d)
print('physics:',len(items),'questions,',len(knowledge),'topics; existing courses:',total,'topics,',worked,'with worked examples')
