from pathlib import Path
import json,collections,random,hashlib,sys
from books_v14.content import POINTS
from books_v14.originals import originals
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'data'
TOC={
 'LA7':[
 ('行列式',[(1,'二阶与三阶行列式'),(4,'全排列和对换'),(6,'n阶行列式的定义'),(7,'行列式的性质'),(15,'行列式按行（列）展开')],20),
 ('矩阵及其运算',[(24,'线性方程组和矩阵'),(29,'矩阵的运算'),(39,'逆矩阵'),(44,'克拉默法则'),(46,'矩阵分块法')],52),
 ('矩阵的初等变换与线性方程组',[(56,'矩阵的初等变换'),(66,'矩阵的秩'),(71,'线性方程组的解')],78),
 ('向量组的线性相关性',[(82,'向量组及其线性组合'),(87,'向量组的线性相关性'),(91,'向量组的秩'),(95,'向量空间'),(101,'线性方程组的解的结构')],109),
 ('相似矩阵及二次型',[(114,'向量的内积、长度及正交性'),(120,'方阵的特征值与特征向量'),(124,'相似矩阵'),(127,'对称矩阵的对角化'),(131,'二次型及其标准形'),(135,'用配方法化二次型成标准形'),(136,'正定二次型')],138),
 ('线性空间与线性变换',[(142,'线性空间的定义与性质'),(146,'维数、基与坐标'),(148,'基变换与坐标变换'),(150,'线性变换'),(153,'线性变换的矩阵表示式')],157)],
 'PS3':[
 ('随机事件',[(1,'样本空间和随机事件'),(3,'事件的关系和运算')],6),
 ('事件的概率',[(8,'概率的概念'),(9,'古典概型'),(12,'几何概型'),(14,'概率的公理化定义')],18),
 ('条件概率与事件的独立性',[(21,'条件概率'),(23,'全概率公式'),(27,'贝叶斯公式'),(30,'事件的独立性'),(33,'伯努利试验和二项概率'),(35,'主观概率')],36),
 ('随机变量及其分布',[(38,'随机变量及分布函数'),(41,'离散型随机变量'),(48,'连续型随机变量')],59),
 ('二维随机变量及其分布',[(61,'二维随机变量及分布函数'),(62,'二维离散型随机变量'),(64,'二维连续型随机变量'),(67,'边缘分布'),(71,'随机变量的独立性'),(75,'条件分布')],79),
 ('随机变量的函数及其分布',[(82,'一维随机变量的函数及其分布'),(87,'多维随机变量的函数的分布')],96),
 ('随机变量的数字特征',[(97,'数学期望与中位数'),(106,'方差和标准差'),(110,'协方差和相关系数'),(114,'切比雪夫不等式及大数律'),(116,'中心极限定理')],123),
 ('统计量和抽样分布',[(126,'统计与统计学'),(131,'统计量'),(136,'抽样分布')],143),
 ('点估计',[(144,'点估计问题'),(146,'估计方法'),(151,'点估计的优良性')],155),
 ('区间估计',[(157,'置信区间'),(159,'正态总体下的置信区间'),(163,'抽样推断')],167),
 ('假设检验',[(169,'检验的基本原理'),(173,'显著性水平检验法与正态总体检验'),(179,'拟合优度检验')],185),
 ('一元线性回归',[(187,'若干基本概念'),(196,'一元线性回归的检验和置信推断'),(204,'预测')],209)]}
