"""Build the Mona edition over v23 without altering notebook storage or question IDs."""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1]
base=(R/'assets/app-ui-v23.js').read_text();app=base
def extract(name):
 a=base.index('function '+name+'(')
 ends=[x for x in [base.find('\nfunction ',a+10),base.find('\nasync function ',a+10),base.find('\nconst Ys=',a+10),base.find('\n\nconst R19_',a+10)] if x>0]
 return base[a:min(ends) if ends else len(base)]
def change(s,a,b):
 assert a in s,a[:100]
 return s.replace(a,b)
study=extract('V18Study')
study=change(study,"[middle,setMiddle]=m.useState('draft')","[menu,setMenu]=m.useState(false),[middle,setMiddle]=m.useState('draft')")
study=change(study,"function next(delta){const to=sequence[index+delta];if(to)pick(to.id,'replace')}","async function next(delta){const to=sequence[index+delta];if(!to)return;try{await v20FlushInk();pick(to.id,'replace')}catch(err){setError('草稿保存未完成，请重试：'+err.message)}}")
study=change(study,"v10('div',{className:'v18-next-prev'},","v10('div',{className:'v18-next-prev'},v10('button',{className:'v24-menu-trigger quiet','aria-haspopup':'dialog',onClick:()=>setMenu(true)},'选题目录'),")
study=change(study,"e.jsx(V18Split,{book,finished:revealed,revealSignal,supportSignal,question:item.id,children:[left,center,right]})","e.jsx(V18Split,{book,finished:revealed,revealSignal,supportSignal,question:item.id,children:[left,center,right]}),menu&&e.jsx(V24QuestionMenu,{state:s,items,records,current:item.id,pick,close:()=>setMenu(false)})")
practice=extract('V18Tree').replace('function V18Tree(','function V24PracticeBrowser(',1)
practice=change(practice,"className:'v18-tree'","className:'v18-tree v24-practice-browser'")
practice=change(practice,"'知识树'","'知识树习题练习'")
practice=change(practice,"'搜索知识树'","'搜索习题知识树'")
ink=extract('V16Handwriting')
ink=change(ink,"[width,setWidth]=m.useState(3)","[width,setWidth]=m.useState(v24ReadPen)")
a=ink.index("v10('details',{className:'v22-size-picker'}")
b=ink.index("v10('button'",a+10)
old=ink[a:b]
assert "aria-label':'笔迹大小" in old
ink=ink[:a]+"e.jsx(V24WidthControl,{value:width,color,onChange:n=>{setWidth(n);v24SavePen(n)}}),"+ink[b:]
for name in ['V18Home','V18Tree','V18Study','V16Handwriting','Zs','useV23Ratings']:
 marker='function '+name+'(';assert app.count(marker)==1,name;app=app.replace(marker,'function '+name+'BeforeV24(',1)
root=extract('Zs')
root=change(root,"v10('h2',{},'知序')","e.jsx(V24Logo,{large:true}),v10('h2',{},V24_BRAND)")
root=change(root,"v10('b',{},rootPage?'知序':title)","v10('div',{className:'v24-site-brand'},e.jsx(V24Logo,{}),v10('b',{},V24_BRAND)),!rootPage&&v10('small',{className:'v24-page-label'},title)")
ratings=extract('useV23Ratings').replace("-v23.json?v=23","-v23.json?v=24")
code='\n'.join([(R/'scripts/ui-v24.js').read_text(),practice,ink,study,ratings,root])
app=app.replace('const Ys=',code+'\nconst Ys=',1).replace('./client-v21.js?v=21','./client-v24.js?v=24')
app=app.replace('title:"知识树",icon:Qe','title:"思维导图",icon:Qe')
app=app.replace('“推荐做”优先覆盖典型例题、独立应用与不同方法；其余题按需巩固。','物理精选习题已由用户选定，全部推荐做。其他教材优先推荐典型例题、独立应用与不同方法；其余题按需巩固。')
app=app.replace('按数学任务本身分析','按题目任务本身分析')
# All the engine's storage keys and database versions remain identical.
(R/'assets/client-v24.js').write_text((R/'assets/client-v21.js').read_text().replace('pages-worker-v21.js?v=21','pages-worker-v24.js?v=24'))
(R/'assets/pages-worker-v24.js').write_text((R/'assets/pages-worker-v21.js').read_text().replace('"?v=21"','"?v=24"'))
(R/'assets/app-ui-v24.js').write_text(app)
# Give PHYS the requested name in every catalogue, while retaining the source scope.
title='物理学（下册）精选习题'
for path in [R/'data/books-v15.json',*sorted((R/'data').glob('book-*-v15.json'))]:
 original=path.read_text();data=json.loads(original)
 def rename(obj):
  if isinstance(obj,dict):
   if obj.get('id')=='PHYS':obj.update(title=title,short_title=title,edition='物理学（下册）· 19 道精选习题')
   for value in obj.values():rename(value)
  elif isinstance(obj,list):
   for value in obj:rename(value)
 rename(data)
 if data!=json.loads(original):path.write_text(json.dumps(data,ensure_ascii=False,indent=2 if original.count('\n')>1 else None)+('\n' if original.endswith('\n') else ''))
index=(R/'index.html').read_text()
index=re.sub(r'app-ui-v(?:23|24)\.js\?v=[\d.]+','app-ui-v24.js?v=24',index)
index=re.sub(r'name="ui-version" content="[^"]*"','name="ui-version" content="mona-upgrade-v24"',index)
index=re.sub(r'<title>.*?</title>','<title>莫那刷题站·全面升级版</title>',index)
if 'ui-v24.css' not in index:index=index.replace('</head>','<link rel="stylesheet" href="/discrete-math/assets/ui-v24.css?v=24">\n<link rel="icon" type="image/png" href="/discrete-math/assets/mona-favicon-v24.png">\n<link rel="preload" as="image" href="/discrete-math/assets/mona-avatar-v24.webp">\n</head>')
index=index.replace('<div id="root"></div>','<div id="root"><div class="loading-screen v24-initial-loader" role="status"><img src="/discrete-math/assets/mona-avatar-v24.webp" width="80" height="80" alt="蒙娜丽莎微笑头像"><h2>莫那刷题站·全面升级版</h2><p>正在读取教材与学习记录…</p></div></div>')
(R/'index.html').write_text(index)
print('Built Mona v24: branding, question drawer, precise pen controls, home practice tree and visual mind map.')
