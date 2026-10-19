from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
app=(R/'assets/app-ui-v20.js').read_text()
for name in ['As','V16Reader']:
 marker='function '+name+'('
 assert app.count(marker)==1,(name,app.count(marker))
 app=app.replace(marker,'function '+name+'BeforeV21(',1)
for old,new in [
 ("['DM2T','DM2','LA7','PS3']","['DM2T','DM2','LA7','PS3','PHYS']"),
 ("./client-v20.js?v=20","./client-v21.js?v=21"),
 ("三本正教材已内置 · 各门课程记录独立保存","数学教材与物理选题 · 各门课程记录独立保存"),
 ("fetch('/discrete-math/data/exercises-'+book+'-v20.json?v=20')","fetch('/discrete-math/data/exercises-'+book+(book==='PHYS'?'-v21.json?v=21':'-v20.json?v=20'))"),
 ("function v15SourceData(book){","function v15SourceData(book){if(book==='PHYS'){if(!v15SourceCache.has(book))v15SourceCache.set(book,fetch('/discrete-math/data/exercises-PHYS-v21.json?v=21').then(r=>{if(!r.ok)throw Error('物理题库加载失败，请刷新重试');return r.json()}).then(d=>({items:d.items.map(i=>i.source),audit:{book_id:book,example_locations:0,exercise_locations:d.items.length,numbering_or_boundary_review:0,coverage_statement:'仅收录用户本次上传的19道物理习题。'}})).catch(err=>{v15SourceCache.delete(book);throw err}));return v15SourceCache.get(book);}"),
 ("if(book==='DM2')return;if(!v17ExampleCache","if(book==='DM2'||book==='PHYS')return;if(!v17ExampleCache"),
 ("a.pdf_page-b.pdf_page||a.id.localeCompare(b.id)","v21SourceOrder(a)-v21SourceOrder(b)||a.id.localeCompare(b.id)"),
 ("(a.pdf_page||a.source_pages?.[0]||0)-(b.pdf_page||b.source_pages?.[0]||0)","v21SourceOrder(a)-v21SourceOrder(b)"),
 ("v10('small',{},'原书第 '+item.printed_page+' 页')","v10('small',{},item.source_label||('原书第 '+item.printed_page+' 页')),item.source_image&&v10('button',{className:'text-button',onClick:()=>readSource(item.image_number)},'原图（含手写解答）')"),
 ("+' · 原书第 '+item.printed_page+' 页 · '+","+' · '+(item.source_label||('原书第 '+item.printed_page+' 页'))+' · '+"),
 ("function V19Solution({item}){\n const [view,setView]=m.useState('answer');","function V19Solution({item}){\n const [view,setView]=m.useState(item?.book_id==='PHYS'?'steps':'answer');"),
 ("[['mixed','例题 + 课后题'],['examples','课本例题'],['exercises','课后习题']]","(book==='PHYS'?[['mixed','上传习题']]:[['mixed','例题 + 课后题'],['examples','课本例题'],['exercises','课后习题']])"),
 ("v10('p',{},'课本例题与课后题，在同一处练习。')","v10('p',{},book==='PHYS'?'按原题号练习，本次仅收录上传的19道题。':'课本例题与课后题，在同一处练习。')"),
 ("return v10('section',{className:'v19-text-shell'},item.status!=='reviewed'","return v10('section',{className:'v19-text-shell'},item.status==='reviewed'&&item.issues?.length>0&&v10('details',{className:'v19-ocr-status'},v10('summary',{},'题图与条件说明'),v10('ul',{},item.issues.map((issue,i)=>v10('li',{key:i},issue)))),item.status!=='reviewed'")
]:
 assert old in app,old
 app=app.replace(old,new)
app=app.replace('const Ys=',(R/'scripts/physics-v21.js').read_text()+'\nconst Ys=',1)
(R/'assets/app-ui-v21.js').write_text(app)
client=(R/'assets/client-v20.js').read_text().replace('["DM2T","DM2","LA7","PS3"]','["DM2T","DM2","LA7","PS3","PHYS"]').replace('pages-worker-v20.js?v=20','pages-worker-v21.js?v=21')
deep_link="""try{const u=new URL(window.location.href),b=u.searchParams.get("book");if(["DM2T","DM2","LA7","PS3","PHYS"].includes(b)){localStorage.setItem("zhixu-current-book",b);u.searchParams.delete("book");window.history.replaceState(window.history.state,"",u.href)}}catch{}\n"""
(R/'assets/client-v21.js').write_text(deep_link+client)
worker=(R/'assets/pages-worker-v20.js').read_text().replace('["DM2T","DM2","LA7","PS3"]','["DM2T","DM2","LA7","PS3","PHYS"]').replace('"?v=20"','"?v=21"')
marker='return G(v.snapshot);'
assert worker.count(marker)==1
worker=worker.replace(marker,marker+'if(r==="/restore/validate"){const data=await ee(T,i.backup,i.raw_backup_text);return {book_id:T.book.id,attempts:data.attempts.length,notes:data.notes.length,sessions:data.sessions.length}}')
(R/'assets/pages-worker-v21.js').write_text(worker)
index=(R/'index.html').read_text()
index=re.sub(r'app-ui-v(?:20|21)\.js\?v=\d+','app-ui-v21.js?v=21',index).replace('content="textbook-workspace-v20"','content="textbook-physics-v21"')
(R/'index.html').write_text(index)
print('Built v21 physics selection over v20 workspace and stable reader.')
