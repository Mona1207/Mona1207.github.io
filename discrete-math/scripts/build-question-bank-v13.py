"""Ship complete, individually authored questions; keep historic IDs and records.

Run from anywhere. Archived v2/v10 shards are the immutable input, so rebuilding
cannot recursively duplicate v13 additions. Eight authored items per point are
reviewed separately from the number of distinct solution methods.
"""
import collections
import copy
import hashlib
import json
import random
import re
from pathlib import Path

from questionbank_v13.author import QUESTIONS
from questionbank_v13 import logic, sets_logic, relations, algebra, counting_graphs, graphs_number
from questionbank_v13.repairs import repair

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
LEGACY_FILES = ['questions-001.json', 'questions-002.json', 'questions-003.json', 'questions-v10.json']
SOURCE_MODULES = ['logic', 'sets_logic', 'relations', 'algebra', 'counting_graphs', 'graphs_number']

# A different title does not make the same solution method a new exercise.
# In particular, language changes, numerals, alphabet size and empty boundary
# counts are not used to inflate the number of fresh methods.
ALIASES = {
 'DM-K01-01-解释固定后命题成立': 'DM-K01-01-真值判定',
 'DM-K01-01-不同情境与命题解释': 'DM-K01-01-未知真假与确定真值',
 'DM-K01-03-矛盾式与不可满足辨析': 'DM-K01-03-公式分类',
 'DM-K01-03-可满足不等于重言': 'DM-K01-03-公式分类',
 'DM-K01-03-从真值列识别重言式': 'DM-K01-03-公式分类',
 'DM-K01-03-异或的可满足赋值': 'DM-K01-03-异或真值',
 'DM-K02-01-等值的反例检验': 'DM-K01-02-充分条件的强度辨析',
 'DM-K03-01-遗漏必要前提的推理': 'DM-K03-01-推理有效性',
 'DM-K03-02-肯定后件的错误形式': 'DM-K03-01-推理有效性',
 'DM-K03-02-否定前件的错误形式': 'DM-K03-01-推理有效性',
 'DM-K03-02-自然语言假言易位': 'DM-K03-01-推理有效性',
 'DM-K03-02-逆与否的等值配对': 'DM-K03-02-逆否等值',
 'DM-K04-01-有的对象不满足性质': 'DM-K04-01-存在量词符号化',
 'DM-K04-02-同字母不同出现的绑定': 'DM-K04-02-自由出现',
 'DM-K04-02-嵌套同名量词的辖域': 'DM-K04-02-自由出现',
 'DM-K05-01-交替量词的存在起始否定': 'DM-K05-01-交替量词的全称起始否定',
 'DM-K05-01-三层量词否定': 'DM-K05-01-交替量词的全称起始否定',
 'DM-K05-02-谓词矩阵的行列覆盖': 'DM-K05-02-无穷域中的依赖见证',
 'DM-K06-01-真子集与相等的冲突': 'DM-K06-01-集合不计顺序和重复',
 'DM-K06-02-按大小限制子集': 'DM-K12-02-无序组合',
 'DM-K07-02-非方形出发到达集合的关系计数': 'DM-K07-02-关系总数',
 'DM-K07-02-空因子上的唯一关系': 'DM-K07-02-关系总数',
 'DM-K07-05-复合中的重复路径不重复计对': 'DM-K07-05-右复合计算',
 'DM-K08-01-空定义域的函数': 'DM-K08-01-函数总数',
 'DM-K08-01-非空域到空陪域': 'DM-K08-01-函数总数',
 'DM-K09-01-有限集合二元运算数量': 'DM-K08-01-函数总数',
 'DM-K12-01-分类计数的重复审查': 'DM-K06-03-并集的容斥计数',
 'DM-K12-01-连续步骤选择量不同的处理': 'DM-K12-01-分支内乘法分支间加法',
 'DM-K12-02-允许重复的有序选择': 'DM-K08-01-函数总数',
 'DM-K14-02-有向可达性不对称': 'DM-K14-02-弱连通与强连通',
 'DM-K17-01-树的平面嵌入面数': 'DM-K17-01-面数与外部面',
}


def canonical(family):
    visited = set()
    while family in ALIASES:
        assert family not in visited, 'alias cycle'
        visited.add(family)
        family = ALIASES[family]
    return family


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':'))+'\n')


def patch_once(text, before, after):
    if after in text:
        return text
    assert text.count(before) == 1, before
    return text.replace(before, after)


