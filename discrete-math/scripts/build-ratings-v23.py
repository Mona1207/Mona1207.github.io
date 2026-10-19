"""Auditable content ratings; these are not empirical facility/error-rate statistics.

The four dimensions describe mathematical demand, never solution prose length,
chapter number, raw number of subquestions, or the student's recorded mistakes.
Every rating retains the observed task features and the topic anchors it used.
"""
from pathlib import Path
import json,re,collections,hashlib
R=Path(__file__).resolve().parents[1];D=R/'data'
def read(p):return json.loads((D/p).read_text())
def save(p,d):(D/p).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
LEVELS={1:'概念辨认',2:'常规应用',3:'进阶推理',4:'综合探究'}
RUBRIC={
 'version':23,'basis':'内容分析暂评','reference':'以已经学习对应章节基本定义、定理和常规方法的本科生为参照；不按零基础体感或题目所在章号评级。',
 'levels':[{'level':1,'name':LEVELS[1],'score':[0,1],'description':'辨认、读写或直接代入一个定义/公式，无实质性方法选择。'},
 {'level':2,'name':LEVELS[2],'score':[2,3],'description':'选用熟悉的标准方法，完成常规计算、直接论证或简单表征转换。'},
 {'level':3,'name':LEVELS[3],'score':[4,5],'description':'需要较明显的方法选择、一般性论证、参数分类、建模或联结多个步骤。'},
 {'level':4,'name':LEVELS[4],'score':[6,8],'description':'多个知识模块与非直接推理相结合，需较复杂构造、多阶段证明或综合模型。'}],
 'dimensions':[
  {'key':'integration','name':'知识整合','anchors':['一个核心概念或公式','同章多个相互依赖的概念','不同知识模块形成必要的推理链']},
  {'key':'strategy','name':'方法选择','anchors':['题目直接给出方法或只是辨认','需要选择一种常规方法','需要构造、反例、逆向设计或比较不同方案']},
  {'key':'reasoning','name':'推理深度','anchors':['读写或直接代入','常规运算/直接论证','多阶段论证、参数分类或结构性推导']},
  {'key':'representation','name':'表征与建模','anchors':['使用题目给定表征','图文/公式转换或常规模型建立','隐含约束、多模型转换或较复杂边界处理']}],
 'excluded_factors':['不按解析篇幅、教学步骤条数、小问数量或题号远近加难度','计算量大但方法固定，不自动升为综合题','原题条件缺失/歧义单独标注，不把缺条件当成数学难度'],
 'recommendation':'每个知识点优先选一题例题入门、一题常规习题，并在有需要时选取不同方法/进阶应用的代表题；相似变式用于巩固。推荐不代表考试频率或必考。',
 'limitations':'尚无统一限时作答样本、通过率和区分度；等级为可解释的内容分析暂评，不能宣称客观测量值。知识点的范围只汇总已加载的单题，整组入口显示其子题范围。'
}
# Explicit curriculum anchors: I/S/R/M, each 0..2. The stem can reduce a
# calculation topic to recognition, or raise a routine case to a proof/model.
DM={
'01-01':(0,0,0,0),'01-02':(0,0,0,1),'01-03':(0,1,1,0),
'02-01':(0,1,1,0),'02-02':(1,1,1,0),'02-S03':(1,1,1,0),'02-S04':(1,1,2,0),
'03-01':(1,1,1,0),'03-02':(0,0,0,1),'03-S03':(1,1,2,0),
'04-01':(0,1,0,1),'04-02':(0,0,0,1),'05-01':(0,1,1,0),'05-02':(0,1,1,1),'05-S03':(1,1,2,0),
'06-01':(0,0,0,0),'06-02':(0,0,1,0),'06-03':(0,1,1,0),'06-S03':(1,1,1,0),'06-S04':(0,1,1,0),
'07-01':(0,0,1,0),'07-02':(0,0,1,0),'07-03':(0,0,1,1),'07-04':(0,1,1,0),'07-05':(1,1,1,0),'07-06':(1,1,1,0),'07-07':(1,1,1,0),'07-08':(0,1,1,1),
'08-01':(0,1,1,0),'08-02':(0,1,1,0),'08-S02':(1,1,1,0),'08-S03':(1,1,1,1),'08-S04':(1,1,1,1),
'09-01':(0,1,1,0),'09-02':(1,1,1,0),'09-S02':(1,1,1,0),'09-S03':(1,1,2,1),
'10-01':(1,1,1,0),'10-02':(1,1,1,0),'10-S03':(1,1,1,0),'10-S04':(1,1,1,0),
'11-01':(0,1,1,1),'11-02':(1,1,1,0),
'12-01':(0,1,0,1),'12-02':(0,1,1,1),'12-S03':(1,1,1,0),'12-S04':(1,1,1,0),
'13-01':(1,1,1,0),'13-02':(1,1,1,1),'13-S01':(1,1,1,1),'13-S03':(1,1,2,0),'13-S05':(1,1,1,1),'13-S06':(1,1,1,1),
'14-01':(0,1,1,0),'14-02':(0,1,1,1),'14-S02':(0,1,1,1),'14-S04':(0,1,1,1),'14-S05':(0,1,1,1),
'15-01':(0,1,1,1),'15-02':(1,1,1,1),'15-S03':(0,1,1,1),
'16-01':(0,1,1,1),'16-02':(0,1,1,1),'16-S03':(1,1,1,1),
'17-01':(0,1,1,1),'17-02':(1,1,1,0),'17-S01':(0,1,1,1),'17-S04':(0,1,1,1),
'18-01':(1,1,1,1),'18-02':(0,1,1,1),'18-S01':(1,1,1,1),'18-S03':(1,1,1,1),'18-S05':(1,1,1,1),'18-S06':(1,1,1,1),
'19-01':(0,1,1,0),'19-02':(0,1,1,0),'19-S01':(0,1,1,0),'19-S04':(1,1,1,0),'19-S05':(1,1,1,0),'19-S06':(1,1,1,1)}
LA={
'01-01':(0,0,1,0),'01-02':(0,0,1,0),'01-03':(0,1,1,0),'01-04':(0,1,1,0),'01-05':(0,1,1,0),
'02-01':(0,0,1,0),'02-02':(0,0,1,0),'02-03':(1,1,1,0),'02-04':(0,1,1,0),'02-05':(1,1,1,0),
'03-01':(0,1,1,0),'03-02':(1,1,1,0),'03-03':(0,1,1,0),'03-04':(1,1,1,0),'03-05':(1,1,1,0),
'04-01':(0,1,1,0),'04-02':(1,1,1,0),'04-03':(1,1,1,0),'04-04':(1,1,1,0),'04-05':(1,1,1,0),
'05-01':(1,1,1,0),'05-02':(1,1,1,0),'05-03':(1,1,1,0),'05-04':(1,1,1,0),'05-05':(1,1,1,0),'05-06':(1,1,1,0),'05-07':(1,1,1,0),
'06-01':(1,1,1,0),'06-02':(1,1,1,0),'06-03':(1,1,1,0),'06-04':(1,1,1,0),'06-05':(1,1,1,0)}
PS={
'01-01':(0,0,0,1),'01-02':(0,0,1,1),'02-01':(0,0,1,0),'02-02':(0,1,1,1),'02-03':(0,1,1,1),'02-04':(0,1,1,0),
'03-01':(1,1,1,1),'03-02':(1,1,1,1),'03-03':(1,1,1,1),'03-04':(0,1,1,0),'03-05':(0,1,1,1),'03-06':(0,1,1,1),
'04-01':(0,1,1,0),'04-02':(0,1,1,0),'04-03':(0,1,1,0),
'05-01':(1,1,1,0),'05-02':(1,1,1,0),'05-03':(1,1,1,1),'05-04':(1,1,1,0),'05-05':(1,1,1,0),'05-06':(1,1,1,1),
'06-01':(1,1,1,1),'06-02':(1,1,1,1),'07-01':(0,1,1,0),'07-02':(1,1,1,0),'07-03':(1,1,1,0),'07-04':(1,1,1,0),'07-05':(1,1,1,1),
'08-01':(0,0,0,1),'08-02':(0,1,1,0),'08-03':(1,1,1,0),
'09-01':(0,1,1,0),'09-02':(1,1,1,1),'09-03':(1,1,1,0),
'10-01':(0,1,1,0),'10-02':(1,1,1,0),'10-03':(1,1,1,1),
'11-01':(0,1,1,0),'11-02':(1,1,1,1),'11-03':(1,1,1,1),
'12-01':(1,1,1,0),'12-02':(1,1,1,1),'12-03':(1,1,1,1)}
PROFILES={**{'DM-K'+k:v for k,v in DM.items()},**{'LA-K'+k:v for k,v in LA.items()},**{'PS-K'+k:v for k,v in PS.items()}}
SKILLS=[
 ('proof','证明|求证|试证|证[：:]|证得'),('counterexample','反例|举例说明|举出.*例'),('construct','构造|设计.*(?:算法|模型)|求.*所有.*(?:关系|函数|图)'),
 ('parameter','参数|讨论.{0,20}(?:有解|无解|解的|可逆|可对角化)|取何值|为何值|何值时'),('model','建立.*模型|模型.*建立|概率模型|建立.*递推|递推关系'),
 ('graph','画出|画.*图|哈斯图|图中|如图|下图|波形图|振动图'),('translate','符号化|表示下列|用.*表示|用集合形式|翻译'),
 ('distribution','分布律|概率密度|分布函数|条件分布'),('estimate','估计|置信|检验|回归|预测'),
 ('algorithm','算法|Warshall|Dijkstra|Kruskal|Prim|匈牙利'),('calculate','计算|求解|求出|求下列|求.*(?:值|矩阵|方程|概率|频率|位置|能量|厚度)'),
 ('recognition','判断|是否|哪些|指出|说明|写出')]
