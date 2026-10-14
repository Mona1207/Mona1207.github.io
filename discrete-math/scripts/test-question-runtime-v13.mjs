import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {webcrypto} from 'node:crypto';
import {practiceGroup} from '../assets/practice-groups-v13.js';
const root=new URL('../',import.meta.url);
const read=p=>fs.readFileSync(new URL(p,root),'utf8');
const book=JSON.parse(read('data/book.json'));
const shards=book.question_files.map(f=>JSON.parse(read('data/'+f)));
const seed={...book,questions:shards.flatMap(f=>f.questions),links:shards.flatMap(f=>f.links)};
const context={practiceGroup,crypto:webcrypto,structuredClone,URLSearchParams,Date,console,self:{},setTimeout,clearTimeout};
vm.createContext(context);
let source=read('assets/pages-worker-v13.js').replace(/^import[^\n]+\n/,'').replace('let K=Promise.resolve();','globalThis.Engine=M;let K=Promise.resolve();');
vm.runInContext(source,context);
const Engine=context.Engine;const fresh=()=>new Engine(structuredClone(seed),null,()=> '2026-10-13T09:00:00.000Z');
let engine=fresh();
const state=engine.state();assert.equal(state.knowledge.length,seed.knowledge.length);
for(const k of state.knowledge){
 const questions=engine.sessionQuestions(k.id,'knowledge',50);
 assert.equal(new Set(questions.map(practiceGroup)).size,questions.length,k.id+' no same-method repeats');
 assert.equal(questions.length,k.practice.new_count,k.id+' displayed count matches session');
 if(!k.unlock.allowed)assert.equal(questions.length,0,k.id+' prerequisites enforced');
}
assert.equal(practiceGroup(engine.getQuestion('DM-X01-02-1')),practiceGroup(engine.getQuestion('DM-X01-02-2')),'truth values are parameter variants');
assert.equal(practiceGroup(engine.getQuestion('DM-X12-02-1')),'DM-K12-02-无序组合');
assert.equal(practiceGroup(engine.getQuestion('DM-X01-01-1')),practiceGroup(seed.questions.find(q=>q.meta.family_id==='DM-K01-01-命题辨认')));
assert.throws(()=>engine.request('/sessions','POST',{target_id:'DM-C01',mode:'chapter'}),/知识点/);
const session=engine.request('/sessions','POST',{target_id:'DM-K01-01',mode:'knowledge',question_count:10});
assert.equal(session.questions.length,state.knowledge.find(k=>k.id==='DM-K01-01').practice.new_count,'does not pad to 10');
for(const q of session.questions){const answer=engine.getQuestion(q.id).answer.accepted[0];const res=engine.request('/attempts','POST',{session_id:session.session.id,question_id:q.id,answer,duration:25});engine.request('/attempts/'+res.attempt.id+'/rate','POST',{rating:'independent'});}
assert.equal(engine.sessionQuestions('DM-K01-01','knowledge',10).length,0,'all future variants excluded');
assert.equal(engine.knowledge('DM-K01-01').mastery,100,'sufficient distinct methods can reach full performance without repetition');
assert.equal(engine.knowledge('DM-K01-01').state,'basic','mastered still requires spaced evidence');
assert.throws(()=>engine.request('/sessions','POST',{target_id:'DM-K01-01',mode:'knowledge'}),/没有新的考法/);
// Shared methods are excluded across knowledge points, not just within a point.
engine=fresh();engine.eligible=()=>true;
const q=seed.questions.find(q=>q.meta.family_id==='DM-K19-01-带余除法');
engine.snapshot.attempts.push({question_id:q.id,session_id:'history',submitted_at:'2026-10-12T09:00:00Z'});
assert(engine.sessionQuestions('DM-K19-02','knowledge',50).every(x=>practiceGroup(x)!==practiceGroup(q)));
engine.snapshot.attempts[0].self_rating='independent';engine.snapshot.attempts[0].actual_result='correct';engine.invalidate();assert.equal(engine.knowledge('DM-K19-02').independent_families,1,'equivalent method evidence transfers without redundant practice');
// Historic inflated evidence is recalculated once per method, with no data deletion.
engine=fresh();const original=engine.request('/sessions','POST',{target_id:'DM-K01-02',mode:'knowledge'});
const variants=seed.questions.filter(q=>q.verification==='verified'&&practiceGroup(q)==='DM-K01-02-蕴涵真值').slice(0,8);
engine.snapshot.attempts=variants.map((q,i)=>({id:'old'+i,session_id:original.session.id,question_id:q.id,self_rating:'independent',actual_result:'correct',duration:1,submitted_at:`2026-10-${String(i+1).padStart(2,'0')}T09:00:00Z`}));engine.invalidate();
assert.equal(engine.knowledge('DM-K01-02').independent_families,1);assert.equal(engine.knowledge('DM-K01-02').independent_questions,1);assert.equal(engine.snapshot.attempts.length,8);
// New point session prunes old unattempted variants while retaining a pending evaluation.
original.session.assistance.authorized_questions=variants.map(q=>q.id);engine.snapshot.attempts=engine.snapshot.attempts.slice(0,1);const resumed=engine.resumeSession(original.session);assert.equal(resumed.questions.length,1);assert.equal(resumed.attempts.length,1);
assert.equal(engine.resumeSession({...original.session,target_id:'DM-C01',mode:'chapter'}),null);
// Review is deliberately opted into, still only one question per method.
engine.snapshot.wrong=variants.map(q=>({question_id:q.id,resolved:false}));assert.equal(engine.sessionQuestions('DM-K01-02','wrong',50).length,1);
// All scored questions have an explicit reviewed grouping; custom questions have a numeric-normalized fallback.
assert(seed.questions.filter(q=>q.verification==='verified').every(q=>!practiceGroup(q).startsWith('custom:')));
assert.equal(practiceGroup({id:'custom1',prompt:'求 25 加 3',meta:{}}),practiceGroup({id:'custom2',prompt:'求 40 加 8',meta:{}}));
for(const id of ['DM-K01-02','DM-K04-02','DM-K18-02'])assert(new Set(seed.links.filter(l=>l.knowledge_id===id).map(l=>seed.questions.find(q=>q.id===l.question_id)).filter(q=>q.verification==='verified').map(practiceGroup)).size>=2);
console.log(`PASS: ${seed.knowledge.length} points; semantic grouping, cross-session/cross-point exclusion, no padding, prerequisites, history preservation, resume, intentional review.`);
// Component contract regression: void elements must never receive children.
// This caught the real browser's React #137 during the chooser return path.
const jsx=(type,props,key)=>({type,props:props||{},key});
const ui={e:{jsx,jsxs:jsx},m:{useState:value=>[typeof value==='function'?value():value,()=>{}]},sessionStorage:{getItem:()=>null},window:{location:{}},z:()=>{}};
for(const icon of ['S','D','J','ee','me','Ke','xe','he','ts','ke'])ui[icon]=()=>null;
ui.B=({text})=>jsx('p',{children:text});ui.De=(state,id)=>{let k=[...state.knowledge,...state.chapters].find(x=>x.id===id);while(k?.chapter_id||k?.parent_id)k=state.chapters.find(x=>x.id===(k.chapter_id||k.parent_id));return k};
vm.createContext(ui);vm.runInContext(read('scripts/ui-v10-components.js'),ui);
const data=fresh().state();
function inspect(node){if(!node||typeof node!=='object')return;if(Array.isArray(node)){node.forEach(inspect);return}if(typeof node.type==='function'){inspect(node.type(node.props));return}if(['input','img','br','hr'].includes(node.type))assert(!('children' in node.props),node.type+' must not have children');inspect(node.props?.children);}
for(const name of ['Es','Ls','Hs','qs'])inspect(ui[name]({state:data,pick:()=>{},onPick:()=>{},report:{}}));
for(const k of data.knowledge)inspect(ui.V10Lesson({k,state:data,pick:()=>{},start:()=>{},bookmark:()=>{},readSource:()=>{}}));
console.log('PASS: homepage, chooser, directory, tree, and all 46 lesson component trees render without invalid void-element children.');

