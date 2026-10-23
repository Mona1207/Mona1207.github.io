const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),cp=require('node:child_process');
const deps=process.env.MONA_QA_DEPENDENCIES;
if(!deps)throw Error('Set MONA_QA_DEPENDENCIES to a directory containing katex, react and react-dom');
const katex=require(path.join(deps,'katex')),React=require(path.join(deps,'react'));
const {renderToStaticMarkup}=require(path.join(deps,'react-dom/server'));
const root=path.resolve(__dirname,'../..'),data=path.join(root,'data');
const errors=[];let formulas=0,changedFields=0;
for(const fn of ['exercises-DM2T-v20.json','examples-DM2T-ready-v17.json','exercises-LA7-v20.json','examples-LA7-ready-v17.json','exercises-PS3-v20.json','examples-PS3-ready-v17.json','exercises-PHYS-v29.json']){
 const current=JSON.parse(fs.readFileSync(path.join(data,fn),'utf8'));
 const baseline=JSON.parse(cp.execFileSync('git',['show','7959c4f6f254284cfde52e43b42cdb69f6e0d425:discrete-math/data/'+fn],{cwd:path.resolve(root,'..'),maxBuffer:12e6}).toString());
 const byId=new Map(baseline.items.map(x=>[x.id,x]));
 if(current.items.length!==baseline.items.length)throw Error('Question count changed: '+fn);
 for(const q of current.items){
  if(!byId.has(q.id))throw Error('Question ID changed: '+q.id);
  for(const field of ['prompt','solution','explanation','common_mistakes']){
   const texts=Array.isArray(q[field])?q[field]:[q[field]||''];
   const old=byId.get(q.id)[field]||[];
   for(const text of texts){
    if(old.includes(text))continue;changedFields++;
    if(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(text))errors.push({id:q.id,field,error:'Unexpected control character'});
    for(const m of text.matchAll(/\$\$([\s\S]*?)\$\$|(?<!\$)\$(?!\$)([^$\n]+?)\$(?!\$)/g)){
     formulas++;
     try{katex.renderToString(m[1]??m[2],{displayMode:m[1]!=null,throwOnError:true,strict:'ignore'});}catch(e){errors.push({id:q.id,field,formula:m[1]??m[2],error:e.message});}
    }
   }
  }
 }
}
const context={v10:React.createElement,e:{jsx:React.createElement},V17Markdown:({text})=>React.createElement('div',{},text)};
vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(__dirname,'solution_view.js'),'utf8'),context);
for(const type of ['exercise','example']){
 const html=renderToStaticMarkup(React.createElement(context.V33SolutionSteps,{item:{kind:type,explanation:['**第1步：建立模型。** 正文推导'],solution:'结果',common_mistakes:['不要漏掉约束']}}));
 if(!html.includes('易错点提示')||!html.includes('正文推导')||!html.includes('完整解答与结果'))throw Error('Solution sections missing');
 if((html.match(/第 1 步/g)||[]).length!==1)throw Error('Repeated step label');
}
fs.writeFileSync(path.join(data,'solution-math-validation.json'),JSON.stringify({formulas_checked:formulas,new_text_fields:changedFields,error_count:errors.length,errors},null,2)+'\n');
console.log(JSON.stringify({formulas_checked:formulas,new_text_fields:changedFields,error_count:errors.length,errors:errors.slice(0,12)}));
if(errors.length)process.exitCode=1;