NAMES={'LA7':('LA','工程数学·线性代数（第七版）',4,176),'PS3':('PS','工程数学·概率统计简明教程（第三版）',10,268)}
catalog=json.loads((DATA/'textbook-catalog-v14.json').read_text())
dm=json.loads((DATA/'book.json').read_text())['book'];dm.update(short_title='离散数学',edition='第2版')
books=[dm]+[{key:c[key] for key in ['id','title','short_title','edition','pdf_pages','printed_offset']} for c in catalog['books']]
for b in books[1:]:b['meta']={'pdf_pages':b['pdf_pages'],'printed_offset':b['printed_offset'],'source':'user_supplied','scanned':True,'source_scope':'local_pdf_reading'}
for bid,(prefix,title,offset,pages) in NAMES.items():
 chapters=[];knowledge=[];questions=[];links=[];deps=[]
 for n,(ct,sections,expage) in enumerate(TOC[bid],1):
  cid=f'{prefix}-C{n:02}';start=sections[0][0];end=(TOC[bid][n][1][0][0]-1) if n<len(TOC[bid]) else (159 if bid=='LA7' else 210)
  chapters.append({'id':cid,'book_id':bid,'parent_id':None,'title':f'第 {n} 章 {ct}','kind':'chapter','order':n,'page':start,'end_page':end,'origin':'textbook','scope_complete':False,'source':{'pdf_page':start+offset}})
  for j,(p,st) in enumerate(sections,1):
   chapters.append({'id':f'{cid}-S{j}','book_id':bid,'parent_id':cid,'title':f'{n}.{j} {st}','kind':'section','order':j,'page':p,'end_page':sections[j][0]-1 if j<len(sections) else expage-1,'origin':'textbook','scope_complete':False,'source':{'pdf_page':p+offset}})
  chapters.append({'id':cid+'-EX','book_id':bid,'parent_id':cid,'title':('习题'+str(n)) if bid=='LA7' else f'第{n}章综合题','kind':'section','order':99,'page':expage,'end_page':end,'origin':'textbook','scope_complete':False,'source':{'pdf_page':expage+offset}})
 counts=collections.Counter()
 for p in [p for p in POINTS if p['book']==bid]:
  n=p['chapter'];counts[n]+=1;kid=f'{prefix}-K{n:02}-{counts[n]:02}';cid=f'{prefix}-C{n:02}-S{p["section"]}';page=TOC[bid][n-1][1][p['section']-1][0]
  knowledge.append({'id':kid,'chapter_id':cid,'title':p['title'],'kind':'concept','weight':1,'critical':True,'verification':'reviewed_math','source':{'printed_page':page,'pdf_page':page+offset,'origin':'system_explanation','basis':'依据上传教材对应主题整理；以下讲解和例题为系统讲解，不冒充原文。'},'content':{'plain':p['title']+'：先理解定义，再用不同考法验证。','definition':p['definition'],'example':p['example'],'errors':p['error'],'confusions':p['error'],'estimated_minutes':8}})
  for j,(method,prompt,choices,reason) in enumerate(p['questions'],1):
   qid=f'{prefix}-N14-{n:02}-{counts[n]:02}-{j:02}';correct=choices[0];choices=list(choices);random.Random(hashlib.sha256(qid.encode()).hexdigest()).shuffle(choices);letter='ABCD'[choices.index(correct)]
   questions.append({'id':qid,'chapter_id':cid,'title':p['title']+' · '+method,'prompt':prompt,'kind':'choice','difficulty':1 if j==1 else 2,'page':page,'source_type':'ai_extra','verification':'verified','answer':{'text':letter+'. '+correct,'accepted':[letter,correct]},'explanation':{'steps':[reason],'summary':reason,'errors':[p['error']],'origin':'系统补充练习，独立推导；非教材原题'},'meta':{'options':[f'{"ABCD"[i]}. {c}' for i,c in enumerate(choices)],'practice_group':kid+'-'+method,'family_id':kid+'-'+method,'label':'系统补充练习 · 非教材原题','source_pdf_page':page+offset,'full_statement_version':14,'statement_review':'对象、条件、取值范围、答案与理由逐项检查'}})
   links.append({'question_id':qid,'knowledge_id':kid,'strength':1})
 for index,o in enumerate(originals(bid),1):
  k=next(k for k in knowledge if k['id']==o['point']);qid=f'{prefix}-T14-{index:03}';choices=o['choices'][:];correct=choices[0];random.Random(qid).shuffle(choices);letter='ABCD'[choices.index(correct)]
  questions.append({'id':qid,'chapter_id':k['chapter_id'],'title':o['ref']+' · 教材题选项改编','prompt':o['prompt'],'kind':'choice','difficulty':2,'page':o['page'],'source_type':'textbook','verification':'verified','answer':{'text':letter+'. '+correct,'accepted':[letter,correct]},'explanation':{'steps':o['reason'],'summary':' '.join(o['reason']),'errors':[k['content']['errors']],'origin':'逐题对照原页；选项和详细推导为系统整理'},'meta':{'options':[f'{"ABCD"[i]}. {c}' for i,c in enumerate(choices)],'practice_group':o['group'],'family_id':o['group'],'label':'教材题 · 选项改编','source_reference':o['ref'],'source_pdf_page':o['page']+offset,'full_statement_version':14}})
  links.append({'question_id':qid,'knowledge_id':k['id'],'strength':1})
 # Only direct definitional prerequisites. Chapters remain organizational groups.
 by_title={k['title']:k['id'] for k in knowledge}
 pairs=( [('矩阵初等变换与等价','初等矩阵与求逆'),('矩阵的秩与阶梯形','线性方程组的有解性'),('矩阵的秩与阶梯形','齐次线性方程组与自由变量'),('向量的线性组合与表示','线性相关与线性无关'),('线性相关与线性无关','向量组的秩与最大无关组'),('特征值与特征向量','相似与可对角化'),('特征值与特征向量','实对称矩阵的正交对角化'),('二次型、合同与标准形','配方法与惯性指数'),('二次型、合同与标准形','正定二次型'),('基与坐标的唯一性','基变换与坐标变换'),('线性变换与核、像','线性变换的矩阵表示')] if bid=='LA7' else [('样本空间与随机事件','事件运算、互斥与对立'),('概率公理、加法公式与补事件','条件概率与乘法公式'),('条件概率与乘法公式','全概率公式'),('全概率公式','贝叶斯公式与逆向推断'),('事件独立性','伯努利试验与二项概率'),('二维离散分布','边缘分布'),('边缘分布','条件分布'),('数学期望与中位数','方差、标准差与二阶矩'),('方差、标准差与二阶矩','协方差与相关系数'),('样本均值与样本方差','正态总体的抽样分布'),('置信区间与置信水平','正态总体均值与方差区间'),('假设检验与两类错误','显著性水平、p值与正态检验'),('一元线性回归与最小二乘','回归检验与置信推断'),('一元线性回归与最小二乘','回归预测与预测区间')] )
 for i,(source,target) in enumerate(pairs,1):deps.append({'id':f'{prefix}-D{i:03}','source_type':'knowledge','source_id':by_title[source],'target_type':'knowledge','target_id':by_title[target],'dependency_type':'prerequisite','required_mastery':None,'is_mandatory':True,'condition_operator':'AND','group_id':'default','verification':'confirmed','description':f'后续定义或推导直接使用“{source}”。这是系统核验的知识依赖，不是按整章强制解锁。'})
 book=next(b for b in books if b['id']==bid)
 # Appendices are book structure, not learning points.
 extra=([('部分习题参考答案',160)] if bid=='LA7' else [('辅助材料 统计软件Excel简介',211),('附表一 二项分布表',236),('附表二 泊松分布表',240),('附表三 标准正态分布表',243),('附表四 χ²分布表',245),('附表五 t分布表',247),('附表六 F分布表',249),('附表七 p值表',254),('参考文献',258)])
 for i,(t,p) in enumerate(extra,1):chapters.append({'id':f'{prefix}-APP{i:02}','book_id':bid,'parent_id':None,'title':t,'kind':'appendix','order':100+i,'page':p,'end_page':p,'origin':'textbook','scope_complete':False,'source':{'pdf_page':p+offset}})
 seed={'book':book,'books':books,'chapters':chapters,'knowledge':knowledge,'dependencies':deps,'relations':[],'original_subheadings':[],'question_files':[f'questions-{bid}-v14.json']}
 sourcebook=next(c for c in catalog['books'] if c['id']==bid)
 for k in knowledge:
  chapter=next(ch for ch in chapters if ch['id']==k['chapter_id'].split('-S')[0]); groups=[g for g in sourcebook['exercise_groups'] if k['source']['printed_page']<=g['printed_page']<=chapter['end_page']];g=groups[0] if groups else next((g for g in sourcebook['exercise_groups'] if chapter['page']<=g['printed_page']<=chapter['end_page']),None)
  if g:k['source'].update(exercise_pdf_page=g['pdf_page'],exercise_title=g['title'])
 (DATA/f'book-{bid}.json').write_text(json.dumps(seed,ensure_ascii=False,separators=(',',':'))+'\n')
 (DATA/f'questions-{bid}-v14.json').write_text(json.dumps({'questions':questions,'links':links},ensure_ascii=False,separators=(',',':'))+'\n')
 print(bid,len(knowledge),'knowledge points',len(questions),'reviewed practice questions',len(deps),'dependencies')
(DATA/'books-v14.json').write_text(json.dumps(books,ensure_ascii=False,separators=(',',':'))+'\n')
