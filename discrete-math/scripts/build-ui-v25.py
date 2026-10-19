"""Uniform refined selectors plus consistent rating filters, over the published v24."""
from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
base=(R/'assets/app-ui-v24.js').read_text();app=base
def extract(name):
 a=base.index('function '+name+'(')
 ends=[x for x in [base.find('\nfunction ',a+10),base.find('\nasync function ',a+10),base.find('\nconst Ys=',a+10),base.find('\n\nconst R19_',a+10)] if x>0]
 return base[a:min(ends) if ends else len(base)]
def change(s,a,b):
 assert a in s,a[:100]
 return s.replace(a,b)
practice=extract('V24PracticeBrowser')
practice=change(practice,'items,records,pick})','items,records,pick,go})')
practice=change(practice,"const key=","const [ratingFilter,setRatingFilter]=useV25RatingFilter('mona-practice-ratings-v25-'+s.settings.current_book),key=")
practice=change(practice,"all=v18Sources(items,'examples').concat(v18Sources(items,'exercises'));","all=v25FilterRatings(v18Sources(items,'examples').concat(v18Sources(items,'exercises')),ratingFilter);const visiblePoints=points.filter(k=>ratingFilter.difficulty==='all'&&ratingFilter.recommendation==='all'||all.some(i=>i.knowledge_ids.includes(k.id)));")
practice=change(practice,"e.jsx(V23RatingGuide,{}),","e.jsx(V25RatingFilters,{value:ratingFilter,items:v20PracticeItems(items),onChange:patch=>setRatingFilter(old=>({...old,...patch})),compact:true}),e.jsx(V23RatingGuide,{}),")
practice=practice.replace('points.map(k=>{','visiblePoints.map(k=>{').replace('!points.length','!visiblePoints.length')
practice=change(practice,"onClick:()=>pick(k.id)","disabled:!related.length,onClick:()=>v25OpenPoint(s,k,items,ratingFilter,pick,go)")
practice=practice.replace("'没有匹配知识点。'","'当前难度与推荐条件下，没有匹配知识点。'")
menu=extract('V24QuestionMenu')
menu=menu.replace("status:'all',query:''","status:'all',query:'',difficulty:'all',recommendation:'all'")
menu=change(menu,"v10('div',{className:'v24-menu-count'}","e.jsx(V25RatingFilters,{value:filter,onChange:change,items:v24FilterQuestionsBeforeV25(s,items,records,filter),compact:true}),v10('div',{className:'v24-menu-count'}")
mapping=extract('V18Tree')
mapping=change(mapping,'items,records,pick})','items,records,pick,go})')
mapping=change(mapping,'const book=s.settings.current_book,','const [ratingFilter,setRatingFilter]=useV25RatingFilter("mona-map-ratings-v25-"+s.settings.current_book),book=s.settings.current_book,')
mapping=change(mapping,'all=v20PracticeItems(items)','all=v25FilterRatings(v20PracticeItems(items),ratingFilter)')
mapping=change(mapping,"v10('small',{className:'v24-map-hint'}","e.jsx(V25RatingFilters,{value:ratingFilter,items:v20PracticeItems(items),onChange:patch=>setRatingFilter(old=>({...old,...patch})),compact:true}),v10('small',{className:'v24-map-hint'}")
mapping=change(mapping,"onClick:()=>pick(point.id)","onClick:()=>v25OpenPoint(s,point,items,ratingFilter,pick,go)")
mapping=mapping.replace("'打开全部关联题目（'","'打开匹配题目（'").replace("'此知识点暂无关联单题。'","'此知识点在当前筛选条件下暂无匹配单题。'")
saved=extract('V18Saved')
saved=change(saved,"const [kind,setKind]","const [ratingFilter,setRatingFilter]=useV25RatingFilter('mona-saved-ratings-v25-'+s.settings.current_book+'-'+mode),[kind,setKind]")
saved=change(saved,'list=items.filter(','unfiltered=items.filter(')
saved=change(saved,"return v10('section'","const list=v25FilterRatings(unfiltered,ratingFilter);return v10('section'")
saved=change(saved,"v10('div',{className:'v18-question-scroll'}","e.jsx(V25RatingFilters,{value:ratingFilter,items:unfiltered,onChange:patch=>setRatingFilter(old=>({...old,...patch})),compact:true}),v10('div',{className:'v18-question-scroll'}")
saved=saved.replace("mode==='star'?'在题目旁点击星标即可收藏。'","unfiltered.length?'当前难度与推荐条件下暂无匹配题目。':mode==='star'?'在题目旁点击星标即可收藏。'")
home=extract('V18Home')
home=change(home,'e.jsx(V24PracticeBrowser,{state:s,items,records,pick})','e.jsx(V24PracticeBrowser,{state:s,items,records,pick,go})')
for name in ['v24FilterQuestions','V24PracticeBrowser','V24QuestionMenu','V18QuestionList','V18Tree','V18Saved','V18Books','V18Home']:
 marker='function '+name+'(';assert app.count(marker)==1,name;app=app.replace(marker,'function '+name+'BeforeV25(',1)
code='\n'.join([(R/'scripts/selection-v25.js').read_text(),practice,menu,mapping,saved,home])
app=app.replace('const Ys=',code+'\nconst Ys=',1)
# Keep all original value/onChange semantics while removing OS-default pickers.
count=0
for pattern in [r"v10\((['\"])select\1\s*,",r'e\.(jsx|jsxs)\((\"|\x27)select\2\s*,']:
 def substitute(match):
  global count
  count+=1
  return 'v10(V25Select,' if match.group(0).startswith('v10') else 'e.'+match.group(1)+'(V25Select,'
 app=re.sub(pattern,substitute,app)
(R/'assets/app-ui-v25.js').write_text(app)
index=(R/'index.html').read_text()
index=re.sub(r'app-ui-v(?:24|25)\.js\?v=[\d.]+','app-ui-v25.js?v=25',index)
index=re.sub(r'name="ui-version" content="[^"]*"','name="ui-version" content="mona-selection-v25"',index)
if 'ui-v25.css' not in index:index=index.replace('</head>','<link rel="stylesheet" href="/discrete-math/assets/ui-v25.css?v=25">\n</head>')
(R/'index.html').write_text(index)
print(f'Built v25: {count} selector sites unified; difficulty and recommendation filters on home, listings, drawer, map and saved questions.')
