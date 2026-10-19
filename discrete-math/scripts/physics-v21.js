function v21SourceOrder(item){return item.sort_order??item.pdf_page??item.source_pages?.[0]??0}
function As(props){
 if(props.state.settings.current_book!=='PHYS')return e.jsx(AsBeforeV21,props);
 const {state:s,go,readSource}=props,book=v14Book(s);
 return v10('section',{className:'v16-books'},
  v10('header',{className:'v16-page-heading'},v10('div',{},v10('h1',{},'我的教材'),v10('p',{},'课程记录分别保存'))),
  v10('div',{className:'v16-book-cards'},s.books.map(b=>v10('button',{key:b.id,className:'v16-book '+(b.id===book.id?'selected':''),'aria-pressed':b.id===book.id,onClick:()=>b.id!==book.id&&v14Switch(b.id)},v10('span',{className:'v16-mini-cover',style:{'--cover':b.id==='PHYS'?'#526a91':'#506b72'}},b.id==='PHYS'?'选题':'教材'),v10('span',{},v10('b',{},b.short_title||b.title),v10('small',{},b.edition||''),v10('small',{},b.id===book.id?'正在学习':'点击切换'))))),
  v10('div',{className:'v16-book-body'},v10('section',{className:'panel'},v10('h2',{},'本次上传的物理习题'),v10('p',{},'共 19 道题，按原题号分组。题号“11-12”表示习题十一第 12 题。'),v10('div',{className:'v16-book-outline'},s.chapters.filter(c=>!c.parent_id).map(c=>v10('button',{key:c.id,onClick:()=>go('exercises',c.id)},v10('b',{},c.title),v10('small',{},c.question_count+' 道题'),e.jsx(S,{size:12}))))),
   v10('aside',{className:'panel v16-book-actions'},v10('h2',{},book.title),v10('p',{},s.knowledge.length+' 个关联知识点 · 19 道上传题目'),v10('p',{className:'caption'},'物理题库仅收录这批图片中的题目。题干已转为文字，解析已独立核对；原图中的条件缺失或歧义在相应题内说明。'),v10('button',{className:'primary',onClick:()=>go('exercises')},'开始物理习题'),v10('button',{className:'quiet',onClick:()=>go('graph')},'查看关联知识'),v10('button',{className:'quiet',onClick:()=>readSource(1)},'查看上传原图（含手写解答）'))));
}
function V16Reader(props){return props.state.settings.current_book==='PHYS'?e.jsx(V21PhysicsSources,props):e.jsx(V16ReaderBeforeV21,props)}
function V21PhysicsSources({page=1,state:s}){
 const {items,error}=useV19Exercises('PHYS'),images=[...new Map(items.map(i=>[i.image_number,{number:i.image_number,name:i.source_image,url:i.source_image_url}])).values()].sort((a,b)=>a.number-b.number),[selected,setSelected]=m.useState(page),image=images.find(i=>i.number===selected)||images[0];
 m.useEffect(()=>setSelected(page),[page]);
 return v10('section',{className:'v16-reader v21-source-reader'},v10('header',{},v10('b',{},'上传原图'),v10('span',{},'原图含手写解答'),v10('select',{'aria-label':'选择物理原题图',value:image?.number||'',onChange:ev=>setSelected(Number(ev.target.value))},images.map(i=>v10('option',{key:i.number,value:i.number},i.name)))),
  error&&v10('p',{role:'alert'},error),image?v10('a',{href:image.url,target:'_blank',rel:'noreferrer',title:'在新页面查看原始图片'},v10('img',{src:image.url,alt:'上传题图 '+image.name,style:{width:'100%',height:'auto',display:'block'}})):v10('p',{role:'status'},'正在读取题图…'));
}
