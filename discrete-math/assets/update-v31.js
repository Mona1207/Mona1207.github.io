/* Foreground release messages for the website and Android WebView. No tracking. */
(()=>{
 'use strict';
 const CURRENT=31,KEY='mona-release-v28',HOME='/discrete-math/',POLL=120000;
 let latest=null,inFlight=null,lastError='',dialog=null,banner=null,previousFocus=null;
 const listeners=new Set();
 function read(){try{return JSON.parse(localStorage.getItem(KEY)||'{}')}catch{return {}}}
 function write(patch){const next={...read(),...patch};try{localStorage.setItem(KEY,JSON.stringify(next))}catch{}return next}
 function safeDownload(value){try{const u=new URL(value);return u.protocol==='https:'&&u.hostname==='mona1207.github.io'&&!u.username&&!u.password&&(!u.port||u.port==='443')&&u.pathname.startsWith('/discrete-math/download/')&&u.pathname.endsWith('.apk')?u.href:null}catch{return null}}
 function valid(data){if(!data||!Number.isSafeInteger(data.web_version)||data.web_version<1)throw Error('版本信息不完整，请稍后重试。');return {...data,release_notes:Array.isArray(data.release_notes)?data.release_notes.filter(n=>typeof n==='string').slice(0,12):[],android:data.android&&typeof data.android==='object'?data.android:null}}
 function nativeInfo(){let name='',code=0;try{name=window.MonaApp?.getVersionName?.()||'';code=Number(window.MonaApp?.getVersionCode?.())||0}catch{}const match=navigator.userAgent.match(/MonaStudy\/([\d.]+)/);return {native:!!window.MonaApp||!!match,name:name||match?.[1]||'',code}}
 function newerName(offered,installed){const a=String(offered||'').split('.').map(Number),b=String(installed||'').split('.').map(Number);if(!installed||a.some(n=>!Number.isFinite(n)))return false;for(let i=0;i<Math.max(a.length,b.length);i++){if((a[i]||0)!==(b[i]||0))return (a[i]||0)>(b[i]||0)}return false}
 function state(){const n=nativeInfo(),a=latest?.android;return {current:CURRENT,latest,checking:!!inFlight,error:lastError,native:n.native,nativeName:n.name,webUpdate:!!latest&&latest.web_version>CURRENT,appUpdate:!!(n.native&&a&&(n.code?Number(a.version_code)>n.code:newerName(a.version_name,n.name))&&safeDownload(a.download_url)),unread:!!latest&&(Number(read().seenWeb)||0)<latest.web_version,automatic:read().automatic!==false}}
 function node(tag,attrs={},...children){const el=document.createElement(tag);for(const [key,value]of Object.entries(attrs)){if(key==='class')el.className=value;else if(key.startsWith('on')&&typeof value==='function')el.addEventListener(key.slice(2),value);else if(value!==undefined&&value!==null)el.setAttribute(key,String(value))}for(const item of children.flat())if(item!==null&&item!==false&&item!==undefined)el.append(typeof item==='string'?document.createTextNode(item):item);return el}
 function button(text,action,klass='',id=''){return node('button',{type:'button',class:klass,'data-action':id,onclick:action},text)}
 function announce(){const s=state();document.querySelectorAll('.v28-update-button').forEach(b=>b.classList.toggle('has-update',s.webUpdate||s.appUpdate||s.unread));if(dialog?.open)renderDialog();renderBanner();listeners.forEach(fn=>fn(s))}
 async function check(manual=false){if(inFlight)return inFlight;lastError='';const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),12000);
  inFlight=(async()=>{try{const response=await fetch(HOME+'version.json?t='+Date.now(),{cache:'no-store',signal:controller.signal});if(!response.ok)throw Error('HTTP '+response.status);latest=valid(await response.json());lastError='';}catch(error){lastError='暂时无法连接更新服务，请检查网络后重试。';}finally{clearTimeout(timeout);inFlight=null;announce()}return state()})();announce();return inFlight;
 }
 function markRead(){if(latest)write({seenWeb:latest.web_version});if(banner){banner.remove();banner=null}announce()}
 function snooze(){write({snoozeUntil:Date.now()+86400000,seenWeb:latest?.web_version||CURRENT});if(banner){banner.remove();banner=null}announce()}
 function close(){dialog?.close();previousFocus?.isConnected&&previousFocus.focus({preventScroll:true})}
 async function applyWeb(){if(!latest||latest.web_version<=CURRENT)return;const active=dialog?.querySelector('[data-action="apply"]');if(active){active.disabled=true;active.textContent='正在保存草稿…'}try{await window.monaPrepareUpdate?.();const u=new URL(location.href);u.searchParams.set('v',String(latest.web_version));location.replace(u.href)}catch{lastError='草稿尚未保存，已为你保留当前页面。请稍后再更新。';renderDialog()}}
 async function downloadApp(){const url=safeDownload(latest?.android?.download_url);if(!url)return;try{await window.monaPrepareUpdate?.();if(window.MonaApp?.openUpdateDownload)window.MonaApp.openUpdateDownload(url);else location.assign(url)}catch{lastError='草稿尚未保存，请稍后再下载更新。';renderDialog()}}
 function renderBanner(){const s=state(),prefs=read();if(dialog?.open||!s.latest||!s.automatic||Date.now()<(prefs.snoozeUntil||0)||(!s.webUpdate&&!s.appUpdate&&!s.unread)){if(banner){banner.remove();banner=null}return}
  const title=s.appUpdate?'App '+s.latest.android.version_name+' 已可更新':s.webUpdate?'新版本 '+(s.latest.web_name||'v'+s.latest.web_version)+' 已就绪':'学习界面已更新至 '+(s.latest.web_name||'v'+s.latest.web_version);
  const stamp=JSON.stringify([title,s.latest.release_notes[0]]);if(banner?.dataset.stamp===stamp)return;if(banner)banner.remove();
  banner=node('aside',{class:'v28-update-banner',role:'status','aria-label':'版本更新消息'},node('strong',{},title),node('p',{},s.latest.release_notes[0]||'查看本次更新内容。'),button('查看更新',open,'','view'),button('稍后提醒',snooze,'v28-banner-later','later'));banner.dataset.stamp=stamp;document.body.append(banner);
 }
 function renderDialog(){if(!dialog)return;const active=document.activeElement?.getAttribute('data-action'),s=state(),d=s.latest,hasUpdate=s.webUpdate||s.appUpdate;
  const title=node('header',{class:'v28-release-head'},node('img',{src:HOME+'assets/avatars-v26/settings.webp',alt:'蒙娜丽莎整理设置',width:48,height:48}),node('div',{},node('h2',{id:'mona-release-title'},'版本与更新'),node('p',{},'网页 v'+CURRENT+(s.nativeName?' · Android '+s.nativeName:''))),button('关闭',close,'v28-release-close','close'));
  const status=s.checking?'正在检查新版本…':s.error?'检查未完成':!d?'检查后显示版本状态':hasUpdate?'有新版本可用':(d.web_version<CURRENT?'当前版本领先于发布通道':'当前已是最新版本');
  const content=node('div',{class:'v28-release-content'},node('div',{class:'v28-release-status',role:'status','aria-live':'polite'},status));
  if(d){content.append(node('section',{},node('h3',{},d.release_title||'本次更新'),node('ul',{},(d.release_notes.length?d.release_notes:['学习体验与稳定性改进。']).map(note=>node('li',{},note)))));content.append(node('p',{class:'v28-release-meta'},(d.web_name||'v'+d.web_version)+' · '+(d.updated_at||'')+(d.android?'\nAndroid '+d.android.version_name+' · '+((d.android.size_bytes||0)/1024).toFixed(0)+' KB':'')));}
  const toggle=node('input',{type:'checkbox','aria-label':'自动接收应用内更新提醒'});toggle.checked=s.automatic;toggle.addEventListener('change',()=>{write({automatic:toggle.checked});announce()});content.append(node('label',{class:'v28-release-preference'},node('span',{},'应用内更新提醒',node('small',{},'打开应用或回到前台时检查，稍后提醒会静音24小时。')),toggle));
  if(s.error)content.append(node('p',{class:'v28-release-error',role:'alert'},s.error));
  const actions=node('footer',{class:'v28-release-actions'},button('稍后提醒',()=>{snooze();close()},'','later'),button(s.checking?'正在检查…':'重新检查',()=>check(true),'','check'));
  if(s.webUpdate)actions.append(button('保存草稿并更新',applyWeb,'v28-primary','apply'));else if(s.appUpdate)actions.append(button('下载 App '+d.android.version_name,downloadApp,'v28-primary','download'));else if(!s.native&&d?.android)actions.append(node('a',{href:HOME+'download/',class:'v28-primary'},'Android 下载'));
  dialog.replaceChildren(title,content,actions);if(s.checking)dialog.querySelector('[data-action="check"]').disabled=true;if(active)dialog.querySelector('[data-action="'+active+'"]')?.focus({preventScroll:true});
 }
 function open(){previousFocus=document.activeElement;if(!dialog){dialog=node('dialog',{class:'v28-release-dialog','aria-labelledby':'mona-release-title'});dialog.addEventListener('cancel',event=>{event.preventDefault();close();markRead()});dialog.addEventListener('close',()=>previousFocus?.isConnected&&previousFocus.focus({preventScroll:true}));document.body.append(dialog)}renderDialog();if(!dialog.open)dialog.showModal();markRead();check(true)}
 function mount(){const header=document.querySelector('.v18-app-header');if(header){const control=header.querySelector('.v28-update-button')||button('版本更新',open,'v28-update-button','updates');if(header.lastElementChild!==control)header.append(control);}}
 document.documentElement.dataset.uiRevision=String(CURRENT);document.addEventListener('DOMContentLoaded',mount);const observer=new MutationObserver(mount);observer.observe(document.getElementById('root')||document.body,{childList:true,subtree:true});mount();
 window.addEventListener('mona-check-update',open);window.addEventListener('mona-native-release',()=>{check(false)});document.addEventListener('visibilitychange',()=>{if(!document.hidden)check()});window.addEventListener('focus',()=>check());window.addEventListener('online',()=>check());
 setTimeout(()=>check(),5000);setInterval(()=>{if(!document.hidden)check()},POLL);
 window.MonaUpdates={check,open,state,subscribe(fn){listeners.add(fn);return()=>listeners.delete(fn)}};
 window.MonaReleasePolicy=Object.freeze({safeDownload,valid,newerName});
})();
