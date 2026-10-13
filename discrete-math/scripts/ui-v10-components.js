// Readable UI source; embedded by build-ui-v10.py into the existing React bundle.
function v10(tag,props,...children){return e.jsxs(tag,{...props,children:children.flat().filter(x=>x!==null&&x!==false&&x!==undefined)});}
function v10Pick(id){window.location.hash='knowledge?node='+encodeURIComponent(id);}
function v10Practice(k){return k.practice||{distinct_count:0,practiced_count:0,new_count:0};}
function v10Status(k){const p=v10Practice(k);return !k.unlock.allowed?'需先学前置知识':p.new_count?`${p.new_count} 道不同考法`:p.distinct_count?'本轮考法已练完':'练习待补充';}
function v10PointRow(k,pick,index){const p=v10Practice(k);return v10('button',{className:'point-row',key:k.id,onClick:()=>pick(k.id)},v10('span',{className:'point-index'},String(index+1).padStart(2,'0')),v10('span',{className:'point-row-copy'},v10('b',{},k.title),v10('small',{},v10Status(k))),v10('span',{className:'point-state'},k.completed_questions?'已学':'待学'),e.jsx(S,{size:16}));}
function Es({state:s,report:t,active:a,go:o,start:n,resume:c,pick}){
 const candidates=s.knowledge.filter(k=>k.unlock.allowed&&v10Practice(k).new_count>0);
 const next=candidates.find(k=>k.completed_questions>0)||candidates[0];
 const current=a&&s.knowledge.find(k=>k.id===a.session.target_id);
 const studied=s.knowledge.filter(k=>k.completed_questions>0).length;
 const hero=current||next;const chosen=pick||v10Pick;
 return v10('div',{className:'v10-home'},
  v10('header',{className:'home-heading'},v10('div',{},v10('p',{className:'eyebrow'},'离散数学 · 个人学习空间'),v10('h1',{},'今天，学懂一点。'),v10('p',{className:'subtle'},'从一个知识点出发，把理解留在每一次练习里。')),v10('div',{className:'home-date'},v10('b',{},studied),v10('span',{},'/ '+s.knowledge.length+' 个知识点已开始'))),
  v10('section',{className:'home-focus'},
   v10('div',{className:'focus-main'},v10('span',{className:'eyebrow'},current?'接着上次的思路':'下一步 · 一个知识点'),v10('h2',{},hero?.title||'换一个角度，回顾所学'),v10('p',{},hero?.content?.plain||'已练过的同类题不会反复出现。到知识树看看，还有哪些概念值得探索。'),v10('div',{className:'focus-actions'},v10('button',{className:'primary',onClick:()=>current?c():hero?chosen(hero.id):o('graph')},current?'继续练习':hero?'学习这个知识点':'浏览知识树',e.jsx(D,{size:17})),v10('button',{className:'text-button',onClick:()=>o('workspace')},'换个知识点',e.jsx(S,{size:15})))),
   v10('div',{className:'focus-aside'},v10('div',{className:'study-orbit','aria-hidden':true},v10('span',{},'∴'),v10('i',{}),v10('i',{}),v10('i',{})),v10('b',{},hero?v10Status(hero):'理解，比刷题更重要'),v10('small',{},'每种考法只安排一次'))),
  v10('div',{className:'home-lower'},
   v10('section',{className:'point-suggestions'},v10('div',{className:'section-heading'},v10('h2',{},'可以从这里继续'),v10('button',{className:'text-button',onClick:()=>o('knowledge')},'全部知识点',e.jsx(S,{size:15}))),candidates.slice(0,4).map((k,i)=>v10PointRow(k,chosen,i)),!candidates.length&&v10('p',{className:'subtle'},'当前可学范围没有新的考法。可以查看知识树或复习错题。')),
   v10('aside',{className:'study-tools'},v10('h2',{},'你的学习手边'),[['wrong','错题回顾','回到还没想通的地方',ee],['notes','学习笔记','留下自己的理解',me],['reports','学习记录','看看每一步的积累',Ke]].map(([id,title,copy,Icon])=>v10('button',{key:id,onClick:()=>o(id)},v10('span',{className:'tool-icon'},e.jsx(Icon,{size:18})),v10('span',{},v10('b',{},title),v10('small',{},copy)),e.jsx(S,{size:15}))))));
}
function Ls({state:s,onStart:t,onPick:a,fail:o}){
 const [query,setQuery]=m.useState(''),[filter,setFilter]=m.useState('all'),[selected,setSelected]=m.useState(''),[busy,setBusy]=m.useState(false);
 const k=s.knowledge.find(x=>x.id===selected),p=k&&v10Practice(k);
 const list=s.knowledge.filter(k=>k.title.toLowerCase().includes(query.toLowerCase())&&(filter!=='ready'||k.unlock.allowed&&v10Practice(k).new_count>0));
 async function begin(){if(!k||busy)return;setBusy(true);try{const res=await z('/sessions','POST',{target_id:k.id,mode:'knowledge',question_count:Math.min(10,p.new_count)});sessionStorage.setItem('session-index-'+res.session.id,'0');t(res);}catch(err){o(err)}finally{setBusy(false)}}
 return v10('div',{className:'v10-directory'},v10('header',{className:'directory-heading'},v10('p',{className:'eyebrow'},'知识点练习'),v10('h2',{},'这次，想练什么？'),v10('p',{className:'subtle'},'按知识点选择。每种考法一道，已练过的同类变式自动跳过。')),
 v10('div',{className:'directory-toolbar'},v10('label',{className:'search-field'},e.jsx(xe,{size:17}),v10('input',{'aria-label':'搜索知识点',placeholder:'搜索知识点，如：真值、集合、树',value:query,onChange:ev=>setQuery(ev.target.value)})),v10('div',{className:'mini-segments','aria-label':'知识点筛选'},[['all','全部'],['ready','有新题可练']].map(([id,title])=>v10('button',{key:id,'aria-pressed':filter===id,onClick:()=>setFilter(id)},title)))),
 v10('div',{className:'picker-layout'},v10('section',{className:'point-picker','aria-label':'选择练习知识点'},list.map((x,i)=>v10('button',{key:x.id,className:'picker-point '+(selected===x.id?'selected':''),'aria-pressed':selected===x.id,onClick:()=>setSelected(x.id)},v10('span',{className:'choice-circle'},selected===x.id?e.jsx(J,{size:13}):String(i+1).padStart(2,'0')),v10('span',{},v10('b',{},x.title),v10('small',{},v10Status(x))),!x.unlock.allowed?e.jsx(he,{size:15}):e.jsx(S,{size:15}))),!list.length&&v10('div',{className:'empty'},'没有匹配的知识点，试试其他关键词或切换“全部”。')),
 v10('aside',{className:'practice-dock'},v10('span',{className:'eyebrow'},'本次练习'),v10('h3',{},k?.title||'先选一个知识点'),v10('p',{className:'subtle'},k?`${p.distinct_count} 种考法 · 已练 ${p.practiced_count} 种`:'题量由不同考法的数量决定，不用为了凑题数重复计算。'),k&&v10('div',{className:'practice-number'},Math.min(10,p.new_count),v10('small',{},'道新题')),
 k&&!k.unlock.allowed&&v10('p',{className:'dock-note'},'先补足前置知识，再回来练习。讲解随时可以阅读。'),k&&k.unlock.allowed&&!p.new_count&&v10('p',{className:'dock-note'},p.distinct_count?'这些考法已经练过了。可以换一个知识点，或在错题回顾中主动复习。':'这个知识点的练习还在补充，可以先阅读讲解。'),
 v10('button',{className:'primary',disabled:!k||!k.unlock.allowed||!p.new_count||busy,onClick:begin},busy?'正在准备…':'开始练习',e.jsx(D,{size:16})),k&&v10('button',{className:'text-button',onClick:()=>a(k.id)},'先看知识讲解',e.jsx(ee,{size:15})))));
}
function Hs({state:s,pick:t}){
 const [query,setQuery]=m.useState('');const list=s.knowledge.filter(k=>k.title.includes(query));
 return v10('div',{className:'v10-directory'},v10('header',{className:'directory-heading'},v10('p',{className:'eyebrow'},'学习目录'),v10('h2',{},'一个知识点，一次专注。'),v10('p',{className:'subtle'},'讲解、例子和练习，都在同一个地方。')),v10('label',{className:'search-field'},e.jsx(xe,{size:17}),v10('input',{'aria-label':'搜索知识点',placeholder:'搜索知识点',value:query,onChange:ev=>setQuery(ev.target.value)})),v10('section',{className:'knowledge-directory'},list.map((k,i)=>v10PointRow(k,t,i)),!list.length&&v10('p',{className:'empty'},'没有找到这个知识点。')));
}
function Ws(props){return e.jsx(Hs,props);}
function Bs(props){return e.jsx(Hs,props);}
function qs({state:s,onPick:t}){
 const [query,setQuery]=m.useState('');const [closed,setClosed]=m.useState(()=>{try{return new Set(JSON.parse(sessionStorage.getItem('tree-closed-'+s.settings.current_book))||s.chapters.filter(k=>!k.parent_id).slice(2).map(k=>k.id))}catch{return new Set()}});
 function toggle(id){setClosed(old=>{const n=new Set(old);n.has(id)?n.delete(id):n.add(id);sessionStorage.setItem('tree-closed-'+s.settings.current_book,JSON.stringify([...n]));return n})}
 const roots=s.chapters.filter(k=>!k.parent_id).map(ch=>({ch,points:s.knowledge.filter(k=>De(s,k.id)?.id===ch.id)})).filter(({ch,points})=>!query||ch.title.includes(query)||points.some(k=>k.title.includes(query)));
 return v10('section',{className:'v10-tree','aria-label':'教材知识树'},v10('header',{className:'directory-heading'},v10('p',{className:'eyebrow'},'从全貌，到每一个概念'),v10('h1',{},'知识树'),v10('p',{className:'subtle'},'章节是目录，知识点是学习的起点。')),v10('label',{className:'search-field'},e.jsx(xe,{size:17}),v10('input',{'aria-label':'搜索知识树',placeholder:'找一个知识点',value:query,onChange:ev=>setQuery(ev.target.value)})),v10('div',{className:'tree-sheet'},roots.map(({ch,points},i)=>{const open=!!query||!closed.has(ch.id);const visible=query&&!ch.title.includes(query)?points.filter(k=>k.title.includes(query)):points;return v10('section',{className:'tree-group',key:ch.id},v10('button',{className:'tree-group-header','aria-expanded':open,onClick:()=>toggle(ch.id)},e.jsx(open?ts:S,{size:16}),v10('b',{},ch.title),v10('small',{},points.length+' 个知识点')),open&&v10('div',{className:'tree-leaves'},visible.map(k=>v10('button',{key:k.id,className:'tree-leaf',onClick:()=>t(k.id)},v10('span',{className:'leaf-dot '+(k.completed_questions?'visited':'')}),v10('span',{},k.title),v10('small',{},!k.unlock.allowed?'前置待学':k.completed_questions?'学习中':'未开始'),e.jsx(S,{size:14}))),!points.length&&v10('p',{className:'subtle'},'本目录暂未整理独立知识点。')))})),!roots.length&&v10('p',{className:'empty'},'没有匹配的知识点。'));
}
function V10LogicDemo(){const[p,setP]=m.useState(true),[q,setQ]=m.useState(false);return v10('div',{className:'logic-demo'},v10('div',{},v10('span',{className:'eyebrow'},'动手看规律'),v10('p',{},'改变真值，观察蕴涵。')),
 v10('div',{className:'logic-controls'},v10('button',{'aria-label':'切换 p 的真值','aria-pressed':p,onClick:()=>setP(!p)},'p',v10('b',{},p?'真':'假')),v10('span',{},'→'),v10('button',{'aria-label':'切换 q 的真值','aria-pressed':q,onClick:()=>setQ(!q)},'q',v10('b',{},q?'真':'假')),v10('span',{},'='),v10('output',{'aria-live':'polite',className:!p||q?'is-true':'is-false'},!p||q?'真':'假')),v10('small',{},'只有“前件真、后件假”时，蕴涵式为假。'))}
