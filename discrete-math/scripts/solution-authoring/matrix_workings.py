"""Produce exact determinant, elimination and inverse workings from visible matrices."""
import json,re
from pathlib import Path
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr,standard_transformations,implicit_multiplication_application,convert_xor
ROOT=Path(__file__).resolve().parents[2]
TRANSFORMS=standard_transformations+(implicit_multiplication_application,convert_xor)

def braces(s,start):
 if start>=len(s) or s[start]!='{':raise ValueError('Expected brace')
 depth=1;i=start+1
 while i<len(s) and depth:
  depth+=(s[i]=='{')-(s[i]=='}');i+=1
 if depth:raise ValueError('Unbalanced cell braces')
 return s[start+1:i-1],i

def cell(s):
 s=s.strip().replace('−','-').replace(r'\left','').replace(r'\right','')
 s=s.replace(r'\dfrac',r'\frac').replace(r'\tfrac',r'\frac')
 while r'\frac' in s:
  i=s.index(r'\frac');a,j=braces(s,i+5);b,k=braces(s,j);s=s[:i]+'(('+a+')/('+b+'))'+s[k:]
 while r'\sqrt' in s:
  i=s.index(r'\sqrt');a,j=braces(s,i+5);s=s[:i]+'sqrt('+a+')'+s[j:]
 for k in ['lambda','alpha','beta','gamma','theta','pi','sin','cos','tan']:
  s=s.replace('\\'+k,k)
 s=re.sub(r'([a-zA-Z])_\{([0-9]+)\}',r'\1_\2',s)
 s=s.replace(r'\cdot','*').replace(r'\times','*').replace('{','(').replace('}',')')
 s=s.replace(r'\,','').replace(r'\!','').replace(r'\;','')
 if not re.fullmatch(r'[a-zA-Z0-9_+*/().^\s-]+',s) or '__' in s:raise ValueError('Unsupported matrix cell')
 if re.search(r'[a-zA-Z]{9,}',s):raise ValueError('Unsupported identifier')
 names={x:sp.Symbol(x) for x in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'}
 names.update({x:sp.Symbol(x) for x in ['lambda','alpha','beta','gamma','theta']})
 names.update({x:sp.Symbol(x) for x in re.findall(r'[a-zA-Z]_\d+',s)})
 names.update({'pi':sp.pi,'sin':sp.sin,'cos':sp.cos,'tan':sp.tan,'sqrt':sp.sqrt})
 return parse_expr(s,local_dict=names,transformations=TRANSFORMS)

def matrices(prompt):
 out=[]
 pat=r'\\begin\{(p|b|v)matrix\}(.+?)\\end\{\1matrix\}'
 for n,m in enumerate(re.finditer(pat,prompt,re.S),1):
  try:
   rows=[[cell(x) for x in row.split('&')] for row in re.split(r'\\\\',m.group(2)) if row.strip()]
   if not rows or len(rows)>5 or len({len(x) for x in rows})!=1:continue
   mat=sp.Matrix(rows)
   out.append((n,m.group(1),mat))
  except (ValueError,TypeError,SyntaxError,sp.SympifyError,NameError):continue
 return out

def L(x):return sp.latex(x,mat_delim='(',mat_str='matrix')

def determinant(A):
 n=A.rows;out=[]
 if n==1:return [f'一阶行列式为唯一元素：${L(A.det())}$。']
 if n==2:
  a,b,c,d=list(A);return ['按二阶定义，主对角乘积减去副对角乘积：$$'+L(A).replace(r'\left(',r'\left|').replace(r'\right)',r'\right|')+'=('+L(a)+')('+L(d)+')-('+L(b)+')('+L(c)+')='+L(sp.expand(A.det()))+'.$$']
 row=max(range(n),key=lambda i:sum(A[i,j]==0 for j in range(n)))
 out.append('选择第 '+str(row+1)+' 行按代数余子式展开；第 $(i,j)$ 项为 $(-1)^{i+j}a_{ij}M_{ij}$，零元素所在项直接为零。')
 terms=[]
 for j in range(n):
  if A[row,j]==0:continue
  minor=A.minor_submatrix(row,j);value=sp.factor(minor.det());term=sp.expand((-1)**(row+j)*A[row,j]*value);terms.append(term)
  out.append('第 '+str(j+1)+' 列：删去第 '+str(row+1)+' 行、第 '+str(j+1)+' 列，余子式行列式为 $$M_{'+str(row+1)+str(j+1)+'}='+L(minor).replace(r'\left(',r'\left|').replace(r'\right)',r'\right|')+'='+L(value)+'.$$其展开贡献为 $$(-1)^{'+str(row+1)+'+'+str(j+1)+'}('+L(A[row,j])+')('+L(value)+')='+L(term)+'.$$')
  if n<=4:out.extend(determinant(minor))
 total=sp.factor(A.det());assert sp.simplify(sum(terms)-total)==0
 out.append('将上面各个展开贡献相加并合并同类项，得到 $$D='+L(sp.Add(*terms,evaluate=False))+'='+L(total)+'.$$若结果含参数，这个多项式恒等式也包含参数为零的情形；本次展开没有除以任何参数。')
 return out

def reduce(A,augment=False):
 n=A.rows;left=A.cols;B=A.row_join(sp.eye(n)) if augment else A.copy();ops=[];pivotrow=0
 for col in range(left):
  k=next((k for k in range(pivotrow,n) if B[k,col]!=0),None)
  if k is None:continue
  if k!=pivotrow:
   B.row_swap(k,pivotrow);ops.append((f'R_{pivotrow+1}\\leftrightarrow R_{k+1}',B.copy()))
  c=B[pivotrow,col]
  if c!=1:
   B.row_op(pivotrow,lambda v,j:sp.cancel(v/c));ops.append((f'R_{pivotrow+1}\\leftarrow ({L(1/c)})R_{pivotrow+1}',B.copy()))
  for k in range(n):
   if k==pivotrow:continue
   c=B[k,col]
   if c==0:continue
   pr=B.row(pivotrow);B.row_op(k,lambda v,j:sp.cancel(v-c*pr[j]));ops.append((f'R_{k+1}\\leftarrow R_{k+1}-({L(c)})R_{pivotrow+1}',B.copy()))
  pivotrow+=1
  if pivotrow==n:break
 return B,ops,pivotrow

def inverse(A):
 det=A.det();out=[r'先检查可逆性：$$\det A='+L(det)+'.$$']
 if not det:return out+['行列式为0，因此此矩阵不可逆，不能继续写 $A^{-1}$。'],False
 B,ops,rank=reduce(A,True)
 out.append(r'将原矩阵与单位矩阵并排：$$(A\mid E)='+L(A.row_join(sp.eye(A.rows)))+'.$$对左右两块同时实施同一行变换，把左半块化成单位阵；不能只改左块。')
 out.extend('作行变换 $'+op+'$，得到 $$'+L(mat)+'.$$' for op,mat in ops)
 inv=B[:,A.cols:];assert inv==A.inv() and A*inv==sp.eye(A.rows)
 out.append('左半块已成为 $E$，所以右半块就是逆矩阵：$$A^{-1}='+L(inv)+'.$$独立乘回核验：$$AA^{-1}='+L(A*inv)+r'=E,\qquad A^{-1}A=E.$$')
 return out,True

def main():
 count=0;blockcount=0
 for fn in ['exercises-LA7-v20.json','examples-LA7-ready-v17.json']:
  p=ROOT/'data'/fn;d=json.loads(p.read_text())
  for item in d['items']:
   if item.get('kind')=='exercise_group':continue
   prompt=item['prompt'];added=[];proofs=[];visible=matrices(prompt)
   item['explanation']=[s for s in item['explanation'] if not s.startswith('**演算补充：')]
   item.pop('computed_derivation',None)
   if item['id']=='SRC-LA7-X130-1277':continue
   for index,typ,A in visible:
    lead=''
    if item['id']=='SRC-LA7-E001-009':
     A[2,:]=sp.Matrix([[1,3,-2,2]])
     lead='本问求第三行代数余子式的线性组合；先将第三行替换为 $(1,3,-2,2)$，再计算所得行列式。以下计算针对替换后的矩阵，不是原矩阵D。\n\n'
    if item['id']=='SRC-LA7-X023-8912':
     C=A.copy();C[0,:]=sp.ones(1,4);D=A.copy();D[:,0]=sp.Matrix([1,-1,1,-1])
     for label,M in [('第一问将第一行替换为 $(1,1,1,1)$',C),('第二问先把余子式转为代数余子式，再将第一列替换为 $(1,-1,1,-1)^T$',D)]:
      added.append('**演算补充：'+label+'。**\n\n'+'\n\n'.join(determinant(M)))
     proofs.append({'method':'cofactor_linear_combination','values':[str(C.det()),str(D.det())],'independent_exact_check':True});continue
    if item['id']=='SRC-LA7-X072-8401' and index==2:
     A=visible[0][2].row_join(A)
     lead=r'第二问计算增广矩阵 $B=(A\mid b)$ 的秩，所以将题干列向量b接到A右侧，不能只计算b的秩。'+'\n\n'
    if item['id']=='SRC-LA7-E003-003':
     for label,M in [('第一问',A),('第二问（对转置矩阵）',A.T)]:
      B,ops,rank=reduce(M,True);P=B[:,M.cols:];F=B[:,:M.cols]
      assert P*M==F and P.det()!=0
      steps=['对 $M='+L(M)+r'$，从 $(M\mid E)$ 出发，同步记录每次行变换。']
      steps+=['作 $'+op+'$，得到 $$'+L(mat)+'.$$' for op,mat in ops]
      steps+=['左半块为行最简形，右半块就是所求可逆左乘矩阵：$$P='+L(P)+r',\quad PM='+L(F)+r',\quad\det P='+L(P.det())+r'\ne0.$$']
      added.append('**演算补充：'+label+'。**\n\n'+'\n\n'.join(steps))
     proofs.append({'method':'record_elementary_matrices','independent_exact_check':True});continue
    if typ=='v' and A.rows==A.cols and A.rows<=4:
     steps=determinant(A);method='exact_cofactor_expansion'
    elif typ in ['p','b'] and A.rows==A.cols and A.rows<=4 and not A.free_symbols and re.search(r'(?<!可)逆矩阵|求[^。\n]*的逆(?:[，。；]|$)',prompt):
     steps,exists=inverse(A);method='gauss_jordan_inverse'
    elif typ in ['p','b'] and not A.free_symbols and re.search(r'求.*秩|秩.*为|行阶梯|行最简',prompt):
     B,ops,rank=reduce(A);steps=['从题干给出的矩阵开始，仅使用初等行变换：$$'+L(A)+'.$$']
     steps+=['作 $'+op+'$，得到 $$'+L(mat)+'.$$' for op,mat in ops]
     steps+=['最简阶梯形有 '+str(rank)+' 个主元，因此这个显式矩阵的秩为 $'+str(rank)+'$。初等行变换可逆，所以变换前后秩不变。'];method='exact_row_reduction'
    else:continue
    added.append('**演算补充：题干中第 '+str(index)+' 个显式矩阵。**\n\n'+lead+'\n\n'.join(steps))
    proofs.append({'matrix_index':index,'method':method,'shape':[A.rows,A.cols],'matrix_entries':[str(x) for x in A],'independent_exact_check':True})
   if not added:continue
   item['explanation']=[s for s in item['explanation'] if not s.startswith('**演算补充：')] + added
   item['computed_derivation']={'method':'exact_symbolic_algebra','proofs':proofs,'scope':'explicit_matrices_in_prompt','all_subquestions_reviewed':False}
   count+=1;blockcount+=len(proofs)
  p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'questions_with_matrix_workings':count,'matrices':blockcount}))

if __name__=='__main__':main()
