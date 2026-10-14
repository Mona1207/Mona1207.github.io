"""Independent witness evaluator retained from the original mathematical audit."""
import math, itertools

def ev(e,p,q):
    return {'p':p,'q':q,'¬p':not p,'¬q':not q,'p→q':p<=q,'q→p':q<=p,'p∧q':p and q,'p∨q':p or q,'p↔q':p==q,'p⊕q':p!=q}[e]

def reachable(n,E):
    adj={i:set() for i in range(1,n+1)}
    for a,b in E:adj[a].add(b);adj[b].add(a)
    todo=[1];vis=set()
    while todo:
        v=todo.pop()
        if v not in vis:vis.add(v);todo.extend(adj[v]-vis)
    return len(vis)==n

def calc(q):
    ch=int(q['chapter_id'][4:6]);k=int(q['id'].split('-')[3]);p=q['meta']['parameters'];f=q['meta']['family_id'].rsplit('-',1)[1]
    if ch==1:
        if 'imperative' in p:return not p['imperative']
        if 'claimed' in p:return p['a']+p['b']==p['claimed']
        return ev(p['expr'],p['p'],p['q'])
    if ch==2:
        if 'conjunction' in p:return not (p['p'] and p['q'] if p['conjunction'] else p['p'] or p['q'])
        return list(p['assignment']) in p['rows'] if 'assignment' in p else len(set(map(tuple,p['rows'])))
    if ch==3:return all(not all(ev(x,a,b) for x in p['premises']) or ev(p['conclusion'],a,b) for a,b in itertools.product([False,True],repeat=2))
    if ch in (4,5):
        if 'candidate' in p:return p['candidate'] in p['free']
        if 'predicate' in p:
            vals=[{'大于':x>p['cut'],'小于':x<p['cut'],'等于':x==p['cut']}[p['predicate']] for x in p['domain']]
            v=all(vals) if p['universal'] else any(vals)
            return not v if p['negate'] else v
        r=lambda a,b: {'小于':a<b,'等于':a==b,'和等于':a+b==p['cut']}[p['relation']]
        return all(any(r(a,b) for b in p['domain']) for a in p['domain']) if p['order'] else any(all(r(a,b) for a in p['domain']) for b in p['domain'])
    if ch==6:
        if k==1:return p['x'] in p['A'] if 'x' in p else set(p['B'])<=set(p['A'])
        if k==2:return len(list(itertools.chain.from_iterable(itertools.combinations(range(p['n']),r) for r in range(p['n']+1))))-int(p['proper'])
        A,B=set(p['A']),set(p['B']);return len({'并':A|B,'交':A&B,'差':A-B,'对称差':A^B}[p['op']])
    if ch==7:
        R=set(map(tuple,p.get('R',[])))
        if k==1:return p['a']*p['b'] if 'a' in p else p['x']+p['y']
        if k==2:return [2**(p['n']**2),p['n']**2-p['r'],p['n']][p['op']]
        if k==3:return int((p['a'],p['b']) in R) if p['cell'] else sum(a==p['a'] for a,b in R)
        if k==4:
            n=p['property']
            return {'自反':all((a,a) in R for a in (1,2,3)),'反自反':all((a,a) not in R for a in (1,2,3)),'对称':R=={(b,a) for a,b in R},'反对称':all(a==b or (b,a) not in R for a,b in R),'传递':all((a,c) in R for a,b,c in itertools.product((1,2,3),repeat=3) if (a,b) in R and (b,c) in R)}[n]
        if k==5:return len({(a,c) for a,b,c in itertools.product((1,2,3),repeat=3) if (a,b) in R and [b,c] in p['S']}) if 'S' in p else (p['b'],p['a']) in R
        if k==6:
            typ=p['closure']
            if typ=='reflexive':return len(R|{(x,x) for x in (1,2,3)})
            if typ=='symmetric':return len(R|{(b,a) for a,b in R})
            M=[[int((a,b) in R) for b in (1,2,3)] for a in (1,2,3)]
            for t in range(3):
                for a in range(3):
                    for b in range(3):M[a][b]=M[a][b] or (M[a][t] and M[t][b])
            return sum(sum(row) for row in M)
        if k==7:return sum((a-p['x'])%p['m']==0 for a in p['A']) if p['one'] else len({a%p['m'] for a in p['A']})
        A=p['A'];op=p['op']
        if op==2:return any(all(a%b==0 for b in A) for a in A)
        return sum(not any(a!=b and (b%a==0 if op==0 else a%b==0) for b in A) for a in A)
    if ch==8:
        if k==1:return all(sum(x==a for x,y in p['F'])==1 for a in p['A']) if 'F' in p else p['m']**p['n']
        inj=len(set(p['outputs']))==p['n'];sur=set(p['outputs'])==set(range(1,p['m']+1));return {'单射':inj,'满射':sur,'双射':inj and sur}[p['type']]
    if ch==9:
        if k==1:return True
        return any((p['x']*y)%p['mod']==1 for y in range(p['mod'])) if p['mult'] else next(y for y in range(p['mod']) if (p['x']+y)%p['mod']==0)
    if ch==10:
        if k==1:return not p['mult'] if 'mult' in p else next(i for i in range(1,p['mod']+1) if i*p['x']%p['mod']==0)
        return p['g']//p['h'] if f=='陪集指数' else p['g']%p['h']==0
    if ch==11:
        if k==1:
            a,b=p['a'],p['b'];return max(i for i in range(1,min(a,b)+1) if a%i==b%i==0) if p['meet'] else next(i for i in range(max(a,b),a*b+1) if i%a==i%b==0)
        A,B,U=set(p['A']),set(p['B']),set(p['U']);return len([U-A,A|B,A&B][p['op']])
    if ch==12:
        if k==1:return p['a']*p['b']*p['c'] if p['multi'] else p['a']+p['b']+p['c']
        return len(list(itertools.combinations(range(p['n']),p['r'])))*(math.factorial(p['r']) if p['ordered'] else 1)
    if ch==13:
        if k==1:
            v=p['values'][:1 if p['first_order'] else 2]
            while len(v)<=p['idx']:v.append(p['c']*v[-1]+p['d'] if p['first_order'] else v[-1]+v[-2])
            assert v==p['values'];return v[-1]
        if p['geometric']:return p['a']**p['idx']
        coefficients=[1]+[0]*p['idx']
        for _ in range(p['a']):coefficients=[sum(coefficients[:i+1]) for i in range(p['idx']+1)]
        return coefficients[-1]
    if ch in (14,15,16,18) and 'edges' in p:
        n=p['n'];E={tuple(e) for e in p['edges']};deg=[sum(v in e for e in E) for v in range(1,n+1)]
        if ch==14:return (2*len(E) if p['total'] else deg[p['v']-1]) if k==1 else reachable(n,E)
        if ch==15:
            if k==1:return reachable(n,E) and sum(d%2 for d in deg)==(0 if p['closed'] else 2)
            return any(all(tuple(sorted((a,b))) in E for a,b in zip(order,order[1:]+order[:1])) for order in itertools.permutations(range(1,n+1)))
        if ch==16:return reachable(n,E) and len(E)==n-1
        if k==2:return next(c for c in range(1,n+1) if any(all(colors[a-1]!=colors[b-1] for a,b in E) for colors in itertools.product(range(c),repeat=n)))
        if not p['matching']:return max(len(S) for r in range(n+1) for S in itertools.combinations(range(1,n+1),r) if not any(a in S and b in S for a,b in E))
        return max(len(S) for r in range(len(E)+1) for S in itertools.combinations(E,r) if len({v for e in S for v in e})==2*len(S))
    if ch==15:return math.factorial(p['n']-1)//2
    if ch==16:
        if k==1:return p['n']-1
        parent=list(range(5));total=0
        def root(x):
            while parent[x]!=x:x=parent[x]
            return x
        for a,b,w in sorted(p['weighted'],key=lambda e:e[2]):
            x,y=root(a),root(b)
            if x!=y:parent[x]=y;total+=w
        return total
    if ch==17:return p['diagonals']+2 if k==1 else (2*p['n']-4 if p['triangle_free'] else 3*p['n']-6)
    if ch==19:return math.gcd(p['a'],p['b']) if k==1 and p['gcd'] else p['a']%p['b'] if k==1 else (p['a']**p['e'])%p['mod'] if p['power'] else p['a']%p['mod']
    raise AssertionError(q['id'])
