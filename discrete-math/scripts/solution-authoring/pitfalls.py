"""Attach referenced topic pitfalls without certifying an unfinished derivation."""
import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FILES={
 'DM2T':['exercises-DM2T-v20.json','examples-DM2T-ready-v17.json'],
 'LA7':['exercises-LA7-v20.json','examples-LA7-ready-v17.json'],
 'PS3':['exercises-PS3-v20.json','examples-PS3-ready-v17.json'],
 'PHYS':['exercises-PHYS-v29.json'],
}

# These rules add warnings only when the triggering operation occurs in the prompt.
RULES={
 'DM2T':[
  (r'只有|仅当|必要条件',r'“只有 $p$，才 $q$”应译为 $q\to p$；箭头指向必要条件，不能按词语先后顺序写。'),
  (r'充分条件|只要',r'“$p$ 是 $q$ 的充分条件”表示 $p\to q$；逆命题 $q\to p$ 需要另行证明。'),
  (r'否定|否定式|量词否定',r'否定整个命题时须同时处理联结词、量词和不等号；$\neg\forall xP(x)\equiv\exists x\neg P(x)$，不能只在最外层加一个否定号后停止。'),
  (r'反例|不成立|是否.*关系|判断.*性质',r'否定全称结论只需一个满足题设却不满足结论的具体反例；证明全称结论则不能只检查几个正例。'),
  (r'对称.*反对称|反对称.*对称',r'反对称的定义是 $aRb\land bRa\Rightarrow a=b$；它不是“不对称”，也不排除自环。'),
  (r'闭包',r'闭包要同时满足“包含原关系”“具有指定性质”“加入的元素最少”。求传递闭包时新增有序对可能继续产生新的传递链。'),
  (r'上确界|下确界|极大元|极小元',r'极大元不一定支配其他元素，最大元却必须大于等于集合中每个元素；上界应在给定偏序集内寻找。'),
  (r'生成树|无向树|树叶|树T|树 T',r'无向树的边数是 $n-1$，路径长度按边数计；用握手定理时树叶的度也必须计入总度数。'),
  (r'完美匹配',r'完美匹配的每条边覆盖两个不同顶点，所以顶点数为偶数是必要条件；偶数阶本身仍不能保证存在完美匹配。'),
  (r'欧拉|哈密顿',r'欧拉问题要求每条边恰经过一次，哈密顿问题要求每个顶点恰经过一次；两类判据不能互换。'),
  (r'同余|模.*逆元',r'同余式两边约去因子 $a$，须检查 $\gcd(a,m)=1$；否则应同时相应约化模数，不能照搬普通等式消去律。'),
  (r'递推|生成函数',r'递推通解中的常数必须由全部初值确定；重根会产生 $n^j r^n$ 因子，非齐次特解与齐次解重合时还需提高 $n$ 的次数。'),
  (r'排列|组合|分配|至少|至多',r'先区分对象是否相同、位置是否有序和是否允许重复；“至少”或“至多”需覆盖全部互斥情形，不能只算恰好一次。'),
 ],
 'LA7':[
  (r'四阶|4阶|n.*阶行列式',r'三阶的对角线法则不能推广到四阶及更高阶；应使用展开、初等变换或分块结构。'),
  (r'行列式|\\det|vmatrix',r'交换两行使行列式变号，某行乘 $c$ 使行列式乘 $c$，倍加不改变行列式；整矩阵乘 $c$ 则应乘 $c^n$。'),
  (r'乘积|AB|BA|矩阵方程',r'矩阵乘法通常不交换；左乘逆矩阵和右乘逆矩阵的位置不同，不能把 $AXB=C$ 写成任意次序的三个因子。'),
  (r'逆矩阵|可逆|A\^\{-1\}|A\^{-1}',r'使用逆矩阵前先说明方阵可逆；$A\ne O$ 不推出可逆。求出候选逆后，应检查乘积为单位阵。'),
  (r'参数|\\lambda|\\alpha|\\beta|[a-z].*取.*值',r'若消元中将某个含参数的式子作为除数，必须另列该式为零的情形；否则可能漏解或误判秩。'),
  (r'秩|阶梯形|解方程|解.*方程组',r'求方程组的解时只能对增广矩阵作行变换。列变换虽可用于求秩，却会改变未知量的含义。'),
  (r'线性无关|线性相关|最大无关组',r'线性相关性应从 $\sum c_i\alpha_i=0$ 判断；含零向量必相关，但不含零向量并不能保证无关。'),
  (r'特征值|特征向量',r'特征向量必须非零；特征值的代数重数与特征子空间维数不一定相等。每个候选向量需代回 $Av=\lambda v$。'),
  (r'相似|对角化',r'可对角化要求存在 $n$ 个线性无关的特征向量；有重特征值不能直接断言不可对角化，也不能直接断言可对角化。'),
  (r'正交|标准正交',r'正交只要求内积为零，标准正交还要求各向量长度为1；施密特正交化后需要再做单位化。'),
  (r'二次型|合同|配方法',r'二次型的交叉项 $c x_ix_j$ 对应对称矩阵中的两个元素 $a_{ij}=a_{ji}=c/2$；合同变换与相似变换的形式不同。'),
  (r'正定|负定',r'实对称矩阵正定可用顺序主子式全正判定；只有行列式为正或对角元全正，都不足以保证正定。'),
  (r'基变换|坐标变换|过渡矩阵',r'若新基矩阵满足 $B_{\rm new}=B_{\rm old}P$，则坐标满足 $x_{\rm old}=Px_{\rm new}$；基与坐标的变换方向相反。'),
 ],
 'PS3':[
  (r'至少|不多于|至多|不超过',r'“至少一个”可用 $1-P(0\text{ 个})$ 计算；“不超过”包含端点。补事件必须相对于同一个样本空间取。'),
  (r'不放回',r'不放回时后次抽取的组成会受前次结果影响；不能直接把各次抽取当独立，也不能不加条件地使用二项分布。'),
  (r'条件概率|P\([^)]*\||P（.*\|',r'条件概率的分母是条件事件的概率，$P(A\mid B)=P(AB)/P(B)$ 且要求 $P(B)>0$；一般不等于 $P(B\mid A)$。'),
  (r'独立|相关',r'独立需要检验联合分布是否分解为边缘分布乘积；不相关一般不能推出独立，互斥事件也一般不独立。'),
  (r'全概率|贝叶斯',r'全概率公式的原因事件必须互斥且穷尽；贝叶斯分母要加上所有能产生观察结果的原因，不能只保留所求那一类。'),
  (r'密度|分布函数',r'连续型随机变量的密度值不是单点概率。概率由对应区间积分得到，分布函数还必须满足单调性、右连续性及两端极限。'),
  (r'二维|联合|边缘|条件密度',r'先画出联合密度的非零区域，再确定积分上下限；边缘化是积分消去另一变量，条件密度还要除以相应边缘密度。'),
  (r'数学期望|期望|E[X（(]|E[XYZ]|均值',r'期望的线性性不要求独立；乘积期望分解 $E(XY)=EX\,EY$ 则需要独立或另行证明相应条件。'),
  (r'方差|D\(X|D（|DX',r'$D(X)=E(X^2)-(EX)^2$，不能把 $E(X^2)$ 写成 $(EX)^2$；$D(aX+b)=a^2D(X)$，常数平移不改变方差。'),
  (r'最大值|最小值',r'最大值分布宜先算“全部不超过 $z$”，最小值宜先算“全部超过 $z$”；把事件概率相乘前必须确认独立。'),
  (r'矩估计|似然|估计量',r'估计量是样本的函数，估计值才是代入数据后的数。极大似然还要检查参数决定的支持集和边界，而非只令导数为零。'),
  (r'无偏',r'无偏要验证对每个允许参数值均有 $E_\theta\hat\theta=\theta$；单次估计碰巧接近真值，不能证明无偏。'),
  (r'置信|区间|误差限',r'置信水平描述重复抽样构造区间的覆盖率；总体方差已知与未知时的枢轴量和分位数不同，不要混用正态与 $t$ 分布。'),
  (r'检验|显著|p值|p 值',r'先按备择假设确定单侧或双侧拒绝域；未拒绝原假设不等于证明原假设为真，显著性水平也不是原假设为真的概率。'),
  (r'回归|预测|最小二乘',r'均值响应的置信区间与单个新观测的预测区间不同；后者包含额外随机误差，因此同等条件下更宽。'),
 ],
 'PHYS':[]}

