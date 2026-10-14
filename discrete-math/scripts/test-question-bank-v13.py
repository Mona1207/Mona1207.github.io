"""Check the shipped bank, complete statements, choices and independent math.

The supplemental authoring source specifies witnesses, not calculation code.
This evaluator derives each expected value by enumeration or a separate
mathematical rule, and checks the actually shuffled published answer.
"""
import collections
import itertools
import json
import math
import re
from pathlib import Path

from questionbank_v13.legacy_oracle import calc
from questionbank_v13.author import QUESTIONS
from questionbank_v13 import logic, sets_logic, relations, algebra, counting_graphs, graphs_number

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'data'


def subsets(values):
    return itertools.chain.from_iterable(itertools.combinations(values, r) for r in range(len(values)+1))


def components(vertices, edges):
    unseen = set(vertices)
    result = []
    while unseen:
        todo = [next(iter(unseen))]
        part = set()
        while todo:
            v = todo.pop()
            if v in part:
                continue
            part.add(v)
            for a,b in edges:
                if v == a and b not in part: todo.append(b)
                if v == b and a not in part: todo.append(a)
        unseen -= part
        result.append(part)
    return result


def norm_edge(a,b,directed=False):
    return (a,b) if directed else tuple(sorted((a,b)))


def check_math(c):
    t = c['kind']
    if t == 'truth_count':
        return sum((not p or q) if c['expression']=='imp' else p!=q
                   for p,q in itertools.product([False,True],repeat=2))
    if t == 'power_set_inverse':
        return next(n for n in range(c['size']+1) if len(list(subsets(list(range(n)))))==c['size'])
    if t == 'combination': return len(list(itertools.combinations(range(c['n']),c['r'])))
    if t == 'fixed_member_subsets':
        return sum(set(range(c['fixed'])) <= set(s) for s in subsets(list(range(c['n']))))
    if t == 'union_size':
        A=set(range(c['a']));B=set(range(c['intersection'])) | set(range(c['a'],c['a']+c['b']-c['intersection']))
        return len(A|B)
    if t == 'product_inverse':
        return next(b for b in range(c['product']+1) if len(list(itertools.product(range(c['a']),range(b))))==c['product'])
    if t == 'relation_count':
        pairs=list(itertools.product(range(c['a']),range(c['b'])))
        return sum(1 for _ in subsets(pairs))
    if t == 'matrix_ones': return sum(v==1 for row in c['matrix'] for v in row)
    if t == 'inverse_cardinality':
        R={(i, i+1) for i in range(c['size'])}
        return len({(b,a) for a,b in R})
    if t == 'partition_relation_size':
        block=[]
        for i,n in enumerate(c['blocks']): block.extend([i]*n)
        return sum(x==y for x,y in itertools.product(block,repeat=2))
    if t == 'function_count':return sum(1 for _ in itertools.product(range(c['m']),repeat=c['n']))
    if t == 'fixed_function_values':
        return sum(all(values[i]==0 for i in range(c['fixed'])) for values in itertools.product(range(c['m']),repeat=c['n']))
    if t == 'binary_operation_count':
        inputs=list(itertools.product(range(c['n']),repeat=2))
        return sum(1 for _ in itertools.product(range(c['n']),repeat=len(inputs)))
    if t in ('three_union','exactly_two_sets'):
        return sum(c['sizes'])-sum(c['pairs'])+c['triple'] if t=='three_union' else sum(p-c['triple'] for p in c['pairs'])
    if t == 'words_at_least_symbol':
        return sum(0 in word for word in itertools.product(range(c['alphabet']),repeat=c['length']))
    if t == 'sum_products':
        return sum(sum(1 for _ in itertools.product(*(range(x) for x in branch))) for branch in c['branches'])
    if t == 'two_roles_overlap':
        A=set(range(c['a']));B=set(range(c['intersection']))|set(range(c['a'],c['a']+c['b']-c['intersection']))
        return sum(a!=b for a,b in itertools.product(A,B))
    if t == 'even_binary_words':
        return sum(sum(word)%2==0 for word in itertools.product([0,1],repeat=c['length']))
    if t == 'multiset_permutation':
        values=[i for i,n in enumerate(c['counts']) for _ in range(n)]
        return len(set(itertools.permutations(values)))
    if t == 'word_count':return len(list(itertools.product(range(c['alphabet']),repeat=c['length'])))
    if t == 'circular_permutation':
        routes=set()
        for p in itertools.permutations(range(c['n'])):
            i=p.index(0); q=p[i:]+p[:i]
            if c['reflection_same']:q=min(q,(q[0],)+tuple(reversed(q[1:])))
            routes.add(q)
        return len(routes)
    if t == 'adjacent_pair_permutation':
        return sum(abs(p.index(0)-p.index(1))==1 for p in itertools.permutations(range(c['n'])))
    if t == 'required_forbidden_combination':
        required=set(range(c['required']));forbidden=set(range(c['required'],c['required']+c['forbidden']))
        return sum(required <= set(s) and not (set(s)&forbidden) for s in itertools.combinations(range(c['n']),c['r']))
    if t in ('weak_compositions','positive_compositions'):
        lower=1 if t=='positive_compositions' else 0
        return sum(sum(s)==c['total'] for s in itertools.product(range(lower,c['total']+1),repeat=c['parts']))
    if t == 'committee_leader':
        return sum(1 for group in itertools.combinations(range(c['n']),c['r']) for _ in group)
    if t == 'two_root_constants':
        C2=(c['a1']-c['a0'])/(c['base']-1)
        return [c['a0']-C2,C2]
    if t == 'polynomial_coefficient':
        return sum(a*b for i,a in enumerate(c['a']) for j,b in enumerate(c['b']) if i+j==c['index'])
    if t == 'graphical_sequence':
        vertices=range(len(c['degrees']));edges=list(itertools.combinations(vertices,2))
        return any(sorted(sum(v in e for e in E) for v in vertices)==sorted(c['degrees']) for E in subsets(edges))
    if t == 'directed_degrees':
        return [sum(b==c['vertex'] for a,b in c['edges']),sum(a==c['vertex'] for a,b in c['edges'])]
    if t == 'directed_degree_sums':
        arcs=[(i,(i+1)%c['edges']) for i in range(c['edges'])]
        return [sum(sum(b==v for a,b in arcs) for v in range(c['edges'])),sum(sum(a==v for a,b in arcs) for v in range(c['edges']))]
    if t == 'complement_degree':return len(set(range(1,c['n']))-set(range(1,c['degree']+1)))
    if t == 'regular_edges':return c['n']*c['degree']//2
    if t == 'remove_vertex_edges':return c['edges']-c['degree']
    if t == 'components':return len(components(range(1,c['n']+1),c['edges']))
    if t == 'merge_components':
        return len(components(range(c['components']),[(0,1)]))
    if t == 'odd_vertices':
        return sorted(v for v in c['vertices'] if sum(v in e for e in c['edges'])%2)
    if t == 'euler_walk':
        expected=collections.Counter(norm_edge(a,b,c['directed']) for a,b in c['edges'])
        actual=collections.Counter(norm_edge(a,b,c['directed']) for a,b in zip(c['walk'],c['walk'][1:]))
        return actual==expected
    if t == 'euler_augmentation':
        # Enumerate edge additions and test that all initially odd parities flip.
        vertices=list(range(c['odd']));pairs=list(itertools.combinations(vertices,2))
        for r in range(c['odd']+1):
            if any(all(sum(v in e for e in E)%2 for v in vertices) for E in itertools.combinations(pairs,r)):
                return r
    if t == 'hamilton_walk':
        w=c['walk'];E={norm_edge(a,b) for a,b in c['edges']}
        return w[0]==w[-1] and len(w)==len(c['vertices'])+1 and set(w[:-1])==set(c['vertices']) and all(norm_edge(a,b) in E for a,b in zip(w,w[1:]))
    if t == 'bipartite_hamilton_count':
        n=c['n'];cycles=set()
        for p in itertools.permutations(range(1,2*n)):
            w=(0,)+p
            if all((a<n)!=(b<n) for a,b in zip(w,w[1:]+w[:1])):
                cycles.add(min(w,(0,)+tuple(reversed(p))))
        return len(cycles)
    if t == 'forest_components':return c['n']-c['edges']
    if t == 'tree_leaves_degree3':
        return next(l for l in range(1,3*c['internal']+1) if l+3*c['internal']==2*(l+c['internal']-1))
    if t == 'full_binary_leaves':
        return next(l for l in range(1,2*c['internal']+1) if 2*c['internal']==l+c['internal']-1)
    if t == 'face_length_bound':
        return max(e for e in range(math.comb(c['n'],2)+1) if c['minimum']*(2-c['n']+e)<=2*e)
    if t == 'cover_independence':return c['n']-c['alpha']
    if t == 'greedy_color_bound':return len(set(range(c['degree']+1)))
    if t == 'disjoint_chromatic':return max(c['values'])
    if t == 'proper_colorings':
        return sum(all(values[c['vertices'].index(a)]!=values[c['vertices'].index(b)] for a,b in c['edges']) for values in itertools.product(range(c['colors']),repeat=len(c['vertices'])))
    if t == 'diophantine_exists':
        return any(c['a']*x+c['b']*y==c['c'] for x,y in itertools.product(range(-2*abs(c['b']),2*abs(c['b'])+1),range(-2*abs(c['a']),2*abs(c['a'])+1)))
    if t == 'linear_congruence_exists':return any((c['a']*x-c['b'])%c['m']==0 for x in range(c['m']))
    if t == 'modular_inverse':return next(y for y in range(c['m']) if (c['a']*y)%c['m']==1)
    if t in ('simultaneous_congruences','simultaneous_exists'):
        solutions=[x for x in range(math.lcm(*c['moduli'])) if all(x%m==r for m,r in zip(c['moduli'],c['remainders']))]
        return bool(solutions) if t=='simultaneous_exists' else solutions[0]
    raise AssertionError('Unknown check '+t)


