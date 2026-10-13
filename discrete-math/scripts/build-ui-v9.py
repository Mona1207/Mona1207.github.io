"""Reproducible, guarded presentation patch over the published V8 entry.
The deployment repository contains compiled assets, not the original TSX project.
Do not patch the learning worker, data schema, question bank, or vendor runtime.
"""
from pathlib import Path
root = Path(__file__).resolve().parents[1]
s = (root / 'assets/index-ByL3H-tF.js').read_text()
def replace(old, new):
    global s
    assert s.count(old) == 1, f'Expected one anchor, found {s.count(old)}: {old[:100]}'
    s = s.replace(old, new, 1)
replace('e.jsx("h1",{children:"开始习题学习"})','e.jsx("h1",{children:a?"继续你的学习。":"从一道题开始。"})')
replace('children:"每天进步一点点，遇见更好的自己"','children:"离散数学 · 先独立思考，再一步步弄懂"')
replace('"选择章节，开始第一题"','"从命题与真值开始，完成一组独立练习。"')
replace('children:"从首章开始"','children:a?"从首章重练":"从首章开始"')
replace('className:"start-first",disabled:!p,onClick:()=>p&&n(p.id,"chapter")','className:"start-first",disabled:!p,onClick:()=>p&&(!a||window.confirm("重新从首章安排一组练习？已有答题与笔记会保留。"))&&n(p.id,"chapter")')
# No-attempt states should not look like measured zero accuracy.
replace('children:[t!=null&&t.attempt_count?Math.round((t.independent_correct||0)/t.attempt_count*100):0,e.jsx("small",{children:"%"})]', 'children:[t!=null&&t.attempt_count?Math.round((t.independent_correct||0)/t.attempt_count*100):"—",e.jsx("small",{children:t!=null&&t.attempt_count?"%":""})]')
replace('"切换主题，舒适护眼"','"选择更适合当前光线的外观"')
replace('"管理个人资料与学习数据"','"本机资料、学习记录与备份"')
# Identify the active page for assistive technology.
replace('className:n===f.id?"active":"",onClick:()=>a(f.id),children:f.title','className:n===f.id?"active":"","aria-current":n===f.id?"page":void 0,onClick:()=>a(f.id),children:f.title')
replace('className:"solution "+(p.attempt.actual_result==="incorrect"?"solution-retry":""),children:', 'className:"solution "+(p.attempt.actual_result==="incorrect"?"solution-retry":""),"aria-live":"polite",children:')
replace('children:["提交独立答案",e.jsx(D,{size:17})]','children:[w?"正在提交…":"提交独立答案",e.jsx(D,{size:17})]')
replace('children:[g+1<t.questions.length?"下一题":"完成本次学习",e.jsx(D,{size:22})]','children:[w?"正在保存…":_?(g+1<t.questions.length?"下一题":"完成本次学习"):"评价理解并继续",e.jsx(D,{size:22})]')
# Put reflection in the reading flow. The existing H handler retains all mastery rules.
anchor='p&&e.jsx("div",{className:"quiz-next",'
inline='''p&&!_&&e.jsxs("section",{className:"inline-reflection","aria-label":"记录本题理解",children:[e.jsx("h2",{children:"这道题，你理解到哪一步？"}),e.jsx("p",{children:"答案已保存。选择实际理解程度后，计入完成题数与掌握度。"}),e.jsx("div",{className:"reflection-choices",children:Os.map(([h,v,R])=>e.jsxs("button",{disabled:w,onClick:()=>H(h),children:[e.jsxs("span",{children:[e.jsx("b",{children:v}),e.jsx("small",{children:R})]}),e.jsx(S,{size:17})]},h))}),p.attempt.actual_result==="incorrect"&&e.jsxs("label",{className:"inline-label",children:["这次主要卡在哪里？",e.jsx("select",{value:Q,onChange:h=>A(h.target.value),children:["概念理解","计算错误","逻辑推理","符号与条件","步骤不完整"].map(h=>e.jsx("option",{children:h},h))})]})]}),p&&_&&e.jsxs("div",{className:"quiz-save-status",role:"status",children:["✓ 已计入学习记录 · ",ve[p.attempt.self_rating]||"评价已保存",d&&e.jsx("p",{children:Object.entries(d.mastery_changes||{}).map(([h,v])=>{const item=s.knowledge.find(O=>O.id===h);return(item?item.title:"知识点")+" "+Math.round(v.before)+"% → "+Math.round(v.after)+"%"}).join(" · ")||"继续通过独立练习积累掌握证据。"})]}),'''
replace(anchor,inline+anchor)
# Consistent adaptive copy for the modal fallback.
replace('children:"选出最符合这次表现的一项。"','children:"选择实际理解程度，保存后继续。看懂解析不等于独立掌握。"')
s=s.replace('"#fdfdf5"','"#f7f8f5"').replace('"#18201b"','"#151c19"')
(root/'assets/app-ui-v9.js').write_text(s)
index=(root/'index.html').read_text()
index=index.replace('reference-v8','quiet-study-v9').replace('#fdfdf5','#f7f8f5').replace('#18201b','#151c19').replace('index-ByL3H-tF.js','app-ui-v9.js')
if 'ui-v9.css' not in index:
    index=index.replace('</head>','  <link rel="stylesheet" href="/discrete-math/assets/ui-v9.css">\n</head>')
(root/'index.html').write_text(index)
print('Created app-ui-v9.js with guarded presentation-only changes.')
