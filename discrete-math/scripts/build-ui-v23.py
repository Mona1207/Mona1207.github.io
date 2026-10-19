from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
base=(R/'assets/app-ui-v22.js').read_text();app=base
def extract(name):
 a=base.index('function '+name+'(');m=re.search(r'\n(?:async )?function ',base[a+10:]);b=a+10+m.start() if m else len(base);return base[a:b]
def change(s,a,b):
 assert a in s,a[:120]
 return s.replace(a,b)
study=extract('V18Study')
study=change(study,"v10('b',{},'题目')","v10('div',{className:'v23-question-title'},v10('b',{},'题目'),e.jsx(V23QuestionBadges,{item}))")
study=change(study,"e.jsx(V19QuestionText,{item:textItem,error:sourceError})","e.jsx(V23RatingDetails,{item}),e.jsx(V19QuestionText,{item:textItem,error:sourceError})")
tree=extract('V18Tree')
tree=change(tree,"v10('div',{className:'v18-tree-body'}","e.jsx(V23RatingGuide,{}),v10('div',{className:'v18-tree-body'}")
tree=change(tree,"v10('small',{},related.length+' 道课本题')","v10('small',{},related.length+' 道课本题'),e.jsx(V23ScopeBadges,{items:related})")
card=extract('V18QuestionCard')
card=change(card,"v10('div',{className:'v18-question-links'}","e.jsx(V23QuestionBadges,{item}),v10('div',{className:'v18-question-links'}")
listing=extract('V18QuestionList')
listing=change(listing,"v10('div',{className:'v18-filter-row'}","e.jsx(V23RatingGuide,{}),v10('div',{className:'v18-filter-row'}")
home=extract('V18Home')
home=change(home,"v10('b',{},last?.title||'还没有练习记录')","v10('b',{},last?.title||'还没有练习记录'),(last||all[0])&&e.jsx(V23QuestionBadges,{item:last||all[0]})")
home=change(home,"e.jsx(V18Battery,{items:scope,records,label:'当前范围练习进度'})","e.jsx(V18Battery,{items:scope,records,label:'当前范围练习进度'}),e.jsx(V23ScopeBadges,{items:scope})")
home=change(home,"v10('b',{},concept.title)","v10('b',{},concept.title),e.jsx(V23ScopeBadges,{items:all.filter(i=>i.knowledge_ids?.includes(concept.id))})")
for name in ['V18Study','V18Tree','V18QuestionCard','V18QuestionList','V18Home','useV15Sources','useV17Examples']:
 marker='function '+name+'(';assert app.count(marker)==1,name;app=app.replace(marker,'function '+name+'BeforeV23(',1)
code='\n'.join([(R/'scripts/ratings-ui-v23.js').read_text(),study,tree,card,listing,home])
app=app.replace('const Ys=',code+'\nconst Ys=',1)
(R/'assets/app-ui-v23.js').write_text(app)
index=(R/'index.html').read_text();index=re.sub(r'app-ui-v(?:22|23)\.js\?v=[\d.]+','app-ui-v23.js?v=23',index)
index=re.sub(r'name="ui-version" content="[^"]*"','name="ui-version" content="textbook-ratings-v23"',index)
if 'ui-v23.css' not in index:index=index.replace('</head>','<link rel="stylesheet" href="/discrete-math/assets/ui-v23.css?v=23">\n</head>')
(R/'index.html').write_text(index)
print('Built v23 question ratings, recommendation badges and explanatory rubric over v22.2.')
