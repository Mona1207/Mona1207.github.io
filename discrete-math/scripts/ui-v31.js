function v31FilterGroups(children){
 const groups=[];
 function walk(node){if(Array.isArray(node)){node.forEach(walk);return}if(!node||typeof node!=='object')return;
  if(node.type===V25RatingFilters){walk(V25RatingFilters(node.props));return}
  if(node.type===V25Select){const p=node.props,options=v25Options(p.children);if(!options.length)return;groups.push({label:(p['aria-label']||p.title||'选择范围').replace(/首页习题|选题菜单|知识讲解|思维导图|筛选/g,'').replace(/^题目/,''),value:String(p.value??p.defaultValue??options[0]?.value??''),options,onSelect:value=>p.onChange?.({target:{value,name:p.name},currentTarget:{value,name:p.name}})});return}
  walk(node.props?.children);
 }
 walk(children);return groups;
}
function V31FilterBar({children,title='统一筛选'}){
 const groups=v31FilterGroups(children),[open,setOpen]=m.useState(false),[query,setQuery]=m.useState(''),panel=m.useRef(null),trigger=m.useRef(null),[uid]=m.useState(()=> 'mona-filter-v31-'+(++v25SelectId)),supports=typeof HTMLElement!=='undefined'&&typeof HTMLElement.prototype.showPopover==='function';
 function close(focus=false){const el=panel.current;try{if(el){if(supports&&el.matches(':popover-open'))el.hidePopover();else if(!supports&&el.open)el.close()}}catch{}setOpen(false);if(focus)trigger.current?.focus({preventScroll:true})}
 m.useEffect(()=>{if(!open)return;const el=panel.current;if(!el)return;
  function position(){const r=trigger.current?.getBoundingClientRect();if(!r)return;const w=Math.min(820,window.innerWidth-24),h=Math.min(610,window.innerHeight-32),left=Math.max(12,Math.min(r.left,window.innerWidth-w-12)),top=Math.max(12,Math.min(r.bottom+7,window.innerHeight-h-12));Object.assign(el.style,{width:w+'px',maxHeight:h+'px',left:left+'px',top:top+'px'})}
  function outside(ev){if(!el.contains(ev.target)&&!trigger.current?.contains(ev.target))close()}
  function escape(ev){if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();close(true)}}
  function other(ev){if(ev.detail!==uid)close()}
  function back(ev){ev.preventDefault();close(true)}
  window.dispatchEvent(new CustomEvent('mona-select-open',{detail:uid}));position();try{supports?el.showPopover():el.showModal()}catch{}
  document.addEventListener('pointerdown',outside,true);document.addEventListener('keydown',escape,true);window.addEventListener('mona-select-open',other);window.addEventListener('mona-close-menu',back);window.addEventListener('resize',position);
  requestAnimationFrame(()=>el.querySelector('button[aria-pressed=true]')?.focus({preventScroll:true}));
  return()=>{try{if(supports&&el.matches(':popover-open'))el.hidePopover();else if(!supports&&el.open)el.close()}catch{}document.removeEventListener('pointerdown',outside,true);document.removeEventListener('keydown',escape,true);window.removeEventListener('mona-select-open',other);window.removeEventListener('mona-close-menu',back);window.removeEventListener('resize',position)};
 },[open]);
 function choose(group,option){if(option.disabled)return;close(true);group.onSelect(option.value)}
 const summary=groups.map(g=>g.options.find(o=>o.value===g.value)?.label).filter(Boolean),filtered=groups.map(g=>({...g,options:g.options.filter(o=>!query||(g.label+' '+o.label).toLowerCase().includes(query.toLowerCase().trim()))})).filter(g=>g.options.length);
 return v10('div',{className:'v31-filter-bar'},v10('button',{type:'button',className:'v31-filter-trigger',ref:trigger,'aria-label':title,'aria-haspopup':'dialog','aria-expanded':open,onClick:()=>{if(open)close(true);else{setQuery('');setOpen(true)}}},v10('span',{className:'v31-filter-icon','aria-hidden':true},'☷'),v10('span',{},v10('b',{},title),v10('small',{},summary.join(' · '))),v10('span',{'aria-hidden':true},'⌄')),
 open&&v10(supports?'div':'dialog',{ref:panel,popover:supports?'manual':undefined,id:uid,className:'v31-filter-panel',role:supports?'dialog':undefined,'aria-label':title+'面板',onCancel:ev=>{ev.preventDefault();close(true)}},v10('header',{},v10('div',{},v10('b',{},title),v10('small',{},'全部条件在此选择 · 选中即应用并收起')),v10('button',{className:'quiet','aria-label':'关闭'+title,onClick:()=>close(true)},'关闭')),v10('input',{className:'v31-filter-search','aria-label':'搜索筛选条件',placeholder:'搜索章节、知识点或筛选条件',value:query,onChange:ev=>setQuery(ev.target.value)}),v10('div',{className:'v31-filter-groups'},filtered.map((group,i)=>v10('section',{key:group.label+i},v10('h3',{},group.label),v10('div',{className:'v31-filter-options',role:'group','aria-label':group.label},group.options.map(option=>v10('button',{key:option.value,type:'button','aria-pressed':option.value===group.value,disabled:option.disabled,title:option.description||option.label,onClick:ev=>{ev.preventDefault();ev.stopPropagation();choose(group,option)}},v10('span',{},option.label),option.count!==undefined&&v10('small',{},option.count)))))),!filtered.length&&v10('p',{className:'v18-empty'},'没有匹配的筛选条件'))));
}
function V31OriginalQuestion({book,item}){
 const [failed,setFailed]=m.useState(false),[retry,setRetry]=m.useState(0),url=item.source_image_url||item.source?.source_image_url;
 if(url)return v10('div',{className:'v31-original-scroll'},!failed?v10('img',{key:retry,src:url+(retry?(url.includes('?')?'&':'?')+'retry='+retry:''),alt:item.title+'教材原图',onError:()=>setFailed(true)}):v10('div',{className:'v18-empty',role:'alert'},v10('p',{},'原图暂未加载，请重试。'),v10('button',{className:'quiet',onClick:()=>{setFailed(false);setRetry(n=>n+1)}},'重新加载原图')));
 if(item.segments?.length)return e.jsx(V15PageCrop,{book,segments:item.segments,label:item.title+'题干原图'});
 return v10('p',{className:'v18-empty'},'此题暂无可显示原图，请切回文字。');
}
function V31StudyTop({state:s,item,items,records,pick,fail}){
 const [menu,setMenu]=m.useState(false),book=s.settings.current_book,kind=item.kind==='example'?'examples':'exercises',sequence=v18StudySequence(items,kind,item.id,book),index=sequence.findIndex(i=>i.id===item.id);
 async function next(delta){const to=sequence[index+delta];if(!to)return;try{await v20FlushInk();pick(to.id,'replace')}catch(err){fail(err)}}
 return v10('div',{className:'v31-study-top'},v10('div',{className:'v31-question-meta'},v10('div',{},v10('b',{},item.title),e.jsx(V23QuestionBadges,{item}),e.jsx(V18Star,{book,item,records,fail})),v10('small',{},v20ChapterLabel(s,item.id,items)+' · '+(item.source_label||((item.printed_page?'教材第 '+item.printed_page+' 页 · ':'')+(kind==='examples'?'课本例题':'课后习题'))))),v10('div',{className:'v31-study-actions'},v10('button',{className:'v24-menu-trigger quiet','aria-haspopup':'dialog',onClick:()=>setMenu(true)},'精确选题'),v10('button',{className:'quiet','aria-label':'上一题',disabled:index<=0,onClick:()=>next(-1)},'‹'),v10('small',{},index>=0?index+1+' / '+sequence.length:''),v10('button',{className:'quiet','aria-label':'下一题',disabled:index<0||index>=sequence.length-1,onClick:()=>next(1)},'›')),menu&&e.jsx(V24QuestionMenu,{state:s,items,records,current:item.id,pick,close:()=>setMenu(false)}));
}
function V31Loading({error='',retry}){
 return v10('div',{className:'v31-launch',role:error?'alert':'status'},v10('div',{className:'v31-launch-glow','aria-hidden':true}),v10('div',{className:'v31-launch-portraits','aria-label':'蒙娜丽莎阅读不同教材'},['DM2T','LA7','PS3','PHYS'].map((book,i)=>v10('img',{key:book,src:'/discrete-math/assets/avatars-v26/'+book+'.webp',alt:['蒙娜丽莎阅读离散数学','蒙娜丽莎阅读线性代数','蒙娜丽莎阅读概率统计','蒙娜丽莎阅读物理学'][i],className:'v31-launch-reader',style:{'--reader':i}}))),v10('small',{className:'v31-launch-eyebrow'},'MONA STUDY'),v10('h1',{},'莫那刷题站'),v10('p',{className:'v31-launch-motto'},'从一道题，读懂一个知识点'),v10('div',{className:'v31-launch-status'},v10('span',{className:'v31-loading-dots','aria-hidden':true},v10('i',{}),v10('i',{}),v10('i',{})),v10('span',{},error||'正在读取教材与学习记录…')),error&&retry&&v10('button',{className:'quiet',onClick:retry},'重新加载'));
}
