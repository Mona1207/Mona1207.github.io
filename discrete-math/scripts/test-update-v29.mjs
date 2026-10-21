import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const source=fs.readFileSync(new URL('../assets/update-v29.js',import.meta.url),'utf8');
function harness({version=29,app=null,saveFails=false,fetchFails=false,prefs={}}={}){
 let fetches=0,saves=0;const order=[],storage=new Map([['mona-release-v28',JSON.stringify(prefs)]]);
 const document=new EventTarget();
 class Element extends EventTarget{
  constructor(tag){super();this.tag=tag;this.children=[];this.attrs={};this.dataset={};this.className='';this.open=false;this.isConnected=true;this.classList={toggle(){}};}
  setAttribute(k,v){this.attrs[k]=v}getAttribute(k){return this.attrs[k]??null}
  append(...items){this.children.push(...items);items.forEach(n=>{if(n&&typeof n==='object')n.parent=this})}
  replaceChildren(...items){this.children=[];this.append(...items)}
  remove(){this.isConnected=false;if(this.parent)this.parent.children=this.parent.children.filter(n=>n!==this)}
  focus(){document.activeElement=this}
  showModal(){this.open=true;this.querySelector('[data-action="close"]')?.focus()}
  close(){this.open=false;this.dispatchEvent(new Event('close'))}
  querySelectorAll(selector){const all=[];const walk=n=>{if(!(n instanceof Element))return;const action=/^\[data-action="([^"]+)"\]$/.exec(selector);if(action?n.attrs['data-action']===action[1]:selector.startsWith('.')?n.className.split(' ').includes(selector.slice(1)):n.tag===selector)all.push(n);n.children.forEach(walk)};this.children.forEach(walk);return all}
  querySelector(s){return this.querySelectorAll(s)[0]||null}
  async click(){const handlers=this.handlers?.click||[];for(const fn of handlers)await fn(new Event('click'))}
  addEventListener(name,fn){super.addEventListener(name,fn);this.handlers??={};(this.handlers[name]??=[]).push(fn)}
 }
 const body=new Element('body'),root=new Element('div'),header=new Element('header');header.className='v18-app-header';root.append(header);body.append(root);
 Object.assign(document,{hidden:false,body,documentElement:new Element("html"),activeElement:header,createElement:tag=>new Element(tag),createTextNode:s=>s,getElementById:id=>id==='root'?root:null,querySelector:s=>body.querySelector(s),querySelectorAll:s=>body.querySelectorAll(s)});
 const window=new EventTarget();window.monaPrepareUpdate=async()=>{order.push('save');saves++;if(saveFails)throw Error('disk full')};if(app)window.MonaApp=app;
 let release={web_version:version,web_name:'v'+version,release_notes:['Readable green UI'],android:{version_code:2,version_name:'1.1.0',size_bytes:78299,download_url:'https://mona1207.github.io/discrete-math/download/mona-study-1.1.0.apk'}};
 const context={window,document,navigator:{userAgent:app?.ua||'Browser'},URL,Event,AbortController,MutationObserver:class{observe(){}},Date,console,localStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v)},location:{href:'https://mona1207.github.io/discrete-math/?v=28#exercises/DM2T-Q1',replace(url){order.push('reload');this.next=url},assign(url){order.push('download');this.next=url}},fetch:async()=>{fetches++;if(fetchFails)throw Error('offline');return {ok:true,json:async()=>release}},setTimeout(){return 1},clearTimeout(){},setInterval(){}};
 vm.createContext(context);vm.runInContext(source,context);
 return {context,window,body,document,order,get fetches(){return fetches},get saves(){return saves},get prefs(){return JSON.parse(storage.get('mona-release-v28'))},release:patch=>release={...release,...patch},action:name=>body.querySelector('[data-action="'+name+'"]'),dialog:()=>body.querySelector('dialog')};
}
let h=harness();await h.window.MonaUpdates.check();const policy=h.window.MonaReleasePolicy;
for(const url of ['http://mona1207.github.io/discrete-math/download/a.apk','https://evil.test/a.apk','https://mona1207.github.io:444/discrete-math/download/a.apk','https://user@mona1207.github.io/discrete-math/download/a.apk','javascript:alert(1)'])assert.equal(policy.safeDownload(url),null,url);
assert(policy.safeDownload('https://mona1207.github.io/discrete-math/download/mona-study-1.1.0.apk'));
assert(policy.newerName('1.10.0','1.9.0'));assert(!policy.newerName('1.1.0','1.1.0'));assert(!policy.newerName('1.0.0','1.1.0'));assert.throws(()=>policy.valid({web_version:'29'}));
assert.equal(h.window.MonaUpdates.state().webUpdate,false);assert(h.body.querySelector('.v28-update-banner'));
h.window.MonaUpdates.open();await h.window.MonaUpdates.check();assert(h.dialog().open);assert.equal(h.prefs.seenWeb,29);assert.equal(h.body.querySelector('.v28-update-banner'),null);await h.action('later').click();assert(h.prefs.snoozeUntil>Date.now()+86000000);assert(!h.dialog().open);
h=harness();h.window.MonaUpdates.open();await h.window.MonaUpdates.check();const cancel=new Event('cancel',{cancelable:true});h.dialog().dispatchEvent(cancel);assert(cancel.defaultPrevented);assert(!h.dialog().open,'Android back and Escape close release dialog');
h=harness({version:30});await Promise.all([h.window.MonaUpdates.check(),h.window.MonaUpdates.check()]);assert.equal(h.fetches,1,'single flight');h.window.MonaUpdates.open();await h.window.MonaUpdates.check();await h.action('apply').click();assert.deepEqual(h.order,['save','reload']);assert(h.context.location.next.includes('v=30#exercises/DM2T-Q1'));
h=harness({version:30,saveFails:true});await h.window.MonaUpdates.check();h.window.MonaUpdates.open();await h.window.MonaUpdates.check();await h.action('apply').click();assert.deepEqual(h.order,['save']);assert(!h.context.location.next);assert(h.window.MonaUpdates.state().error.includes('草稿尚未保存'));
h=harness({fetchFails:true});await h.window.MonaUpdates.check();assert(h.window.MonaUpdates.state().error);assert(!h.window.MonaUpdates.state().checking);h.window.MonaUpdates.open();await h.window.MonaUpdates.check();assert(!h.action('check').disabled,'retry remains usable');
h=harness({prefs:{automatic:false}});await h.window.MonaUpdates.check();assert(!h.body.querySelector('.v28-update-banner'));h.window.MonaUpdates.open();await h.window.MonaUpdates.check();assert(h.dialog().open,'manual check ignores reminder preference');
h=harness({app:{ua:'MonaStudy/1.0.0'}});await h.window.MonaUpdates.check();assert(h.window.MonaUpdates.state().appUpdate,'old app UA fallback');h.window.MonaUpdates.open();await h.window.MonaUpdates.check();await h.action('download').click();assert.deepEqual(h.order,['save','download']);
h=harness({app:{getVersionCode:()=>2,getVersionName:()=> '1.1.0'}});await h.window.MonaUpdates.check();assert(!h.window.MonaUpdates.state().appUpdate,'installed current APK');
h=harness({app:{getVersionCode:()=>1,getVersionName:()=> '1.0.0',openUpdateDownload:url=>h.order.push('native:'+url)}});await h.window.MonaUpdates.check();h.window.MonaUpdates.open();await h.window.MonaUpdates.check();await h.action('download').click();assert.equal(h.order[0],'save');assert(h.order[1].startsWith('native:https://mona1207.github.io/'));
const release=JSON.parse(fs.readFileSync(new URL('../version.json',import.meta.url)));const apk=fs.readFileSync(new URL('../download/mona-study-1.1.0.apk',import.meta.url));const {createHash}=await import('node:crypto');assert.equal(createHash('sha256').update(apk).digest('hex'),release.android.sha256);assert.equal(apk.length,release.android.size_bytes);assert.equal(release.web_version,29);assert.equal(release.android.version_code,2);
console.log('PASS v29: release validation, HTTPS download origin, single-flight checks, offline retry, current/new web and APK versions, old app fallback, reminder preferences, 24-hour snooze, save-before-reload/download, blocked save failure, route preservation and actual APK manifest hash.');
