const V30_MAP_LAYOUTS=[['right','向右树状'],['left','向左树状'],['down','向下层级'],['balanced','左右分支'],['outline','紧凑目录']];
function v30MapLayout(tree,collapsed=new Set(),mode='right'){
 const base=v24MapLayout(tree,collapsed);
 function transform(layout,fn){const nodes=layout.nodes.map(n=>({...n,...fn(n)})),byId=new Map(nodes.map(n=>[n.id,n]));return {...layout,nodes,edges:layout.edges.map(e=>({source:byId.get(e.source.id),target:byId.get(e.target.id)}))}}
 if(mode==='left')return transform(base,n=>({x:base.width-n.x-n.w}));
 if(mode==='down'){
  const nodes=[],edges=[];let maxDepth=0;
  function measure(n,depth){const children=collapsed.has(n.id)?[]:n.children;const node={...n,depth,w:n.type==='book'?210:264,h:n.type==='knowledge'?132:112,visibleChildren:children.map(c=>measure(c,depth+1))};node.span=Math.max(node.w,node.visibleChildren.reduce((v,c)=>v+c.span,0)+Math.max(0,children.length-1)*30);return node}
  function place(n,left,parent){maxDepth=Math.max(maxDepth,n.depth);const node={...n,x:left+(n.span-n.w)/2,y:24+n.depth*194};nodes.push(node);if(parent)edges.push({source:parent,target:node});let x=left+(n.span-n.visibleChildren.reduce((v,c)=>v+c.span,0)-Math.max(0,n.visibleChildren.length-1)*30)/2;for(const child of n.visibleChildren){place(child,x,node);x+=child.span+30}}
  const root=measure(tree,0);place(root,24,null);return {nodes,edges,width:root.span+48,height:maxDepth*194+180};
 }
 if(mode==='outline'){
  const nodes=[],edges=[];let y=24,maxX=0;
  function visit(n,depth,parent){const node={...n,x:24+depth*66,y,w:Math.max(264,380-depth*20),h:n.type==='knowledge'?112:88};nodes.push(node);if(parent)edges.push({source:parent,target:node});maxX=Math.max(maxX,node.x+node.w);y+=node.h+18;if(!collapsed.has(n.id))for(const child of n.children)visit(child,depth+1,node)}
  visit(tree,0,null);return {nodes,edges,width:maxX+24,height:y+6};
 }
 if(mode==='balanced'&&!collapsed.has(tree.id)&&tree.children.length===1&&!collapsed.has(tree.children[0].id)&&tree.children[0].children.length>1){
  const layout=v30MapLayout(tree.children[0],collapsed,'balanced'),shifted=transform(layout,n=>({y:n.y+160})),pivot=shifted.nodes[0],book={...tree,x:pivot.x+(pivot.w-210)/2,y:pivot.y-160,w:210,h:112};return {nodes:[book,...shifted.nodes],edges:[{source:book,target:pivot},...shifted.edges],width:layout.width,height:layout.height+160};
 }
 if(mode==='balanced'&&!collapsed.has(tree.id)&&tree.children.length>1){
  const half=Math.ceil(tree.children.length/2),leftBase=v24MapLayout({...tree,children:tree.children.slice(0,half)},collapsed),rightBase=v24MapLayout({...tree,children:tree.children.slice(half)},collapsed),height=Math.max(leftBase.height,rightBase.height),rootX=leftBase.width-24-leftBase.nodes[0].w;
  const left=transform(leftBase,n=>({x:leftBase.width-n.x-n.w,y:n.y+(height-leftBase.height)/2})),right=transform(rightBase,n=>({x:n.x+rootX-24,y:n.y+(height-rightBase.height)/2}));
  left.nodes[0].children=tree.children;const nodes=left.nodes.concat(right.nodes.slice(1)),byId=new Map(nodes.map(n=>[n.id,n]));return {nodes,edges:left.edges.concat(right.edges).map(e=>({source:byId.get(e.source.id),target:byId.get(e.target.id)})),width:rootX-24+rightBase.width,height};
 }
 return base;
}
function v30MapEdge(a,b,mode){
 if(mode==='outline')return 'M '+(a.x+18)+' '+(a.y+a.h)+' V '+(b.y+b.h/2)+' H '+b.x;
 if(mode==='down'||Math.abs(a.x+a.w/2-b.x-b.w/2)<1){const x=a.x+a.w/2,y=a.y+a.h,xx=b.x+b.w/2,yy=b.y,mid=(y+yy)/2;return 'M '+x+' '+y+' C '+x+' '+mid+', '+xx+' '+mid+', '+xx+' '+yy}
 const left=b.x<a.x,x=left?a.x:a.x+a.w,y=a.y+a.h/2,xx=left?b.x+b.w:b.x,yy=b.y+b.h/2,mid=(x+xx)/2;return 'M '+x+' '+y+' C '+mid+' '+y+', '+mid+' '+yy+', '+xx+' '+yy;
}
let v30SwitchBusy=false;
async function v14Switch(id){
 if(v30SwitchBusy||!['DM2T','DM2','LA7','PS3','PHYS'].includes(id))return false;
 v30SwitchBusy=true;
 try{
  await v20FlushInk();
  if(localStorage.getItem('zhixu-current-book')===id&&window.monaGoHome){await window.monaGoHome();return true}
  localStorage.setItem('zhixu-current-book',id);
  history.replaceState({zx:true,zxV26:true,zxTrail:[],zxScroll:0},'','#home');
  window.location.reload();return true;
 }catch(err){window.dispatchEvent(new CustomEvent('mona-navigation-error',{detail:'教材未切换：草稿或教材设置尚未保存，请重试。'+err.message}));return false}
 finally{v30SwitchBusy=false}
}
