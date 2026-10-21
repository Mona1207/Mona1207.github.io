import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';
const read=p=>fs.readFileSync(new URL('../'+p,import.meta.url),'utf8'),app=read('assets/app-ui-v30.js');
function extract(name){const a=app.indexOf('function '+name+'(');assert(a>=0,name);const m=/\n(?:(?:async )?function |(?:const|let|var) [A-Za-z_$]|\/\/)/.exec(app.slice(a+10));return app.slice(a,a+10+m.index)}
const ctx={console,Set,Map,Math,v14Book:s=>s.book,v24Roots:s=>s.chapters.filter(c=>!c.parent_id)};vm.createContext(ctx);for(const n of ['v24MapTree','v24MapLayout'])vm.runInContext(extract(n),ctx);vm.runInContext(read('scripts/map-layouts-v30.js'),ctx);
let checked=0;
for(const id of ['DM2T','LA7','PS3','PHYS']){
 const data=JSON.parse(read('data/book-'+id+'-v15.json')),state={...data,book:data.book},roots=ctx.v24Roots(state);
 for(const focus of ['all',roots[0].id]){
  const tree=ctx.v24MapTree(state,focus),sets=[new Set(),new Set(roots.map(c=>c.id)),new Set([tree.id]),new Set(state.chapters.filter((_,i)=>i%3===0).map(c=>c.id))];
  for(const mode of ['right','left','down','balanced','outline'])for(const folded of sets){
   const layout=ctx.v30MapLayout(tree,folded,mode),ids=new Set(layout.nodes.map(n=>n.id));assert.equal(ids.size,layout.nodes.length);assert.equal(layout.edges.length,layout.nodes.length-1);
   for(const a of layout.nodes){assert([a.x,a.y,a.w,a.h].every(Number.isFinite));assert(a.x>=0&&a.y>=0&&a.x+a.w<=layout.width+.01&&a.y+a.h<=layout.height+.01,mode+' bounds '+a.id);for(const b of layout.nodes){if(a===b)continue;assert(a.x+a.w<=b.x||b.x+b.w<=a.x||a.y+a.h<=b.y||b.y+b.h<=a.y,mode+' overlap '+a.id+' '+b.id)}}
   for(const {source:a,target:b}of layout.edges){assert(a.children.some(c=>c.id===b.id),'exact textbook parent');const path=ctx.v30MapEdge(a,b,mode);assert(!/NaN|undefined/.test(path));}
   checked++;
  }
 }
}
// Book changes wait for persistence, reset route, and retain book on save failure.
let ops=[],store=new Map([['zhixu-current-book','PHYS']]),release;
ctx.localStorage={getItem:k=>store.get(k),setItem:(k,v)=>{ops.push('book');store.set(k,v)}};ctx.history={replaceState:(s,t,url)=>{assert.equal(url,'#home');assert.equal(s.zxTrail.length,0);ops.push('route')}};ctx.CustomEvent=class extends Event{constructor(type,opt){super(type);this.detail=opt.detail}};ctx.window={location:{reload:()=>ops.push('reload')},dispatchEvent:()=>ops.push('error'),monaGoHome:async()=>ops.push('home')};ctx.v20FlushInk=()=>new Promise(r=>release=r);
let pending=ctx.v14Switch('LA7');await Promise.resolve();assert.deepEqual(ops,[]);await ctx.v14Switch('PS3');release();assert.equal(await pending,true);assert.deepEqual(ops,['book','route','reload']);
ops=[];ctx.v20FlushInk=async()=>{throw Error('disk full')};assert.equal(await ctx.v14Switch('PHYS'),false);assert.equal(store.get('zhixu-current-book'),'LA7');assert.deepEqual(ops,['error']);
ops=[];ctx.v20FlushInk=async()=>{};assert.equal(await ctx.v14Switch('LA7'),true);assert.deepEqual(ops,['home']);
assert(app.includes("onClick:()=>v14Switch(b.id)"));assert(app.includes("'aria-label':'思维导图版式'"));assert(app.includes("'更多')+'筛选'"));assert(read('index.html').includes('app-ui-v30.js?v=30'));assert(read('assets/update-v30.js').includes('const CURRENT=30'));
console.log('PASS v30: '+checked+' full-book/chapter/collapsed layouts, exact parents, unique nodes, no overlap, finite edges, save-before-switch, failure recovery, same-book home and release wiring.');
