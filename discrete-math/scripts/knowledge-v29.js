// Formula compatibility is applied before Markdown parsing, so TeX is never a code sample.
function v29MathText(value){
 let text=String(value??'').replace(/\r\n?/g,'\n');
 text=text.replace(/\\\[([\s\S]*?)\\\]/g,(_,s)=>'\n\n$$\n'+s.trim()+'\n$$\n\n').replace(/\\\(([\s\S]*?)\\\)/g,(_,s)=>'$'+s.trim()+'$');
 text=text.replace(/```(?:math|latex|tex)\s*\n([\s\S]*?)```/gi,(_,s)=>'\n\n$$\n'+s.trim().replace(/^\$\$|\$\$$/g,'').trim()+'\n$$\n\n');
 text=text.replace(/`([^`\n]+)`/g,(all,s)=>/\\[a-zA-Z]+|[=∑∫√≤≥]|\$/.test(s)?(s.startsWith('$')?s:'$'+s+'$'):all);
 return text.replace(/(?<!\$)\$\$([^\n]*?)\$\$(?!\$)/g,(_,s)=>'\n\n$$\n'+s.trim()+'\n$$\n\n');
}
function V29WorkedExamples({content,showCases=true}){
 const cases=showCases?(content.worked_examples||content.exam_cases||[]):[],example=content.example;
 return v10(e.Fragment,{},example&&v10('section',{className:'v29-worked-example'},v10('h3',{},'先看一个例子'),e.jsx(V17Markdown,{text:example})),cases.length>0&&v10('section',{className:'v29-examples'},v10('h3',{},'逐步理解'),cases.map((item,index)=>v10('details',{key:index,open:index===0,className:'v29-worked-example'},v10('summary',{},item.title||'例子 '+(index+1)),item.prompt&&e.jsx(V17Markdown,{text:item.prompt}),v10('ol',{},(item.steps||[]).map((step,i)=>v10('li',{key:i},e.jsx(V17Markdown,{text:step})))),item.answer&&v10('div',{className:'v29-example-result'},e.jsx(V17Markdown,{text:item.answer})),item.label&&v10('small',{},item.label)))));
}
function V29KnowledgeBody({point,tab,practice=false}){
 const content=point.content||{};
 return v10(e.Fragment,{},v22KnowledgeSections(content,tab).filter(([title,text])=>!(tab==='method'&&title==='推导与解释'&&text===content.example)).map(([title,text])=>v10('section',{key:title,className:'v29-knowledge-section'},v10('h3',{},title),e.jsx(V17Markdown,{text}))),tab==='definition'&&content.symbols&&v10('details',{className:'v29-symbols'},v10('summary',{},'符号与单位'),e.jsx(V17Markdown,{text:content.symbols})),tab==='method'&&e.jsx(V29WorkedExamples,{content,showCases:!practice}),tab==='errors'&&content.check&&v10('section',{},v10('h3',{},'做完怎样检查'),e.jsx(V17Markdown,{text:content.check})));
}
function V19KnowledgeSupport({points,state:s,pick,selected,onSelect,readSource}){
 const [tab,setTab]=m.useState('definition'),point=s.knowledge.find(k=>k.id===selected)||points[0];m.useEffect(()=>setTab('definition'),[point?.id]);
 return v10('section',{className:'v19-knowledge-support'},points.length>1&&v10(V25Select,{'aria-label':'本题对应知识点',value:point?.id,onChange:ev=>onSelect(ev.target.value)},points.map(k=>v10('option',{key:k.id,value:k.id},k.title))),v10('nav',{className:'mini-segments'},[['definition','概念与公式'],['method','推导与例子'],['errors','易错与检查']].map(([id,title])=>v10('button',{key:id,'aria-pressed':tab===id,onClick:()=>setTab(id)},title))),v10('div',{className:'v19-knowledge-scroll'},point?v10(e.Fragment,{},v10('h3',{},point.title),e.jsx(V22KnowledgeSource,{state:s,point,readSource}),e.jsx(V29KnowledgeBody,{point,tab,practice:true}),e.jsx(V18Prerequisites,{state:s,id:point.id,pick})):v10('p',{},'本题知识点关联待补充。')),v10('small',{className:'v19-before-answer'},'先理解知识，再作答；提交后查看分步解析并自评。'));
}
function V18Concept({state:s,k,pick,readSource}){
 const [tab,setTab]=m.useState('definition');m.useEffect(()=>setTab('definition'),[k.id]);
 return v10('section',{className:'v18-concept'},v10('header',{className:'v18-compact-heading'},v10('h1',{},k.title),v10('button',{className:'quiet',onClick:()=>pick(k.id)},'查看对应题号')),e.jsx(V18Prerequisites,{state:s,id:k.id,pick}),v10('nav',{className:'mini-segments'},[['definition','概念与公式'],['method','推导与例子'],['errors','易错与检查']].map(([id,title])=>v10('button',{key:id,'aria-pressed':tab===id,onClick:()=>setTab(id)},title))),v10('div',{className:'v18-concept-body'},e.jsx(V22KnowledgeSource,{state:s,point:k,readSource}),e.jsx(V29KnowledgeBody,{point:k,tab})));
}