def set_literal(text):
    """Normalize literal set options so {a,a} cannot masquerade as a distractor."""
    text=text.replace(' ', '')
    if text=='∅':return ('set',frozenset())
    if not text.startswith('{') or not text.endswith('}'):
        return ('literal',text)
    inner=text[1:-1]
    depth=0;items=[];start=0
    for i,char in enumerate(inner):
        if char in '{(':depth+=1
        if char in '})':depth-=1
        if char==',' and depth==0:items.append(inner[start:i]);start=i+1
    if inner:items.append(inner[start:])
    return ('set',frozenset(set_literal(x) for x in items))


def audit():
    book=json.loads((DATA/'book.json').read_text())
    shards=[json.loads((DATA/f).read_text()) for f in book['question_files']]
    questions=[q for shard in shards for q in shard['questions']]
    links=[l for shard in shards for l in shard['links']]
    by_id={q['id']:q for q in questions}
    knowledge={k['id'] for k in book['knowledge']}
    assert len(questions)==len(by_id)==2211
    assert len(QUESTIONS)==368 and len(knowledge)==46
    assert all(q['verification']=='verified' for q in questions)
    assert all(l['question_id'] in by_id and l['knowledge_id'] in knowledge for l in links)
    assert all(any(l['question_id']==q['id'] for l in links) for q in questions)
    assert len([q for q in questions if q['source_type']=='textbook'])==5
    assert book['book']['meta']['content_complete'] is False
    assert book['book']['meta']['pending_ocr_count']==718

    for q in questions:
        assert len(q['prompt'])>=15, q['id']
        assert not re.search(r'同样的|同上一题|如图|上题|上述关系|前述集合|略去|题干待补|待核验',q['prompt']),q['id']
        assert q['meta']['full_statement_version']==13
        assert q['explanation']['steps'] and q['explanation']['summary'],q['id']
        if q['kind']=='choice':
            options=q['meta']['options']
            assert 2<=len(options)<=4 and len(options)==len(set(options)),q['id']
            letter=q['answer']['accepted'][0]
            assert letter in 'ABCD'[:len(options)],q['id']
            assert options['ABCD'.index(letter)]==q['answer']['text'],q['id']
            assert q['answer']['text'].split('. ',1)[1] in q['answer']['accepted'],q['id']
            content=[o.split('. ',1)[1] for o in options]
            assert len(set(map(set_literal,content)))==len(content),q['id']+' semantically identical set options'
    generated=[q for q in questions if q['id'].startswith('DM-V2-')]
    assert len(generated)==1743
    for q in generated:
        result=calc(q)
        assert result==q['meta']['expected_value'],q['id']
        text='成立' if result is True else '不成立' if result is False else str(result)
        assert text in q['answer']['accepted'],q['id']

    # Verify authoring source and the shuffled public bank correspond exactly.
    position=collections.Counter();oracle_count=0
    for source in QUESTIONS:
        point=source['point'];position[point]+=1
        q=by_id[f'DM-N13-{point[4:]}-{position[point]:03}']
        assert source['prompt'] in q['prompt']
        assert q['answer']['accepted'][1]==source['choices'][0],q['id']
        assert len(source['reason'])>=24 and len(q['meta']['options'])==4
        if source['check']:
            c=source['check'];value=check_math(c)
            assert value==c['expected'],(q['id'],value,c)
            assert q['meta']['audit_check']==c,q['id']
            oracle_count+=1
    assert set(position.values())=={8} and set(position)==knowledge

    # Real omissions reproduced in isolation, with no dependence on another item.
    assert 'A={1,2}、B={2,3}' in by_id['DM-X06-03-2']['prompt']
    assert 'S(x) 表示' in by_id['DM-X04-01-1']['prompt'] and 'D(x) 表示' in by_id['DM-X04-01-1']['prompt']
    assert '行、列都按 1、2 排列' in by_id['DM-X07-03-1']['prompt']
    assert 'n≥1' in by_id['DM-X13-01-1']['prompt']
    assert 'R⊆A×A' in by_id['DM-T07-135-3-4']['prompt']
    assert '陪域' in by_id['DM-N13-08-01-003']['prompt']
    letters=collections.Counter(q['answer']['accepted'][0] for q in questions if q['id'].startswith('DM-N13-'))
    assert set(letters)==set('ABCD') and min(letters.values())>=60
    print(f'PASS: {len(questions)} complete shipped statements; {len(generated)} independently recomputed legacy answers; {oracle_count} supplemental math witnesses; 368 authored questions across 46 points; options and shuffled answers consistent.')


if __name__=='__main__':audit()