function Vs(props){
 const {id,state:s,pick,start,readSource,bookmark}=props;const k=s.knowledge.find(k=>k.id===id);
 if(!k){const chapter=s.chapters.find(c=>c.id===id);if(chapter)return v10('section',{className:'v10-directory'},v10('p',{className:'eyebrow'},'知识点目录'),v10('h2',{},chapter.title),v10('p',{className:'subtle'},'选择一个知识点开始学习。'),s.knowledge.filter(k=>k.chapter_id===id||De(s,k.id)?.id===id).map((k,i)=>v10PointRow(k,pick,i)));return e.jsx(VsLegacy,props)}
 return e.jsx(V10Lesson,{...props,k},id);
}
function V10Lesson({k,state:s,pick,start,readSource,bookmark}){
 const [open,setOpen]=m.useState(false);const p=v10Practice(k),content=k.content||{},root=De(s,k.id);
 const unique=new Set();const groups=s.questions.filter(q=>q.verification==='verified'&&k.question_ids.includes(q.id)).filter(q=>{const id=q.meta.practice_group||q.meta.family_id||q.id;if(unique.has(id))return false;unique.add(id);return true});
 const next=s.knowledge.find(x=>x.id!==k.id&&x.unlock.allowed&&v10Practice(x).new_count>0);
 const conditions=(k.unlock.conditions||[]).filter(c=>!c.met);const bookmarked=s.bookmarks.some(b=>b.target_id===k.id);
 const redundant=new Set([content.plain,content.definition,content.example,content.errors,content.confusions]);
 const extra=[['conditions','适用条件'],['reason','推导思路'],['method','使用方法']].filter(([key])=>{const val=content[key];if(!val||redundant.has(val)||val.startsWith('适用条件见严格定义')||val.startsWith('从定义逐项检查条件。下面的例题'))return false;redundant.add(val);return true});
 return v10('article',{className:'knowledge-lesson'},
 v10('header',{className:'lesson-heading'},v10('div',{},v10('p',{className:'eyebrow'},root?.title||'知识点学习'),v10('h2',{},k.title),v10('p',{className:'lesson-intro'},content.plain)),v10('button',{className:'bookmark-button','aria-label':bookmarked?'取消收藏知识':'收藏知识','aria-pressed':bookmarked,onClick:()=>bookmark(k.id,'knowledge')},e.jsx(ke,{size:20}),v10('span',{},bookmarked?'已收藏':'收藏'))),
 v10('div',{className:'lesson-layout'},
 v10('div',{className:'lesson-main'},
 v10('section',{className:'lesson-paper'},v10('div',{className:'lesson-section-label'},v10('span',{},'01'),v10('h3',{},'把概念弄清楚')),v10('div',{className:'definition-block'},e.jsx(B,{text:content.definition||content.plain||'讲解正在补充。'})),extra.map(([key,title])=>v10('div',{className:'lesson-extra',key},v10('h4',{},title),e.jsx(B,{text:content[key]}))),
 content.example&&v10('div',{className:'lesson-example'},v10('div',{className:'lesson-section-label'},v10('span',{},'02'),v10('h3',{},'用一个例子理解')),e.jsx(B,{text:content.example})),
 k.id==='DM-K01-02'&&e.jsx(V10LogicDemo,{}),
 (content.errors||content.confusions)&&v10('div',{className:'lesson-caution'},v10('h4',{},'这里容易想错'),[...new Set([content.errors,content.confusions].filter(Boolean))].map((text,i)=>e.jsx(B,{text},i))),
 v10('div',{className:'lesson-source'},v10('small',{},'系统整理讲解 · 可对照教材阅读'),v10('button',{className:'text-button',onClick:()=>readSource(Number(k.source?.pdf_page)||(k.page||1)+8)},'查看教材',e.jsx(S,{size:14})))),
 v10('section',{className:'lesson-practice-list'},v10('button',{className:'practice-disclosure','aria-expanded':open,onClick:()=>setOpen(!open)},v10('div',{},v10('span',{className:'eyebrow'},'03 · 学以致用'),v10('h3',{},'这个知识点，会怎么考？')),v10('span',{},p.distinct_count+' 种考法',e.jsx(open?ts:S,{size:17}))),open&&v10('ol',{},groups.map(q=>v10('li',{key:q.id},v10('span',{},(q.meta.practice_group||q.meta.family_id||q.title).replace(/^DM-K\d+-\d+-/,'')),v10('small',{},q.source_type==='textbook'?'教材原题':'补充练习')))))),
 v10('aside',{className:'lesson-sidebar'},v10('section',{className:'lesson-practice-card'},v10('span',{className:'eyebrow'},'理解之后，试一试'),v10('h3',{},!k.unlock.allowed?'先阅读，再练习':p.new_count?'用练习检验理解':p.distinct_count?'已完成本轮考法':'先把概念学明白'),v10('div',{className:'practice-number'},k.unlock.allowed?Math.min(10,p.new_count):'—',v10('small',{},k.unlock.allowed?'道新题':'待解锁')),
 v10('p',{},!k.unlock.allowed?'完成下方前置知识的验证后，即可练习。你可以先自由阅读本页讲解。':p.new_count?'每道题对应不同考法。换数字的同类题，不再重复安排。':p.distinct_count?'这些考法已经练过。可以继续学习其他知识点，错题留在回顾里。':'暂时没有已核验练习，讲解和教材仍可阅读。'),
 v10('button',{className:'primary',disabled:!k.unlock.allowed||!p.new_count,onClick:()=>start(k.id,'knowledge')},!k.unlock.allowed?'先完成前置知识':p.new_count?'开始练习':'暂无新题',e.jsx(D,{size:16})),
 k.unlock.allowed&&!p.new_count&&next&&v10('button',{className:'text-button',onClick:()=>pick(next.id)},'看看下一个知识点',e.jsx(S,{size:15})),v10('small',{className:'practice-caption'},'已练 '+p.practiced_count+' / '+p.distinct_count+' 种考法')),
 conditions.length>0&&v10('section',{className:'prerequisite-note'},v10('h4',{},'先理解这些，会更顺畅'),conditions.map(c=>v10('button',{key:c.id,onClick:()=>pick(c.id)},v10('span',{},c.title),e.jsx(S,{size:14})))),
 v10('section',{className:'lesson-progress'},v10('div',{},v10('h4',{},'理解的积累'),v10('b',{},Math.round(k.mastery)+'%')),v10('div',{className:'meter'},v10('i',{style:{width:k.mastery+'%'}})),v10('p',{},k.evidence_sufficient?'来自不同考法的独立作答':'还需不同考法的独立验证'),p.distinct_count<2&&v10('small',{},'当前独立考法不足，暂不标记为掌握。')))));
}
