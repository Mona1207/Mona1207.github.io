// Brand, precise selection and a textbook hierarchy rendered as a real node map.
const V24_BRAND='莫那刷题站·全面升级版';
const V24_LOGO='/discrete-math/assets/mona-avatar-v24.webp';
function V24Logo({large=false}){return v10('img',{className:'v24-logo'+(large?' v24-logo-large':''),src:V24_LOGO,alt:'蒙娜丽莎微笑头像',width:large?64:26,height:large?64:26,draggable:false})}
function V24ModuleTitle({title,tag='h2',id}){return v10('div',{className:'v24-module-title'},e.jsx(V24Logo,{}),v10(tag,{id},title))}
function v24Roots(s){return s.chapters.filter(c=>!c.parent_id).sort((a,b)=>(a.order||0)-(b.order||0))}
function v24FilterQuestions(s,items,records,filter){
 const q=(filter.query||'').trim().toLowerCase();
 return v20PracticeItems(items).filter(i=>(filter.chapter==='all'||De(s,i.section_id||i.knowledge_ids?.[0])?.id===filter.chapter)&&(filter.point==='all'||i.knowledge_ids?.includes(filter.point))&&(filter.kind==='mixed'||(filter.kind==='examples')===(i.kind==='example'))&&(filter.status!=='star'||records[i.id]?.star)&&(filter.status!=='new'||!v18Done(records[i.id]))&&(!q||(i.title+' '+(i.source_label||'')+' '+i.knowledge_ids.map(id=>s.knowledge.find(k=>k.id===id)?.title||'').join(' ')).toLowerCase().includes(q)));
}
async function v24ChooseQuestion({book,item,list,pick,close}){
 // Flush the mounted notebook before replacing its route. A failed save keeps it open.
 await v20FlushInk();v20SetSequence(book,list);close?.();pick(item.id,'replace');
}
function V24QuestionMenu({state:s,items,records,current,pick,close}){
 const [filter,setFilter]=m.useState({chapter:'all',point:'all',kind:'mixed',status:'all',query:''}),[error,setError]=m.useState(''),[busy,setBusy]=m.useState(false),dialog=m.useRef(null),lock=m.useRef(false),book=s.settings.current_book;
 const list=v24FilterQuestions(s,items,records,filter),points=s.knowledge.filter(k=>filter.chapter==='all'||De(s,k.id)?.id===filter.chapter);
 m.useEffect(()=>{const el=dialog.current,previous=document.activeElement;el?.showModal();return()=>{el?.close();previous?.focus?.()}},[]);
 function change(patch){setFilter(old=>({...old,...patch}));setError('')}
 async function choose(item){if(lock.current)return;lock.current=true;setBusy(true);try{await v24ChooseQuestion({book,item,list,pick,close})}catch(err){setError('草稿保存未完成，请重试：'+err.message)}finally{lock.current=false;setBusy(false)}}
 return v10('dialog',{className:'v24-question-menu',ref:dialog,'aria-labelledby':'v24-menu-title',onCancel:ev=>{ev.preventDefault();if(!lock.current)close()},onClick:ev=>{if(ev.target===ev.currentTarget&&!lock.current)close()}},
  v10('div',{className:'v24-menu-inner'},v10('header',{className:'v24-menu-heading'},e.jsx(V24ModuleTitle,{title:'精确选题',tag:'h2',id:'v24-menu-title'}),v10('button',{className:'quiet','aria-label':'关闭选题菜单',disabled:busy,onClick:close},'关闭')),
   v10('p',{className:'caption'},'按章节、知识点或原题号直接跳转'),
   v10('label',{className:'search-field'},e.jsx(xe,{size:14}),v10('input',{autoFocus:true,'aria-label':'选题菜单搜索',placeholder:'题号 / 知识点，例如 9-15',value:filter.query,onChange:ev=>change({query:ev.target.value})})),
   v10('div',{className:'v24-menu-filters'},v10('label',{},'章节',v10('select',{'aria-label':'选题菜单章节',value:filter.chapter,onChange:ev=>change({chapter:ev.target.value,point:'all'})},v10('option',{value:'all'},'全部章节'),v24Roots(s).map(c=>v10('option',{key:c.id,value:c.id},c.title)))),
    v10('label',{},'知识点',v10('select',{'aria-label':'选题菜单知识点',value:filter.point,onChange:ev=>change({point:ev.target.value})},v10('option',{value:'all'},'全部知识点'),points.map(k=>v10('option',{key:k.id,value:k.id},k.title)))),
    v10('label',{},'类型',v10('select',{'aria-label':'选题菜单类型',value:filter.kind,onChange:ev=>change({kind:ev.target.value})},(book==='PHYS'?[['mixed','精选习题']]:[['mixed','例题 + 习题'],['examples','课本例题'],['exercises','课后习题']]).map(([id,title])=>v10('option',{key:id,value:id},title)))),
    v10('label',{},'进度',v10('select',{'aria-label':'选题菜单进度',value:filter.status,onChange:ev=>change({status:ev.target.value})},[['all','全部题目'],['new','尚未自评'],['star','星标题目']].map(([id,title])=>v10('option',{key:id,value:id},title))))),
   v10('div',{className:'v24-menu-count'},v10('small',{},list.length+' 道题'),v10('button',{className:'text-button',onClick:()=>change({chapter:'all',point:'all',kind:'mixed',status:'all',query:''})},'清除筛选')),
   error&&v10('p',{className:'error-banner',role:'alert'},error),
   v10('div',{className:'v24-menu-list','aria-busy':busy},list.map(i=>v10('button',{key:i.id,className:'v24-menu-question','aria-current':i.id===current?'true':undefined,disabled:busy,onClick:()=>choose(i)},v10('div',{},v10('b',{},i.title),i.id===current&&v10('span',{className:'v24-current-label'},'当前题')),v10('small',{},v20ChapterLabel(s,i.id,items)),e.jsx(V23QuestionBadges,{item:i}),v10('small',{},records[i.id]?.star?'★ 已星标':v18Done(records[i.id])?'已自评':'尚未自评'))),!list.length&&v10('p',{className:'v18-empty'},'没有匹配题目，试试清除筛选。')),
   v10('footer',{},'切换题目会先保存当前草稿')));
}
function v24PenWidth(n){const value=Number(n);return Number.isFinite(value)?Math.round(Math.max(.5,Math.min(20,value))*10)/10:2}
function v24ReadPen(){try{return v24PenWidth(JSON.parse(localStorage.getItem('mona-pen-v24')||'{}').width??2)}catch{return 2}}
function v24SavePen(width){try{localStorage.setItem('mona-pen-v24',JSON.stringify({width:v24PenWidth(width)}))}catch{}}
function V24WidthControl({value,onChange,color}){
 const [open,setOpen]=m.useState(false),dialog=m.useRef(null);
 m.useEffect(()=>{if(!open)return;const el=dialog.current,previous=document.activeElement;el?.showModal();return()=>{el?.close();previous?.focus?.()}},[open]);
 function change(n){onChange(v24PenWidth(n))}
 return v10('div',{className:'v24-width-control'},v10('div',{className:'v24-width-presets'},[1,2,4].map(n=>v10('button',{key:n,'aria-label':'笔粗细 '+n+' px','aria-pressed':Math.abs(value-n)<.05,title:n+' px',onClick:()=>change(n)},v10('i',{style:{height:n+'px',background:color}})))),
  v10('button',{className:'v24-width-toggle','aria-label':'精细调节笔粗细','aria-haspopup':'dialog',onClick:()=>setOpen(true)},value.toFixed(1)+' px'),
  open&&v10('dialog',{className:'v24-width-dialog',ref:dialog,'aria-labelledby':'v24-width-title',onCancel:ev=>{ev.preventDefault();setOpen(false)},onClick:ev=>{if(ev.target===ev.currentTarget)setOpen(false)}},v10('div',{className:'v24-width-inner'},v10('header',{},v10('h2',{id:'v24-width-title'},'笔迹粗细'),v10('button',{className:'quiet',onClick:()=>setOpen(false)},'完成')),
   v10('div',{className:'v24-width-preview','aria-label':'笔迹粗细预览'},v10('i',{style:{height:value+'px',background:color}})),
   v10('div',{className:'v24-width-number'},v10('button',{'aria-label':'笔粗细减少 0.1 px',disabled:value<=.5,onClick:()=>change(value-.1)},'−'),v10('label',{},v10('input',{type:'number',min:.5,max:20,step:.1,value,'aria-label':'笔粗细数值',onChange:ev=>{if(ev.target.value!=='')change(ev.target.value)}}),' px'),v10('button',{'aria-label':'笔粗细增加 0.1 px',disabled:value>=20,onClick:()=>change(value+.1)},'+')),
   v10('input',{type:'range',min:.5,max:20,step:.1,value,'aria-label':'笔迹大小',onChange:ev=>change(ev.target.value)}),
   v10('div',{className:'v24-width-choices'},[.5,1,1.5,2,3,4,6,8].map(n=>v10('button',{key:n,'aria-pressed':Math.abs(value-n)<.05,onClick:()=>change(n)},n+' px'))),v10('small',{},'0.5–20 px · 每次微调 0.1 px · 自动记住上次粗细'))));
}
function V24ConceptLauncher({state:s,items,pick}){
 const [chapter,setChapter]=m.useState('all'),[point,setPoint]=m.useState(''),points=s.knowledge.filter(k=>chapter==='all'||De(s,k.id)?.id===chapter),current=points.find(k=>k.id===point)||points[0];
 return v10('article',{className:'v24-concept-launcher'},e.jsx(V24ModuleTitle,{title:'知识点讲解'}),v10('p',{},'围绕教材梳理概念、条件、方法与易错点。'),v10('label',{},'章节',v10('select',{value:chapter,'aria-label':'知识讲解章节',onChange:ev=>{setChapter(ev.target.value);setPoint('')}},v10('option',{value:'all'},'全部章节'),v24Roots(s).map(c=>v10('option',{key:c.id,value:c.id},c.title)))),v10('label',{},'知识点',v10('select',{value:current?.id||'','aria-label':'选择知识点讲解',onChange:ev=>setPoint(ev.target.value)},points.map(k=>v10('option',{key:k.id,value:k.id},k.title)))),current&&v10('div',{className:'v24-concept-preview'},v10('b',{},current.title),e.jsx(V23ScopeBadges,{items:v20PracticeItems(items).filter(i=>i.knowledge_ids.includes(current.id))}),v10('p',{},String(current.content?.plain||current.content?.definition||'').replace(/\$[^$]+\$/g,'').slice(0,110))),v10('button',{className:'primary',disabled:!current,onClick:()=>pick(current.id,'concept')},'查看知识讲解'));
}
function V18Home({state:s,items,records,go,pick}){
 const all=v20PracticeItems(items),book=s.settings.current_book,last=all.filter(i=>records[i.id]?.last_opened_at||records[i.id]?.answer||records[i.id]?.shown).sort((a,b)=>(records[b.id].last_opened_at||records[b.id].updated_at||'').localeCompare(records[a.id].last_opened_at||records[a.id].updated_at||''))[0],next=last||all[0],progress=v18Progress(all,records);
 function resume(){if(!next)return;v20SetSequence(book,all);pick(next.id)}
 return v10('section',{className:'v24-home'},v10('header',{className:'v24-home-heading'},e.jsx(V24Logo,{large:true}),v10('div',{},v10('small',{},'当前教材'),v10('h1',{},v14Book(s).title)),v10('button',{className:'quiet',onClick:()=>go('books')},'切换教材')),
  v10('section',{className:'v24-continue'},v10('div',{},e.jsx(V24ModuleTitle,{title:'从上次的题开始练'}),v10('h2',{},last?.title||(book==='PHYS'?'从第一道精选题开始':'从第一道题开始')),next&&e.jsx(V23QuestionBadges,{item:next}),v10('p',{},last?v20ChapterLabel(s,last.id,items):'选择一道题，开始今天的练习。')),v10('div',{className:'v24-continue-actions'},v10('button',{className:'primary',disabled:!next,onClick:resume},last?'继续练习 →':'开始第一题 →'),v10('small',{},'草稿与学习进度按教材保存'))),
  v10('div',{className:'v24-home-workspace'},e.jsx(V24PracticeBrowser,{state:s,items,records,pick}),e.jsx(V24ConceptLauncher,{state:s,items,pick})),
  v10('div',{className:'v18-home-stats'},[[progress.done,'已自评题目'],[all.length,book==='PHYS'?'精选习题':'课本例题与习题'],[all.filter(i=>records[i.id]?.star).length,'星标题目']].map(([value,title])=>v10('div',{key:title},v10('b',{},value),v10('small',{},title)))),
  v10('nav',{className:'v18-home-links'},[['graph','知识思维导图'],['bookmarks','星标习题'],['notes','笔记汇总'],['reports','学习进度']].map(([id,title])=>v10('button',{key:id,className:'quiet',onClick:()=>go(id)},title,e.jsx(S,{size:12})))));
}
function v24MapTree(s,focus='all',query=''){
 const seen=new Set(),q=query.trim().toLowerCase();
 function branch(c){if(seen.has(c.id))return null;seen.add(c.id);return {id:c.id,title:c.title,type:c.parent_id?'section':'chapter',data:c,children:[...s.chapters.filter(x=>x.parent_id===c.id).sort((a,b)=>(a.order||0)-(b.order||0)).map(branch).filter(Boolean),...s.knowledge.filter(k=>k.chapter_id===c.id).map(k=>({id:k.id,title:k.title,type:'knowledge',data:k,children:[]}))]}}
 function prune(node,inherited=false){const match=inherited||node.title.toLowerCase().includes(q),children=node.children.map(c=>prune(c,match)).filter(Boolean);return match||children.length?{...node,children}:null}
 const children=v24Roots(s).filter(c=>focus==='all'||c.id===focus).map(branch).map(n=>q?prune(n):n).filter(Boolean);
 return {id:'v24-book',title:v14Book(s).title,type:'book',children};
}
function v24MapLayout(tree,collapsed=new Set()){
 const nodes=[],edges=[],gap=26,widths=[210,226,210,264],xs=[24,310,612,900];let maxDepth=0;
 function measure(node,depth){const children=collapsed.has(node.id)?[]:node.children;node={...node,depth,visibleChildren:children.map(c=>measure(c,depth+1)),w:widths[Math.min(depth,3)],h:node.type==='knowledge'?132:112};node.span=Math.max(node.h,node.visibleChildren.reduce((n,c)=>n+c.span,0)+Math.max(0,node.visibleChildren.length-1)*gap);return node}
 function place(node,top,parent){const depth=node.depth;maxDepth=Math.max(depth,maxDepth);const n={...node,x:xs[Math.min(depth,3)]+Math.max(0,depth-3)*310,y:top+(node.span-node.h)/2};nodes.push(n);if(parent)edges.push({source:parent,target:n});let y=top+(node.span-(node.visibleChildren.reduce((n,c)=>n+c.span,0)+Math.max(0,node.visibleChildren.length-1)*gap))/2;for(const c of node.visibleChildren){place(c,y,n);y+=c.span+gap}}
 const root=measure(tree,0);place(root,24,null);return {nodes,edges,width:xs[Math.min(maxDepth,3)]+Math.max(0,maxDepth-3)*310+widths[Math.min(maxDepth,3)]+32,height:root.span+48};
}
function V18Tree({state:s,items,records,pick}){
 const book=s.settings.current_book,roots=v24Roots(s),[focus,setFocus]=m.useState(roots[0]?.id||'all'),[query,setQuery]=m.useState(''),[collapsed,setCollapsed]=m.useState(new Set()),[selected,setSelected]=m.useState(''),[zoom,setZoom]=m.useState(.8),viewport=m.useRef(null),drag=m.useRef(null),all=v20PracticeItems(items),tree=v24MapTree(s,query?'all':focus,query),layout=v24MapLayout(tree,query?new Set():collapsed),point=s.knowledge.find(k=>k.id===selected),related=point?all.filter(i=>i.knowledge_ids.includes(point.id)):[];
 m.useEffect(()=>{const el=viewport.current;if(el){setZoom(Math.min(1,Math.max(.35,(el.clientWidth-24)/layout.width)));el.scrollTop=0;el.scrollLeft=0}},[focus,book]);
 function toggle(n){if(n.type==='knowledge'){setSelected(n.id);return}if(n.type==='book'){setFocus('all');setCollapsed(new Set(roots.map(c=>c.id)));return}setCollapsed(old=>{const next=new Set(old);next.has(n.id)?next.delete(n.id):next.add(n.id);return next})}
 function changeZoom(value){const next=Math.max(.35,Math.min(1.8,value)),el=viewport.current,ratio=next/zoom,x=el?(el.scrollLeft+el.clientWidth/2)*ratio-el.clientWidth/2:0,y=el?(el.scrollTop+el.clientHeight/2)*ratio-el.clientHeight/2:0;setZoom(next);requestAnimationFrame(()=>{if(el){el.scrollLeft=x;el.scrollTop=y}})}
 function down(ev){if(ev.pointerType==='touch'||ev.button!==0||ev.target.closest?.('button'))return;drag.current={x:ev.clientX,y:ev.clientY,left:ev.currentTarget.scrollLeft,top:ev.currentTarget.scrollTop};ev.currentTarget.setPointerCapture?.(ev.pointerId)}
 function move(ev){if(!drag.current)return;ev.currentTarget.scrollLeft=drag.current.left-(ev.clientX-drag.current.x);ev.currentTarget.scrollTop=drag.current.top-(ev.clientY-drag.current.y)}
 return v10('section',{className:'v24-map-page'},v10('header',{className:'v18-compact-heading'},e.jsx(V24ModuleTitle,{title:'知识思维导图',tag:'h1'}),v10('label',{className:'search-field'},e.jsx(xe,{size:14}),v10('input',{'aria-label':'搜索思维导图',placeholder:'搜索章节 / 知识点',value:query,onChange:ev=>{setQuery(ev.target.value);setSelected('')}}))),
  v10('div',{className:'v24-map-toolbar'},v10('select',{'aria-label':'思维导图章节',value:focus,onChange:ev=>{setFocus(ev.target.value);setQuery('');setSelected('');setCollapsed(ev.target.value==='all'?new Set(roots.map(c=>c.id)):new Set())}},v10('option',{value:'all'},'全书总览'),roots.map(c=>v10('option',{key:c.id,value:c.id},c.title))),v10('button',{className:'quiet',onClick:()=>setCollapsed(new Set())},'展开全部'),v10('button',{className:'quiet',onClick:()=>setCollapsed(new Set(tree.children.map(c=>c.id)))},'收起分支'),v10('div',{className:'v24-map-zoom'},v10('button',{'aria-label':'缩小脑图',onClick:()=>changeZoom(zoom-.1)},'−'),v10('span',{},Math.round(zoom*100)+'%'),v10('button',{'aria-label':'放大脑图',onClick:()=>changeZoom(zoom+.1)},'+'),v10('button',{onClick:()=>{changeZoom(Math.min(1,(viewport.current?.clientWidth-24)/layout.width))}},'适合宽度'))),
  v10('small',{className:'v24-map-hint'},'实线表示教材从属关系：教材 → 章 → 节 → 知识点。点击分支展开或收起，点击知识点选题；拖动空白或滚动查看。'),
  v10('div',{className:'v24-map-body'+(point?' has-detail':'')},v10('div',{className:'v24-map-viewport',ref:viewport,tabIndex:0,'aria-label':'教材知识结构脑图，可滚动或拖动查看',onPointerDown:down,onPointerMove:move,onPointerUp:()=>{drag.current=null},onPointerCancel:()=>{drag.current=null}},v10('div',{style:{width:layout.width*zoom,height:layout.height*zoom},className:'v24-map-scroll-size'},v10('div',{className:'v24-map-canvas',style:{width:layout.width,height:layout.height,transform:'scale('+zoom+')'}},
   v10('svg',{className:'v24-map-edges',width:layout.width,height:layout.height,'aria-hidden':true},layout.edges.map(({source:a,target:b})=>{const x=a.x+a.w,y=a.y+a.h/2,xx=b.x,yy=b.y+b.h/2;return v10('path',{key:a.id+'-'+b.id,d:'M '+x+' '+y+' C '+(x+(xx-x)/2)+' '+y+', '+(x+(xx-x)/2)+' '+yy+', '+xx+' '+yy,fill:'none',stroke:'currentColor',strokeWidth:2})})),
   layout.nodes.map(n=>{const scope=n.type==='knowledge'?all.filter(i=>i.knowledge_ids.includes(n.id)):n.type==='book'?all:v18Scope(all,s,n.id);return v10('button',{key:n.id,className:'v24-map-node v24-node-'+n.type+(selected===n.id?' selected':''),style:{left:n.x,top:n.y,width:n.w,height:n.h},'aria-expanded':n.children.length?!collapsed.has(n.id):undefined,'aria-pressed':n.type==='knowledge'?selected===n.id:undefined,onClick:()=>toggle(n)},v10('small',{},n.type==='book'?'当前教材':n.type==='chapter'?'章':n.type==='section'?'节':'知识点'),v10('b',{},n.title),n.type!=='book'&&e.jsx(V23ScopeBadges,{items:scope}),n.children.length>0&&v10('span',{className:'v24-node-toggle','aria-hidden':true},collapsed.has(n.id)?'+':'−'))})))),
   point&&v10('aside',{className:'v24-map-detail'},v10('header',{},e.jsx(V24ModuleTitle,{title:point.title}),v10('button',{className:'quiet','aria-label':'关闭知识点详情',onClick:()=>setSelected('')},'关闭')),e.jsx(V23ScopeBadges,{items:related}),e.jsx(V18Battery,{items:related,records,label:point.title+'学习进度'}),v10('button',{className:'primary',onClick:()=>pick(point.id,'concept')},'知识点讲解'),v10('button',{className:'quiet',disabled:!related.length,onClick:()=>pick(point.id)},'打开全部关联题目（'+related.length+'）'),e.jsx(V18Prerequisites,{state:s,id:point.id,pick:id=>{const k=s.knowledge.find(k=>k.id===id);if(k){setSelected(id);setFocus(De(s,id)?.id||'all');setCollapsed(new Set())}}}),v10('div',{className:'v24-map-question-list'},related.map(i=>v10('button',{key:i.id,onClick:()=>{v20SetSequence(book,related);pick(i.id)}},v10('b',{},i.title),e.jsx(V23QuestionBadges,{item:i}))),!related.length&&v10('p',{},'此知识点暂无关联单题。')))),
  e.jsx(V23RatingGuide,{}));
}
