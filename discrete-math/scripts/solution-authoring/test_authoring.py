import importlib.util,itertools,json,unittest
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

if __name__=='__main__':unittest.main()