def build():
    book = json.loads((DATA / 'book.json').read_text())
    points = {k['id']: k for k in book['knowledge']}
    archived = [json.loads((DATA / f).read_text()) for f in LEGACY_FILES]
    questions = copy.deepcopy([q for shard in archived for q in shard['questions']])
    links = copy.deepcopy([l for shard in archived for l in shard['links']])
    point_for = {l['question_id']: l['knowledge_id'] for l in links}
    assert len(questions) == 1843
    old_groups_source = (ROOT / 'assets/practice-groups-v10.js').read_text()
    groups = json.loads(re.search(r'const groups=(\{.*?\});\n', old_groups_source).group(1))
    revised = 0
    for q in questions:
        revised += repair(q, point_for[q['id']])
        # The historical builder called XOR "否定真值" by falling through.
        if q.get('meta', {}).get('generator') and '⊕' in q['prompt']:
            groups[q['id']] = 'DM-K01-03-异或真值'

    added = collections.Counter()
    authored_families = set()
    for entry in QUESTIONS:
        point = entry['point']
        assert point in points
        added[point] += 1
        qid = f'DM-N13-{point[4:]}-{added[point]:03}'
        family = f'{point}-{entry["method"]}'
        assert family not in authored_families, family
        authored_families.add(family)
        correct = entry['choices'][0]
        choices = entry['choices'].copy()
        random.Random(int(hashlib.sha256(qid.encode()).hexdigest(), 16)).shuffle(choices)
        letter = 'ABCD'[choices.index(correct)]
        k = points[point]
        steps = [s+'。' for s in entry['reason'].split('。') if s]
        meta = {
            'options': [f'{"ABCD"[i]}. {x}' for i, x in enumerate(choices)],
            'family_id': family,
            'practice_group': canonical(family),
            'authoring': 'individually_reviewed_v13',
            'full_statement_version': 13,
            'statement_review': '题意、对象、范围、完整数据与答案推导已逐项核对',
            'label': '系统补充练习 · 非教材原题',
        }
        if entry['check']:
            meta['audit_check'] = entry['check']
        prompt = entry['prompt']
        if re.search(r'\{[a-z](?:,[a-z])+\}', prompt):
            prompt = '题中用不同字母列出的集合元素均互异。\n\n'+prompt
        questions.append({
            'id': qid, 'chapter_id': k['chapter_id'],
            'title': k['title']+f' · 补充练习 {added[point]:02}',
            'prompt': prompt, 'kind': 'choice',
            'difficulty': entry['level'], 'page': k['source']['printed_page'],
            'source_type': 'ai_extra', 'verification': 'verified',
            'answer': {'text': f'{letter}. {correct}', 'accepted': [letter, correct]},
            'explanation': {'steps': steps, 'summary': entry['reason'],
                            'errors': [k['content']['errors']],
                            'origin': '完整自拟补充题；按定义、定理条件或穷举独立推导'},
            'meta': meta,
        })
        links.append({'question_id': qid, 'knowledge_id': point, 'strength': 1})
        groups[qid] = canonical(family)

    assert len(QUESTIONS) == 368 and set(added.values()) == {8} and len(added) == 46
    assert set(ALIASES) <= authored_families
    assert set(groups) == {q['id'] for q in questions}
    known_families = set(groups.values()) | authored_families
    assert all(canonical(v) in known_families for v in ALIASES.values())
    qindex = {q['id']: q for q in questions}
    assert len(qindex) == len(questions)
    for q in questions:
        assert q['prompt'].strip() and q['explanation']['steps']
        assert q['meta']['full_statement_version'] == 13
    for l in links:
        assert l['question_id'] in qindex and l['knowledge_id'] in points

    # Each shard stays small enough for individual transport and atomic publication.
    shards = []
    for start in range(0, len(questions), 180):
        part = questions[start:start+180]
        ids = {q['id'] for q in part}
        name = f'questions-v13-{len(shards)+1:03}.json'
        save(DATA/name, {'questions': part, 'links': [l for l in links if l['question_id'] in ids]})
        shards.append(name)
    book['question_files'] = shards
    total_methods = len(set(groups.values()))
    book['book']['meta'].update({
        'content_version': '3.0.0', 'question_statement_version': 13,
        'verified_question_count': len(questions), 'distinct_practice_methods': total_methods,
        'exercise_families': total_methods,
        'authored_additions_v13': len(QUESTIONS),
        'supplemental_generator': '既有有限穷举题＋逐题编写的完整补充练习；均不冒充教材原题',
    })
    save(DATA/'book.json', book)
    group_source = '// Generated by scripts/build-question-bank-v13.py. Method aliases are reviewed explicitly.\n'
    group_source += 'const groups='+json.dumps(groups, ensure_ascii=False, separators=(',', ':'))+';\n'
    group_source += 'export function practiceGroup(q){return groups[q.id]||q.meta?.practice_group||q.meta?.family_id||("custom:"+q.prompt.normalize("NFKC").replace(/[-+]?\\d+(?:\\.\\d+)?/g,"#").replace(/\\s+/g,""));}\n'
    (ROOT/'assets/practice-groups-v13.js').write_text(group_source)

    # Upgrade content, without resetting IndexedDB or editing personal history.
    worker = (ROOT/'assets/pages-worker-v10.js').read_text()
    worker = patch_once(worker, './practice-groups-v10.js', './practice-groups-v13.js')
    worker = patch_once(worker, '"?v=10"', '"?v=13"')
    worker = patch_once(worker,
        'for(const s of this.snapshot.questionOverrides)e.set(s.id,s);',
        'for(const s of this.snapshot.questionOverrides){const base=e.get(s.id);e.set(s.id,base&&(base.meta?.full_statement_version||0)>(s.meta?.full_statement_version||0)?{...s,...base}:s);}')
    worker = patch_once(worker, '{expected_value:d,parameters:s,...h}=l.meta',
                        '{expected_value:d,parameters:s,audit_check:check,...h}=l.meta')
    worker = patch_once(worker, '补充题采用确定性计算或有限穷举核验；不冒充原题。',
                        '补充题按定义、定理条件、独立计算或有限穷举核验；不冒充教材原题。')
    (ROOT/'assets/pages-worker-v13.js').write_text(worker)
    client = (ROOT/'assets/client-v10.js').read_text().replace('pages-worker-v10.js?v=10.2', 'pages-worker-v13.js?v=13')
    assert 'pages-worker-v13.js?v=13' in client
    (ROOT/'assets/client-v13.js').write_text(client)
    app_path = ROOT/'assets/app-ui-v12.js'
    app = patch_once(app_path.read_text(), './client-v10.js?v=10.2', './client-v13.js?v=13')
    app_path.write_text(app)
    index_path = ROOT/'index.html'
    index = patch_once(index_path.read_text(), 'app-ui-v12.js?v=12.1', 'app-ui-v12.js?v=13')
    index_path.write_text(index)

    by_point = []
    for kid, k in points.items():
        ids = [l['question_id'] for l in links if l['knowledge_id'] == kid]
        by_point.append({'id': kid, 'title': k['title'], 'questions': len(ids),
                         'distinct_methods': len({groups[i] for i in ids}),
                         'added_questions': added[kid]})
    report = {
        'version': 13, 'verified_questions': len(questions),
        'textbook_questions': sum(q['source_type'] == 'textbook' for q in questions),
        'added_questions': len(QUESTIONS), 'legacy_prompt_revisions': revised,
        'complete_statements': len(questions), 'legacy_distinct_methods': 146,
        'distinct_methods': total_methods, 'points': by_point,
        'method_aliases': ALIASES,
        'pending_ocr_questions_not_published': book['book']['meta']['pending_ocr_count'],
        'review_scope': '补充题逐项核对题干、选项和推导；旧题补足独立作答上下文。未收录未经核验的扫描原题。',
    }
    save(DATA/'question-audit-v13.json', report)
    (ROOT/'README.md').write_text(f'''# 知序 · 离散数学

{len(questions):,} 道已核验习题，按解法合并为 {total_methods} 种练习考法，覆盖 46 个知识点。普通练习跨学习、跨知识点排除已做考法，不用改数字的变式填充题量；主动复习可重做。

本次新增 368 道逐题编写的补充题，每个知识点 8 道。旧题补足谓词定义、关系底集、图类型、完整边集、函数定义域/陪域以及递推适用下标等上下文。每题提供独立题干、完整选项或开放题要求及答案推导。

访问 https://Mona1207.github.io/discrete-math/?v=bank-v13

IndexedDB 保留个人学习记录并支持备份恢复；题目编号沿用。已导入的旧官方题会采用新的完整题干，自定义题保留。新增题均明确标为系统补充练习，不冒充教材原题。718 道待 OCR 核验的候选原题没有发布。

重建：`python discrete-math/scripts/build-question-bank-v13.py`。核验：`python discrete-math/scripts/test-question-bank-v13.py` 和 `node discrete-math/scripts/test-question-runtime-v13.mjs`。
''')
    print(json.dumps({k: report[k] for k in ['verified_questions', 'added_questions', 'legacy_prompt_revisions', 'distinct_methods']}, ensure_ascii=False))
    print(f'{len(shards)} shards; point methods range {min(p["distinct_methods"] for p in by_point)}–{max(p["distinct_methods"] for p in by_point)}')


if __name__ == '__main__':
    build()
