function v26RouteKey(route){return [route.page,route.detail||'',route.source||''].join('|')}
function v26RootRoute(page='home'){return {page,detail:null,source:null}}
function v26IsRoot(route){return ['home','graph','settings'].includes(route.page)&&!route.detail&&!route.source}
function v26RouteFamily(route){if(route.source)return 'reader';if(v26IsRoot(route))return 'root';if(route.detail?.startsWith('SRC-'))return 'question';if(route.page==='concept')return 'concept';if(['examples','exercises'].includes(route.page))return 'listing';if(route.page==='practice')return 'practice';return 'utility'}
function v26Transition(current,target,trail=[],replace=false){
 const key=v26RouteKey(target),at=trail.findIndex(r=>v26RouteKey(r)===key);
 if(at>=0)return {action:'rewind',steps:trail.length-at,trail:trail.slice(0,at),route:target};
 const a=v26RouteFamily(current),b=v26RouteFamily(target),peers=a===b&&(['question','reader','concept','practice','utility'].includes(a)||a==='listing'&&(!!current.detail===!!target.detail));
 return {action:replace||peers?'replace':'push',trail:replace||peers?trail:[...trail,current],route:target};
}
function v26Fallback(route){if(route.source)return {...route,source:null};if(route.detail?.startsWith('SRC-'))return {page:route.page,detail:null,source:null};if(route.page==='concept')return v26RootRoute('graph');return v26RootRoute(['books','rules','account'].includes(route.page)?'settings':'home')}
function Cs(){
 const [route,setRoute]=m.useState(()=>{const r=de(),old=history.state;history.replaceState({zx:true,zxV26:true,zxTrail:old?.zxV26&&!v26IsRoot(r)?old.zxTrail||[]:[],zxScroll:0},'',te(r));return r}),[navError,setNavError]=m.useState(''),pending=m.useRef(null),locked=m.useRef(false);
 m.useEffect(()=>{function receive(){window.dispatchEvent(new Event('zhixu-flush-ink'));if(pending.current){const to=pending.current;pending.current=null;history.replaceState({zx:true,zxV26:true,zxTrail:to.trail,zxScroll:0},'',te(to.route))}locked.current=false;setRoute(de());requestAnimationFrame(()=>window.scrollTo({top:Number(history.state?.zxScroll)||0,behavior:'instant'}))}window.addEventListener('popstate',receive);window.addEventListener('hashchange',receive);return()=>{window.removeEventListener('popstate',receive);window.removeEventListener('hashchange',receive)}},[]);
 function write(target,trail,replace=true){history[replace?'replaceState':'pushState']({zx:true,zxV26:true,zxTrail:trail,zxScroll:0},'',te(target));setRoute(target);window.scrollTo({top:0,behavior:'instant'})}
 async function guard(fn){if(locked.current)return;locked.current=true;try{await v20FlushInk();setNavError('');fn()}catch(err){setNavError('草稿尚未保存，已留在当前页面。'+err.message)}finally{if(!pending.current)locked.current=false}}
 function root(page){if(!['home','graph','settings'].includes(page))return;const target=v26RootRoute(page),trail=history.state?.zxV26?history.state.zxTrail||[]:[];if(trail.length){pending.current={route:target,trail:[]};history.go(-trail.length)}else write(target,[],true)}
 function navigate(target,replace=false){return guard(()=>{if(v26RouteKey(de())===v26RouteKey(target))return;if(v26IsRoot(target)){root(target.page);return}const trail=history.state?.zxV26?history.state.zxTrail||[]:[],step=v26Transition(de(),target,trail,replace);if(step.action==='rewind'){pending.current=step;history.go(-step.steps)}else write(target,step.trail,step.action==='replace')})}
 function goRoot(page){return guard(()=>root(page))}
 function back(){return guard(()=>{const trail=history.state?.zxV26?history.state.zxTrail||[]:[];if(trail.length)history.back();else {const target=v26Fallback(de());if(v26RouteKey(target)!==v26RouteKey(de()))write(target,[],true)}})}
 return {route,navigate,goRoot,back,navError,clearNavError:()=>setNavError('')};
}