def level(d):return 1 if sum(d)<=1 else 2 if sum(d)<=3 else 3 if sum(d)<=5 else 4
def clean(s):return re.sub(r'!\[[^\]]*\]\([^)]*\)','',s or '')
def rating(q,book,knowledge):
 ids=q.get('knowledge_ids',[]);topics=[knowledge[i]['title'] for i in ids if i in knowledge];anchors=[(i,PROFILES[i]) for i in ids if i in PROFILES]
 assert anchors,(book,q['id'],ids)
 d=list(max((a for _,a in anchors),key=lambda a:(sum(a),a)))
 p=clean(q.get('prompt',''));sol=clean(q.get('solution',''));skills=[n for n,patt in SKILLS if re.search(patt,p,re.I)];features=[]
 # A list of repetitions is not a multi-step chain. Start from the actual task.
 if 'proof' in skills:
  d[1]=max(d[1],1);d[2]=max(d[2],1);features.append('题干要求论证，需说明适用条件而非只写结果')
 if 'counterexample' in skills or 'construct' in skills:
  d[1]=2;d[2]=max(d[2],1);features.append('需要自行选择反例或构造对象')
 if 'parameter' in skills:
  d[1]=max(d[1],1);d[2]=2;features.append('需要处理参数取值或区分情形')
 if 'model' in skills:
  d[1]=max(d[1],1);d[3]=max(d[3],1);features.append('需要从题意建立模型或关系式')
 if 'graph' in skills or 'translate' in skills:
  d[3]=max(d[3],1);features.append('涉及图形、语言与数学表征之间的转换')
 # Evidence of a real structural chain, not merely the number of associated IDs.
 if re.search(r'先.*再.*(?:证明|讨论)|分别讨论|分情况|分类讨论',p) and ('proof' in skills or 'parameter' in skills):
  d[2]=2;features.append('明确要求多阶段推理或分类论证')
 if 'proof' in skills and re.search(r'任意|任给|充要|当且仅当|必要且充分|一般|设.{0,35}为.{0,20}[nmn]阶|n\\times n',p):
  d[2]=2;features.append('需要对一般对象或充要条件进行论证')
 if book=='LA7':
  # Computation with a chosen standard algorithm is routine, even if lengthy.
  if not any(x in skills for x in ['proof','counterexample','construct','parameter','model']):
   d[2]=1;d[1]=max(1,d[1])
  if re.search(r'正交.*(?:对角化|标准形)|特征.*(?:二次型|正定)|(?:秩|线性无关).*(?:解空间|通解)',p):
   d[0]=2;features.append('题干联结特征结构、二次型或解空间等不同知识模块')
  if 'proof' in skills and re.search(r'幂零|幂等|可交换|交换|A\^\{?k|A\^n|n阶|n 阶',p):
   d[1]=2;features.append('需利用矩阵结构建立一般结论')
 if book=='PS3':
  if 'proof' in skills and re.search(r'期望|方差|无偏|一致|独立|密度|分布|统计量',p):
   d[2]=2;features.append('需要依据概率/统计定义建立一般结论')
  if re.search(r'二维|联合|二重|[XYxy]\\le.*[XYxy]|条件.*(?:密度|期望)',p) and ('distribution' in skills or 'proof' in skills):
   d[3]=max(d[3],1);features.append('需要同时处理联合/条件关系或积分区域')
  if re.search(r'最大似然|极大似然',p) and re.search(r'(?:是否|证明|讨论).*(?:无偏|一致|有效)|并求.*(?:均值|方差)|[；;。].*求.*(?:均值|方差)|求其(?:均值|方差)',p):
   d[0]=2;d[2]=2;features.append('估计求解后还需分析估计量性质或后续推断')
 if book=='DM2T' and 'proof' in skills:
  if re.search(r'必要.*充分|充要|当且仅当',p):
   d[2]=2;features.append('需要双向证明，而非只核对一个实例')
  if re.search(r'平面.*(?:色|匹配)|(?:群|环|域).*(?:同态|同构)|递推.*生成函数|生成函数.*递推',p):
   d[0]=2;features.append('需要联结不同知识模块中的结论')
 # Calibrate named standard tasks; a late chapter or the word “construct”
 # alone must not turn simple rule application into an advanced problem.
 if book=='DM2T' and re.search(r'构造.{0,15}(?:满足|推理)|满足.{0,15}推理|(?:附加律|化简律|假言推理定律|德摩根律|拒取式)',p) and not re.search(r'消解|归结|充要',p):
  d=[0,1,1,1 if 'translate' in skills else 0];features=['根据指定推理规则给出实例或符号化，属于标准规则应用']
 if book=='DM2T' and re.search(r'构造证明',p) and re.search(r'6 是偶数|大学生都勤奋',p):
  d=[0,1,1,1];features=['把给定语句转成量词形式后使用一条常规推理规则']
 if book=='LA7' and re.search(r'用矩阵记号表示.*二次型|写出.*二次型.*矩阵',p):
  d=[0,0,1,1];features=['按二次型系数规则填对称矩阵，无需对角化或一般性证明']
 if book=='PS3' and not any(x in skills for x in ['proof','counterexample','construct','parameter']):
  if re.search(r'全概率|贝叶斯|条件概率', ' '.join(topics)):
   d=[0,1,1,1];features=['识别给定概率条件后使用标准条件概率、全概率或贝叶斯公式']
  if re.search(r'概率依次为|对应概率|只能取',p) and re.search(r'联合分布律|分布律',p):
   d=[0,0,1,1];features=['已给出取值及概率，整理分布表并处理相同函数值即可']
  if re.search(r'(?:x̄|\\bar|样本均值|样本平均).*(?:置信区间|检验)|H[₀0].*H[₁1]',p) and not re.search(r'两总体|两个总体|方差相等|甲.*乙',p):
   d=[0,1,1,1];features=['题目给出单总体条件、样本统计量及推断目标，选用标准区间或检验流程']
 # Pure recognition/reading remains elementary even in a later chapter.
 pure=bool(re.search(r'^(?:\d+[.、]?\s*)?(?:判断|指出|写出|列出|说明|确定)',p)) and not any(x in skills for x in ['proof','counterexample','construct','parameter','model','estimate','distribution','algorithm','calculate'])
 elementary={'DM-K01-01','DM-K01-02','DM-K04-02','DM-K06-01','DM-K06-02','DM-K07-01','DM-K07-02','DM-K09-01','LA-K02-01','PS-K01-01'}
 if pure and ids and all(i in elementary for i in ids) and re.search(r'命题|真值|自由变元|约束变元|样本空间|随机试验|二元关系|二元运算|子集|幂集|矩阵的阶|阶数|顶点的度|元素个数|哪些.*(?:可逆|对称|零矩阵)',p):
  d=[0,0,0,1 if any(x in skills for x in ['graph','translate']) or '样本空间' in p else 0];features=['按定义辨认或读写对象，不需要一般性证明']
 if not features:features=['在对应知识点内选择并执行常规方法' if level(d)>1 else '直接使用定义、给定表征或单一关系式']
 return {'level':level(d),'dimensions':d,'skills':skills or ['calculate'],'basis':'content_analysis','evidence':features,'topics':topics,'confidence':'rule_estimate','recommended':False,'recommendation_reasons':[]}

