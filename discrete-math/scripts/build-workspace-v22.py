"""Build the unbounded notebook over the checked physics release."""
from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
def replace(s,a,b):
    assert a in s,a[:120]
    return s.replace(a,b)

ink=(R/'scripts/ink-v20.js').read_text()
ink=replace(ink,"v20Clamp((ev.clientX-rect.left-view.x)/view.scale/paper.width,0,1),v20Clamp((ev.clientY-rect.top-view.y)/view.scale/paper.height,0,1)","(ev.clientX-rect.left-view.x)/view.scale/paper.width,(ev.clientY-rect.top-view.y)/view.scale/paper.height")
ink=replace(ink,"p.some(n=>!Number.isFinite(n)||n<0||n>1)","p.some(n=>!Number.isFinite(n))||p[2]<0||p[2]>1||draft.version<3&&(p[0]<0||p[0]>1||p[1]<0||p[1]>1)")
ink=replace(ink,"image.x<0||image.y<0||image.w<=0||image.h<=0||image.x+image.w>1.001||image.y+image.h>1.001","image.w<=0||image.h<=0||draft.version<3&&(image.x<0||image.y<0||image.x+image.w>1.001||image.y+image.h>1.001)")
a=ink.index('function v20ImageLayer(');b=ink.index('function V16Handwriting(',a)
ink=ink[:a]+'''function v20ImageLayer(image,paper,view,viewport){const w=viewport.width/view.scale*.8,h=w*image.height/image.width;return {id:crypto.randomUUID(),data:image.data,x:(-view.x+viewport.width*.08)/view.scale/paper.width,y:(-view.y+viewport.height*.08)/view.scale/paper.height,w:w/paper.width,h:h/paper.height}}
function v22InkBounds(draft){const p=draft.paper,boxes=[];for(const s of draft.strokes)for(const q of s.points){const r=s.width*p.width;boxes.push([q[0]*p.width-r,q[1]*p.height-r,q[0]*p.width+r,q[1]*p.height+r])}for(const i of draft.images||[])boxes.push([i.x*p.width,i.y*p.height,(i.x+i.w)*p.width,(i.y+i.h)*p.height]);if(!boxes.length)return {x:0,y:0,width:960,height:1280};let x=Infinity,y=Infinity,right=-Infinity,bottom=-Infinity;for(const b of boxes){x=Math.min(x,b[0]);y=Math.min(y,b[1]);right=Math.max(right,b[2]);bottom=Math.max(bottom,b[3])}return {x:x-24,y:y-24,width:Math.max(80,right-x+48),height:Math.max(80,bottom-y+48)}}
''' + ink[b:]
ink=replace(ink,"label='手写草稿'","label='手写草稿',headingExtra")
ink=replace(ink,'version:2,paper','version:3,paper')
ink=replace(ink,'dpr=Math.min(window.devicePixelRatio||1,2)','dpr=Math.max(1,window.devicePixelRatio||1)')
a=ink.index(' function paint(){');b=ink.index(' function repaint()',a)
ink=ink[:a]+''' function paint(){const c=canvas.current;if(!c)return;const {width:w,height:h,dpr}=size.current,ctx=c.getContext('2d'),p=draft.current.paper,v=view.current;ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);ctx.fillStyle='#fff';ctx.fillRect(0,0,w,h);ctx.save();ctx.translate(v.x,v.y);ctx.scale(v.scale,v.scale);const left=-v.x/v.scale,top=-v.y/v.scale,right=left+w/v.scale,bottom=top+h/v.scale;
 if(grid){const step=32*Math.max(1,Math.ceil(8/(32*v.scale)));ctx.strokeStyle='#e5e9e4';ctx.lineWidth=.6/v.scale;ctx.beginPath();for(let x=Math.floor(left/step)*step;x<=right;x+=step){ctx.moveTo(x,top);ctx.lineTo(x,bottom)}for(let y=Math.floor(top/step)*step;y<=bottom;y+=step){ctx.moveTo(left,y);ctx.lineTo(right,y)}ctx.stroke()}
 for(const layer of draft.current.images){let img=imageCache.current.get(layer.data);if(!img){img=new Image();imageCache.current.set(layer.data,img);img.onload=repaint;img.src=layer.data}if(img.complete&&img.naturalWidth)ctx.drawImage(img,layer.x*p.width,layer.y*p.height,layer.w*p.width,layer.h*p.height)}ctx.restore();
 let off=inkCache.current;if(!off){off=document.createElement('canvas');inkCache.current=off}if(off.width!==c.width||off.height!==c.height){off.width=c.width;off.height=c.height}const ic=off.getContext('2d');ic.setTransform(1,0,0,1,0,0);ic.clearRect(0,0,off.width,off.height);ic.setTransform(dpr*v.scale,0,0,dpr*v.scale,dpr*v.x,dpr*v.y);v20PaintInk(ic,draft.current.strokes,p);if(active.current?.stroke)v20PaintInk(ic,[active.current.stroke],p);ctx.setTransform(1,0,0,1,0,0);ctx.drawImage(off,0,0);ctx.setTransform(dpr,0,0,dpr,0,0);
 if(active.current?.lasso?.length){ctx.save();ctx.translate(v.x,v.y);ctx.scale(v.scale,v.scale);ctx.strokeStyle='#496f5c';ctx.fillStyle='#496f5c18';ctx.lineWidth=1.5/v.scale;ctx.setLineDash([6/v.scale,4/v.scale]);ctx.beginPath();active.current.lasso.forEach((q,i)=>i?ctx.lineTo(q[0]*p.width,q[1]*p.height):ctx.moveTo(q[0]*p.width,q[1]*p.height));ctx.closePath();ctx.fill();ctx.stroke();ctx.restore()}}
''' + ink[b:]
ink=replace(ink,"function fit(){const p=draft.current.paper,w=size.current.width;setView({scale:v20Clamp((w-16)/p.width,.15,2),x:8,y:8})}","function fit(){const b=v22InkBounds(draft.current),w=size.current.width,h=size.current.height,scale=v20Clamp(Math.min((w-24)/b.width,(h-24)/b.height),.15,2);setView({scale,x:(w-b.width*scale)/2-b.x*scale,y:12-b.y*scale})}")
ink=replace(ink,"function fit(){const b=v22InkBounds(draft.current)","function fit(){if(!draft.current.strokes.length&&!draft.current.images.length){setView({scale:1,x:16,y:16});return}const b=v22InkBounds(draft.current)")
ink=replace(ink,"const restored=structuredClone(v20ValidateDraft(image.draft_snapshot));change(restored)","const restored={...structuredClone(v20ValidateDraft(image.draft_snapshot)),version:3};change(restored)")
ink=replace(ink,"setStatus('双指缩放或移动 · 手写笔书写')","setStatus('无界笔记 · 双指缩放或移动')")
a=ink.index(' async function fullImage(');b=ink.index(' async function saveImageNote()',a)
ink=ink[:a]+''' async function fullImage(value=currentDraft()){const current=structuredClone(value),p=current.paper,b=v22InkBounds(current),scale=Math.min(2,8192/b.width,8192/b.height,Math.sqrt(32000000/(b.width*b.height))),out=document.createElement('canvas');out.width=Math.ceil(b.width*scale);out.height=Math.ceil(b.height*scale);const ctx=out.getContext('2d');ctx.fillStyle='#fff';ctx.fillRect(0,0,out.width,out.height);ctx.setTransform(scale,0,0,scale,-b.x*scale,-b.y*scale);for(const layer of current.images){let image=imageCache.current.get(layer.data);if(!image||!image.complete){image=await new Promise((resolve,reject)=>{const img=new Image();img.onload=()=>resolve(img);img.onerror=()=>reject(Error('图片未能读取'));img.src=layer.data})}ctx.drawImage(image,layer.x*p.width,layer.y*p.height,layer.w*p.width,layer.h*p.height)}const off=document.createElement('canvas');off.width=out.width;off.height=out.height;const ic=off.getContext('2d');ic.setTransform(scale,0,0,scale,-b.x*scale,-b.y*scale);v20PaintInk(ic,current.strokes,p);ctx.setTransform(1,0,0,1,0,0);ctx.drawImage(off,0,0);return out}
''' + ink[b:]
a=ink.index("  v10('header',{className:'v20-ink-tools'}");b=ink.index("  v10('div',{className:'v16-ink-surface",a)
ink=ink[:a]+'''  v10('header',{className:'v22-note-heading'},v10('b',{},'演算与笔记'),
   v10('div',{className:'v22-inline-tools'},V20_COLORS.map(([c,name])=>v10('button',{key:c,className:'v20-color','aria-label':name,'aria-pressed':color===c&&!['erase','lasso'].includes(tool),style:{'--ink-color':c},onClick:()=>{setColor(c);setTool('fountain')}})),
   v10('button',{'aria-pressed':tool==='erase',onClick:()=>setTool(tool==='erase'?'fountain':'erase')},'橡皮'),
   v10('details',{className:'v22-size-picker'},v10('summary',{},width+' px'),v10('label',{},'粗细',v10('input',{type:'range',min:1,max:20,step:.5,value:width,'aria-label':'笔迹大小',onChange:ev=>setWidth(Number(ev.target.value))}))),
   v10('button',{'aria-pressed':tool==='lasso',onClick:()=>setTool(tool==='lasso'?'fountain':'lasso')},'套索'),
   v10('button',{disabled:!history.current.length,'aria-label':'撤销草稿操作',onClick:undoInk},'撤销'),v10('button',{disabled:!redo.current.length,'aria-label':'重做草稿操作',onClick:redoInk},'重做')),headingExtra),
''' + ink[b:]
ink=replace(ink,"'适应宽度'","'查看全部'")
ink=replace(ink,"'双指缩放、移动'","'无界画布 · 双指移动'")
ink=replace(ink,"role:'status',title:status","role:'status',title:status")
(R/'scripts/ink-v22.js').write_text(ink)

