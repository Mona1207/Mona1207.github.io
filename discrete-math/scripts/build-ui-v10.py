from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
def swap(s,a,b,new):
 start=s.index(a);end=s.index(b,start);return s[:start]+new+s[end:]
w=(root/'assets/pages.worker-qfrGCWkM.js').read_text()
w='import {practiceGroup} from "./practice-groups-v10.js";\n'+w
w=w.replace('new URL("/discrete-math/data/"+l,self.location.origin)','new URL("/discrete-math/data/"+l+"?v=10",self.location.origin)')
w=w.replace('default_mode:"chapter"','default_mode:"knowledge"')
w=swap(w,'sessionQuestions(e,i,t){','validateSnapshot(e){',(root/'scripts/worker-v10-methods.js').read_text())
w=w.replace('meta:h,attempt_count:','meta:{...h,practice_group:practiceGroup(e)},attempt_count:')
w=w.replace('question_ids:[...l],completed_questions:','question_ids:[...l],practice:this.practiceSummary(t.id),completed_questions:')
w=w.replace('h.add(String(f.meta.family_id||f.id))','h.add(practiceGroup(f))')
# Transfer evidence for the same audited method across point boundaries.
w=w.replace('t=new Set((this.indexes.qByKp.get(e)||[]).map(w=>w.id)),a=this.snapshot.attempts', 't=new Set((this.indexes.qByKp.get(e)||[]).map(w=>w.id)),methodGroups=new Set((this.indexes.qByKp.get(e)||[]).map(practiceGroup)),a=this.snapshot.attempts')
w=w.replace('let E=(this.indexes.links.get(f.id)||[]).find(N=>N.knowledge_id===e).strength*','let E=((this.indexes.links.get(f.id)||[]).find(N=>N.knowledge_id===e)?.strength??1)*')
# Count one latest rated attempt per semantic method toward confidence.
old='this.snapshot.attempts.filter(w=>t.has(w.question_id)&&w.self_rating).sort((w,o)=>o.submitted_at.localeCompare(w.submitted_at)).slice(0,30)'
new='this.snapshot.attempts.filter(w=>t.has(w.question_id)&&w.self_rating).sort((w,o)=>o.submitted_at.localeCompare(w.submitted_at)).filter((w,i,a)=>a.findIndex(o=>practiceGroup(this.getQuestion(o.question_id))===practiceGroup(this.getQuestion(w.question_id)))===i).slice(0,30)'
assert old in w;w=w.replace(old,new.replace('t.has(w.question_id)&&w.self_rating','methodGroups.has(practiceGroup(this.getQuestion(w.question_id)))&&w.self_rating'))
# Knowledge prerequisites determine practice eligibility; chapter order is directory only.
w=w.replace('this.unlock(e.chapter_id).allowed&&(this.indexes.links.get(e.id)||[]).every','(this.indexes.links.get(e.id)||[]).every')
start='if(a==="/sessions"&&i==="POST"){const o=t.target_id;'
assert start in w
w=w.replace(start,start+'''if(!this.seed.knowledge.some(k=>k.id===o)&&!['wrong','review'].includes(t.mode))throw Error("请先选择一个知识点，再开始练习。");''')
w=w.replace('t.mode||"chapter"','t.mode||"knowledge"')
w=w.replace('当前没有符合前置、核验和所选模式的题目；可调整范围或先巩固前置知识。','这个知识点暂时没有新的考法可练。已做过的同类变式不会重复安排；可以学习下一个知识点。')
w=w.replace('return h.sessions.push(E),','for(const old of h.sessions)if(!old.ended_at)old.ended_at=this.now();return h.sessions.push(E),')
a='if(a==="/sessions/latest"){'; b='if(s[0]==="sessions"&&s[2]==="end")'
w=swap(w,a,b,'if(a==="/sessions/latest"){return this.resumeSession(h.sessions.filter(f=>!f.ended_at).at(-1))}')
(root/'assets/pages-worker-v10.js').write_text(w)
client=(root/'assets/client-BHieulgK.js').read_text().replace('pages.worker-qfrGCWkM.js','pages-worker-v10.js')
(root/'assets/client-v10.js').write_text(client)
app=(root/'assets/app-ui-v9.js').read_text().replace('client-BHieulgK.js','client-v10.js')
for name in ['Es','Ls','Vs','qs','Ws','Hs','Bs']:
 app=app.replace('function '+name+'(','function '+name+'Legacy(',1)
app=app.replace('const Ys=',(root/'scripts/ui-v10-components.js').read_text()+'\nconst Ys=')
app=app.replace('resume:F})','resume:F,pick:Q})')
app=app.replace('className:"page-content page-"+n','className:"page-content page-"+n+(c?" page-detail":"")')
# Detail back behavior after ending practice goes to its knowledge point.
app=app.replace('onBack:o,onFinish:o','onBack:o,onFinish:()=>{const id=p?.session.target_id;t({page:"knowledge",detail:r.knowledge.some(k=>k.id===id)?id:null,source:null})}')
# Chapter links in retained utilities open the point directory instead of chapter practice.
old='if(!d){b(!0);try{const L=await z("/sessions","POST",{target_id:f,mode:P});'
new='if(!d){if(r.chapters.some(k=>k.id===f)){Q(f);return}b(!0);try{const L=await z("/sessions","POST",{target_id:f,mode:P});'
assert old in app;app=app.replace(old,new)
# Question preview intentionally chosen from history may be reviewed, not chapter-mode practice.
app=app.replace('onClick:()=>o(s,"chapter")','onClick:()=>a(x.links?.[0]?.knowledge_id||s)')
app=app.replace('n==="framework"&&e.jsx(Us,','n==="framework"&&e.jsx(Hs,')
# Exercise heading identifies its point instead of a chapter subsection.
app=app.replace('s.chapters.find(h=>h.id===l.chapter_id)','s.knowledge.find(h=>h.question_ids?.includes(l.id))')
(root/'assets/app-ui-v10.js').write_text(app)
index=(root/'index.html').read_text().replace('app-ui-v9.js?v=9.1','app-ui-v10.js?v=10').replace('quiet-study-v9','knowledge-study-v10')
if 'ui-v10.css' not in index:index=index.replace('</head>','  <link rel="stylesheet" href="/discrete-math/assets/ui-v10.css?v=10">\n</head>')
index=index.replace('app-ui-v10.js?v=10"','app-ui-v10.js?v=10.1"')
(root/'index.html').write_text(index)
print('Built v10 UI, client and selection engine')
