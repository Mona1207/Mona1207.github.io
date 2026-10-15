from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
app=(R/'assets/app-ui-v16.js').read_text()
# Account-page export shares the same complete format as the notebook/settings.
a=app.index('async function we(');b=app.index('const vs=',a)
app=app[:a]+"async function we(path='/backup'){const state=await z('/state');return v17Export(state.settings.current_book,path==='/restore/previous')}"+app[b:]
for name in ['V15SourceQuestion','V14Backup','Ks','useV15Sources']:
 token='function '+name+'(';assert app.count(token)==1,name;app=app.replace(token,'function '+name+'BeforeV17(',1)
# Keep the scored question and scratch board mounted when switching to images.
a=app.index('function V16AnswerPane(');b=app.index('function V15Lesson(',a);piece=app[a:b]
piece=piece.replace("draftVisible=!result||tab==='draft'","draftVisible=tab!=='notes'&&(!result||tab==='draft')")
piece=piece.replace("m.useState('solution'),draftVisible","m.useState('draft'),draftVisible")
piece=piece.replace(" return v10('aside'"," m.useEffect(()=>{if(result)setTab('solution')},[result?.attempt.id]);\n return v10('aside'",1)
piece=piece.replace("result&&v10('div',{className:'v16-answer-tabs'}","v10('div',{className:'v16-answer-tabs'}")
piece=piece.replace("'aria-pressed':tab==='solution',onClick:()=>setTab('solution')","'aria-pressed':tab==='solution',disabled:!result,onClick:()=>setTab('solution')")
piece=piece.replace("'手写草稿'),v10('span'","'手写草稿'),v10('button',{'aria-pressed':tab==='notes',onClick:()=>setTab('notes')},'图片笔记'),result&&v10('span'")
piece=piece.replace("hidden:tab==='draft'","hidden:tab!=='solution'")
needle="result&&v10('section',{className:'v14-explanation"
piece=piece.replace(needle,"tab==='notes'&&e.jsx(V17ImageNotes,{book:s.settings.current_book,target:question.id},question.id),\n "+needle,1)
app=app[:a]+piece+app[b:]
# Surface actual transcription progress, rather than treating an OCR draft as checked.
a=app.index('function V16SourceBank(');b=app.index('function Ws(',a);piece=app[a:b]
piece=piece.replace("' 个例题 · '","' 个例题 · '")
piece=piece.replace("audit.example_locations+' 个例题 · '+audit.exercise_locations+' 个编号习题 · '+audit.exercise_groups_indexed+' 组完整习题'","audit.example_locations+' 个例题 · 文字已校订 '+(audit.reviewed_examples||0)+' / '+(audit.text_examples||0)+' · '+audit.exercise_locations+' 个习题'")
piece=piece.replace("'原书 '+i.printed_page+' 页'+", "(i.kind==='example'?(i.text_status==='reviewed'?'文字题干与答案 · 已校订':'OCR 文字 · 待校订')+' · ':'')+'原书 '+i.printed_page+' 页'+")
app=app[:a]+piece+app[b:]
# Store a rendered handwriting draft directly as an image note too.
a=app.index('function V16Handwriting(');b=app.index('const v16Embedded',a) if 'const v16Embedded' in app[a:] else app.index('function v16Viewport',a)
piece=app[a:b]
needle_export=' function exportPng()'
save_note=" function saveImageNote(){const src=canvas.current;if(!src)return;const out=document.createElement('canvas');out.width=src.width;out.height=src.height;const ctx=out.getContext('2d');ctx.fillStyle='#fff';ctx.fillRect(0,0,out.width,out.height);ctx.drawImage(src,0,0);out.toBlob(async blob=>{if(!blob)return;try{await v17ImportImage(book,question,new File([blob],book+'-'+question+'-手写笔记.png',{type:'image/png'}));setStatus('已存为本题图片笔记，完整备份会包含它')}catch(err){setStatus(err.message)}},'image/png')}\n"
assert needle_export in piece;piece=piece.replace(needle_export,save_note+needle_export,1)
piece=piece.replace("v10('button',{onClick:exportPng", "v10('button',{onClick:saveImageNote,disabled:!ink.current.length},'存为笔记'),v10('button',{onClick:exportPng",1)
app=app[:a]+piece+app[b:]

# Also offer the same inline notebook beside untranscribed homework/source items.
a=app.index('function V15SourceQuestionBeforeV17(');b=app.index('function V15LessonBeforeV16(',a);piece=app[a:b]
piece=piece.replace("['knowledge','相关知识']]","['knowledge','相关知识'],['notes','图片笔记']]")
piece=piece.replace("tab==='draft'?", "tab==='notes'?e.jsx(V17ImageNotes,{book:s.settings.current_book,target:id},id):tab==='draft'?")
app=app[:a]+piece+app[b:]
# Flush active strokes for a complete backup, including the stroke currently held down.
needle="document.addEventListener('visibilitychange',flush);return()=>document.removeEventListener('visibilitychange',flush)"
replacement="const backupFlush=()=>{if(loaded.current)v16InkSave(key,active.current?[...ink.current,active.current.stroke]:ink.current).catch(()=>{})};document.addEventListener('visibilitychange',flush);window.addEventListener('zhixu-flush-ink',backupFlush);return()=>{document.removeEventListener('visibilitychange',flush);window.removeEventListener('zhixu-flush-ink',backupFlush)}"
assert needle in app;app=app.replace(needle,replacement)
components='\n'.join((R/'scripts'/p).read_text() for p in ['notebook-v17.js','examples-ui-v17.js'])
app=app.replace('const Ys=',components+'\nconst Ys=',1)
needle='m.useEffect(()=>{r&&fe(r.settings.theme)},[r==null?void 0:r.settings.theme])'
assert needle in app;app=app.replace(needle,needle+",m.useEffect(()=>{if(r)v17RecoverPending(r.settings.current_book).then(done=>done&&K()).catch(w)},[r==null?void 0:r.settings.current_book])")
app=app.replace('./client-v16.js?v=16','./client-v17.js?v=17')
(R/'assets/app-ui-v17.js').write_text(app)
(R/'assets/client-v17.js').write_text((R/'assets/client-v16.js').read_text().replace('pages-worker-v16.js?v=16','pages-worker-v17.js?v=17'))
(R/'assets/pages-worker-v17.js').write_text((R/'assets/pages-worker-v16.js').read_text())
index=(R/'index.html').read_text();index=re.sub(r'app-ui-v(?:16|17)\.js\?v=\d+','app-ui-v17.js?v=17',index);index=re.sub(r'<link rel="stylesheet" href="/discrete-math/assets/ui-v17.css[^>]*>\s*','',index);index=index.replace('</head>','<link rel="stylesheet" href="/discrete-math/assets/ui-v17.css?v=17">\n</head>');(R/'index.html').write_text(index)
print('Built v17: structured examples, inline image notebooks, complete media backups.')
