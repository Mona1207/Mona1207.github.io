import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {webcrypto} from 'node:crypto';
import {practiceGroup} from '../assets/practice-groups-v10.js';
const root=new URL('../',import.meta.url);
const read=p=>fs.readFileSync(new URL(p,root),'utf8');
const book=JSON.parse(read('data/book.json'));
const shards=book.question_files.map(f=>JSON.parse(read('data/'+f)));
const seed={...book,questions:shards.flatMap(f=>f.questions),links:shards.flatMap(f=>f.links)};
const context={practiceGroup,crypto:webcrypto,structuredClone,URLSearchParams,Date,console,self:{},setTimeout,clearTimeout};
vm.createContext(context);
let source=read('assets/pages-worker-v10.js').replace(/^import[^\n]+\n/,'').replace('let K=Promise.resolve();','globalThis.Engine=M;let K=Promise.resolve();');
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
assert.equal(session.questions.length,2,'does not pad to 10');
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
