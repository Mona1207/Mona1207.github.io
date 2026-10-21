from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[1]
app=(R/'assets/app-ui-v30.js').read_text()
def extract(name):
 a=app.index('function '+name+'(');m=re.search(r'\n(?:(?:async )?function |(?:const|let|var) [A-Za-z_$]|//)',app[a+10:]);return app[a:a+10+m.start()]
def edit(name,fn):
 global app
 old=extract(name);new=fn(old);assert old!=new,name;app=app.replace(old,new,1)
def end_call(s,start):
 start=s.index('(',start);stack=0;quote=None;escaped=False
 for i in range(start,len(s)):
  c=s[i]
  if quote:
   if escaped:escaped=False
   elif c=='\\':escaped=True
   elif c==quote:quote=None
   continue
  if c in "'\"`":quote=c
  elif c=='(':stack+=1
  elif c==')':
   stack-=1
   if stack==0:return i+1
 raise ValueError('call not closed')
def wrap_block(old,start,end,title):
 a=old.index(start);b=old.index(end,a);return old[:a]+"v10(V31FilterBar,{title:'"+title+"'},"+old[a:b]+')'+old[b:]
# Commit the closing state before invoking callbacks, and hide the native popover immediately.
def selection(old):
 old=old.replace('function close(focus=false){setOpen(false);if(focus)trigger.current?.focus()}',"function close(focus=false){try{const el=menu.current;if(el?.matches(':popover-open'))el.hidePopover()}catch{}setOpen(false);if(focus)trigger.current?.focus({preventScroll:true})}")
 old=old.replace('onClick:()=>choose(option)', 'onClick:ev=>{ev.preventDefault();ev.stopPropagation();choose(option)}')
 return old
edit('V25Select',selection)
# All module headings use text, while the application brand keeps its portrait.
edit('V24ModuleTitle',lambda old:"function V24ModuleTitle({title,tag='h2',id}){return v10('div',{className:'v24-module-title v26-module-title v31-module-title'},v10(tag,{id},title))}")
edit('V18Settings',lambda old:old.replace("className:'v26-setting-tile',key:id,", "className:'v26-setting-tile',key:id,'data-v31-kind':id,"))
edit('V26PracticeLauncher',lambda old:wrap_block(old,"v10('div',{className:'v26-home-fields'}",",v10('div',{className:'v26-scope-summary'}",'练习范围'))
edit('V24ConceptLauncher',lambda old:wrap_block(old,"v10('label',{},'章节'",',current&&','知识范围'))
def map_ui(old):
 a=old.index("v10('div',{className:'v24-map-toolbar v27-map-controls'},")+len("v10('div',{className:'v24-map-toolbar v27-map-controls'},")
 b=old.index(",v10('div',{className:'v27-map-actions'}",a)
 return old[:a]+"v10(V31FilterBar,{title:'脑图范围与版式'},"+old[a:b]+')'+old[b:]
edit('V18Tree',map_ui)
def question_menu(old):
 old=old.replace("[expanded,setExpanded]=m.useState(false),",'')
 a=old.index("v10('div',{className:'v24-menu-filters'},")
 b=old.index(",v10('div',{className:'v24-menu-count'},",a)
 block=old[a:b].replace('expanded&&e.jsx(V25RatingFilters','e.jsx(V25RatingFilters')
 old=old[:a]+"v10(V31FilterBar,{title:'筛选题目'},"+block+')'+old[b:]
 a=old.index("v10('button',{className:'text-button','aria-expanded':expanded,")
 b=end_call(old,a)
 old=old[:a]+old[b+1:]
 return old
edit('V24QuestionMenu',question_menu)
def question_list(old):
 a=old.index("v10('div',{className:'v25-filter-basics'},")
 b=old.index(",kind==='exercises'",a)
 block=old[a:b]
 search_a=block.index("v10('label',{className:'v25-question-search'}")
 search=block[search_a:end_call(block,search_a)]
 return old[:a]+"v10('div',{className:'v31-list-controls'},"+search+",v10(V31FilterBar,{title:'筛选题目'},"+block+'))'+old[b:]
edit('V18QuestionList',question_list)
def practice(old):
 needle="e.jsx(V25RatingFilters,{value:ratingFilter,items:v20PracticeItems(items),onChange:patch=>setRatingFilter(old=>({...old,...patch})),compact:true})"
 assert needle in old
 return old.replace(needle,"v10(V31FilterBar,{title:'习题筛选'},"+needle+')',1)
edit('V24PracticeBrowser',practice)
def saved(old):
 a=old.index("e.jsx(V25RatingFilters,");b=end_call(old,a)
 return old[:a]+"v10(V31FilterBar,{title:'记录筛选'},"+old[a:b]+')'+old[b:]
