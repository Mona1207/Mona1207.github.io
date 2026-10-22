"""Exhaustive, reproducible truth-table derivations for propositional exercises."""
import itertools,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
REPLACEMENTS={r'\leftrightarrow':'↔',r'\Leftrightarrow':'↔',r'\iff':'↔',r'\to':'→',r'\rightarrow':'→',r'\Rightarrow':'→',r'\implies':'→',r'\land':'∧',r'\wedge':'∧',r'\lor':'∨',r'\vee':'∨',r'\neg':'¬',r'\lnot':'¬',r'\oplus':'⊕',r'\uparrow':'↑',r'\downarrow':'↓',r'\equiv':'↔',r'\left':'',r'\right':'',r'\,':'',r'\;':'',r'\!':''}

class Formula:
 def __init__(self,text):
  s=text
  for a,b in REPLACEMENTS.items():s=s.replace(a,b)
  s=s.replace('{','(').replace('}',')').replace(' ','').replace('\n','')
  if not s or re.search(r'[^pqrs01¬∧∨→↔⊕↑↓()]',s):raise ValueError('Not a supported propositional formula')
  self.tokens=list(s);self.pos=0;self.tree=self.parse(0)
  if self.pos!=len(self.tokens):raise ValueError('Trailing formula tokens')
  self.variables=sorted(set(re.findall('[pqrs]',s)))
  if not 1<=len(self.variables)<=4:raise ValueError('Variable count')
 def peek(self):return self.tokens[self.pos] if self.pos<len(self.tokens) else None
 def parse(self,level):
  groups=[['↔'],['→'],['∨','⊕','↓'],['∧','↑']]
  if level==4:
   t=self.peek();self.pos+=1
   if t=='¬':return ('¬',self.parse(4))
   if t=='(':
    node=self.parse(0)
    if self.peek()!=')':raise ValueError('Unclosed parenthesis')
    self.pos+=1;return node
   if t in ['p','q','r','s','0','1']:return t
   raise ValueError('Expected atom')
  node=self.parse(level+1)
  while self.peek() in groups[level]:
   op=self.peek();self.pos+=1
   node=(op,node,self.parse(level if op=='→' else level+1))
  return node
 @staticmethod
 def ev(node,env):
  if isinstance(node,str):return int(node) if node in ['0','1'] else env[node]
  op=node[0];a=Formula.ev(node[1],env)
  if op=='¬':return 1-a
  b=Formula.ev(node[2],env)
  return {'∧':a&b,'∨':a|b,'→':int(not a or b),'↔':int(a==b),'⊕':int(a!=b),'↑':1-(a&b),'↓':1-(a|b)}[op]
 def rows(self):
  return [(dict(zip(self.variables,v)),self.ev(self.tree,dict(zip(self.variables,v)))) for v in itertools.product([0,1],repeat=len(self.variables))]
 @staticmethod
 def latex(node):
  if isinstance(node,str):return node
  if node[0]=='¬':return r'\neg('+Formula.latex(node[1])+')'
  ops={'∧':r'\land','∨':r'\lor','→':r'\to','↔':r'\leftrightarrow','⊕':r'\oplus','↑':r'\uparrow','↓':r'\downarrow'}
  return '('+Formula.latex(node[1])+ops[node[0]]+' '+Formula.latex(node[2])+')'
 def columns(self):
  out=[]
  def visit(node):
   if isinstance(node,str):return
   for child in node[1:]:visit(child)
   if node not in out:out.append(node)
  visit(self.tree);return out
 def derivation(self,text,index,principal=False):
  rows=self.rows();cols=self.columns();variables=self.variables
  # Display every intermediate subformula, rather than skipping to F's value.
  headers=variables+[self.latex(x) for x in cols]
  table=r'\begin{array}{'+'c'*len(headers)+'}'+r'&'.join(headers)+r'\\\hline '
  table+=r'\\'.join('&'.join(str(env[v]) for v in variables)+'&'+'&'.join(str(self.ev(c,env)) for c in cols) for env,value in rows)+r'\end{array}'
  true=[''.join(str(e[v]) for v in variables) for e,n in rows if n]
  false=[''.join(str(e[v]) for v in variables) for e,n in rows if not n]
  kind='重言式' if not false else '矛盾式' if not true else '非重言的可满足式'
  answer=f'**公式 {index}：${text}$。** 变项按 ${",".join(variables)}$ 排列，共 $2^{len(variables)}={len(rows)}$ 组赋值。先计算否定，再按括号从内向外计算，最后得到最外层联结词的值。蕴涵仅在前件为1、后件为0时取0；双条件仅在两侧真值相同时取1。\n\n$$'+table+'$$'
  answer+='\n\n依上表逐行读取，成真赋值：'+('、'.join(true) if true else '无')+'；成假赋值：'+('、'.join(false) if false else '无')+'。故该式为**'+kind+'**。这些赋值覆盖全部情况，既给出结论，也能检查是否漏行。'
  if principal:
   def term(env,minor):
    return '('+(r'\land ' if minor else r'\lor ').join((v if bool(env[v])==minor else r'\neg '+v) for v in variables)+')'
   dnf=r'\lor '.join(term(e,True) for e,n in rows if n) or '0'
   cnf=r'\land '.join(term(e,False) for e,n in rows if not n) or '1'
   answer+='\n\n主析取范式对每个成真赋值写一个极小项（该行的1写原变项、0写否定），再析取：$$'+dnf+'$$主合取范式对每个成假赋值写一个极大项（该行的0写原变项、1写否定），再合取：$$'+cnf+'$$每个项都含全部变项一次；因此极小项与极大项的符号选择规则相反。'
  return answer,{'formula':text,'variable_order':variables,'true':true,'false':false,'classification':kind}

def main():
 report=[]
 for filename in ['exercises-DM2T-v20.json','examples-DM2T-ready-v17.json']:
  p=ROOT/'data'/filename;d=json.loads(p.read_text())
  for item in d['items']:
   if item.get('kind')=='exercise_group':continue
   prompt=item['prompt']
   if not re.search(r'真值表|成真赋值|成假赋值|主析取范式|主合取范式|逻辑等值|公式的类型',prompt):continue
   if re.search(r'已知|设.*真值|当.*真值',prompt):continue
   formulae=[]
   for text in re.findall(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)',prompt,re.S):
    try:
     f=Formula(text)
     if f.columns():formulae.append((text,f))
    except ValueError:continue
   if not formulae:continue
   added=[];proof=[]
   for i,(text,f) in enumerate(formulae,1):
    step,evidence=f.derivation(text,i,'主析取范式' in prompt or '主合取范式' in prompt);added.append(step);proof.append(evidence)
   item['computed_derivation']={'method':'exhaustive_truth_table','proofs':proof,'scope':'supported_formulas_in_prompt','all_subquestions_reviewed':False}
   item['explanation']=[s for s in item.get('explanation',[]) if not s.startswith('**公式 ')] + added
   report.append({'id':item['id'],'formula_count':len(proof)})
  p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'questions_with_exhaustive_proofs':len(report),'formulas':sum(x['formula_count'] for x in report)},ensure_ascii=False))
 (ROOT/'data'/'computed-logic-proofs-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