study=(R/'scripts/study-v20.js').read_text()
study=replace(study,"[revealed,setRevealed]=m.useState(false)","[revealed,setRevealed]=m.useState(false),[selectedKnowledge,setSelectedKnowledge]=m.useState(item.knowledge_ids[0]||''),[rightView,setRightView]=m.useState('knowledge'),[supportSignal,setSupportSignal]=m.useState(0)")
study=replace(study," function save(changes)"," m.useEffect(()=>{setRevealed(false);setRightView('knowledge');setSelectedKnowledge(item.knowledge_ids[0]||'');setFinishedGroup(false)},[item.id]);\n function showKnowledge(id){setSelectedKnowledge(id);setRightView('knowledge');setSupportSignal(n=>n+1)}\n function save(changes)")
study=replace(study,"v10('small',{},'原书第 '+item.printed_page+' 页')","v10('small',{},item.source_label||('原书第 '+item.printed_page+' 页')),item.source_image&&v10('button',{className:'text-button',onClick:()=>readSource(item.image_number)},'原图')")
study=replace(study,"onClick:()=>pick(k.id,'concept')},k.title,e.jsx(S,{size:10})","'aria-pressed':rightView==='knowledge'&&selectedKnowledge===k.id,onClick:()=>showKnowledge(k.id)},k.title,e.jsx(S,{size:10})")
study=replace(study,"setRevealed(true);setRevealSignal","setRevealed(true);setRightView('solution');setRevealSignal")
study=replace(study,"const center=v10(e.Fragment,{},\n  v10('header',{className:'v18-column-heading'},v10('b',{},'演算与笔记'),v10('div',{className:'mini-segments'},[['draft','草稿'],['notes','图片笔记']].map(([id,title])=>v10('button',{key:id,'aria-pressed':middle===id,onClick:()=>setMiddle(id)},title)))),","const noteTabs=v10('div',{className:'mini-segments'},[['draft','草稿'],['notes','图片笔记']].map(([id,title])=>v10('button',{key:id,'aria-pressed':middle===id,onClick:()=>setMiddle(id)},title)));\n const center=v10(e.Fragment,{},\n  middle==='notes'&&v10('header',{className:'v18-column-heading'},v10('b',{},'演算与笔记'),noteTabs),")
study=replace(study,"label:'本题手写草稿'","label:'本题手写草稿',headingExtra:noteTabs")
study=replace(study,"v10('b',{},revealed?'答案与解析':'对应知识讲解')","v10('b',{},rightView==='solution'?'答案与解析':'知识点讲解'),revealed&&v10('nav',{className:'mini-segments'},[['knowledge','知识'],['solution','解析']].map(([id,title])=>v10('button',{key:id,'aria-pressed':rightView===id,onClick:()=>setRightView(id)},title)))")
study=replace(study,"revealed?e.jsx(V19Solution,{item:textItem}):e.jsx(V19KnowledgeSupport,{points,state:s,pick})","rightView==='solution'&&revealed?e.jsx(V19Solution,{item:textItem},item.id):e.jsx(V19KnowledgeSupport,{points,state:s,pick:showKnowledge,selected:selectedKnowledge,onSelect:showKnowledge,readSource})")
study=replace(study,"revealed&&v10('footer'","revealed&&rightView==='solution'&&v10('footer'")
study=replace(study,"finished:revealed,revealSignal,question:item.id","finished:revealed,revealSignal,supportSignal,question:item.id")
# Only replace the active study component and split; preserve the physics source hooks.
study=study[:study.index('const v19ExerciseCache=')] + (R/'scripts/study-v20.js').read_text().split('function v19Ratio',1)[1]
study=study.replace("\n(value){if(!Array", "\nfunction v19Ratio(value){if(!Array",1)
# The split functions are reused with larger default note width and intrinsic-safe tracks.
study=replace(study,'[34,32,34]','[30,42,28]')
study=replace(study,"ratioKey='zhixu-three-columns-v18-'","ratioKey='zhixu-three-columns-v22-'")
study=replace(study,'question}){','question,supportSignal=0}){')
study=replace(study," m.useEffect(()=>{if(finished)open()},[finished,revealSignal,question]);"," m.useEffect(()=>{if(finished)open()},[finished,revealSignal,question]);\n m.useEffect(()=>{if(supportSignal>0)open()},[supportSignal]);")
study=replace(study,"actual[0]+'fr 10px '+actual[1]+'fr 10px '+actual[2]+'fr'","'minmax(0,'+actual[0]+'fr) 10px minmax(0,'+actual[1]+'fr) 10px minmax(0,'+actual[2]+'fr)'")
(R/'scripts/study-v22.js').write_text(study)