// Exhaust each point through the real session/attempt APIs. The second session
// gets remaining methods rather than padded numeric variants from the first.
for(const k of seed.knowledge){
 // Isolate bank coverage; normal prerequisite enforcement is checked above.
 const e=fresh();e.eligible=()=>true;e.unlock=id=>({id,allowed:true,reasons:[]});
 const all=e.sessionQuestions(k.id,'knowledge',50);const expected=all.length;
 assert(expected>=6,k.id+' usable expansion');
 const visited=new Set();let batches=0;
 while(e.sessionQuestions(k.id,'knowledge',50).length){
  const s=e.request('/sessions','POST',{target_id:k.id,mode:'knowledge',question_count:10});
  assert(s.questions.length>0&&s.questions.length<=10);
  for(const publicQ of s.questions){
   const q=e.getQuestion(publicQ.id);const group=practiceGroup(q);
   assert(!visited.has(group),k.id+' no repeat across batches');visited.add(group);
   assert(!('answer' in publicQ)&&!('explanation' in publicQ));
   assert(!('audit_check' in publicQ.meta)&&!('expected_value' in publicQ.meta)&&!('parameters' in publicQ.meta),'private solution witnesses are not leaked');
   const res=e.request('/attempts','POST',{session_id:s.session.id,question_id:q.id,answer:q.answer.accepted[0],duration:30});
   assert.equal(res.attempt.actual_result,'correct',q.id+' shuffled option still graded correctly');
   e.request('/attempts/'+res.attempt.id+'/rate','POST',{rating:'independent'});
  }
  assert(++batches<=3,'finite exhaustion');
 }
 assert.equal(visited.size,expected,k.id+' all available methods delivered');
 assert.equal(e.knowledge(k.id).mastery,100,k.id+' varied evidence reaches full current performance');
 assert.throws(()=>e.request('/sessions','POST',{target_id:k.id,mode:'knowledge'}),/没有新的考法/);
}