edit('V18Saved',saved)
def study(old):
 old=old.replace("[menu,setMenu]=m.useState(false),","[original,setOriginal]=m.useState(false),",1)
 a=old.index("v10('header',{className:'v18-column-heading'},")
 b=old.index(",\n  v10('details',{className:'v18-typed-answer'}",a)
 left="""v10('header',{className:'v18-column-heading v31-question-heading'},v10('b',{},'题目'),v10('div',{className:'mini-segments','aria-label':'题目显示方式'},v10('button',{'aria-pressed':!original,onClick:()=>setOriginal(false)},'文字'),v10('button',{'aria-pressed':original,disabled:!(item.source_image_url||item.source?.source_image_url||item.segments?.length),onClick:()=>setOriginal(true)},'原图'))),
  v10('details',{className:'v31-question-context'},v10('summary',{},'关联知识与评级'),v10('div',{className:'v18-related-chips'},points.map(k=>v10('button',{className:'v18-chip',key:k.id,'aria-pressed':rightView==='knowledge'&&selectedKnowledge===k.id,onClick:()=>showKnowledge(k.id)},k.title,e.jsx(S,{size:10})))),e.jsx(V23RatingDetails,{item})),
  original?e.jsx(V31OriginalQuestion,{book,item},item.id):e.jsx(V19QuestionText,{item:textItem,error:sourceError})"""
 old=old[:a]+left+old[b:]
 a=old.index("v10('header',{className:'v18-study-heading'},")
 b=end_call(old,a)
 old=old[:a]+old[b+1:]
 old=old.replace(",menu&&e.jsx(V24QuestionMenu,{state:s,items,records,current:item.id,pick,close:()=>setMenu(false)})",'')
 return old
edit('V18Study',study)
def shell(old):
 a=old.index("if(!state)return ");b=old.index('\n const current=',a)
 old=old[:a]+"if(!state)return e.jsx(V31Loading,{error,retry:()=>refresh().catch(fail)});"+old[b:]
 a=old.index("v10('div',{className:'v24-site-brand'},")
 b=end_call(old,a)
 old=old[:a]+"studying?e.jsx(V31StudyTop,{...common,item},item.id):"+old[a:b]+old[b:]
 old=old.replace("!rootPage&&v10('small',{className:'v24-page-label'},title)","!rootPage&&!studying&&v10('small',{className:'v24-page-label'},title)")
 return old
edit('Zs',shell)
# Android/web back handles the one-layer panel before any route change.
edit('Cs',lambda old:old.replace("document.querySelector('.v27-select-menu')","document.querySelector('.v27-select-menu, .v31-filter-panel')"))
# Existing Android 1.1.0 bridge also recognizes the new selector's established class.
app=app.replace("className:'v31-filter-panel',role:","className:'v31-filter-panel v27-select-menu',role:") if False else app
extra=(R/'scripts/ui-v31.js').read_text().replace("className:'v31-filter-panel',role:","className:'v31-filter-panel v27-select-menu',role:")
app=app.replace('const Ys=',extra+'\nconst Ys=',1)
app=re.sub(r'(?m)^[ \t]+$', '', app)
(R/'assets/app-ui-v31.js').write_text(app)
index=(R/'index.html').read_text().replace('app-ui-v30.js?v=30','app-ui-v31.js?v=31').replace('mona-tablet-v30','mona-soft-v31').replace('update-v30.js?v=30','update-v31.js?v=31')
if 'ui-v31.css' not in index:index=index.replace('</head>','<link rel="stylesheet" href="/discrete-math/assets/ui-v31.css?v=31">\n</head>')
readers=''.join('<img class="v31-launch-reader" src="/discrete-math/assets/avatars-v26/'+book+'.webp" alt="蒙娜丽莎阅读教材" style="--reader:'+str(i)+'">' for i,book in enumerate(['DM2T','LA7','PS3','PHYS']))
loading='<div class="v31-launch" role="status"><div class="v31-launch-glow" aria-hidden="true"></div><div class="v31-launch-portraits">'+readers+'</div><small class="v31-launch-eyebrow">MONA STUDY</small><h1>莫那刷题站</h1><p class="v31-launch-motto">从一道题，读懂一个知识点</p><div class="v31-launch-status"><span class="v31-loading-dots" aria-hidden="true"><i></i><i></i><i></i></span><span>正在读取教材与学习记录…</span></div></div>'
index=re.sub(r'<div id="root">.*</div></body>',lambda m:'<div id="root">'+loading+'</div></body>',index,flags=re.S)
(R/'index.html').write_text(index)
(R/'assets/update-v31.js').write_text((R/'assets/update-v30.js').read_text().replace('const CURRENT=30','const CURRENT=31'))
release=json.loads((R/'version.json').read_text());release.update(web_version=31,web_name='v31 · 柔光立体与统一筛选',release_title='统一筛选、柔光界面与沉浸刷题',updated_at='2026-10-21',release_notes=['多项筛选整合在同一面板，选择后立即应用并收起。','统一模块对齐、柔和立体表面与右下角学习插画，移除模块标题头像。','蒙娜丽莎阅读形象动态切换，搭配主题色柔幻弥散启动背景。','刷题信息与切题按钮合并到顶部白栏；原图在题目区域替换文字显示。']);(R/'version.json').write_text(json.dumps(release,ensure_ascii=False,indent=2)+'\n')
print('Built v31: one-layer filters, soft UI, reading launch and in-place originals')
