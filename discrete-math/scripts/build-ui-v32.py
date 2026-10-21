from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[1]
app=(R/'assets/app-ui-v31.js').read_text()
def extract(name):
 a=app.index('function '+name+'(');m=re.search(r'\n(?:(?:async )?function |(?:const|let|var) [A-Za-z_$]|//)',app[a+10:]);return app[a:a+10+m.start()]
def edit(name,fn):
 global app
 old=extract(name);new=fn(old);assert old!=new,name;app=app.replace(old,new,1)
def home(old):
 a=old.index("v10('header',{className:'v24-home-heading");b=old.index("v10('div',{className:'v26-home-columns'}",a)
 return old[:a]+old[b:]
edit('V18Home',home)
def settings(old):
 a=old.index("v10('header',{className:'v18-compact-heading");b=old.index("v10('div',{className:'v18-settings-scroll'}",a)
 return old[:a]+old[b:]
edit('V18Settings',settings)
def graph(old):
 old=old.replace("e.jsx(V24ModuleTitle,{title:'知识思维导图',tag:'h1'}),",'')
 return old.replace("className:'v18-compact-heading'","className:'v32-map-search'")
edit('V18Tree',graph)
def shell(old):
 old=old.replace("v10('b',{},V24_BRAND)","v10('b',{},page==='home'?v14Book(state).title:page==='settings'?'设置':page==='graph'?'知识思维导图':V24_BRAND)")
 needle="v10('nav',{'aria-label':'主导航'},"
 old=old.replace(needle,"page==='settings'&&v10('div',{className:'v32-header-actions'},v10('button',{className:'quiet',onClick:()=>window.dispatchEvent(new Event('mona-check-update'))},'检查更新'),v10('a',{className:'quiet',href:'/discrete-math/download/'},'Android App')),"+needle)
 return old
edit('Zs',shell)
def filters(old):
 old=old.replace('close(true);group.onSelect(option.value)','group.onSelect(option.value)')
 old=old.replace('全部条件在此选择 · 选中即应用并收起','连续选择全部条件 · 点确定收起')
 old=old.replace("v10('button',{className:'quiet','aria-label':'关闭'+title,onClick:()=>close(true)},'关闭')", "v10('button',{className:'primary v32-filter-confirm','aria-label':'确定'+title,onClick:()=>close(true)},'确定')")
 return old
edit('V31FilterBar',filters)
def study_header(old):
 return old.replace("v10('div',{className:'v31-question-meta'},", "v10('div',{className:'v31-question-meta'},v10('div',{className:'v32-study-book'},e.jsx(V24Logo,{book}),v10('span',{},v14Book(s).title)),",1)
edit('V31StudyTop',study_header)
def practice_tree(old):
 return old.replace("v10('button',{'aria-pressed':chapter==='all',onClick:()=>{setChapter('all');setSection('all');setQuery('')}},'全部章节'),",'')
edit('V24PracticeBrowser',practice_tree)
def practice_preview(old):
 needle="v10('button',{className:'primary v26-enter-tree'"
 preview="v10('div',{className:'v32-home-scope'},v10('small',{},chosen?'本次练习知识点':'当前范围 · 知识点预览'),v10('ul',{},(chosen?[chosen]:points).filter(k=>scope.some(i=>i.knowledge_ids.includes(k.id))).slice(0,4).map(k=>v10('li',{key:k.id},v10('span',{},k.title),v10('small',{},scope.filter(i=>i.knowledge_ids.includes(k.id)).length+' 题'))))),"
 return old.replace(needle,preview+needle,1)
edit('V26PracticeLauncher',practice_preview)
def guide_preview(old):
 needle=".slice(0,110))),v10('button'"
 extra=".slice(0,110)),current.content?.lesson_guide&&v10('div',{className:'v32-home-guide'},v10('small',{},'从一个问题开始理解'),v10('b',{},current.content.lesson_guide.question),e.jsx(V17Markdown,{text:current.content.lesson_guide.walkthrough})),v10('div',{className:'v32-home-steps'},['理解概念','跟着推导','教材例题'].map(label=>v10('span',{key:label},label)))),v10('button'"
 return old.replace(needle,extra,1)
edit('V24ConceptLauncher',guide_preview)
# Replace the old concept function, keeping the integration identity unchanged.
app=app.replace(extract('V18Concept'),'')
extra=(R/'scripts/lesson-v32.js').read_text()
app=app.replace('const Ys=',extra+'\nconst Ys=',1)
edit('v17ValidateAssets',lambda old:old.replace('v20ValidateDraft(ink.value);','{v20ValidateDraft(ink.value);if(ink.value.lesson_page)v32ValidateLesson(ink.value)}'))
edit('v22SourceContext',lambda old:re.sub(r'basis:physical\?.*?}}',"basis:physical?'依据上传的第七版下册对应小节组织讲解，附教材定位页；推导与例子标明来源。':'依据当前教材对应小节组织导学，教材例题与独立讲解分别标识。'}}",old))
app=app.replace('client-v29.js?v=29','client-v32.js?v=32')
app=re.sub(r'(?m)^[ \t]+$','',app)
(R/'assets/app-ui-v32.js').write_text(app)
client=(R/'assets/client-v29.js').read_text().replace('pages-worker-v29.js','pages-worker-v32.js').replace('v=29','v=32')
(R/'assets/client-v32.js').write_text(client)
(R/'assets/pages-worker-v32.js').write_text((R/'assets/pages-worker-v29.js').read_text().replace('?v=29','?v=32'))
index=(R/'index.html').read_text().replace('app-ui-v31.js?v=31','app-ui-v32.js?v=32').replace('mona-soft-v31','mona-lessons-v32').replace('update-v31.js?v=31','update-v32.js?v=32')
index=index.replace('app-ui-v32.js?v=32"','app-ui-v32.js?v=32.1"')
if 'ui-v32.css' not in index:index=index.replace('</head>','<link rel="stylesheet" href="/discrete-math/assets/ui-v32.css?v=32">\n</head>')
(R/'index.html').write_text(index)
(R/'assets/update-v32.js').write_text((R/'assets/update-v31.js').read_text().replace('const CURRENT=31','const CURRENT=32'))
release=json.loads((R/'version.json').read_text());release.update(web_version=32,web_name='v32 · 教材导学与页内批注',release_title='详细导学、页内手写与整洁顶部栏',updated_at='2026-10-21',release_notes=['233个知识点补充问题引导与逐步理解，优先展开教材例题。','知识点上方可直接调用画笔、荧光笔、橡皮、撤销和重做；页内笔迹与文字笔记自动保存并纳入完整备份。','平板讲解文字在左，图示与教材定位页在右；手机自动纵向适配。','首页取消切换教材按钮，书名与logo合并到顶部白条；设置与脑图标题同样统一。','统一筛选可连续选择，点确定收起；答题顶部显示教材名与logo，知识树选题移除全部章节按钮。','首页补充知识点范围预览、学习问题和导学内容，收紧模块留白。']);(R/'version.json').write_text(json.dumps(release,ensure_ascii=False,indent=2)+'\n')
print('Built v32 guided lessons, persistent page ink and unified headers')
