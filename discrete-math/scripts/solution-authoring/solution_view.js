function V33SolutionSteps({item}){
 const steps=Array.isArray(item.explanation)?item.explanation:[];
 const answer=Array.isArray(item.solution)?item.solution.join('\n\n'):item.solution||'';
 const mistakes=Array.isArray(item.common_mistakes)?item.common_mistakes:[];
 return v10('section',{className:'v33-complete-solution'},
  steps.map((value,i)=>{
   const text=typeof value==='string'?value:String(value?.body||'');
   const heading=text.match(/^\*\*([^*]+)\*\*\s*/);
   const title=heading?heading[1].replace(/^(?:第\s*\d+\s*步\s*[:：.、]?|\d+[.、：])\s*/,''):'分步推导';
   return v10('section',{className:'v33-solution-step',key:i},
    v10('h3',{},v10('span',{className:'solution-step-number'},'第 '+(i+1)+' 步'),title),
    e.jsx(V17Markdown,{text:heading?text.slice(heading[0].length):text}));
  }),
  !steps.length&&v10('p',{className:'v19-answer-missing'},'本题的逐步推导尚待补充。'),
  answer&&v10('section',{className:'v33-solution-step solution-final-answer'},v10('h3',{},'完整解答与结果'),e.jsx(V17Markdown,{text:answer})),
  mistakes.length>0&&v10('aside',{className:'solution-mistakes','aria-label':'易错点提示'},
   v10('h3',{},'易错点提示'),
   v10('ol',{},mistakes.map((text,i)=>v10('li',{key:i},e.jsx(V17Markdown,{text:String(text)})))))
 );
}
