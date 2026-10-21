from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[1]
app=(R/'assets/app-ui-v29.js').read_text()
def extract(name):
 a=app.index('function '+name+'(')
 match=re.search(r'\n(?:(?:async )?function |(?:const|let|var) [A-Za-z_$]|//)',app[a+10:])
 return app[a:a+10+match.start()]
def patch_function(name,fn):
 global app
 old=extract(name);new=fn(old);assert old!=new,name;app=app.replace(old,new,1)
patch_function('v14Switch',lambda old:'function v14SwitchBeforeV30'+old[len('function v14Switch'):])
# Every book card is a selection, including the current book.
app=app.replace('onClick:()=>!active&&v14Switch(b.id)','onClick:()=>v14Switch(b.id)')
app=app.replace('onClick:()=>b.id!==book.id&&v14Switch(b.id)','onClick:()=>v14Switch(b.id)')
app=app.replace("'19 道精选题 · 全部推荐做'","'63 道教材习题 · 知识图解'")
def router(old):
 old=old.replace("window.monaNativeBack=back;","function navigationError(ev){setNavError(String(ev.detail||'操作未完成，请重试。'))}window.addEventListener('mona-navigation-error',navigationError);window.monaNativeBack=back;")
 old=old.replace('delete window.monaNativeBack;',"window.removeEventListener('mona-navigation-error',navigationError);delete window.monaNativeBack;")
 # The same web back behavior also closes the top overlay before navigating.
 old=old.replace('function back(){return guard(',"function back(){if(document.querySelector('.v27-select-menu')){window.dispatchEvent(new Event('mona-close-menu',{cancelable:true}));return Promise.resolve()}const dialog=document.querySelector('dialog[open]');if(dialog){dialog.dispatchEvent(new Event('cancel',{cancelable:true}));return Promise.resolve()}return guard(")
 return old
patch_function('Cs',router)
def map_ui(old):
 old=old.replace("mapMounted=m.useRef(false),[focus", "mapMounted=m.useRef(false),[mapMode,setMapMode]=m.useState(()=>{try{const saved=localStorage.getItem('mona-map-layout-v30-'+book);return V30_MAP_LAYOUTS.some(([id])=>id===saved)?saved:'right'}catch{return 'right'}}),[focus")
 old=old.replace('layout=v24MapLayout(tree,query?new Set():collapsed)','layout=v30MapLayout(tree,query?new Set():collapsed,mapMode)')
 old=old.replace("[focus,book]);","[focus,book,mapMode]);",1)
 old=old.replace("className:'v24-map-page'","className:'v24-map-page v30-map-'+mapMode")
 selector="v10(V25Select,{'aria-label':'思维导图版式',value:mapMode,onChange:ev=>{const mode=ev.target.value;mapMounted.current=true;savedMap.current={};setMapMode(mode);try{localStorage.setItem('mona-map-layout-v30-'+book,mode)}catch{}}},V30_MAP_LAYOUTS.map(([id,label])=>v10('option',{key:id,value:id},label))),"
 old=old.replace("className:'v24-map-toolbar v27-map-controls'},","className:'v24-map-toolbar v27-map-controls'},"+selector)
 old=old.replace("return v10('path',{key:a.id+'-'+b.id,d:'M '+x+' '+y+' C '+(x+(xx-x)/2)+' '+y+', '+(x+(xx-x)/2)+' '+yy+', '+xx+' '+yy", "return v10('path',{key:a.id+'-'+b.id,d:v30MapEdge(a,b,mapMode)")
 old=old.replace("'适合宽度')))),", "'适合宽度'),v10('button',{onClick:()=>{const el=viewport.current;if(el)changeZoom(Math.min(1,(el.clientWidth-24)/layout.width,(el.clientHeight-24)/layout.height))}},'适合窗口')))),")
 return old
patch_function('V18Tree',map_ui)
def menu(old):
 old=old.replace("[error,setError]=m.useState('')","[expanded,setExpanded]=m.useState(false),[error,setError]=m.useState('')",1)
 old=old.replace("v10('p',{className:'caption'},'按章节、知识点或原题号直接跳转'),",'')
 old=old.replace("v10('div',{className:'v24-menu-filters'},", "v10('div',{className:'v24-menu-filters'},",1)
 old=old.replace("e.jsx(V25RatingFilters,{value:filter,onChange:change,items:v24FilterQuestionsBeforeV25(s,items,records,filter),compact:true}),v10('div',{className:'v24-menu-count'},", "expanded&&e.jsx(V25RatingFilters,{value:filter,onChange:change,items:v24FilterQuestionsBeforeV25(s,items,records,filter),compact:true}),v10('div',{className:'v24-menu-count'},v10('button',{className:'text-button','aria-expanded':expanded,onClick:()=>setExpanded(v=>!v)},(expanded?'收起':'更多')+'筛选'+(filter.difficulty!=='all'||filter.recommendation!=='all'?' · 已启用':'')),")
 return old
patch_function('V24QuestionMenu',menu)
app=app.replace('const Ys=',(R/'scripts/map-layouts-v30.js').read_text()+'\nconst Ys=',1)
(R/'assets/app-ui-v30.js').write_text(app)
index=(R/'index.html').read_text().replace('app-ui-v29.js?v=29','app-ui-v30.js?v=30').replace('mona-learning-v29','mona-tablet-v30').replace('update-v29.js?v=29','update-v30.js?v=30')
if 'ui-v30.css' not in index:index=index.replace('</head>','<link rel="stylesheet" href="/discrete-math/assets/ui-v30.css?v=30">\n</head>')
(R/'index.html').write_text(index)
update=(R/'assets/update-v29.js').read_text().replace('const CURRENT=29','const CURRENT=30')
assert update!=(R/'assets/update-v29.js').read_text()
(R/'assets/update-v30.js').write_text(update)
release=json.loads((R/'version.json').read_text());release.update(web_version=30,web_name='v30 · 平板整屏与高效选题',updated_at='2026-10-21',release_title='平板整屏、五种脑图版式与双列选题',release_notes=['平板首页、设置与学习页压缩固定区域，更多内容在一屏展示。','思维导图新增向右、向左、向下、左右分支、紧凑目录五种版式，按教材记住选择。','选择任一本教材后自动回首页，切换前保存草稿；返回优先关闭弹层。','精确选题缩小筛选区，题目双列排列，难度与推荐筛选可展开。'])
(R/'version.json').write_text(json.dumps(release,ensure_ascii=False,indent=2)+'\n')
print('Built tablet UI v30; textbook content and Android metadata retained')
