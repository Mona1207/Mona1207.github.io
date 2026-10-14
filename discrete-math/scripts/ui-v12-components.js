// Clarity workspace. Visual interactions explain real concepts without recording attempts.
function V12Mark(){return v10('svg',{viewBox:'0 0 32 32',fill:'none','aria-hidden':true},v10('path',{d:'M8 23L16 8L24 23H8Z',stroke:'currentColor',strokeWidth:1.8,strokeLinejoin:'round'}),[[8,23],[16,8],[24,23]].map(([cx,cy])=>v10('circle',{key:cx,cx,cy,r:3,fill:'currentColor'})));}
function v12Symbol(k){return ({'DM-K01-01':'p','DM-K01-02':'→','DM-K01-03':'T/F'}[k.id]||{'02':'≡','03':'∴','04':'∀','05':'∃','06':'∈','07':'R','08':'f','09':'∘','10':'G','11':'∨','12':'!','13':'aₙ','14':'G','15':'G','16':'T','17':'G','18':'χ','19':'≡'}[k.id.slice(4,6)]||'·');}
function V12SetLab({pick}){
 const [mode,setMode]=m.useState('intersection');
 const modes=[['intersection','交集','A ∩ B','{3}','两个集合共同的元素'],['union','并集','A ∪ B','{1, 2, 3, 4}','属于任意一个集合的元素'],['difference','差集','A − B','{1, 2}','只属于 A、不属于 B 的元素']];
 const selected=modes.find(x=>x[0]===mode);
 return v10('aside',{className:'set-lab','aria-label':'集合运算实验台'},
  v10('div',{className:'lab-heading'},v10('span',{className:'lab-dot','aria-hidden':true}),v10('b',{},'小小实验室'),v10('span',{},'集合运算')),
  v10('div',{className:'lab-modes','aria-label':'选择集合运算'},modes.map(([id,label])=>v10('button',{key:id,'aria-pressed':mode===id,onClick:()=>setMode(id)},label))),
  v10('svg',{className:'set-diagram',viewBox:'0 0 340 188',role:'img','aria-label':selected[2]+' = '+selected[3]},
   v10('defs',{},v10('clipPath',{id:'set-overlap-v12'},v10('circle',{cx:211,cy:98,r:64})),v10('mask',{id:'set-difference-v12'},v10('rect',{width:340,height:188,fill:'white'}),v10('circle',{cx:211,cy:98,r:64,fill:'black'}))),
   v10('circle',{className:'set-outline',cx:129,cy:98,r:64}),v10('circle',{className:'set-outline',cx:211,cy:98,r:64}),
   mode==='intersection'?v10('circle',{className:'set-fill',cx:129,cy:98,r:64,clipPath:'url(#set-overlap-v12)'}):mode==='union'?v10('g',{className:'set-fill'},v10('circle',{cx:129,cy:98,r:64}),v10('circle',{cx:211,cy:98,r:64})):v10('circle',{className:'set-fill',cx:129,cy:98,r:64,mask:'url(#set-difference-v12)'}),
   v10('circle',{className:'set-stroke',cx:129,cy:98,r:64}),v10('circle',{className:'set-stroke',cx:211,cy:98,r:64}),
   v10('text',{className:'set-label',x:94,y:22},'A'),v10('text',{className:'set-label',x:242,y:22},'B'),
   v10('text',{className:mode!=='intersection'?'set-number selected':'set-number',x:110,y:82},'1'),v10('text',{className:mode!=='intersection'?'set-number selected':'set-number',x:110,y:118},'2'),v10('text',{className:mode!=='difference'?'set-number selected':'set-number',x:170,y:102},'3'),v10('text',{className:mode==='union'?'set-number selected':'set-number',x:232,y:102},'4')),
  v10('div',{className:'lab-result','aria-live':'polite'},v10('b',{},selected[2]),v10('span',{},'='),v10('strong',{},selected[3])),v10('p',{className:'lab-description'},selected[4]),
  v10('button',{className:'lab-link',onClick:()=>pick('DM-K06-03')},'学习集合运算',e.jsx(D,{size:15})));
}
function V12Mastery({state:s,pick,go,report}){
 const [hover,setHover]=m.useState('');const point=s.knowledge.find(k=>k.id===hover);
 const mastered=s.knowledge.filter(k=>k.state==='mastered').length;
 const started=s.knowledge.filter(k=>k.completed_questions>0).length;
 return v10('section',{className:'mastery-workspace'},
  v10('div',{className:'mastery-map'},v10('div',{className:'section-heading'},v10('h2',{},'你的理解，正在连接'),v10('button',{className:'text-button',onClick:()=>go('knowledge')},'全部知识点',e.jsx(S,{size:14}))),
   v10('div',{className:'mastery-cells','aria-label':'知识点掌握度地图'},s.knowledge.map(k=>v10('button',{key:k.id,className:'mastery-cell '+(k.state==='mastered'?'mastered':k.state==='basic'?'basic':k.completed_questions?'learning':'unstarted'),'aria-label':k.title+'，'+(k.evidence_sufficient?'掌握度 '+Math.round(k.mastery)+'%':'待验证'),title:k.title,onMouseEnter:()=>setHover(k.id),onFocus:()=>setHover(k.id),onClick:()=>pick(k.id)},v10('i',{'aria-hidden':true})))),
   v10('div',{className:'map-caption','aria-live':'polite'},v10('span',{},point?point.title+' · '+(point.evidence_sufficient?Math.round(point.mastery)+'%':'待验证'):'每一格，都是一个知识点。点开即可学习。'),v10('div',{className:'map-legend'},v10('span',{},v10('i',{className:'unstarted'}),'未开始'),v10('span',{},v10('i',{className:'learning'}),'学习中'),v10('span',{},v10('i',{className:'basic'}),'基本掌握'),v10('span',{},v10('i',{className:'mastered'}),'已掌握')))),
  v10('button',{className:'home-evidence',onClick:()=>go('reports')},v10('span',{className:'evidence-label'},'学习积累',e.jsx(S,{size:14})),v10('div',{className:'evidence-numbers'},v10('span',{},v10('b',{},started),v10('small',{},'/ '+s.knowledge.length+' 个已开始')),v10('span',{},v10('b',{},report?.completed_questions||0),v10('small',{},'完成题目'))),v10('span',{className:'evidence-note'},mastered+' 个知识点已有掌握证据')));
}
function Es({state:s,report:t,active:a,go:o,start:n,resume:c,pick}){
 const candidates=s.knowledge.filter(k=>k.unlock.allowed&&v10Practice(k).new_count>0);
 const next=candidates.find(k=>k.completed_questions>0)||candidates[0];
 const current=a&&s.knowledge.find(k=>k.id===a.session.target_id),hero=current||next,chosen=pick||v10Pick;
 const suggestions=candidates.filter(k=>k.id!==hero?.id).slice(0,3),p=hero&&v10Practice(hero);
 return v10('div',{className:'clarity-home'},
  v10('header',{className:'workspace-heading'},v10('div',{},v10('p',{className:'workspace-kicker'},'离散数学',v10('span',{},'个人学习空间')),v10('h1',{},'让每个概念，都清楚一点。')),v10('button',{className:'workspace-search',onClick:()=>o('knowledge')},e.jsx(xe,{size:17}),'找一个知识点')),
  v10('div',{className:'workspace-hero'},
   v10('section',{className:'learning-stage'},v10('div',{className:'stage-topline'},v10('span',{className:'stage-badge'},v10('i',{}),current?'继续上次练习':'下一步 · 知识点学习'),v10('span',{className:'stage-number'},hero?.id.replace('DM-K','K')||'知识树')),
    v10('h2',{},hero?.title||'回到知识树，整理你的理解'),v10('p',{className:'stage-description'},hero?.content?.plain||'这一轮的新考法已经学完了。还有哪些概念值得回顾？'),
    v10('ol',{className:'learning-flow','aria-label':'学习顺序'},[['01','读懂概念'],['02','独立作答'],['03','回顾总结']].map(([id,label])=>v10('li',{key:id},v10('span',{},id),v10('b',{},label)))),
    v10('div',{className:'stage-actions'},v10('button',{className:'primary',onClick:()=>current?c():hero?chosen(hero.id):o('graph')},current?'继续练习':hero?'开始学习':'打开知识树',e.jsx(D,{size:18})),v10('button',{className:'stage-pick',onClick:()=>o('workspace')},'自主选择',e.jsx(S,{size:16}))),
    v10('div',{className:'stage-footer'},v10('span',{},hero?(p.new_count?Math.min(10,p.new_count)+' 道新题 · '+p.distinct_count+' 种考法':v10Status(hero)):'自由回顾'),v10('span',{},'读懂，再练习'))),e.jsx(V12SetLab,{pick:chosen})),
  e.jsx(V12Mastery,{state:s,pick:chosen,go:o,report:t}),
  v10('section',{className:'recommendations'},v10('div',{className:'section-heading'},v10('h2',{},'接下来，也可以学'),v10('span',{className:'subtle'},'按知识点，慢慢展开')),v10('div',{className:'recommendation-grid'},suggestions.map(k=>v10('button',{key:k.id,className:'next-point',onClick:()=>chosen(k.id)},v10('span',{className:'next-symbol','aria-hidden':true},v12Symbol(k)),v10('div',{},v10('b',{},k.title),v10('small',{},v10Status(k))),e.jsx(S,{size:16}))),!suggestions.length&&v10('p',{className:'subtle'},'到知识树自由探索，或回顾错题与笔记。'))),
  v10('div',{className:'workspace-tools'},[['wrong','错题本','把没想通的留给下一次',ee],['notes','我的笔记','整理自己的理解',me],['reports','学习记录','看看每一步的积累',Ke]].map(([id,title,copy,Icon])=>v10('button',{key:id,onClick:()=>o(id)},e.jsx(Icon,{size:19}),v10('span',{},v10('b',{},title),v10('small',{},copy)),e.jsx(S,{size:14})))));
}
function V10Lesson({k,state:s,pick,start,readSource,bookmark}){
 const [view,setView]=m.useState('concept'),[open,setOpen]=m.useState(false);
 const p=v10Practice(k),content=k.content||{},root=De(s,k.id),bookmarked=s.bookmarks.some(b=>b.target_id===k.id);
 const unique=new Set();const groups=s.questions.filter(q=>q.verification==='verified'&&k.question_ids.includes(q.id)).filter(q=>{const id=q.meta.practice_group||q.meta.family_id||q.id;if(unique.has(id))return false;unique.add(id);return true});
 const next=s.knowledge.find(x=>x.id!==k.id&&x.unlock.allowed&&v10Practice(x).new_count>0),conditions=(k.unlock.conditions||[]).filter(c=>!c.met);
 const redundant=new Set([content.plain,content.definition,content.example,content.errors,content.confusions]);
 const extra=[['conditions','适用条件'],['reason','为什么成立'],['method','怎样使用']].filter(([key])=>{const val=content[key];if(!val||redundant.has(val)||val.startsWith('适用条件见严格定义')||val.startsWith('从定义逐项检查条件。下面的例题'))return false;redundant.add(val);return true});
 const tabs=[['concept','理解概念'],['example','看个例子'],['caution','易错提醒']];
 return v10('article',{className:'clarity-lesson'},
  v10('header',{className:'clarity-lesson-heading'},v10('div',{},v10('p',{className:'lesson-location'},root?.title||'知识点学习',v10('span',{},k.id.replace('DM-K','K'))),v10('h1',{},k.title),v10('p',{},content.plain)),v10('button',{className:'bookmark-button','aria-label':bookmarked?'取消收藏知识':'收藏知识','aria-pressed':bookmarked,onClick:()=>bookmark(k.id,'knowledge')},e.jsx(ke,{size:19}),v10('span',{},bookmarked?'已收藏':'收藏'))),
  v10('div',{className:'clarity-lesson-grid'},
   v10('div',{className:'clarity-reading'},v10('section',{className:'reading-surface'},
    v10('div',{className:'reading-tabs',role:'tablist','aria-label':'知识点内容',onKeyDown:ev=>{const i=tabs.findIndex(x=>x[0]===view);if(['ArrowLeft','ArrowRight','Home','End'].includes(ev.key)){ev.preventDefault();const n=ev.key==='Home'?0:ev.key==='End'?tabs.length-1:(i+(ev.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;setView(tabs[n][0]);ev.currentTarget.querySelectorAll('button')[n].focus();}}},tabs.map(([id,label])=>v10('button',{key:id,id:'lesson-tab-'+id,role:'tab','aria-controls':'lesson-panel-'+id,'aria-selected':view===id,tabIndex:view===id?0:-1,onClick:()=>setView(id)},label))),
    v10('div',{className:'reading-content',key:view,role:'tabpanel',id:'lesson-panel-'+view,'aria-labelledby':'lesson-tab-'+view,tabIndex:0},
     v10('span',{className:'reading-eyebrow'},view==='concept'?'概念 / CONCEPT':view==='example'?'例子 / EXAMPLE':'提醒 / REMINDER'),
     view==='concept'&&v10('div',{},v10('div',{className:'reading-definition'},e.jsx(B,{text:content.definition||content.plain||'讲解正在补充。'})),extra.map(([key,title])=>v10('div',{className:'reading-extra',key},v10('h3',{},title),e.jsx(B,{text:content[key]}))),k.id==='DM-K01-02'&&e.jsx(V10LogicDemo,{})),
     view==='example'&&v10('div',{className:'reading-example'},e.jsx(B,{text:content.example||'这一知识点的例子仍在补充，可以对照教材阅读。'}),k.id==='DM-K01-02'&&e.jsx(V10LogicDemo,{})),
     view==='caution'&&v10('div',{className:'reading-caution'},e.jsx(ee,{size:22}),v10('div',{},[...new Set([content.errors,content.confusions].filter(Boolean))].map((text,i)=>e.jsx(B,{text},i)),!content.errors&&!content.confusions&&v10('p',{},'对照定义，逐项确认条件是否满足。')))),
    v10('footer',{className:'reading-source'},v10('span',{},'系统整理讲解'),v10('button',{className:'text-button',onClick:()=>readSource(Number(k.source?.pdf_page)||(k.page||1)+8)},'对照教材',e.jsx(S,{size:14})))),
   v10('section',{className:'lesson-practice-list'},v10('button',{className:'practice-disclosure','aria-expanded':open,onClick:()=>setOpen(!open)},v10('div',{},v10('h3',{},'会怎么考？'),v10('p',{},'查看这个知识点的独立考法')),v10('span',{},p.distinct_count+' 种',e.jsx(open?ts:S,{size:17}))),open&&v10('ol',{},groups.map(q=>v10('li',{key:q.id},v10('span',{},(q.meta.practice_group||q.meta.family_id||q.title).replace(/^DM-K\d+-\d+-/,'')),v10('small',{},q.source_type==='textbook'?'教材原题':'补充练习')))))),
   v10('aside',{className:'clarity-practice'},v10('section',{className:'practice-companion'},v10('span',{className:'companion-kicker'},'准备好了，就试一试'),v10('h2',{},'独立练习'),v10('div',{className:'practice-number'},k.unlock.allowed?Math.min(10,p.new_count):'—',v10('small',{},k.unlock.allowed?'道新题':'待解锁')),
    v10('p',{},!k.unlock.allowed?'完成前置知识验证后即可练习。本页讲解可以自由阅读。':p.new_count?'每种考法一道，已经做过的同类变式自动跳过。':p.distinct_count?'这些考法已练过。可以学习下一个知识点，或主动回顾错题。':'练习还在补充，可以先阅读讲解。'),
    v10('button',{className:'primary',disabled:!k.unlock.allowed||!p.new_count,onClick:()=>start(k.id,'knowledge')},!k.unlock.allowed?'先学前置知识':p.new_count?'开始练习':'暂无新题',e.jsx(D,{size:17})),k.unlock.allowed&&!p.new_count&&next&&v10('button',{className:'text-button',onClick:()=>pick(next.id)},'下一个知识点',e.jsx(S,{size:14})),v10('small',{className:'practice-caption'},'已练 '+p.practiced_count+' / '+p.distinct_count+' 种考法')),
    v10('section',{className:'companion-progress'},v10('div',{},v10('h3',{},'当前掌握度'),v10('b',{},Math.round(k.mastery)+'%')),v10('div',{className:'meter'},v10('i',{style:{width:k.mastery+'%'}})),v10('p',{},k.evidence_sufficient?'来自不同考法的独立作答':'还需独立作答验证理解')),
    conditions.length>0&&v10('section',{className:'prerequisite-note'},v10('h4',{},'先理解这些'),conditions.map(c=>v10('button',{key:c.id,onClick:()=>pick(c.id)},v10('span',{},c.title),e.jsx(S,{size:14})))))));
}
