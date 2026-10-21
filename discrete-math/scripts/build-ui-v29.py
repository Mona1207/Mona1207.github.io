from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[1]
app=(R/'assets/app-ui-v27.js').read_text()
for name in ['V19KnowledgeSupport','V18Concept','As']:
 needle='function '+name+'(';assert app.count(needle)==1,(name,app.count(needle));app=app.replace(needle,'function '+name+'BeforeV29(',1)
needle='function B({text:s}){return e.jsx(gs,{remarkPlugins:[Ns],rehypePlugins:[bs],children:s})}'
assert needle in app;app=app.replace(needle,needle.replace('children:s','children:v29MathText(s)'))
app=app.replace('./client-v24.js?v=24','./client-v29.js?v=29').replace("'-v21.json?v=21'","'-v29.json?v=29'").replace('exercises-PHYS-v21.json?v=21','exercises-PHYS-v29.json?v=29')
app=app.replace('仅收录用户本次上传的19道物理习题。','包含原有19题、习题十一至十四的全部选择题及用户指定题，共63道；下册第九至十六章知识讲解。')
app=app.replace('按原题号练习，本次仅收录上传的19道题。','按原题号练习，含新增选择题和指定习题，共 63 道。')
app=app.replace('按上传的课后题及对应章节主题整理；完整物理教材正文尚未提供。','依据上传的第七版下册对应章节整理；推导、例子、图示与解析为学习补充。')
app=app.replace("(book==='PHYS'?[['mixed','上传习题']]","(book==='PHYS'?[['mixed','物理习题']]")
app=app.replace("'原图（含手写解答）'","item.source_type==='uploaded_textbook_pdf'?'对照教材页':'原图（含手写解答）'")
app=app.replace("'上传原图'),v10('span',{},'原图含手写解答')","'教材与原题图'),v10('span',{},'教材页与历史上传题图')")
extra=r'''
function As(props){
 if(props.state.settings.current_book!=='PHYS')return e.jsx(AsBeforeV29,props);
 const {state:s,go}=props,book=v14Book(s),{items}=useV19Exercises('PHYS');
 return v10('section',{className:'v16-books'},v10('header',{className:'v16-page-heading'},v10('div',{},v10('h1',{},'我的教材'),v10('p',{},'课程记录分别保存'))),v10('div',{className:'v16-book-cards'},s.books.map(b=>v10('button',{key:b.id,className:'v16-book '+(b.id===book.id?'selected':''),'aria-pressed':b.id===book.id,onClick:()=>b.id!==book.id&&v14Switch(b.id)},v10('span',{className:'v16-mini-cover',style:{'--cover':b.id==='PHYS'?'#526a91':'#506b72'}},'教材'),v10('span',{},v10('b',{},b.short_title||b.title),v10('small',{},b.edition||''),v10('small',{},b.id===book.id?'正在学习':'点击切换'))))),v10('div',{className:'v16-book-body'},v10('section',{className:'panel'},v10('h2',{},'物理学 · 第七版下册'),v10('p',{},'按原书第九至十六章组织。题号“11-12”表示习题十一第 12 题。'),v10('div',{className:'v16-book-outline'},s.chapters.filter(c=>!c.parent_id).map(c=>v10('button',{key:c.id,onClick:()=>go('exercises',c.id)},v10('b',{},c.title),v10('small',{},items.filter(i=>i.chapter===Number(c.id.slice(4,6))).length+' 道题'),e.jsx(S,{size:12}))))),v10('aside',{className:'panel v16-book-actions'},v10('h2',{},book.title),v10('p',{},s.knowledge.length+' 个知识点 · '+items.length+' 道教材习题'),v10('p',{className:'caption'},'已补充全部 75 节知识讲解，保留旧题及学习记录；新增习题十一至十四的 25 道选择题和 19 道指定题。讲解与解析为独立编写。'),v10('button',{className:'primary',onClick:()=>go('exercises')},'开始物理习题'),v10('button',{className:'quiet',onClick:()=>go('graph')},'查看全书知识结构'))));
}
'''
app=app.replace('const Ys=',(R/'scripts/knowledge-v29.js').read_text()+'\n'+extra+'\nconst Ys=',1)
(R/'assets/app-ui-v29.js').write_text(app)
client=(R/'assets/client-v24.js').read_text().replace('pages-worker-v24.js?v=24','pages-worker-v29.js?v=29');(R/'assets/client-v29.js').write_text(client)
worker=(R/'assets/pages-worker-v24.js').read_text().replace('"?v=24"','"?v=29"');(R/'assets/pages-worker-v29.js').write_text(worker)
index=(R/'index.html').read_text();index=re.sub(r'app-ui-v\d+\.js\?v=[\d.]+','app-ui-v29.js?v=29',index);index=re.sub(r'name="ui-version" content="[^"]*"','name="ui-version" content="mona-learning-v29"',index)
if 'ui-v29.css' not in index:index=index.replace('</head>','<link rel="stylesheet" href="/discrete-math/assets/ui-v29.css?v=29">\n</head>')
index=index.replace('update-v28.js?v=28','update-v29.js?v=29');(R/'index.html').write_text(index)
update=(R/'assets/update-v28.js').read_text().replace('CURRENT=28','CURRENT=29').replace('CURRENT_WEB=28','CURRENT_WEB=29').replace('WEB_VERSION=28','WEB_VERSION=29')
# Keep the user's existing reminder preferences and stable update surface.
update=re.sub(r'const CURRENT_WEB\s*=\s*28', 'const CURRENT_WEB=29', update)
(R/'assets/update-v29.js').write_text(update)
release=json.loads((R/'version.json').read_text());release.update(updated_at='2026-10-21',release_title='公式直观显示与物理下册内容扩充',web_version=29,web_name='v29 · 公式与物理全书讲解',release_notes=['统一公式直接排版，支持数学代码块与多种分隔符。','物理下册第九至十六章：75节、78个知识点及教学图示。','新增25道选择题和19道指定题，原有19题和学习记录保留。','讲解页新增推导、例子、符号说明与检查方法。']);(R/'version.json').write_text(json.dumps(release,ensure_ascii=False,indent=2)+'\n')
print('Built v29 without changing APK metadata or local learning-record keys')