def targeted(item,book,knowledge):
 prompt=item.get('prompt','');notes=[];basis=[]
 for pattern,note in RULES[book]:
  if re.search(pattern,prompt):notes.append(note);basis.append({'type':'prompt_condition','pattern':pattern})
 for kid in item.get('knowledge_ids',[]):
  k=knowledge.get(kid,{})
  note=k.get('content',{}).get('errors','').strip()
  if note and note not in notes:notes.append(note);basis.append({'type':'related_knowledge','knowledge_id':kid,'title':k.get('title','')})
 # A source-mapping gap remains a gap; do not fill it with unrelated boilerplate.
 return list(dict.fromkeys(notes))[:4],basis

def main():
 report=[]
 for book,files in FILES.items():
  knowledge={k['id']:k for k in json.loads((ROOT/'data'/f'book-{book}-v15.json').read_text())['knowledge']}
  for fn in files:
   p=ROOT/'data'/fn;d=json.loads(p.read_text())
   for item in d['items']:
    if item.get('kind')=='exercise_group':continue
    notes,basis=targeted(item,book,knowledge)
    if notes:
     item['common_mistakes']=notes
     item['common_mistakes_basis']={'status':'topic_guidance','references':basis,'individual_derivation_verified':False}
    report.append({'id':item['id'],'book':book,'file':fn,'pitfall_count':len(notes)})
   p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'questions':len(report),'with_pitfalls':sum(x['pitfall_count']>0 for x in report),'missing':[x['id'] for x in report if not x['pitfall_count']]},ensure_ascii=False))

if __name__=='__main__':main()
