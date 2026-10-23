import hashlib,importlib.util,itertools,json,math,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
def module(name):
 spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
logic=module('logic_proofs');mat=module('matrix_workings');norm=module('normalize_text')

class DerivationTests(unittest.TestCase):
 def test_truth_functions_and_scope(self):
  for text,expected in [(r'p\to q',[1,1,0,1]),(r'p\leftrightarrow q',[1,0,0,1]),(r'\neg(p\lor q)',[1,0,0,0]),(r'p\uparrow q',[1,1,1,0]),(r'p\downarrow q',[1,0,0,0])]:
   self.assertEqual([v for e,v in logic.Formula(text).rows()],expected)
  for text in [r'p\to(q\to p)',r'((p\to q)\land(q\to r))\to(p\to r)']:
   self.assertTrue(all(v for e,v in logic.Formula(text).rows()))
  with self.assertRaises(ValueError):logic.Formula(r'\forall xp(x)')
 def test_escaping_preserves_real_tex_rows_and_negation(self):
  for s in [r'$\begin{matrix}a&b\\c&d\end{matrix}$',r'$\begin{matrix}1&2\\n&4\end{matrix}$',r'$\neg p\land\nu$',r'$\nabla f$']:
   self.assertEqual(norm.normalize(s),s)
  self.assertEqual(norm.normalize(r'line\nnext $\neg p$'),'line\nnext $\\neg p$')
  self.assertEqual(norm.normalize(r'$\\begin{matrix}1&2\\\\3&4\\end{matrix}$'),r'$\begin{matrix}1&2\\3&4\end{matrix}$')
 def test_exact_row_operations_record_the_left_transform(self):
  sp=mat.sp
  for A in [sp.Matrix([[1,2],[2,5]]),sp.Matrix([[0,2,1],[1,1,3],[2,0,4]]),sp.Matrix([[-5,3,1],[2,-1,1]])]:
   B,ops,rank=mat.reduce(A,True);P=B[:,A.cols:];F=B[:,:A.cols]
   self.assertEqual(P*A,F);self.assertNotEqual(P.det(),0);self.assertEqual(F,A.rref()[0]);self.assertEqual(rank,A.rank())
   if A.rows==A.cols and A.det():self.assertEqual(P,A.inv())
 def test_symbolic_and_numeric_determinants(self):
  A=mat.matrices(r'$\begin{vmatrix}a&b&c\\b&c&a\\c&a&b\end{vmatrix}$')[0][2]
  a,b,c=[mat.sp.Symbol(x) for x in 'abc']
  self.assertEqual(mat.sp.expand(A.det()-(3*a*b*c-a**3-b**3-c**3)),0)
  self.assertTrue(mat.determinant(A))
 def test_authored_logical_equivalences(self):
  pairs=[
   (r'\neg((p\land q)\leftrightarrow q)',r'\neg p\land q'),
   (r'(p\lor q)\to(p\land r)',r'(\neg p\land\neg q)\lor(p\land r)'),
   (r'\neg(p\leftrightarrow q)',r'(p\lor q)\land\neg(p\land q)'),
   (r'\neg(p\to(q\leftrightarrow(q\land r)))',r'p\land q\land\neg r'),
   (r'p\leftrightarrow(q\leftrightarrow r)',r'(p\land((q\land r)\lor(\neg q\land\neg r)))\lor(\neg p\land((q\land\neg r)\lor(\neg q\land r)))'),
   (r'(p\leftrightarrow r)\land q',r'\neg(p\land\neg r)\land\neg(r\land\neg p)\land q'),
   (r'(p\to(q\land\neg p))\land q\land r',r'\neg(p\lor\neg q\lor\neg r)'),
   (r'(p\land q)\lor r',r'(p\to\neg q)\to r'),
   (r'(p\to\neg q)\land r',r'\neg((p\to\neg q)\to\neg r)'),
   (r'(p\land q)\leftrightarrow r',r'\neg((\neg(p\to\neg q)\to r)\to\neg(r\to\neg(p\to\neg q)))'),
   (r'(\neg p\land r)\lor(p\land\neg r)',r'(\neg p\to\neg r)\to\neg(p\to r)'),
   (r'(p\to q)\leftrightarrow r',r'(p\lor r)\land(\neg q\lor r)\land(\neg p\lor q\lor\neg r)'),
   (r'(p\to q)\leftrightarrow r',r'(p\land\neg q\land\neg r)\lor(\neg p\land r)\lor(q\land r)'),
  ]
  for a,b in pairs:
   A,B=logic.Formula(a),logic.Formula(b);variables=sorted(set(A.variables+B.variables))
   for values in itertools.product([0,1],repeat=len(variables)):
    env=dict(zip(variables,values))
    self.assertEqual(A.ev(A.tree,env),B.ev(B.tree,env),(a,b,env))
  for text,true in [(r'(p\to q)\leftrightarrow r',[1,3,4,7]),(r'(p\lor q)\to r',[0,1,3,5,7])]:
   self.assertEqual([int(''.join(str(e[v]) for v in logic.Formula(text).variables),2) for e,n in logic.Formula(text).rows() if n],true)
 def test_authored_determinant_identities_from_actual_prompts(self):
  sp=mat.sp;root=HERE.parents[1]
  doc=json.loads((root/'data/exercises-LA7-v20.json').read_text());byid={x['id']:x for x in doc['items']}
  def matrices(n):return [A for _,_,A in mat.matrices(byid[f'SRC-LA7-E001-{n:03}']['prompt'])]
  a,b,c,d,e,f,x,y,z=sp.symbols('a b c d e f x y z')
  expected=[0,0,4*a*b*c*d*e*f,0,a*b*c*d+a*b+a*d+c*d+1,16]
  for A,value in zip(matrices(4),expected):self.assertEqual(sp.expand(A.det()-value),0)
  self.assertEqual(len(matrices(4)),len(expected))
  M=matrices(5);self.assertEqual(sp.expand(M[0].det()-(x+3)*(x*x-3)),0)
  self.assertEqual(sp.expand(M[1].det()-(a-x)*(b-x)*(c-x)*(b-a)*(c-a)*(c-b)),0)
  M=matrices(6);self.assertEqual(len(M),6)
  self.assertEqual(sp.expand(M[0].det()-(a-b)**3),0)
  self.assertEqual(sp.expand(M[1].det()-(a**3+b**3)*M[2].det()),0)
  self.assertEqual(sp.expand(M[3].det()),0)
  V=(a-b)*(a-c)*(a-d)*(b-c)*(b-d)*(c-d)
  self.assertEqual(sp.expand(M[4].det()-V*(a+b+c+d)),0)
  for n in range(2,9):
   D=sp.Matrix(n,n,lambda i,j:abs(i-j))
   self.assertEqual(D.det(),(-1)**(n-1)*(n-1)*2**(n-2))
  exampledoc=json.loads((root/'data/examples-LA7-ready-v17.json').read_text())
  example=next(q for q in exampledoc['items'] if q['id']=='SRC-LA7-X023-8912')
  A=mat.matrices(example['prompt'])[0][2]
  self.assertEqual([A.cofactor(0,j) for j in range(4)],[-5,-5,16,-2])
  self.assertEqual(sum(A.minor_submatrix(i,0).det() for i in range(4)),0)
 def test_chapter_two_matrix_equations_against_source_answers(self):
  root=HERE.parents[1];sp=mat.sp
  doc=json.loads((root/'data/exercises-LA7-v20.json').read_text());Q={q['id']:q for q in doc['items']}
  def values(n,field='prompt'):return [A for _,_,A in mat.matrices(Q[f'SRC-LA7-E002-{n:03}'][field])]
  M=values(14);X=values(14,'solution');self.assertEqual(len(X),4)
  for A,B,C,x in [(M[0],sp.eye(2),M[1],X[0]),(sp.eye(2),M[2],M[3],X[1]),(M[4],M[5],M[6],X[2]),(M[7],M[8],M[9],X[3])]:
   self.assertEqual(A*x*B,C)
  A=values(17)[0];B=values(17,'solution')[0];self.assertEqual(A*B,A+2*B)
  A=values(18)[0];B=values(18,'solution')[0];self.assertEqual(A*B+sp.eye(3),A*A+B)
  A=values(26)[0];self.assertEqual(A**4,values(26,'solution')[0]);self.assertEqual(A.det()**8,10**16)
  M=values(1);answers=values(1,'solution')
  self.assertEqual(M[0]*M[1],answers[0]);self.assertEqual(M[3]*sp.Matrix([[-1,2]]),answers[1]);self.assertEqual(M[4]*M[5],answers[2])
  examples=json.loads((root/'data/examples-LA7-ready-v17.json').read_text());E={q['id']:q for q in examples['items']}
  q=E['SRC-LA7-X046-0751'];P,D=[A for _,_,A in mat.matrices(q['prompt'])]
  answer=mat.matrices(q['solution'])[-1][2]
  for power in range(7):self.assertEqual(P*D**power*P.inv(),answer.subs({v:power for v in answer.free_symbols}))
 def test_probability_counts_by_independent_enumeration(self):
  from fractions import Fraction
  dice=list(itertools.product(range(1,7),repeat=2))
  self.assertEqual(sum(i+j==7 for i,j in dice),6)
  self.assertEqual(sum(i+j<=5 for i,j in dice),10)
  self.assertEqual(sum((i+j)%2==0 for i,j in dice),18)
  self.assertEqual(Fraction(5*math.comb(45,2),math.comb(50,3)),Fraction(99,392))
  # Ordered room assignments and ticket-seat permutations are enumerated, not
  # evaluated with the formula used in the written derivation.
  self.assertEqual(sum(len(set(a))==3 for a in itertools.product(range(5),repeat=3)),60)
  for n in range(1,8):
   matches=sum(any(i==p[i] for i in range(n)) for p in itertools.permutations(range(n)))
   self.assertEqual(Fraction(matches,math.factorial(n)),sum((Fraction((-1)**(k+1),math.factorial(k)) for k in range(1,n+1)),Fraction(0)))
  for r in range(1,8):
   for n in range(r+1):
    S=set(range(n));sample=list(itertools.combinations(range(r),n))
    for k in range(n+1):
     count=sum(len(S.intersection(a))==k for a in sample)
     expected=math.comb(n,k)*math.comb(r-n,n-k) if 0<=n-k<=r-n else 0
     self.assertEqual(count,expected)
  for n in [4,5]:
   p=1-Fraction(math.prod(range(12-n+1,13)),12**n)
   self.assertEqual(p>=Fraction(1,2),n==5)
 def test_full_solution_sets_in_chapter_three(self):
  sp=mat.sp;root=HERE.parents[1]
  Q={q['id']:q for q in json.loads((root/'data/exercises-LA7-v20.json').read_text())['items']}
  q=Q['SRC-LA7-E003-014'];As=[A for _,_,A in mat.matrices(q['prompt'])];vectors=[A for _,_,A in mat.matrices(q['solution'])]
  start=0
  for A,count in zip(As,[1,2,1,2]):
   basis=sp.Matrix.hstack(*vectors[start:start+count]);start+=count
   self.assertEqual(A*basis,sp.zeros(A.rows,count));self.assertEqual(basis.rank(),A.cols-A.rank())
  q=Q['SRC-LA7-E003-015'];Ms=[A for _,_,A in mat.matrices(q['prompt'])];solutions=[A for _,_,A in mat.matrices(q['solution'])]
  self.assertLess(Ms[0].rank(),Ms[0].row_join(Ms[1]).rank())
  for pair,x in zip([2,4,6],solutions):
   A,b=Ms[pair:pair+2];self.assertEqual(A*x,b)
   params=sorted(x.free_symbols,key=str)
   directions=sp.Matrix.hstack(*(x.diff(p) for p in params))
   self.assertEqual(directions.rank(),A.cols-A.rank())
 def test_reasoning_tables_and_resolution_steps(self):
  inference=module('discrete_chapter_three')
  for index,(premises,goal) in enumerate(inference.forms,1):
   variables,rows=inference.inference(premises,goal)
   self.assertEqual(not any(P and not C for bits,pv,P,C,I in rows),index in [1,3,6])
  for premises,goal,clauses,path in inference.RESOLUTION_CASES:
   self.assertTrue(inference.valid(premises,goal))
   result=inference.resolvent(clauses,path)
   self.assertTrue(any(r'\square' in text for text in result))
  with self.assertRaises(AssertionError):inference.resolvent([['p'],['-p']],[(1,2,'q')])
  self.assertTrue(inference.valid([r'(p\lor q)\to(r\land s)',r'(s\lor t)\to u'],r'p\to u'))
  self.assertFalse(inference.valid([r'p\to q','q'],'p'))
 def test_vector_coordinates_and_parameter_branches(self):
  sp=mat.sp;root=HERE.parents[1]
  Q={q['id']:q for q in json.loads((root/'data/exercises-LA7-v20.json').read_text())['items']}
  A=sp.Matrix.hstack(sp.Matrix([1,1,1]),sp.Matrix([1,0,-1]),sp.Matrix([1,0,1]))
  B=sp.Matrix.hstack(sp.Matrix([1,2,1]),sp.Matrix([2,3,4]),sp.Matrix([3,4,3]))
  P=mat.matrices(Q['SRC-LA7-E004-024']['solution'])[0][2]
  self.assertEqual(A*P,B);self.assertEqual(B*sp.Matrix([-8,-1,5]),A*sp.Matrix([1,1,3]))
  a,b,c=sp.symbols('alpha beta c')
  A=sp.Matrix([[a,-2,-1],[2,1,1],[10,5,4]]);target=sp.Matrix([1,b,-1])
  self.assertEqual(A.det(),-a-4)
  for bv in [-2,0,3]:
   M=A.subs(a,-4);rhs=target.subs(b,bv)
   self.assertEqual(M.rank()==M.row_join(rhs).rank(),bv==0)
  self.assertEqual(A.subs(a,-4)*sp.Matrix([c,-2*c-1,1]),target.subs(b,0))
 def test_spectral_answers_and_quadratic_changes(self):
  sp=mat.sp;root=HERE.parents[1]
  Q={q['id']:q for q in json.loads((root/'data/exercises-LA7-v20.json').read_text())['items']}
  A=mat.matrices(Q['SRC-LA7-E005-020']['prompt'])[0][2];P=mat.matrices(Q['SRC-LA7-E005-020']['solution'].replace(r'\sqrt2',r'\sqrt{2}'))[0][2]
  A=A.subs({s:4 for s in A.free_symbols})
  self.assertEqual(sp.simplify(P.T*P),sp.eye(3));self.assertEqual(sp.simplify(P.T*A*P),sp.diag(5,-4,5))
  A=mat.matrices(Q['SRC-LA7-E005-021']['solution'])[0][2]
  for value,v in [(2,[0,1,1]),(-2,[1,1,1]),(1,[1,1,0])]:self.assertEqual(A*sp.Matrix(v),value*sp.Matrix(v))
  Cs=[A for _,_,A in mat.matrices(Q['SRC-LA7-E005-032']['solution'].replace(r'\sqrt2',r'\sqrt{2}'))]
  As=[sp.Matrix([[1,1,-2],[1,3,0],[-2,0,5]]),sp.Matrix([[1,0,1],[0,0,1],[1,1,2]]),sp.Matrix([[2,1,0],[1,1,-1],[0,-1,4]])]
  Cs[2]=Cs[2]/sp.sqrt(2)
  for A,C,D in zip(As,Cs,[sp.diag(1,1,-1),sp.diag(1,-1,1),sp.eye(3)]):
   self.assertNotEqual(C.det(),0);self.assertEqual(sp.simplify(C.T*A*C),D)
  a=sp.Symbol('a');A=sp.Matrix([[1,a,-1],[a,1,2],[-1,2,5]])
  self.assertEqual(sp.factor(A.det()),-a*(5*a+4))
  for value,positive in [(sp.Rational(-1,2),True),(sp.Rational(-4,5),False),(0,False),(sp.Rational(1,2),False),(-1,False)]:
   M=A.subs(a,value);self.assertEqual(all(M[:k,:k].det()>0 for k in range(1,4)),positive)
 def test_operator_and_change_of_basis_answers(self):
  sp=mat.sp;root=HERE.parents[1]
  Q={q['id']:q for q in json.loads((root/'data/exercises-LA7-v20.json').read_text())['items']}
  P,N=[A for _,_,A in mat.matrices(Q['SRC-LA7-E006-006']['solution'])]
  self.assertEqual(P*N/27,sp.eye(4));self.assertEqual((P-sp.eye(4))*sp.Matrix([1,1,1,-1]),sp.zeros(4,1));self.assertEqual((P-sp.eye(4)).nullspace().__len__(),1)
  C,R=[A for _,_,A in mat.matrices(Q['SRC-LA7-E006-005']['solution'])]
  A=sp.Matrix([[1,2,3],[2,3,7],[1,3,-2]]);B=sp.Matrix([[3,5,1],[1,2,1],[4,1,-6]])
  self.assertEqual(B*C,A);self.assertEqual(A*R,B);self.assertEqual(C*R,sp.eye(3))
  t=sp.Symbol('x');basis=[t*t*sp.exp(t),t*sp.exp(t),sp.exp(t)]
  D=mat.matrices(Q['SRC-LA7-E006-010']['solution'])[0][2]
  for j,p in enumerate(basis):self.assertEqual(sp.simplify(sp.diff(p,t)-sum(D[i,j]*basis[i] for i in range(3))),0)
  L=sp.Matrix([[1,0],[1,1]]);basis=[sp.Matrix([[1,0],[0,0]]),sp.Matrix([[0,1],[1,0]]),sp.Matrix([[0,0],[0,1]])]
  D=mat.matrices(Q['SRC-LA7-E006-011']['solution'])[0][2]
  for j,p in enumerate(basis):self.assertEqual(L*p*L.T,sum((D[i,j]*basis[i] for i in range(3)),sp.zeros(2)))
 def test_conditional_models_by_enumeration(self):
  from fractions import Fraction as F
  # Three cards, six equally likely labeled faces, rather than two equiprobable cards after conditioning.
  faces=[('RR','R'),('RR','R'),('WW','W'),('WW','W'),('RW','R'),('RW','W')]
  white=[card for card,face in faces if face=='W']
  self.assertEqual(F(white.count('WW'),len(white)),F(2,3))
  # Practice and match are separately uniform pairs; used balls retain their identity but cease being new.
  pairs=list(itertools.combinations(range(6),2));counts=[0,0,0]
  for practice in pairs:
   new=set(range(4))-set(practice);k=len(set(practice)&set(range(4)))
   for match in pairs:
    if set(match)<=new:counts[k]+=1
  self.assertEqual(F(sum(counts),len(pairs)**2),F(4,25))
  self.assertEqual([F(n,sum(counts)) for n in counts],[F(1,6),F(2,3),F(1,6)])
  # Forward exact state recursion verifies Pólya's invariant without using the induction formula.
  for c in [0,1,3]:
   states={(2,3):F(1)}
   for step in range(6):
    self.assertEqual(sum(prob*F(a,a+b) for (a,b),prob in states.items()),F(2,5))
    nxt={}
    for (a,b),prob in states.items():
     for key,p in [((a+c,b),F(a,a+b)),((a,b+c),F(b,a+b))]:nxt[key]=nxt.get(key,F(0))+prob*p
    states=nxt;self.assertEqual(sum(states.values()),1)
 def test_adder_and_application_assignments(self):
  for x,y,z in itertools.product([0,1],repeat=3):
   h=x^y;d=x&y;s=h^z;c=d|(h&z)
   self.assertEqual(x+y+z,2*c+s)
   self.assertFalse(d and (h&z))
  professor=[];research=[]
  for p,q,r in itertools.product([0,1],repeat=3):
   counts=[sum([1-p,q]),sum([1-q,p]),sum([1-q,1-r])]
   if sorted(counts)==[0,1,2]:professor.append((p,q,r))
   if (not p or r) and (not q or not r) and (r or p or q):research.append((p,q,r))
  self.assertEqual(professor,[(0,1,0),(1,0,1)])
  self.assertEqual(research,[(0,0,1),(0,1,0),(1,0,1)])
 def test_physics_values_and_fixed_cold_heat(self):
  import math
  self.assertAlmostEqual(.5*.01*(8*math.pi)**2*.005**2,7.895683520871487e-5)
  qhot1=2000/(1-300/500);qc=qhot1-2000;qhot2=3000+qc
  self.assertEqual(qc,3000);self.assertEqual(qhot2,6000);self.assertNotEqual(qhot1,qhot2)
  self.assertAlmostEqual(300/(1-3000/qhot2),600)
 def test_ledger_is_not_a_false_completion_claim(self):
  root=HERE.parents[1];d=json.loads((root/'data/detailed-solutions-review-ledger.json').read_text())
  self.assertEqual(d['total'],1724);self.assertFalse(d['all_questions_complete']);self.assertGreater(d['remaining_count'],0)
  ids=[x['id'] for x in d['items']];self.assertEqual(len(ids),len(set(ids)))
  self.assertTrue(all(x['has_pitfall_guidance'] for x in d['items']))
  for x in d['items']:
   if x['status']=='question_specific_checked':
    doc=json.loads((root/'data'/x['file']).read_text());q=next(i for i in doc['items'] if i['id']==x['id'])
    self.assertGreaterEqual(len(q['explanation']),3);self.assertTrue(q['common_mistakes'])
    self.assertEqual(q['detail_review']['scope'],'all_stated_subquestions')
    self.assertEqual(q['detail_review']['prompt_sha256'],hashlib.sha256(q['prompt'].encode()).hexdigest())
  self.assertEqual(d['reviewed_count']+d['remaining_count'],d['total'])
  self.assertEqual(d['reviewed_count'],len(d['complete']))
  self.assertEqual(d['remaining_count'],len(d['remaining']))
  for book,chapter,count in [('DM2T',1,40),('DM2T',2,51),('DM2T',3,26),('LA7',1,23),('LA7',2,48),('LA7',3,37),('LA7',4,64),('LA7',5,52),('LA7',6,26),('PS3',1,27),('PS3',2,38),('PS3',3,58)]:
   rows=[x for x in d['items'] if x['book_id']==book and x['chapter']==chapter]
   self.assertEqual(len(rows),count)
   self.assertTrue(all(x['status'] in ['question_specific_checked','previous_detailed_review'] for x in rows))
   self.assertTrue(all(x['pitfalls_question_specific'] for x in rows))

if __name__=='__main__':unittest.main()
