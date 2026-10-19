from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
app=(R/'assets/app-ui-v26.js').read_text()
def extract(name):
 a=app.index('function '+name+'(')
 end=re.search(r'\n(?:(?:async )?function |(?:const|let|var) [A-Za-z_$]|//)',app[a+10:])
 return app[a:a+10+end.start()] if end else app[a:]
mapping=extract('V18Tree')
ratings="e.jsx(V25RatingFilters,{value:ratingFilter,items:v20PracticeItems(items),onChange:patch=>setRatingFilter(old=>({...old,...patch})),compact:true})"
assert mapping.count(ratings)==1
mapping=mapping.replace(ratings+',','',1)
mapping=mapping.replace("className:'v24-map-toolbar'","className:'v24-map-toolbar v27-map-controls'")
needle="v10('button',{className:'quiet',onClick:()=>setCollapsed(new Set())},'展开全部')"
assert needle in mapping
mapping=mapping.replace(needle,ratings+",v10('div',{className:'v27-map-actions'},"+needle)
needle="'适合宽度'))),"
assert needle in mapping
mapping=mapping.replace(needle,"'适合宽度')))),")
app=app.replace('function V18Tree(','function V18TreeBeforeV27(',1).replace('function V25Select(','function V25SelectBeforeV27(',1)
needle="window.addEventListener('popstate',receive);window.addEventListener('hashchange',receive);return()=>{window.removeEventListener('popstate',receive);window.removeEventListener('hashchange',receive)}"
assert needle in app
app=app.replace(needle,"window.monaNativeBack=back;window.monaGoHome=()=>goRoot('home');"+needle.replace("window.removeEventListener('popstate',receive)","delete window.monaNativeBack;delete window.monaGoHome;window.removeEventListener('popstate',receive)"),1)
needle="e.jsx(V24ModuleTitle,{title:'设置',tag:'h1',scene:'settings'}))"
assert needle in app
app=app.replace(needle,"e.jsx(V24ModuleTitle,{title:'设置',tag:'h1',scene:'settings'}),v10('div',{className:'v27-settings-actions'},v10('button',{className:'quiet',onClick:()=>window.dispatchEvent(new Event('mona-check-update'))},'检查更新'),v10('a',{className:'quiet',href:'/discrete-math/download/'},'Android App')))",1)
app=app.replace('const Ys=',(R/'scripts/selection-v27.js').read_text()+'\n'+mapping+'\nwindow.monaPrepareUpdate=()=>v20FlushInk();\nconst Ys=',1)
(R/'assets/app-ui-v27.js').write_text(app)
index=(R/'index.html').read_text()
index=re.sub(r'app-ui-v(?:26|27)\.js\?v=[\d.]+','app-ui-v27.js?v=27',index)
index=re.sub(r'name="ui-version" content="[^"]*"','name="ui-version" content="mona-app-v27"',index)
if 'ui-v27.css' not in index:index=index.replace('</head>','<link rel="stylesheet" href="/discrete-math/assets/ui-v27.css?v=27">\n<script defer src="/discrete-math/assets/update-v27.js?v=27"></script>\n</head>')
(R/'index.html').write_text(index)
print('Built v27 with compact anchored selectors and larger mind map.')