app=(R/'assets/app-ui-v21.js').read_text()
for name in ['V16Handwriting','v20ValidateDraft','v20PaperPoint','v20ImageLayer','V18Study','V18Split','v19Ratio','v19FitRatios','v19MoveRatio','v18Sources','V19KnowledgeSupport','V18Concept','v17ValidateAssets']:
    marker='function '+name+'('
    assert app.count(marker)==1,(name,app.count(marker))
    app=app.replace(marker,'function '+name+'BeforeV22(',1)
# Reuse the old validation for metadata and image bytes, after validating real vector coordinates.
app=replace(app,"p.some(n=>!Number.isFinite(n)||n<0||n>1))throw Error('手写笔迹坐标无效')","p.some(n=>!Number.isFinite(n))||p[2]<0||p[2]>1||ink.value.version<3&&(p[0]<0||p[0]>1||p[1]<0||p[1]>1))throw Error('手写笔迹坐标无效')")
app=replace(app,"V18Concept,{state,k:point,pick}","V18Concept,{state,k:point,pick,readSource}")
parts=[]
for name in ['v20PaperPoint','v20ValidateDraft','v20ImageLayer','v22InkBounds','V16Handwriting']:
    a=ink.index('function '+name+'(')
    match=re.search(r'\n(?:async )?function ',ink[a+10:])
    b=a+10+match.start() if match else len(ink)
    parts.append(ink[a:b])
code='\n'.join(parts+[study,(R/'scripts/knowledge-v22.js').read_text()])
app=app.replace('const Ys=',code+'\nconst Ys=',1)
(R/'assets/app-ui-v22.js').write_text(app)
index=re.sub(r'app-ui-v(?:20|21|22)\.js\?v=[\d.]+','app-ui-v22.js?v=22.1',(R/'index.html').read_text())
index=re.sub(r'name="ui-version" content="[^"]*"','name="ui-version" content="textbook-infinite-notes-v22.2"',index)
if 'ui-v22.css' not in index:index=index.replace('</head>','<link rel="stylesheet" href="/discrete-math/assets/ui-v22.css?v=22.2">\n</head>')
index=re.sub(r'ui-v22\.css\?v=[\d.]+','ui-v22.css?v=22.2',index)
(R/'index.html').write_text(index)
print('Built v22: selected in-place knowledge, vector infinite notes and bounded responsive tracks.')
