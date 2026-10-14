from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
app=(ROOT/'assets/app-ui-v14.js').read_text()
for name in ['Vs','Ws','As']:
 token='function '+name+'(';assert app.count(token)==1;app=app.replace(token,'function '+name+'BeforeV15(',1)
app=app.replace('const Ys=',(ROOT/'scripts/ui-v15-components.js').read_text()+'\nconst Ys=',1)
app=app.replace('./client-v14.js?v=14','./client-v15.js?v=15')
app=app.replace('e.jsx(V14Reader,{page:i,state:r})','e.jsx(V15Reader,{page:i,state:r})')
app=app.replace("['DM2','LA7','PS3'].includes(id)","['DM2T','DM2','LA7','PS3'].includes(id)")
app=app.replace('textbook-catalog-v14.json','textbook-catalog-v15.json')
# The original-problem index is a first-class learning resource.
app=app.replace("['framework','全书框架','对照原书目录与知识点',be]", "['framework','全书框架','对照原书目录与知识点',be],['questions','原书例题与习题','按知识点关联全部原书题目定位',ee]")
app=app.replace('questions:"习题库"','questions:"原书例题与习题"')
(ROOT/'assets/app-ui-v15.js').write_text(app)
client=(ROOT/'assets/client-v14.js').read_text().replace('["LA7","PS3"].includes(id)?id:"DM2"','["DM2T","DM2","LA7","PS3"].includes(id)?id:"DM2T"').replace('catch{return "DM2"}','catch{return "DM2T"}').replace('pages-worker-v14.js?v=14','pages-worker-v15.js?v=15')
client=client.replace('const selected=', '''try{if(!localStorage.getItem("zhixu-textbook-v15")){const previous=localStorage.getItem("zhixu-current-book");if(!previous||previous==="DM2")localStorage.setItem("zhixu-current-book","DM2T");localStorage.setItem("zhixu-textbook-v15","1")}}catch{}const selected=''',1)
(ROOT/'assets/client-v15.js').write_text(client)
w=(ROOT/'assets/pages-worker-v14.js').read_text()
w=w.replace('["LA7","PS3"].includes(id)?id:"DM2"','["DM2T","DM2","LA7","PS3"].includes(id)?id:"DM2T"').replace('catch{return "DM2"}','catch{return "DM2T"}')
w=w.replace('selectedBook==="DM2"?"zhixu-pages-v2":"zhixu-pages-v14-"+selectedBook','selectedBook==="DM2"?"zhixu-pages-v2":selectedBook==="DM2T"?"zhixu-pages-v15-DM2T":"zhixu-pages-v14-"+selectedBook')
w=w.replace('"book-"+selectedBook+".json"','"book-"+selectedBook+"-v15.json"').replace('"?v=14"','"?v=15"').replace('books-v14.json','books-v15.json')
# Lecture answer examples are study material only; grading still uses independent attempts.
(ROOT/'assets/pages-worker-v15.js').write_text(w)
index=(ROOT/'index.html').read_text();index=re.sub(r'app-ui-v(?:14|15)\.js\?v=[\d.]+','app-ui-v15.js?v=15',index);index=index.replace('warm-learning-v14','textbook-workspace-v15');index=re.sub(r'<link rel="stylesheet" href="/discrete-math/assets/ui-v15.css[^>]*>\s*','',index);index=index.replace('</head>','<link rel="stylesheet" href="/discrete-math/assets/ui-v15.css?v=15">\n</head>');(ROOT/'index.html').write_text(index)
print('Built textbook-aware UI v15; old course databases preserved; tablet two-pane viewport.')