# The complete 19-item physics batch is reviewed against the actual requested
# model, including the difference between long explanations and hard inference.
PHYS={
 '9-13':((0,1,1,1),'由位移与速度方向确定初相，四种初始条件重复同一常规方法'),
 '9-14':((1,0,1,1),'由静伸长求角频率，再用给定初始条件写标准振动方程'),
 '9-15':((0,1,1,1),'从振动图读周期和初始条件，求相位或时间'),
 '9-17':((1,1,2,1),'联立牛顿第二定律与振动加速度，并检查支持力为零的接触边界'),
 '9-28':((0,1,1,0),'使用简谐运动关系求参数，再代入能量公式'),
 '9-30':((0,1,1,0),'由动势能分配或完整周期平均求解，不因讲解步骤多而升为高难'),
 '10-10':((0,1,1,1),'由给定波源方程和波速，按标准传播延迟写出行波方程'),
 '10-15':((1,1,1,1),'结合瞬时波形、质点运动方向与传播相位建立方程'),
 '10-16':((0,1,1,1),'已知传播方向与速度，从波形读参数后写行波和指定点方程'),
 '10-27':((1,0,1,1),'由给定驻波方程读取行波参数、波节间距，再按时间求导算速度'),
 '10-28':((0,1,1,1),'将两列波和差化积，按空间振幅因子求指定振幅的位置'),
 '10-29':((1,1,1,1),'分别建立声源与观察者的带符号速度关系，原图缺失声速另作资料说明'),
 '11-15':((0,1,1,0),'比较两路附加光程并使用双缝明纹条件'),
 '11-16':((1,1,1,1),'先判两界面反射相位，再枚举允许的干涉波长'),
 '11-24':((0,1,1,0),'比较同级牛顿环直径平方与介质折射率的关系'),
 '11-25':((1,1,2,1),'将膜厚范围、界面相位与干涉级次对应，检查端点后计数'),
 '11-27':((1,1,2,1),'把屏上位置转换为衍射角，保留满足级次与波长条件的全部候选'),
 '11-34':((1,1,2,1),'分别处理正入射和斜入射的级次范围，再用屏面几何求白光谱宽度'),
 '11-35':((1,1,2,1),'联立正入射主极大与缺级条件，检查缝宽的多种可能和实际可见级次')}

