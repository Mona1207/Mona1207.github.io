"""Mona contextual portraits, compact home, logical navigation and real map pinch."""
from pathlib import Path
import re
R=Path(__file__).resolve().parents[1]
base=(R/'assets/app-ui-v25.js').read_text();app=base
def extract(name):
 a=base.index('function '+name+'(')
 end=re.search(r'\n(?:(?:async )?function |(?:const|let|var) [A-Za-z_$]|//)',base[a+10:])
 return base[a:a+10+end.start()] if end else base[a:]
def change(s,a,b):
 assert a in s,a[:130]
 return s.replace(a,b)
# Cs is embedded in the original minified import line. Replace its exact span.
a=app.index('function Cs(');b=app.index('const ve=',a);app=app[:a]+app[b:]
app=change(app,'const _s=[','const _s=["practice",')
normal=extract('v18NormalizeRoute')
normal=change(normal,"const aliases=","if(s.settings.current_book==='PHYS'&&route.page==='examples')route={...route,page:'exercises'};if(route.page==='practice')return {...route,source:null};const aliases=")
mapping=extract('V18Tree')
mapping=change(mapping,'roots=v24Roots(s),','roots=v24Roots(s),savedMap=m.useRef(v26ReadMapView(book)),mapMounted=m.useRef(false),')
mapping=change(mapping,"m.useState(roots[0]?.id||'all')","m.useState(()=>roots.some(c=>c.id===savedMap.current.focus)||savedMap.current.focus==='all'?savedMap.current.focus:roots[0]?.id||'all')")
mapping=change(mapping,"[query,setQuery]=m.useState('')","[query,setQuery]=m.useState(()=>typeof savedMap.current.query==='string'?savedMap.current.query:'')")
mapping=change(mapping,"[collapsed,setCollapsed]=m.useState(new Set())","[collapsed,setCollapsed]=m.useState(()=>new Set(Array.isArray(savedMap.current.collapsed)?savedMap.current.collapsed:[]))")
mapping=change(mapping,"[selected,setSelected]=m.useState('')","[selected,setSelected]=m.useState(()=>s.knowledge.some(k=>k.id===savedMap.current.selected)?savedMap.current.selected:'')")
mapping=change(mapping,"[zoom,setZoom]=m.useState(.8)","[zoom,setZoom]=m.useState(()=>v26ClampZoom(Number(savedMap.current.zoom)||.8))")
mapping=change(mapping,";\n m.useEffect",",gestures=useV26MapGestures(viewport,zoom,setZoom);\n m.useEffect")
mapping=change(mapping,"Math.max(.35,(el.clientWidth-24)/layout.width)","Math.max(.2,(el.clientWidth-24)/layout.width)")
start=mapping.index(' m.useEffect(()=>{const el=viewport.current;')
end=mapping.index('\n function toggle',start)
mapping=mapping[:start]+" m.useEffect(()=>{const el=viewport.current;if(!el)return;if(!mapMounted.current&&savedMap.current.zoom){mapMounted.current=true;requestAnimationFrame(()=>{el.scrollLeft=Number(savedMap.current.left)||0;el.scrollTop=Number(savedMap.current.top)||0})}else {mapMounted.current=true;setZoom(Math.min(1,Math.max(.2,(el.clientWidth-24)/layout.width)));el.scrollLeft=0;el.scrollTop=0}},[focus,book]);\n m.useEffect(()=>{const el=viewport.current;if(!el)return;function persist(){v26SaveMapView(book,{focus,query,collapsed:[...collapsed],selected,zoom,left:el.scrollLeft,top:el.scrollTop})}el.addEventListener('scroll',persist,{passive:true});persist();return()=>{persist();el.removeEventListener('scroll',persist)}},[book,focus,query,collapsed,selected,zoom]);"+mapping[end:]
mapping=change(mapping,"Math.max(.35,Math.min(1.8,value))","v26ClampZoom(value)")
mapping=change(mapping,"onPointerDown:down,onPointerMove:move,onPointerUp:()=>{drag.current=null},onPointerCancel:()=>{drag.current=null}","...gestures")
mapping=mapping.replace('拖动空白或滚动查看。','双指捏合缩放，一指拖动查看。')
mapping=change(mapping,"e.jsx(V24ModuleTitle,{title:point.title})","e.jsx(V24ModuleTitle,{title:point.title,scene:'knowledge'})")
practice=extract('V24PracticeBrowser')
practice=change(practice,"v10('h1',{},'知识树习题练习')","e.jsx(V24ModuleTitle,{title:'知识树习题练习',tag:'h1'})")
concept=extract('V24ConceptLauncher')
concept=change(concept,"className:'v24-concept-launcher'","className:'v24-concept-launcher v26-home-card v26-knowledge-card'")
concept=change(concept,"'查看知识讲解'","'进入知识点讲解'")
books=extract('V18Books')
books=change(books,"e.jsx(ee,{size:27}),v10('span',{},b.id==='PHYS'?'物理':b.id==='LA7'?'线代':b.id==='PS3'?'概率':'离散')","e.jsx(V26BookCover,{book:b})")
root=extract('Zs')
root=change(root,'{route,navigate,goRoot,back}=Cs()','{route,navigate,goRoot,back,navError,clearNavError}=Cs()')
root=change(root,"else if(page==='graph')","else if(page==='practice')content=e.jsx(V26PracticePage,{...common,target:id},book);\n else if(page==='graph')")
root=change(root,"account:'本机学习账户'","account:'本机学习账户',practice:'知识树习题练习'")
root=change(root,"className:'v24-site-brand'},e.jsx(V24Logo,{})","className:'v24-site-brand'},e.jsx(V24Logo,{scene:page==='settings'?'settings':page==='graph'?'map':page==='practice'?'practice':'brand',book:page==='home'?book:undefined})")
root=change(root,"error&&v10('div',{className:'error-banner'","(error||navError)&&v10('div',{className:'error-banner'")
root=change(root,"v10('span',{},error),v10('button',{className:'text-button',onClick:()=>setError('')}","v10('span',{},error||navError),v10('button',{className:'text-button',onClick:()=>{setError('');clearNavError()}}")
for name in ['V24Logo','V24ModuleTitle','V18Battery','V18Home','V18Settings','V18Tree','V24PracticeBrowser','V24ConceptLauncher','V18Books','v18NormalizeRoute','Zs']:
 marker='function '+name+'(';assert app.count(marker)==1,name;app=app.replace(marker,'function '+name+'BeforeV26(',1)
