from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
app=(R/'assets/app-ui-v17.js').read_text()
assert app.count('function Zs(')==1
app=app.replace('function Zs(','function ZsBeforeV18(',1)
# Keep legacy hashes readable, then normalize them into the new source-first flow.
old='const _s=["home","books","framework","graph","knowledge","questions","workspace","path","wrong","bookmarks","notes","reviews","reports","ai","settings","rules","account"]'
assert old in app;app=app.replace(old,old[:-1]+',"examples","exercises","concept"]')
a=app.index('function Ss(');b=app.index('function Cs(',a)
app=app[:a]+'''function Ss(route){if(route.source)return {...route,source:null};if(route.detail)return {page:route.page==='concept'?'graph':route.page,detail:null,source:null};return {page:['examples','exercises','reports','wrong','bookmarks'].includes(route.page)?'home':'settings',detail:null,source:null}}'''+app[b:]
code='\n'.join((R/'scripts'/file).read_text() for file in ['study-v18.js','pages-v18.js'])
app=app.replace('const Ys=',code+'\nconst Ys=',1).replace('./client-v17.js?v=17','./client-v18.js?v=18')
(R/'assets/app-ui-v18.js').write_text(app)
(R/'assets/client-v18.js').write_text((R/'assets/client-v17.js').read_text().replace('pages-worker-v17.js?v=17','pages-worker-v18.js?v=18'))
worker=(R/'assets/pages-worker-v17.js').read_text();a=worker.index('unlock(e){');b=worker.index('validateDependencies(',a)
worker=worker[:a]+'''unlock(e){this.getNode(e);const conditions=(this.indexes.dependencies.get(e)||[]).filter(d=>d.dependency_type==='prerequisite').map(d=>({id:d.source_id,title:this.getNode(d.source_id).title,type:d.source_type,description:d.description,met:true,advisory:true}));return {allowed:true,prerequisites_met:true,warning:false,state:'unlocked',conditions,reasons:[]}}'''+worker[b:]
(R/'assets/pages-worker-v18.js').write_text(worker)
index=(R/'index.html').read_text();index=re.sub(r'app-ui-v(?:17|18)\.js\?v=\d+','app-ui-v18.js?v=18',index);index=re.sub(r'<link rel="stylesheet" href="/discrete-math/assets/ui-v18.css[^>]*>\s*','',index);index=index.replace('</head>','<link rel="stylesheet" href="/discrete-math/assets/ui-v18.css?v=18">\n</head>');(R/'index.html').write_text(index)
print('Built v18: unlocked source-first study, continuous knowledge tree, stars/progress and adjustable three-column workspace.')
