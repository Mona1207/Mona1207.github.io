function V18Study({state:s,item,example,items,records,pick,back,fail,readSource,error:sourceError}){
 const book=s.settings.current_book,record=records[item.id]||{},textItem=example||item.text_item,[middle,setMiddle]=m.useState('draft'),[error,setError]=m.useState(''),[revealSignal,setRevealSignal]=m.useState(0),[revealed,setRevealed]=m.useState(false),[ratingBusy,setRatingBusy]=m.useState(false),[finishedGroup,setFinishedGroup]=m.useState(false),points=item.knowledge_ids.map(id=>s.knowledge.find(k=>k.id===id)).filter(Boolean),kind=item.kind==='example'?'examples':'exercises',sequence=v18StudySequence(items,kind,item.id,book),index=sequence.findIndex(i=>i.id===item.id),ratingLock=m.useRef(false);
 m.useEffect(()=>{try{v18SaveRecord(book,item.id,{last_opened_at:new Date().toISOString()})}catch(e){setError(e.message)}},[book,item.id]);
 function save(changes){try{v18SaveRecord(book,item.id,changes);setError('');return true}catch(e){setError('本机保存失败，请下载备份：'+e.message);return false}}
 async function rate(rating){if(ratingLock.current||!revealed)return;ratingLock.current=true;setRatingBusy(true);try{if(!save({rating,shown:true}))return;await v20FlushInk();const to=sequence[index+1];if(to)pick(to.id,'replace');else setFinishedGroup(true)}catch(e){setError('草稿保存未完成，请重试：'+e.message)}finally{ratingLock.current=false;setRatingBusy(false)}}
 function next(delta){const to=sequence[index+delta];if(to)pick(to.id,'replace')}
 const left=v10(e.Fragment,{},
  v10('header',{className:'v18-column-heading'},v10('b',{},'题目'),v10('small',{},'原书第 '+item.printed_page+' 页')),
  v10('div',{className:'v18-related-chips'},points.map(k=>v10('button',{className:'v18-chip',key:k.id,onClick:()=>pick(k.id,'concept')},k.title,e.jsx(S,{size:10})))),
  e.jsx(V19QuestionText,{item:textItem,error:sourceError}),
  v10('details',{className:'v18-typed-answer'},v10('summary',{},'文字思路（可选）'),v10('textarea',{'aria-label':'本题文字思路',rows:3,value:record.answer||'',onChange:ev=>save({answer:ev.target.value})})),
  v10('footer',{className:'v19-submit'},v10('button',{className:'primary',disabled:!textItem,onClick:()=>{if(save({shown:true})){setRevealed(true);setRevealSignal(n=>n+1)}}},revealed?'重新查看解析':'答完，查看解析'))
 );
 const center=v10(e.Fragment,{},
  v10('header',{className:'v18-column-heading'},v10('b',{},'演算与笔记'),v10('div',{className:'mini-segments'},[['draft','草稿'],['notes','图片笔记']].map(([id,title])=>v10('button',{key:id,'aria-pressed':middle===id,onClick:()=>setMiddle(id)},title)))),
  v10('div',{className:'v18-ink-persistent',hidden:middle!=='draft'},e.jsx(V16Handwriting,{book,question:item.id,label:'本题手写草稿'},item.id)),
  middle==='notes'&&e.jsx(V17ImageNotes,{book,target:item.id,state:s,items,onImport:()=>setMiddle('draft')},item.id)
 );
 const right=v10(e.Fragment,{},
  v10('header',{className:'v18-column-heading'},v10('b',{},revealed?'答案与解析':'对应知识讲解')),
  revealed?e.jsx(V19Solution,{item:textItem}):e.jsx(V19KnowledgeSupport,{points,state:s,pick}),
  revealed&&v10('footer',{className:'v18-reflection'},v10('small',{},finishedGroup?'本组已完成 · 自评已保存':'自评后自动进入下一题'),v10('div',{},V18_RATINGS.map(([id,title])=>v10('button',{key:id,'aria-pressed':v16VisibleRating(record.rating)===id,disabled:ratingBusy,onClick:()=>rate(id)},title))))
 );
 return v10('article',{className:'v18-study'},
  v10('header',{className:'v18-study-heading'},v10('button',{className:'text-button',onClick:back},e.jsx(Ne,{size:14}),'返回'),v10('b',{},item.title),v10('small',{},v20ChapterLabel(s,item.id,items)+' · '+(kind==='examples'?'课本例题':'课后习题')),e.jsx(V18Star,{book,item,records,fail}),v10('div',{className:'v18-next-prev'},v10('button',{className:'quiet',disabled:index<=0,onClick:()=>next(-1)},'上一题'),v10('small',{},index>=0?index+1+' / '+sequence.length:''),v10('button',{className:'quiet',disabled:index<0||index>=sequence.length-1,onClick:()=>next(1)},'下一题'))),
  error&&v10('p',{role:'alert',className:'error-banner'},error),
  e.jsx(V18Split,{book,finished:revealed,revealSignal,question:item.id,children:[left,center,right]})
 );
}