all_rows=[];summary=[]
for book in ['DM2T','LA7','PS3','PHYS']:
 seed=read(f'book-{book}-v15.json');knowledge={k['id']:k for k in seed['knowledge']}
 exercises=read(f'exercises-{book}-v'+('21' if book=='PHYS' else '20')+'.json')['items']
 examples=[] if book=='PHYS' else [{**q,'kind':'example'} for q in read(f'examples-{book}-ready-v17.json')['items']]
 singles=[*examples,*[q for q in exercises if q['kind']=='exercise']];groups=[q for q in exercises if q['kind']=='exercise_group'];ratings={}
 for q in singles:
  if book=='PHYS':
   dims,evidence=PHYS[q['number']];r={'level':level(dims),'dimensions':list(dims),'skills':[n for n,p in SKILLS if re.search(p,q['prompt'],re.I)] or ['calculate'],'basis':'content_analysis','evidence':[evidence],'topics':[knowledge[i]['title'] for i in q['knowledge_ids']],'confidence':'content_reviewed','recommended':False,'recommendation_reasons':[]}
  else:r=rating(q,book,knowledge)
  ratings[q['id']]=r
 # Explicitly reviewed corrections are versioned separately and cannot drift.
 corrections=R/'scripts/ratings-reviewed-v23.json'
 for id,change in (json.loads(corrections.read_text()) if corrections.exists() else {}).items():
  if id in ratings:
   ratings[id].update(change,confidence='content_reviewed');ratings[id]['level']=level(ratings[id]['dimensions'])
 # Recommendation is coverage, not predicted exam frequency or ease alone.
 for kid,k in knowledge.items():
  related=[q for q in singles if kid in q.get('knowledge_ids',[])];selected=[]
  def choose(pool,reason):
   if not pool:return
   # Prefer unambiguous source conditions, then a representative routine item.
   q=min(pool,key=lambda q:(bool(q.get('issues')),ratings[q['id']]['confidence']!='content_reviewed',abs(ratings[q['id']]['level']-2),len(ratings[q['id']]['skills']),q.get('chapter',0),q['id']))
   r=ratings[q['id']];r['recommended']=True;r['recommendation_reasons'].append(k['title']+'：'+reason);selected.append(q['id'])
  choose([q for q in related if q['kind']=='example' and ratings[q['id']]['level']<=2],'先用例题建立基本方法')
  choose([q for q in related if q['kind']=='exercise' and ratings[q['id']]['level']<=2],'用课后题独立验证常规方法')
  if not selected:choose(related,'本知识点的现有代表题')
  covered={skill for id in selected for skill in ratings[id]['skills']}
  for family,reason in [('proof','补充论证方法'),('counterexample','补充反例或边界辨析'),('model','补充建模方法'),('graph','补充图形与公式转换')]:
   pool=[q for q in related if q['id'] not in selected and family in ratings[q['id']]['skills']]
   if family not in covered and len(selected)<4:
    choose(pool,reason);covered.update(skill for id in selected for skill in ratings[id]['skills'])
  if len(selected)<3:choose([q for q in related if q['id'] not in selected and ratings[q['id']]['level']>=3],'完成基础后尝试进阶迁移')
 for q in singles:
  r=ratings[q['id']]
  if book=='PHYS':
   r['recommended']=True
   r['recommendation_reasons']=['物理学（下册）已由用户筛选为精选题目，19 道均推荐完成；难度独立评定']
  if not r['recommended']:r['recommendation_reasons']=['同一知识点已有代表题，本题用于继续巩固或拓展；并非不重要']
  all_rows.append({'book':book,'id':q['id'],'title':q['title'],'prompt':q['prompt'],'solution':q.get('solution',''),'knowledge_ids':q['knowledge_ids'],**r})
 for q in groups:
  prefix=q['id'].replace('-G','-E')+'-';children=[v for id,v in ratings.items() if id.startswith(prefix)]
  assert children,q['id']
  ratings[q['id']]={'range':[min(c['level'] for c in children),max(c['level'] for c in children)],'kind':'group','recommended_count':sum(c['recommended'] for c in children),'total':len(children),'basis':'aggregate','evidence':['整组包含多道题，显示子题难度范围，不把整组当作单题评级']}
 payload={'version':23,'book':book,'rubric':RUBRIC,'items':ratings};save(f'ratings-{book}-v23.json',payload)
 report={'book':book,'single_questions':len(singles),'group_entries':len(groups),'recommended':sum(r['recommended'] for r in ratings.values() if 'level' in r),'levels':dict(sorted(collections.Counter(r['level'] for r in ratings.values() if 'level' in r).items())),'knowledge_points_with_questions':sum(any(kid in q.get('knowledge_ids',[]) for q in singles) for kid in knowledge),'source_hash':hashlib.sha256(json.dumps(singles,sort_keys=True,ensure_ascii=False).encode()).hexdigest()};summary.append(report)
save('rating-audit-v23.json',{'version':23,'rubric':RUBRIC,'books':summary})
Path('/tmp/zhixu-rating-review-v23.json').write_text(json.dumps(all_rows,ensure_ascii=False))
print(json.dumps(summary,ensure_ascii=False))
