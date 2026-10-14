from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
app = (root / 'assets/app-ui-v10.js').read_text()
for name in ['Es', 'V10Lesson']:
    old = 'function ' + name + '('
    assert old in app
    app = app.replace(old, 'function ' + name + 'BeforeV12(', 1)
app = app.replace('const Ys=', (root / 'scripts/ui-v12-components.js').read_text() + '\nconst Ys=', 1)
app = app.replace('className:"app-shell refined-shell "', 'className:"app-shell refined-shell clarity-shell "')
old = 'children:["知序",e.jsx("span",{children:"个人学习空间"})]'
assert old in app
app = app.replace(old, 'children:[e.jsx(V12Mark,{}),"知序",e.jsx("span",{children:"学习实验室"})]', 1)
app = app.replace('onClick:()=>a(f.id),children:f.title', 'onClick:()=>a(f.id),children:[e.jsx(f.icon,{size:16}),f.title]', 1)
app = app.replace('workspace:"习题学习"', 'workspace:"知识点练习"')
app = app.replace("v10('p',{className:'eyebrow'},'从全貌，到每一个概念'),v10('h1',{},'知识树'),v10('p',{className:'subtle'},'章节是目录，知识点是学习的起点。')", "v10('h1',{},'知识树')")
(root / 'assets/app-ui-v12.js').write_text(app)
index = (root / 'index.html').read_text()
index = re.sub(r'app-ui-v(?:10|11|12)\.js\?v=[\d.]+', 'app-ui-v12.js?v=12.1', index)
index = re.sub(r'content="(?:study-desk-v11|clarity-workspace-v12)"', 'content="clarity-workspace-v12"', index)
index = re.sub(r'\s*<link rel="stylesheet" href="/discrete-math/assets/ui-v(?:11|12)\.css[^>]+>', '', index)
index = index.replace('</head>', '  <link rel="stylesheet" href="/discrete-math/assets/ui-v12.css?v=12.1">\n</head>')
index = index.replace('#f7f8f5', '#f5f6fa').replace('#151c19', '#15171d')
(root / 'index.html').write_text(index)
print('Built clarity workspace with interactive sets, progress map, and focused lesson views.')
