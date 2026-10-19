from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
# Keep the published, independently tested reader hotfix as the baseline.
app=(R/'assets/app-ui-reader-v19.js').read_text()
for name in ['V18Split','V18Study','useV15Sources','useV17Examples','V18QuestionCard','v18Sources','V16Handwriting','V17ImageNotes','v17ValidateAssets','V18Home','Ks','v18StudySequence']:
 marker='function '+name+'('
 assert app.count(marker)==1,(name,app.count(marker))
 app=app.replace(marker,'function '+name+'BeforeV20(',1)
code='\n'.join((R/'scripts'/name).read_text() for name in ['ink-v20.js','notebook-v20.js','study-v20.js','workspace-v20.js'])
app=app.replace('const Ys=',code+'\nconst Ys=',1).replace('./client-v18.js?v=18','./client-v20.js?v=20')
(R/'assets/client-v20.js').write_text((R/'assets/client-v18.js').read_text().replace('pages-worker-v18.js?v=18','pages-worker-v20.js?v=20'))
(R/'assets/pages-worker-v20.js').write_text((R/'assets/pages-worker-v18.js').read_text().replace('"?v=16"','"?v=20"'))
(R/'assets/app-ui-v20.js').write_text(app)
index=(R/'index.html').read_text()
index=re.sub(r'app-ui-(?:reader-v19|v20)\.js\?v=[\d.]+','app-ui-v20.js?v=20',index)
index=re.sub(r'<link rel="stylesheet" href="/discrete-math/assets/ui-v(?:19|20)\.css[^>]*>\s*','',index)
index=index.replace('</head>','<link rel="stylesheet" href="/discrete-math/assets/ui-v19.css?v=20">\n<link rel="stylesheet" href="/discrete-math/assets/ui-v20.css?v=20">\n</head>')
index=re.sub(r'name="ui-version" content="[^"]*"','name="ui-version" content="textbook-workspace-v20"',index)
(R/'index.html').write_text(index)
print('Built v20 study and notebook workspace over stable reader v19.1.')