// A restore of an old official question must not reintroduce an incomplete
// statement, and must not mutate the backed-up personal data.
engine=fresh();
const repaired=engine.getQuestion('DM-X06-03-2');
const historic={...structuredClone(repaired),prompt:'同样的 A、B，A−B 是什么？',meta:{...repaired.meta,full_statement_version:undefined}};
engine.snapshot.questionOverrides=[historic];
engine.snapshot.attempts=[{id:'historic-attempt',question_id:historic.id,session_id:'historic-session',submitted_at:'2026-10-01T00:00:00Z'}];
engine.snapshot.notes=[{id:'historic-note',target_id:'DM-K06-03',text:'保留笔记'}];
const before=JSON.stringify(engine.snapshot);
engine.invalidate();
assert(engine.getQuestion(historic.id).prompt.includes('A={1,2}、B={2,3}'));
assert.equal(JSON.stringify(engine.snapshot),before,'read-time official content upgrade preserves personal snapshot');
const custom={...structuredClone(repaired),id:'custom-question',prompt:'自定义题干保留',meta:{...repaired.meta,full_statement_version:undefined}};
engine.snapshot.questionOverrides.push(custom);engine.invalidate();
assert.equal(engine.getQuestion('custom-question').prompt,'自定义题干保留');

// Explicit aliases connect supplemental wording to historic evidence, including
// repeats presented under another knowledge point.
const aliases=[
 ['DM-N13-06-02-007','DM-X12-02-1'],
 ['DM-N13-09-01-005','DM-N13-12-02-002'],
 ['DM-N13-03-02-005','DM-X03-02-1'],
 ['DM-N13-07-02-004','DM-T07-135-3-1'],
 ['DM-N13-01-03-006',seed.questions.find(q=>q.meta.generator&&q.prompt.includes('⊕')).id],
];
for(const [id,old] of aliases){
 assert.equal(practiceGroup(seed.questions.find(q=>q.id===id)),practiceGroup(seed.questions.find(q=>q.id===old)),id+' related method merged');
 const e=fresh();e.eligible=()=>true;e.snapshot.attempts.push({question_id:old,session_id:'old',submitted_at:'2026-10-01T00:00:00Z'});
 const point=seed.links.find(l=>l.question_id===id).knowledge_id;
 assert(e.sessionQuestions(point,'knowledge',50).every(q=>practiceGroup(q)!==practiceGroup(e.getQuestion(id))),id+' historic attempt excludes added wording');
}
const groups=new Set(seed.questions.map(practiceGroup));
const audit=JSON.parse(read('data/question-audit-v13.json'));
assert.equal(groups.size,audit.distinct_methods);
assert.equal(groups.size,483);
assert.equal(seed.questions.length,2211);
for(const k of seed.knowledge){const ids=seed.links.filter(l=>l.knowledge_id===k.id&&l.question_id.startsWith('DM-N13-'));assert.equal(ids.length,8,k.id+' eight authored additions');}
assert(read('assets/app-ui-v12.js').includes('./client-v13.js?v=13'));
assert(read('assets/client-v13.js').includes('pages-worker-v13.js?v=13'));
assert(read('assets/pages-worker-v13.js').includes('"?v=13"'));
assert(read('assets/pages-worker-v13.js').includes('zhixu-pages-v2'),'existing DB retained');
assert(read('index.html').includes('app-ui-v12.js?v=13'));
console.log('PASS: 46 points exhausted in real sessions; 483 distinct methods; 2,211 questions; supplemental cross-point aliases; legacy restore repair; history/custom content retained; no answer witness disclosure; cache versions updated.');