const v19ExerciseCache=new Map();
function useV17Examples(book){const data=useV17ExamplesBeforeV20(book),context=data.items.find(i=>i.id==='SRC-DM2T-X147-2324');return book!=='DM2T'||!context?data:{...data,items:data.items.map(i=>i.id==='SRC-DM2T-X147-8110'?{...i,prompt:i.prompt+'\n\n引用条件（例 7.20）：\n\n'+context.prompt.replace(/求集合[\s\S]*$/,'')}:i)}}
function useV19Exercises(book){
 const [state,setState]=m.useState({book,items:[],error:''});
 m.useEffect(()=>{let live=true;setState({book,items:[],error:''});if(book==='DM2')return;
  if(!v19ExerciseCache.has(book))v19ExerciseCache.set(book,fetch('/discrete-math/data/exercises-'+book+'-v20.json?v=20').then(r=>{if(!r.ok)throw Error('习题文字加载失败，请刷新重试');return r.json()}).catch(error=>{v19ExerciseCache.delete(book);throw error}));
  v19ExerciseCache.get(book).then(data=>live&&setState({...data,book,error:''})).catch(error=>live&&setState({book,items:[],error:error.message}));return()=>{live=false};
 },[book]);return state.book===book?state:{book,items:[],error:''};
}
function useV15Sources(book){const base=useV15SourcesBeforeV20(book),texts=useV19Exercises(book),excluded=new Set(texts.excluded_ids||[]),originals=base.items.filter(i=>!excluded.has(i.id)),byId=new Map(texts.items.map(i=>[i.id,i])),known=new Set(originals.map(i=>i.id));return {...base,items:[...originals.map(item=>byId.has(item.id)?{...item,...byId.get(item.id).source,knowledge_ids:byId.get(item.id).knowledge_ids||item.knowledge_ids,text_item:byId.get(item.id)}:item),...texts.items.filter(i=>!known.has(i.id)).map(i=>({...i.source,knowledge_ids:i.knowledge_ids,text_item:i}))],error:base.error||texts.error,audit:base.audit?{...base.audit,coverage_statement:'例题与课后习题均以OCR文字展示。未校订的题干与书后简答明确标注；无原书答案的题不冒充已有解析。',exercise_texts:texts.items.length}:base.audit};}
function V19QuestionText({item,error}){
 if(!item)return v10('div',{className:'v19-text-body',role:error?'alert':'status'},error||'正在读取 OCR 题目文字…');
 if(item.kind==='example'||item.text_origin?.includes('例题'))return e.jsx(V17ExampleText,{example:item});
 return v10('section',{className:'v19-text-shell'},item.status!=='reviewed'&&v10('details',{className:'v19-ocr-status'},v10('summary',{},'OCR 文字 · 数学符号待校订'),v10('p',{},'矩阵、分式、上下标及图形尚未逐项核验，请勿据此认定原书内容。'),(item.issues||[]).map((s,i)=>v10('p',{key:i},s))),v10('div',{className:'v19-text-body'},item.status==='reviewed'?e.jsx(V17Markdown,{text:item.prompt}):v10('div',{className:'v19-raw-ocr'},item.prompt||'此段未可靠识别，待补充校订文字。')));
}
function V19Solution({item}){
 const [view,setView]=m.useState('answer');
 if(!item)return v10('div',{className:'v19-text-body',role:'status'},'正在读取解析文字…');
 if(item.kind==='example'||!item.kind)return e.jsx(V17ExampleText,{example:item,solution:true});
 return v10('section',{className:'v19-text-shell'},
  v10('nav',{className:'mini-segments'},[['answer','解答'],['steps','分步讲解']].map(([id,title])=>v10('button',{key:id,'aria-pressed':view===id,onClick:()=>setView(id)},title))),
  v10('div',{className:'v19-text-body'},view==='answer'?v10(e.Fragment,{},v10('p',{className:'caption'},item.solution_origin||'本题解答尚待补充'),item.solution?(item.answer_status==='reviewed'?e.jsx(V17Markdown,{text:item.solution}):v10(e.Fragment,{},v10('p',{className:'v19-inline-status'},'以下书后答案为 OCR 初稿，数学符号待校订。'),v10('div',{className:'v19-raw-ocr'},item.solution))):v10('p',{className:'v19-answer-missing'},'尚无可用的完整文字解答；此项不代表已完成解析。')):(item.explanation?.length?v10(e.Fragment,{},v10('p',{className:'caption'},'以下为学习补充，与原书答案区分。'),item.explanation.map((step,i)=>v10('section',{className:'v19-solution-step',key:i},v10('b',{},'第 '+(i+1)+' 步'),e.jsx(V17Markdown,{text:step})))):v10('p',{className:'v19-answer-missing'},'本题分步讲解尚待补充，相关知识可从题目旁的知识点进入。')))
 );
}
function V19KnowledgeSupport({points,state:s,pick}){
 const [selected,setSelected]=m.useState(points[0]?.id||''),[tab,setTab]=m.useState('definition'),point=points.find(k=>k.id===selected)||points[0],c=point?.content||{};
 return v10('section',{className:'v19-knowledge-support'},
  points.length>1&&v10('select',{'aria-label':'本题对应知识点',value:point?.id,onChange:ev=>setSelected(ev.target.value)},points.map(k=>v10('option',{value:k.id,key:k.id},k.title))),
  v10('nav',{className:'mini-segments'},[['definition','定义与条件'],['method','方法'],['errors','易错点']].map(([id,title])=>v10('button',{key:id,'aria-pressed':tab===id,onClick:()=>setTab(id)},title))),
  v10('div',{className:'v19-knowledge-scroll'},point?v10(e.Fragment,{},v10('h3',{},point.title),
   (tab==='definition'?[['定义',c.definition],['定理',c.theory],['适用条件',c.conditions]]:tab==='method'?[['解题方法',c.method],['推导依据',c.reason]]:[['常见错误',c.errors],['容易混淆',c.confusions]]).filter(([,text])=>text).map(([title,text])=>v10('section',{key:title},v10('h4',{},title),e.jsx(V17Markdown,{text}))),
   e.jsx(V18Prerequisites,{state:s,id:point.id,pick}),v10('button',{className:'text-button',onClick:()=>pick(point.id,'concept')},'打开完整知识点')):v10('p',{},'本题知识点关联待校订。')),
  v10('small',{className:'v19-before-answer'},'答完后，右栏切换为解析与自评。')
 );
}
function v19Ratio(value){if(!Array.isArray(value)||value.length!==3||value.some(x=>!Number.isFinite(x)||x<0)||value[0]<=0||value[1]<=0)return [34,32,34];const sum=value.reduce((a,b)=>a+b,0);return value.map(x=>x/sum*100)}
function v19FitRatios(value,width,collapsed=false){
 const base=v19Ratio(value),available=Math.max(1,width-20),minimum=(width<900?[175,165,0]:[210,190,0]).map(x=>x/available*100);
 let result=collapsed?[base[0]/(base[0]+base[1])*100,base[1]/(base[0]+base[1])*100,0]:base.slice();
 for(let n=0;n<4;n++){let deficit=0;for(let i=0;i<2;i++)if(result[i]<minimum[i]){deficit+=minimum[i]-result[i];result[i]=minimum[i]}if(!deficit)break;const flex=result.map((x,i)=>Math.max(0,x-minimum[i])),sum=flex.reduce((a,b)=>a+b,0);if(sum)result=result.map((x,i)=>x-deficit*flex[i]/sum)}return result;
}
function v19MoveRatio(actual,index,delta,width){const out=actual.slice(),minimum=(width<900?[175,165,0]:[210,190,0]).map(x=>x/Math.max(1,width-20)*100),sum=out[index]+out[index+1],next=Math.max(minimum[index],Math.min(sum-minimum[index+1],out[index]+delta));out[index]=next;out[index+1]=sum-next;return out;}
function V18Split({book,children,finished=false,revealSignal=0,question}){
 const ratioKey='zhixu-three-columns-v18-'+book,panelKey='zhixu-right-panel-v19-'+book,[ratios,setRatios]=m.useState(()=>{try{return v19Ratio(JSON.parse(localStorage.getItem(ratioKey)||'null'))}catch{return [34,32,34]}}),[collapsed,setCollapsed]=m.useState(()=>{try{return !finished&&localStorage.getItem(panelKey)==='closed'}catch{return false}}),[width,setWidth]=m.useState(1024),[mobile,setMobile]=m.useState(0),box=m.useRef(null),drag=m.useRef(null),actual=v19FitRatios(ratios,width,collapsed),label=finished?'解析与自评':'知识讲解';
 m.useEffect(()=>{const observer=new ResizeObserver(()=>{if(box.current)setWidth(box.current.clientWidth)});if(box.current){setWidth(box.current.clientWidth);observer.observe(box.current)}return()=>observer.disconnect()},[]);
 function panel(closed){setCollapsed(closed);try{localStorage.setItem(panelKey,closed?'closed':'open')}catch{}if(closed)setMobile(n=>n===2?0:n)}
 function open(){const right=Math.max(ratios[2],190/Math.max(1,width-20)*100),sum=ratios[0]+ratios[1];save([ratios[0]/sum*(100-right),ratios[1]/sum*(100-right),right]);panel(false);setMobile(2)}
 m.useEffect(()=>{if(finished)open()},[finished,revealSignal,question]);
 function save(value){setRatios(value);try{localStorage.setItem(ratioKey,JSON.stringify(value))}catch{}}
 function reset(){save([34,32,34]);panel(false)}
 function begin(ev,index){if(ev.button!==0)return;ev.preventDefault();drag.current={id:ev.pointerId,index,x:ev.clientX,actual:actual.slice(),width:box.current.clientWidth,remember:ratios.slice()};ev.currentTarget.setPointerCapture(ev.pointerId)}
 function adjust(d,delta){const moved=v19MoveRatio(d.actual,d.index,delta,d.width);if(d.index===1&&moved[2]*(d.width-20)/100<52){panel(true);return}if(d.index===1)panel(false);if(collapsed&&d.index===0){const right=ratios[2],sum=100-right;save([moved[0]*sum/100,moved[1]*sum/100,right])}else{const sum=moved.reduce((a,b)=>a+b,0);save(moved.map(x=>x/sum*100))}}
 function move(ev){const d=drag.current;if(!d||d.id!==ev.pointerId)return;ev.preventDefault();adjust(d,(ev.clientX-d.x)/Math.max(1,d.width-20)*100)}
 function end(ev){if(drag.current?.id!==ev.pointerId)return;drag.current=null;if(ev.currentTarget.hasPointerCapture(ev.pointerId))ev.currentTarget.releasePointerCapture(ev.pointerId)}
 function key(ev,index){if(ev.key==='Home'){ev.preventDefault();reset()}else if(ev.key==='End'&&index===1){ev.preventDefault();panel(true)}else if(['ArrowLeft','ArrowRight'].includes(ev.key)){ev.preventDefault();if(collapsed&&index===1&&ev.key==='ArrowLeft'){open();return}adjust({actual,index,width},(ev.key==='ArrowRight'?1:-1)*(ev.shiftKey?5:1))}}
 return v10('div',{className:'v18-split-shell v19-split-shell'+(collapsed?' v19-right-closed':'')},
  v10('div',{className:'v18-split-toolbar'},v10('nav',{'aria-label':'小屏答题分区'},['题目','草稿',label].map((title,i)=>v10('button',{key:i,'aria-pressed':mobile===i&&!((i===2)&&collapsed),onClick:()=>{if(i===2)panel(false);setMobile(i)}},title))),v10('small',{},'拖动分隔条；右栏可缩至隐藏'),v10('button',{className:'text-button v19-panel-toggle','aria-expanded':!collapsed,onClick:()=>collapsed?open():panel(true)},(collapsed?'展开':'收起')+label),v10('button',{className:'text-button',onClick:reset},'重置比例')),
  v10('div',{className:'v18-split',ref:box,style:{gridTemplateColumns:actual[0]+'fr 10px '+actual[1]+'fr 10px '+actual[2]+'fr'}},children.map((child,i)=>v10(e.Fragment,{key:i},i>0&&v10('div',{className:'v18-resizer',role:'separator',tabIndex:0,'aria-label':i===1?'调整题目与草稿宽度':'调整或收起右栏','aria-orientation':'vertical',title:i===2?'拖到右侧收起；双击或向左键展开；Home重置，End收起':'拖动调整；方向键微调，Home重置','aria-valuenow':Math.round(actual[i-1]),'aria-valuemin':0,'aria-valuemax':100,onPointerDown:ev=>begin(ev,i-1),onPointerMove:move,onPointerUp:end,onPointerCancel:end,onLostPointerCapture:end,onDoubleClick:()=>i===2&&collapsed?open():reset(),onKeyDown:ev=>key(ev,i-1)},v10('i',{})),v10('section',{className:'v18-study-column v18-column-'+i+(mobile===i?' mobile-selected':''),hidden:i===2&&collapsed,'aria-label':['题目','手写草稿与图片笔记',label][i]},child))))
 );
}

function v18Sources(items,kind){if(kind==='examples')return items.filter(i=>i.kind==='example');const numbered=items.filter(i=>i.kind==='exercise'),groups=items.filter(i=>i.kind==='exercise_group'&&!numbered.some(q=>q.group_title===i.title.replace(/ · (?:完整原页|整组文字)$/,'')));return [...numbered,...groups].sort((a,b)=>a.pdf_page-b.pdf_page||a.id.localeCompare(b.id))}
