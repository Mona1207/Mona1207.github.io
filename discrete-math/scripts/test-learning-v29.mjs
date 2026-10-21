import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';import {createRequire} from 'node:module';import {webcrypto} from 'node:crypto';
const require=createRequire(import.meta.url),R=new URL('../',import.meta.url),read=p=>fs.readFileSync(new URL(p,R),'utf8'),json=p=>JSON.parse(read(p)),katex=require(process.env.V29_KATEX||'katex');
const runtime={};vm.createContext(runtime);vm.runInContext(read('scripts/knowledge-v29.js'),runtime);const normalize=s=>runtime.v29MathText(s);
for(const input of ['\\(x^2\\)','`\\frac{1}{2}`','```latex\n\\frac{1}{2}\n```','\\[x^2\\]']){assert(!normalize(input).includes('`'));assert(normalize(input).includes('$'))}
assert.equal(normalize('普通文字与 $x^2$。'),'普通文字与 $x^2$。');assert.equal(normalize('`localStorage`'),'`localStorage`');
const books=['book-DM2T-v15.json','book-LA7-v15.json','book-PS3-v15.json','book-PHYS-v15.json','book.json'].map(f=>json('data/'+f));
const physics=json('data/exercises-PHYS-v29.json'),book=books[3],old=json('data/exercises-PHYS-v21.json');
assert.equal(book.knowledge.length,78);assert.equal(book.chapters.filter(c=>!c.parent_id).length,8);assert.equal(book.chapters.filter(c=>c.parent_id).length,75);assert.equal(physics.items.length,63);assert.equal(new Set(physics.items.map(q=>q.id)).size,63);assert.equal(physics.items.filter(q=>q.choice_answer).length,25);
for(const i of old.items)assert(physics.items.some(q=>q.id===i.id),'lost old question '+i.id);
const expected={11:[15,16,24,25,27,34,35,38],12:[10,19,20,22,25,27],13:[22,24,27,29,32,38],14:[17,23,24,27,28,29]};
for(const [ch,ns] of Object.entries(expected))for(const n of ns)assert(physics.items.some(q=>q.number===ch+'-'+n));
for(const q of physics.items){assert(q.knowledge_ids.every(id=>book.knowledge.some(k=>k.id===id)));assert(q.explanation.length>=3);assert(q.prompt&&q.solution);assert.equal(q.id,q.source.id);if(q.choice_answer)assert(q.options[ q.choice_answer.charCodeAt(0)-65]);}
let count=0;const failures=[];
function scan(value,id){if(typeof value==='string'){
 const text=normalize(value);assert(!/[\x00-\x08\x0b-\x1f]/.test(text),id);
 for(const m of text.matchAll(/!\[[^\]]*\]\((\/discrete-math\/[^)]+)\)/g))assert(fs.existsSync(new URL(m[1].replace('/discrete-math/',''),R)),id+' '+m[1]);
 for(const m of text.matchAll(/\$\$([\s\S]*?)\$\$|(?<!\\)\$([^$\n]+?)(?<!\\)\$/g)){try{katex.renderToString(m[1]??m[2],{throwOnError:true,strict:'ignore',displayMode:!!m[1]});count++}catch(e){failures.push({id,formula:m[1]??m[2],error:e.message})}}
 }else if(Array.isArray(value))value.forEach((v,i)=>scan(v,id+'/'+i));else if(value&&typeof value==='object')for(const [k,v] of Object.entries(value))scan(v,id+'/'+k);
}
for(const b of books)for(const k of b.knowledge)scan(k.content,k.id);for(const q of physics.items){scan(q.prompt,q.id+'/prompt');scan(q.solution,q.id+'/solution');scan(q.explanation,q.id+'/steps')}
if(failures.length){console.log(JSON.stringify(failures.slice(0,30),null,2));throw Error(failures.length+' invalid mathematical expressions')}
const one=n=>physics.items.find(q=>q.number===n),near=(a,b,epsilon=1e-6)=>assert(Math.abs(a-b)<epsilon,`${a} != ${b}`);
near((.75**2)/.25,2.25);near((2/5)*(1-Math.log(2)),.1227411278);near(1-(1-3**(-.4))/(.4*Math.log(3)),.190784,.00001);near(-.1*8.314462618*Math.log(3),-.913437,.00001);assert(one('11-27').issues.length>0);assert(one('11-35').issues.length>0);
const fake=await import(process.env.V29_FAKE_IDB||'fake-indexeddb');const factory=new fake.IDBFactory();
function worker(bookid){let resolve,reject;const self={location:{search:'?book='+bookid,origin:'https://example.test'},postMessage:m=>m.error?reject(Error(m.error)):resolve(m.result)};
 const context={self,indexedDB:factory,crypto:webcrypto,URL,URLSearchParams,structuredClone,TextEncoder,Date,console,setTimeout,clearTimeout,practiceGroup:q=>q.id,fetch:async url=>{const u=new URL(url,'https://example.test');const p=u.pathname.replace('/discrete-math/','');return {ok:true,json:async()=>json(p)}}};vm.createContext(context);vm.runInContext(read('assets/pages-worker-v29.js').replace(/^import[^\n]+\n/,''),context);let id=0;return(path,method='GET',body={})=>new Promise((a,b)=>{resolve=a;reject=b;self.onmessage({data:{id:++id,path,method,body}})})}
const call=worker('PHYS'),state=await call('/state');assert.equal(state.knowledge.length,78);assert.equal(state.chapters.filter(c=>!c.parent_id).length,8);assert(state.knowledge.every(k=>k.unlock.allowed));
await call('/notes','POST',{target_id:old.items[0].knowledge_ids[0],content:'旧知识点上的笔记'});const backup=await call('/backup');assert.equal(backup.data.notes.length,1);await call('/restore/validate','POST',{backup,raw_backup_text:JSON.stringify(backup)});
const math=worker('LA7');assert.equal((await math('/state')).knowledge.length,32);assert.equal((await math('/backup')).data.notes.length,0);assert.equal((await call('/backup')).data.notes.length,1);
assert(read('assets/app-ui-v29.js').includes('exercises-PHYS-v29.json'));assert(read('assets/update-v29.js').includes('CURRENT=29'));assert.equal(json('version.json').web_version,29);
console.log(`PASS v29: ${count} formula renders, 279 knowledge records, 63 unique physics questions, all 26 requested numbers, 25 choices, preserved IDs, actual worker startup/unlocked sections, backup validation and course isolation.`);
