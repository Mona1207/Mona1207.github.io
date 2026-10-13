// Warm study desk: readable type, a tactile concept note, and knowledge-first entry.
function V11Note({state:s,pick}){
 const topics=[['DM-K01-02','命题','p → q','从“如果”开始，理解逻辑。'],['DM-K06-03','集合','A ∩ B','找到两个集合共同的部分。'],['DM-K07-03','关系','a → b','把抽象关系，画成看得见的连接。']];
 const [selected,setSelected]=m.useState(0);const [id,label,formula,copy]=topics[selected];
 return v10('aside',{className:'concept-note','aria-label':'概念手记'},v10('div',{className:'note-tabs','aria-label':'选择概念'},topics.map((t,i)=>v10('button',{key:t[0],'aria-pressed':selected===i,onClick:()=>setSelected(i)},t[1]))),
 v10('div',{className:'note-page',key:id},v10('div',{className:'note-topline'},v10('span',{},'概念手记'),v10('span',{},'0'+(selected+1))),
 v10('div',{className:'note-art','aria-hidden':true},selected===0?v10('div',{className:'implication-art'},v10('span',{},'p'),v10('i',{},'→'),v10('span',{},'q')):selected===1?v10('div',{className:'venn-art'},v10('i',{}),v10('i',{})):v10('div',{className:'relation-art'},v10('span',{},'a'),v10('i',{},'↗'),v10('span',{},'b'),v10('span',{},'c'))),
 v10('strong',{className:'note-formula'},formula),v10('p',{},copy),v10('button',{className:'note-link',onClick:()=>pick(id)},'翻开这一页',e.jsx(D,{size:16}))));
}
function Es({state:s,report:t,active:a,go:o,start:n,resume:c,pick}){
 const candidates=s.knowledge.filter(k=>k.unlock.allowed&&v10Practice(k).new_count>0);
 const next=candidates.find(k=>k.completed_questions>0)||candidates[0];const current=a&&s.knowledge.find(k=>k.id===a.session.target_id);const hero=current||next,chosen=pick||v10Pick;
 const studied=s.knowledge.filter(k=>k.completed_questions>0).length;
 return v10('div',{className:'studio-home'},
 v10('section',{className:'desk-intro'},v10('div',{className:'desk-main'},v10('p',{className:'desk-kicker'},v10('span',{className:'tiny-sun','aria-hidden':true},'✳'),'你的离散数学学习空间'),v10('h1',{},'把离散数学，',v10('br',{}),'一点点学明白。'),v10('p',{className:'desk-description'},'先读懂一个概念，再用不同考法检验理解。'),
 v10('div',{className:'continue-note'},v10('span',{className:'continue-icon','aria-hidden':true},e.jsx(ee,{size:22})),v10('div',{},v10('small',{},current?'上次学到这里':'从这里开始'),v10('h2',{},hero?.title||'探索下一个知识点'),v10('span',{},hero?v10Status(hero):'打开知识树，回顾学过的概念')),v10('button',{className:'continue-arrow','aria-label':current?'继续上次练习':'打开推荐知识点',onClick:()=>current?c():hero?chosen(hero.id):o('graph')},e.jsx(D,{size:20}))),
 v10('div',{className:'desk-actions'},v10('button',{className:'primary',onClick:()=>current?c():hero?chosen(hero.id):o('graph')},current?'继续练习':'开始学习',e.jsx(D,{size:17})),v10('button',{className:'desk-secondary',onClick:()=>o('workspace')},'自己选知识点',e.jsx(S,{size:15})))),e.jsx(V11Note,{state:s,pick:chosen})),
 v10('div',{className:'desk-summary'},v10('span',{},v10('b',{},studied),'/ '+s.knowledge.length+' 个知识点已开始'),v10('i',{}),v10('span',{},'不同考法，一次专注'),v10('button',{onClick:()=>o('reports')},'查看学习记录',e.jsx(S,{size:14}))),
 v10('div',{className:'desk-bottom'},v10('section',{className:'desk-points'},v10('div',{className:'section-heading'},v10('div',{},v10('span',{className:'eyebrow'},'下一页，也很值得'),v10('h2',{},'继续探索')),v10('button',{className:'text-button',onClick:()=>o('knowledge')},'全部知识点',e.jsx(S,{size:15}))),candidates.slice(0,3).map((k,i)=>v10PointRow(k,chosen,i)),!candidates.length&&v10('p',{className:'subtle'},'已完成当前可练考法，可以回顾笔记与错题。')),
 v10('aside',{className:'desk-tools'},v10('h2',{},'随手收好'),[['wrong','错题本','把没想通的，再想一遍。',ee],['notes','我的笔记','留住属于自己的理解。',me]].map(([id,title,copy,Icon])=>v10('button',{key:id,onClick:()=>o(id)},v10('span',{className:'tool-icon'},e.jsx(Icon,{size:21})),v10('span',{},v10('b',{},title),v10('small',{},copy)),e.jsx(S,{size:16}))))));
}
