from pathlib import Path
root=Path(__file__).resolve().parents[1]
s=(root/'assets/app-ui-v10.js').read_text()
s=s.replace('function Es({','function EsV10({',1)
s=s.replace('const Ys=',(root/'scripts/ui-v11-home.js').read_text()+'\nconst Ys=')
s=s.replace('className:"app-shell refined-shell "','className:"app-shell refined-shell studio-shell "')
# Simplify the lesson's visual labels; preserve its content and actions.
s=s.replace("'把概念弄清楚'","'核心概念'").replace("'用一个例子理解'","'看一个例子'").replace("'这里容易想错'","'记住这一点'").replace("'理解之后，试一试'","'下一步 · 独立练习'").replace("'用练习检验理解'","'准备好试一试了吗？'").replace("'理解的积累'","'当前掌握度'")
s=s.replace("'每道题对应不同考法。换数字的同类题，不再重复安排。'","'每种考法只选一道，专注理解，不重复刷题。'")
s=s.replace("String(index+1).padStart(2,'0')","({'01':'p','02':'≡','03':'∴','04':'∀','05':'∃','06':'∈','07':'R','08':'f','09':'∘','10':'G','11':'∨','12':'!','13':'aₙ','14':'G','15':'G','16':'T','17':'G','18':'χ','19':'≡'}[k.id.slice(4,6)]||'·')",1)
s=s.replace('workspace:"习题学习"','workspace:"知识点练习"')
(root/'assets/app-ui-v11.js').write_text(s)
index=(root/'index.html').read_text().replace('app-ui-v10.js?v=10.2','app-ui-v11.js?v=11').replace('content="knowledge-study-v10"','content="study-desk-v11"')
if 'ui-v11.css' not in index:index=index.replace('</head>','  <link rel="stylesheet" href="/discrete-math/assets/ui-v11.css?v=11">\n</head>')
(root/'index.html').write_text(index)
print('Built study-desk UI; learning engine and records unchanged.')
