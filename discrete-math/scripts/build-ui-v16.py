from pathlib import Path
import re
R=Path(__file__).resolve().parents[1];app=(R/'assets/app-ui-v15.js').read_text()
for name in ['Es','Ps','As','qs','Ls','Hs','V14Framework','Ws','V15Lesson','Bs','$s']:
 token='function '+name+'(';assert app.count(token)==1,(name,app.count(token));app=app.replace(token,'function '+name+'BeforeV16(',1)
# Keep all submission/restore/grading behavior; replace only the answer-side component.
ms_start=app.index('function Ms(');ms_end=app.index('function V14Backup(',ms_start);ms=app[ms_start:ms_end]
def call_end(text,start):
 quote=None;escape=False;depth=0
 for i in range(text.index('(',start),len(text)):
  c=text[i]
  if quote:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c==quote:quote=None
   continue
  if c in "'\"`":quote=c
  elif c=='(':depth+=1
  elif c==')':
   depth-=1
   if not depth:return i+1
 raise ValueError('unbalanced call')
start=ms.index("v10('aside',{className:'v14-solution-pane'");end=call_end(ms,start)
ms=ms[:start]+"e.jsx(V16AnswerPane,{state:s,question,point,result,answer,used,saved,rating,setRating,errorType,setErrorType,busy,index,total:active.questions.length,onPick,next},question.id)"+ms[end:]
app=app[:ms_start]+ms+app[ms_end:]
# Secondary long lists are paged as well; their records and actions stay unchanged.
for name,next_name,size,token in [('Fs','Ks',2,'list.map('),('Ks','$sBeforeV16',6,'list.map(')]:
 start=app.index('function '+name+'(');end=app.index('function '+next_name+'(',start);piece=app[start:end]
 opening=piece.index('{',piece.index('})')+1) if False else piece.index('\n')+1
 piece=piece[:opening]+" const [listPage,setListPage]=m.useState(1);\n"+piece[opening:]
 if name=='$s':
  piece=piece.replace(token,'s.knowledge.slice((listPage-1)*6,listPage*6).map(',1)
  heading="v10('h2',{},'知识点掌握情况'),";piece=piece.replace(heading,heading+"e.jsx(V16Pager,{page:listPage,pages:Math.max(1,Math.ceil(s.knowledge.length/6)),setPage:setListPage,label:'页掌握记录'}),",1)
 else:
  piece=piece.replace(token,'list.slice((listPage-1)*'+str(size)+',listPage*'+str(size)+').map(',1)
  piece=piece.replace('onChange:ev=>setQuery(ev.target.value)','onChange:ev=>{setQuery(ev.target.value);setListPage(1)}')
  piece=piece.replace('onClick:()=>setFilter(id)','onClick:()=>{setFilter(id);setListPage(1)}')
  marker="v10('section',{className:'panel v14-wrong'}," if name=='Fs' else "v10('section',{className:'panel v14-note-list'},"
  piece=piece.replace(marker,marker+"e.jsx(V16Pager,{page:listPage,pages:Math.max(1,Math.ceil(list.length/"+str(size)+")),setPage:setListPage,label:'页记录'}),",1)
 app=app[:start]+piece+app[end:]
# Exact source crops now load their matching embedded chapter PDF.
old="const pdf=await v15Document(book),page=await pdf.getPage(segment.page);";assert old in app;app=app.replace(old,"const page=await v16Page(book,segment.page);")
app=app.replace("'关联或查看原书 PDF'","'重新打开原页'")
# Original source question: the same persistent ink board is available before and after comparison.
qstart=app.index('function V15SourceQuestion(');qend=app.index('function V15LessonBeforeV16(',qstart);q=app[qstart:qend]
q=q.replace("[tab,setTab]=m.useState('solution')","[tab,setTab]=m.useState('draft')")
q=q.replace("[['solution','原书解答'],['knowledge','相关知识']]","[['draft','手写草稿'],['solution','原书解答'],['knowledge','相关知识']]")
q=q.replace("tab==='knowledge'?", "tab==='draft'?e.jsx(V16Handwriting,{book:s.settings.current_book,question:id,label:'原题演算 · 手写草稿'},id):tab==='knowledge'?")
q=q.replace("save(rating,true);setShown(true)","save(rating,true);setShown(true);setTab('solution')")
q=q.replace("onClick:()=>setShown(true)","onClick:()=>{setShown(true);setTab('solution')}")
q=q.replace("[['pending','待核验'],['understood','对照后理解'],['confused','仍有疑问']]","V16_RATINGS")
q=q.replace("'理解记录 · 不自动计入掌握度'","'原题自评 · 待核验，不自动计入掌握度'")
q=q.replace("'保存作答并对照'","'对照原书解答'").replace("'我的作答与思路'","'文字答案或补充（可选）'").replace("'aria-pressed':rating===id","'aria-pressed':v16VisibleRating(rating)===id")
# Even with no typed answer, a learner may compare a worked example after handwriting.
q=q.replace("disabled:!answer.trim(),onClick:()=>{save(rating,true)","disabled:false,onClick:()=>{save(rating,true)")
q=q.replace("disabled:!answer.trim(),onClick:()=>save(id)","disabled:!shown,onClick:()=>save(id)")
app=app[:qstart]+q+app[qend:]
components='\n'.join((R/'scripts'/name).read_text()for name in ['handwriting-v16.js','embedded-pdf-v16.js','ui-v16-components.js'])
assert app.count('const Ys=')==1;app=app.replace('const Ys=',components+'\nconst Ys=',1)
app=app.replace('不包含原书 PDF 与密钥。切换教材后可分别导出。','不含教材文件与手写草稿；手写草稿可在画板导出 PNG。各教材记录分别备份。')
app=app.replace('./client-v15.js?v=15','./client-v16.js?v=16').replace('e.jsx(V15Reader,{page:i,state:r})','e.jsx(V16Reader,{page:i,state:r})')
app=app.replace('source-audit-v15.json?v=15','source-audit-v15.json?v=16').replace("file+'?v=15'","file+'?v=16'")
(R/'assets/app-ui-v16.js').write_text(app)
(R/'assets/client-v16.js').write_text((R/'assets/client-v15.js').read_text().replace('pages-worker-v15.js?v=15','pages-worker-v16.js?v=16'))
(R/'assets/pages-worker-v16.js').write_text((R/'assets/pages-worker-v15.js').read_text().replace('"?v=15"','"?v=16"'))
index=(R/'index.html').read_text();index=re.sub(r'app-ui-v(?:15|16)\.js\?v=\d+','app-ui-v16.js?v=16',index);index=re.sub(r'<link rel="stylesheet" href="/discrete-math/assets/ui-v16.css[^>]*>\s*','',index);index=index.replace('</head>','<link rel="stylesheet" href="/discrete-math/assets/ui-v16.css?v=16">\n</head>');(R/'index.html').write_text(index)
print('Built v16: embedded source pages, chapter browser, compact tablet layout, persistent handwriting and three ratings.')