cover="function V26BookCover({book:b}){return ['DM2T','LA7','PS3','PHYS'].includes(b.id)?v10('img',{src:'/discrete-math/assets/covers-v26/'+b.id+'.webp',alt:b.title+'封面',loading:'lazy',width:60,height:82}):e.jsx(ee,{size:27})}"
code='\n'.join([(R/'scripts/navigation-v26.js').read_text(),(R/'scripts/gestures-v26.js').read_text(),(R/'scripts/ui-v26.js').read_text(),normal,mapping,practice,concept,books,cover,root])
app=app.replace('const Ys=',code+'\nconst Ys=',1)
(R/'assets/app-ui-v26.js').write_text(app)
index=(R/'index.html').read_text();index=re.sub(r'app-ui-v(?:25|26)\.js\?v=[\d.]+','app-ui-v26.js?v=26',index)
index=re.sub(r'name="ui-version" content="[^"]*"','name="ui-version" content="mona-context-v26"',index)
if 'ui-v26.css' not in index:index=index.replace('</head>','<link rel="stylesheet" href="/discrete-math/assets/ui-v26.css?v=26">\n</head>')
(R/'index.html').write_text(index)
print('Built v26: contextual portraits, three home cards, separate practice tree, logical route stack, map pinch, particle progress and four-column settings.')
