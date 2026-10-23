"""A per-question ledger: adding text or a template never certifies a complete solution."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
FILES={
 'DM2T':['exercises-DM2T-v20.json','examples-DM2T-ready-v17.json'],
 'LA7':['exercises-LA7-v20.json','examples-LA7-ready-v17.json'],
 'PS3':['exercises-PS3-v20.json','examples-PS3-ready-v17.json'],
 'PHYS':['exercises-PHYS-v29.json']}
CONDITIONAL={f'SRC-PHYS-E{x}' for x in ['010-029','011-027','011-034','011-035','014-024']}

def main():
 old=json.loads((ROOT/'data/detailed-solutions-audit-v33.json').read_text());previous=set(old['complete'])
 rows=[];summary={}
 for book,files in FILES.items():
  for fn in files:
   p=ROOT/'data'/fn;d=json.loads(p.read_text())
   for item in d['items']:
    if item.get('kind')=='exercise_group':continue
    if book=='PHYS':
     item['detail_review']={'status':'question_specific_checked','scope':'all_stated_subquestions','prompt_sha256':hashlib.sha256(item['prompt'].encode()).hexdigest(),'check':'逐项核对模型、公式来源、代入、单位、符号、选择题排错及各小问结论。','source_revision':'7959c4f6f254284cfde52e43b42cdb69f6e0d425','conditional_answer':item['id'] in CONDITIONAL,'original_source_retranscribed_in_this_pass':False}
     item['common_mistakes_basis']['individual_derivation_verified']=True
    reviewed=item.get('detail_review',{}).get('status')=='question_specific_checked'
    computed=item.get('computed_derivation',{})
    status='question_specific_checked' if reviewed else 'previous_detailed_review' if item['id'] in previous else 'computed_supplement_needs_full_review' if computed else 'needs_detailed_derivation_review'
    rows.append({'id':item['id'],'book_id':book,'title':item.get('title',''),'kind':'example' if '-X' in item['id'] else 'exercise','file':fn,'chapter':item.get('chapter',item.get('source',{}).get('chapter')),'status':status,'has_pitfall_guidance':bool(item.get('common_mistakes')),'pitfalls_question_specific':item.get('common_mistakes_basis',{}).get('individual_derivation_verified',False),'has_computed_supplement':bool(computed),'conditional_answer':item['id'] in CONDITIONAL})
   # Keep the repository's original minified style, and the original readable physics file.
   p.write_text(json.dumps(d,ensure_ascii=False,indent=2) +'\n' if book=='PHYS' else json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
  selected=[x for x in rows if x['book_id']==book]
  summary[book]={'total':len(selected),'detailed_reviewed':sum(x['status'] in ['question_specific_checked','previous_detailed_review'] for x in selected),'current_pass_checked':sum(x['status']=='question_specific_checked' for x in selected),'with_pitfall_guidance':sum(x['has_pitfall_guidance'] for x in selected),'with_computed_supplements':sum(x['has_computed_supplement'] for x in selected)}
 complete=[x['id'] for x in rows if x['status'] in ['question_specific_checked','previous_detailed_review']]
 ledger={'schema_version':1,'goal':'全部教材例题及独立习题：逐小问完整详细推导、公式依据、计算过程、结论核对及易错点。','source_revision':'7959c4f6f254284cfde52e43b42cdb69f6e0d425','total':len(rows),'reviewed_count':len(complete),'remaining_count':len(rows)-len(complete),'all_questions_complete':len(complete)==len(rows),'complete':complete,'remaining':[x['id'] for x in rows if x['id'] not in set(complete)],'by_book':summary,'review_policy':['不按篇幅、分步数量或字段存在与否直接判定已完成。','OCR及原答案校订不等于详细推导复核。','知识点易错提示不等于每小问推导均已复核。','机器算出的真值表和矩阵演算按补充材料记录；题目要求的证明方法和所有小问仍须核对。','条件缺失或答案依赖约定时，保留通式与分支，不虚构原题条件。'],'items':rows}
 (ROOT/'data/detailed-solutions-review-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:ledger[k] for k in ['total','reviewed_count','remaining_count','all_questions_complete','by_book']},ensure_ascii=False))

if __name__=='__main__':main()
