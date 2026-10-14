from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
app=(ROOT/'assets/app-ui-v12.js').read_text()
# Preserve all old versions for rollback; replace names only in v14 output.
for name in ['Es','As','Bs','Fs','Ks','$s','Ps','Ms']:
 token='function '+name+'(';assert app.count(token)==1,name;app=app.replace(token,'function '+name+'BeforeV14(',1)
app=app.replace('const Ys=',(ROOT/'scripts/ui-v14-components.js').read_text()+'\nconst Ys=',1)
app=app.replace('./client-v13.js?v=13','./client-v14.js?v=14')
app=app.replace('className:"app-shell refined-shell clarity-shell "','className:"app-shell refined-shell clarity-shell warmth-shell "')
# Framework and path are now different screens. Every source page uses active book's range.
app=app.replace('n==="framework"&&e.jsx(Hs,','n==="framework"&&e.jsx(V14Framework,')
app=app.replace('e.jsx(Ds,{page:i})','e.jsx(V14Reader,{page:i,state:r})')
app=app.replace('Math.min(445,Math.max(1,f))','Math.min(v14Book(r)?.meta?.pdf_pages||445,Math.max(1,f))')
app=app.replace('max:445,value:i','max:v14Book(r)?.meta?.pdf_pages||445,value:i')
app=app.replace('children:"/ 445"','children:"/ "+(v14Book(r)?.meta?.pdf_pages||445)')
app=app.replace('disabled:i===445','disabled:i===(v14Book(r)?.meta?.pdf_pages||445)')
# Props for notes editing and report are real application data.
app=app.replace('report:j,go:$,pick:Q,start:G,readSource:A,fail:w','report:j,go:$,pick:Q,start:G,readSource:A,fail:w,refresh:K')
old='onFinish:()=>{const id=p?.session.target_id;t({page:"knowledge",detail:r.knowledge.some(k=>k.id===id)?id:null,source:null})}'
assert old in app;app=app.replace(old,'onFinish:()=>t({page:"reports",detail:null,source:null})')
# Hide duplicated chapter-mode settings; dedicated book picker owns switching.
app=app.replace('onChange:l=>f("current_book",l.target.value)','onChange:l=>v14Switch(l.target.value)')
app=app.replace('[["chapter","按章"],["knowledge","知识专项"],["weak","薄弱训练"],["review","间隔复习"]]','[["knowledge","知识专项"],["weak","薄弱训练"],["review","间隔复习"]]')
app=app.replace('children:"默认单次题数"','children:"单次题数上限（不重复凑题）"')
start=app.index('u==="data"&&e.jsxs("section"',app.index('function Is('))
end=app.index(',u==="dependencies"',start)
app=app[:start]+'u==="data"&&e.jsx(V14Backup,{state:s,refresh:t,notify:a,fail:o})'+app[end:]
# IDs remain supplementary; names make advanced prerequisite choices readable.
app=app.replace('children:[l.id," · ",l.title]','children:[l.title," · ",l.id]')
app=app.replace('children:[l.source_id," → ",l.target_id]','children:[Y.find(v=>v.id===l.source_id)?.title||l.source_id," → ",Y.find(v=>v.id===l.target_id)?.title||l.target_id]')
# Defaults must belong to each book rather than old DM point IDs.
app=app.replace('m.useState("DM-K06-01")','m.useState(s.knowledge[0]?.id||"")').replace('m.useState("DM-K07-01")','m.useState(s.knowledge[1]?.id||"")')
app=app.replace("v10('small',{className:'practice-caption'},'已练 '","k.source?.exercise_pdf_page&&v10('button',{className:'text-button',onClick:()=>readSource(k.source.exercise_pdf_page)},'对照原书：'+k.source.exercise_title,e.jsx(S,{size:14})),v10('small',{className:'practice-caption'},'已练 '")
(ROOT/'assets/app-ui-v14.js').write_text(app)
# Book selection is local and each book gets a separate worker/database.
client=(ROOT/'assets/client-v13.js').read_text()
client=client.replace('const a=new Worker(new URL("/discrete-math/assets/pages-worker-v13.js?v=13",import.meta.url)', 'const selected=(()=>{try{const id=localStorage.getItem("zhixu-current-book");return ["LA7","PS3"].includes(id)?id:"DM2"}catch{return "DM2"}})();const a=new Worker(new URL("/discrete-math/assets/pages-worker-v14.js?v=14&book="+selected,import.meta.url)')
(ROOT/'assets/client-v14.js').write_text(client)
w=(ROOT/'assets/pages-worker-v13.js').read_text()
w=w.replace('var se=Object.defineProperty;', 'const selectedBook=(()=>{try{const id=new URLSearchParams(self.location?.search||"").get("book");return ["LA7","PS3"].includes(id)?id:"DM2"}catch{return "DM2"}})();var se=Object.defineProperty;')
w=w.replace('current_book:"DM2"','current_book:selectedBook')
w=w.replace('const Z="zhixu-pages-v2"','const Z=selectedBook==="DM2"?"zhixu-pages-v2":"zhixu-pages-v14-"+selectedBook')
w=w.replace('books:[this.seed.book]','books:this.seed.books||[this.seed.book]')
w=w.replace('config:{...O},dependencies:structuredClone(e.dependencies)', 'config:{...O,current_book:e.book.id},dependencies:structuredClone(e.dependencies)')
w=w.replace('"?v=13"','"?v=14"')
w=w.replace('r("book.json")','r(selectedBook==="DM2"?"book.json":"book-"+selectedBook+".json")')
w=w.replace('T={...i,questions:l.flatMap(d=>d.questions),links:l.flatMap(d=>d.links)}}else T=i;', 'T={...i,questions:l.flatMap(d=>d.questions),links:l.flatMap(d=>d.links)}}else T=i;const catalog=await fetch(r("books-v14.json"));if(!catalog.ok)throw Error("教材切换目录加载失败");T.books=await catalog.json();')
# Engine state exposes the full exercise archive catalog independently of scored bank.
# Exact per-book backup validation prevents an empty backup crossing course namespaces.
w=w.replace('if(e.schema!==2)throw Error("备份版本不支持");','if(e.schema!==2)throw Error("备份版本不支持");if(e.config?.current_book!==this.seed.book.id)throw Error("此备份属于另一教材，请先切换到对应教材后恢复");')
w=w.replace('attempts:h.attempts.slice(-200).reverse()', 'attempts:h.attempts.slice().reverse()')
w=w.replace('if(a==="/settings"){const o={...h.config,...t.config};','if(a==="/settings"){if(t.config?.current_book&&t.config.current_book!==this.seed.book.id)throw Error("请在设置—我的教材中切换课程");const o={...h.config,...t.config};')
w=w.replace('if(r==="/backup")return G(v.snapshot);', 'if(r==="/backup")return G(v.snapshot);if(r==="/restore/validate"){const data=await ee(T,i.backup,i.raw_backup_text);return {book_id:T.book.id,attempts:data.attempts.length,notes:data.notes.length,sessions:data.sessions.length}}')
(ROOT/'assets/pages-worker-v14.js').write_text(w)
index=(ROOT/'index.html').read_text().replace('app-ui-v12.js?v=13','app-ui-v14.js?v=14').replace('clarity-workspace-v12','warm-learning-v14').replace('知序 · 离散数学学习实验室','知序 · 数学学习空间').replace('#f5f6fa','#f8f7f3').replace('#15171d','#1d211f')
index=re.sub(r'<link rel="stylesheet" href="/discrete-math/assets/ui-v14.css[^>]*>\s*','',index)
index=index.replace('</head>','<link rel="stylesheet" href="/discrete-math/assets/ui-v14.css?v=14">\n</head>')
(ROOT/'index.html').write_text(index)
print('Built v14 UI, separate book engines, reader and cache URLs.')
