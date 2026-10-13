practiceSummary(id){
 const all=this.questions(id).filter(q=>q.verification==='verified');
 const groups=new Set(all.map(practiceGroup));
 const seen=new Set(this.snapshot.attempts.map(a=>practiceGroup(this.getQuestion(a.question_id))));
 const fresh=this.sessionQuestions(id,'knowledge',50);
 return {distinct_count:groups.size,practiced_count:[...groups].filter(g=>seen.has(g)).length,new_count:fresh.length};
}
sessionQuestions(id,mode,limit){
 let pool=this.questions(id).filter(q=>this.eligible(q));
 const review=mode==='wrong'||mode==='review';
 if(mode==='wrong')pool=pool.filter(q=>this.snapshot.wrong.some(a=>a.question_id===q.id&&!a.resolved));
 if(mode==='review')pool=pool.filter(q=>this.snapshot.reviews.some(a=>a.question_id===q.id&&a.due_at<=this.now()));
 if(mode==='weak')pool=pool.filter(q=>(this.indexes.links.get(q.id)||[]).some(a=>this.knowledge(a.knowledge_id).effective_mastery<60));
 const seen=new Set(this.snapshot.attempts.map(a=>practiceGroup(this.getQuestion(a.question_id))));
 if(!review)pool=pool.filter(q=>!seen.has(practiceGroup(q)));
 // Prefer textbook/manual representatives. Never refill with parameter variants.
 pool.sort((a,b)=>Number(a.source_type!=='textbook')-Number(b.source_type!=='textbook')||Number(!!a.meta.generator)-Number(!!b.meta.generator)||a.difficulty-b.difficulty||a.id.localeCompare(b.id));
 const groups=new Set(),result=[];
 for(const q of pool){const key=practiceGroup(q);if(!groups.has(key)){groups.add(key);result.push(q);}}
 return result.slice(0,limit);
}
resumeSession(session){
 if(!session)return null;
 // Old chapter sessions stay in history, but are no longer active learning flows.
 if(!this.seed.knowledge.some(k=>k.id===session.target_id)&&!['wrong','review'].includes(session.mode))return null;
 const attempts=this.snapshot.attempts.filter(a=>a.session_id===session.id);
 const own=new Set(attempts.map(a=>a.question_id));
 const other=new Set(this.snapshot.attempts.filter(a=>a.session_id!==session.id).map(a=>practiceGroup(this.getQuestion(a.question_id))));
 const groups=new Set(),ids=session.assistance.authorized_questions;
 // Keep already-submitted questions visible for evaluation/history, but drop
 // unattempted variants of any submitted or earlier-session method.
 for(const a of attempts)groups.add(practiceGroup(this.getQuestion(a.question_id)));
 const selected=ids.filter(id=>{if(own.has(id))return true;const g=practiceGroup(this.getQuestion(id));if(groups.has(g)||other.has(g)&&!['wrong','review'].includes(session.mode))return false;groups.add(g);return true;});
 if(!selected.length)return null;
 return {session:{...session,question_count:selected.length},questions:selected.map(id=>this.publicQuestion(this.getQuestion(id),true)),attempts};
}
