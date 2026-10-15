"""OCR all indexed textbook examples into text, retaining uncertainty honestly.

No PDF/image is required by the resulting example reader. Unreviewed OCR is
explicitly flagged and is never eligible for automatic grading. The input PDF
and Tesseract chi_sim model are supplied by the build operator.
"""
from pathlib import Path
import argparse, concurrent.futures, csv, hashlib, json, os, re, subprocess
import fitz

ROOT = Path(__file__).resolve().parents[1]
PARSER = argparse.ArgumentParser()
PARSER.add_argument('--pdf', type=Path, default=Path('/workspace/scratch/11c744d1f965/upload/离散数学 第2版.pdf'))
PARSER.add_argument('--ocr-directory', type=Path, default=Path('/workspace/scratch/11c744d1f965/tmp/v15/ocr/DM2T'))
PARSER.add_argument('--model-directory', type=Path, default=Path('/workspace/scratch/11c744d1f965/ocr-models'))
PARSER.add_argument('--cache', type=Path, default=Path('/workspace/scratch/11c744d1f965/tmp/v17/DM2T'))
PARSER.add_argument('--high-resolution', action='store_true')
PARSER.add_argument('--workers', type=int, default=3)
ARGS = PARSER.parse_args()
ARGS.cache.mkdir(parents=True, exist_ok=True)
TARGET = ROOT / 'data/examples-DM2T-v17.json'

def normalize(text):
    text = text.replace('\x0c', '').replace('﹐', '，').replace('﹑', '、')
    text = re.sub(r'(?<=[\u4e00-\u9fff]) +(?=[\u4e00-\u9fff])', '', text)
    text = re.sub(r' *\n *', '\n', text)
    return re.sub(r'\n{3,}', '\n\n', text).strip()

def low_resolution(segment):
    path = ARGS.ocr_directory / f'{segment["page"]:03}.tsv'
    rows = list(csv.DictReader(path.open(), delimiter='\t', quoting=csv.QUOTE_NONE))
    height = int(rows[0]['height'])
    lines = {}
    for row in rows:
        if row.get('level') != '5' or not row.get('text', '').strip():
            continue
        center = (int(row['top']) + int(row['height']) / 2) / height
        if segment['top'] <= center < segment['bottom']:
            key = (row['block_num'], row['par_num'], row['line_num'])
            lines.setdefault(key, []).append(row)
    out = []
    for words in lines.values():
        words.sort(key=lambda r:int(r['left']))
        out.append((min(int(r['top']) for r in words), ' '.join(r['text'] for r in words)))
    return normalize('\n'.join(t for _, t in sorted(out)))

def cache_key(segment):
    return f'{segment["page"]:03}-{segment["top"]:.4f}-{segment["bottom"]:.4f}'

def high_resolution(segment):
    key = cache_key(segment)
    output = ARGS.cache / (key + '.txt')
    if output.exists():
        return output.read_text()
    with fitz.open(ARGS.pdf) as doc:
        page = doc[segment['page'] - 1]
        clip = fitz.Rect(0, page.rect.height * segment['top'], page.rect.width, page.rect.height * segment['bottom'])
        image = ARGS.cache / (key + '.png')
        page.get_pixmap(matrix=fitz.Matrix(3, 3), clip=clip).save(image)
    result = subprocess.run(['tesseract', str(image), 'stdout', '--tessdata-dir', str(ARGS.model_directory), '-l', 'chi_sim', '--psm', '6'], check=True, capture_output=True, text=True, env={**os.environ, 'OMP_THREAD_LIMIT':'1'})
    text = normalize(result.stdout)
    output.write_text(text)
    image.unlink()
    return text

def examples():
    result = [item for path in sorted((ROOT/'data').glob('originals-DM2T-v15-*.json')) for item in json.loads(path.read_text())['items'] if item['kind']=='example']
    return sorted(result, key=lambda x:(x['pdf_page'], x['segments'][0]['top']))

# Only entries checked directly against rendered source pages belong here.
# Keeping corrections in the extraction script makes rebuilds reproducible.
REVIEWED = {'例 1.1': {'prompt': '判断下列句子是否为命题。\n'
                     '(1) 4 是素数。\n'
                     '(2) $\\sqrt{5}$ 是无理数。\n'
                     '(3) $x$ 大于 $y$，其中 $x$ 和 $y$ 是任意的两个数。\n'
                     '(4) 火星上有水。\n'
                     '(5) 2050 年元旦是晴天。\n'
                     '(6) $\\pi$ 大于 $\\sqrt{2}$ 吗？\n'
                     '(7) 请不要吸烟！\n'
                     '(8) 这朵花真美丽啊！\n'
                     '(9) 我正在说假话。',
           'solution': '(1)、(2)、(4)、(5) 是命题；(1) 为假命题，(2) 为真命题。(4)、(5) 的真值在原书讨论中未知，但每句都有唯一的真值。\n'
                       '(3) 不是命题，因为自由变量 $x,y$ 尚未取定，不能确定唯一真值。\n'
                       '(6)、(7)、(8) 分别为疑问句、祈使句和感叹句，不是命题。\n'
                       '(9) 是说谎者悖论：假定它真就推出它假，假定它假又推出它真，不能赋予一致的真值，所以不是命题。',
           'explanation': ['先判断句式：只有能作真假判断的陈述句才可能是命题；问题、命令和感叹直接排除。',
                           '再判断真值是否唯一。(3) 随变量取值变化，必须先给变量取值或加量词，才能作确定判断。',
                           '“我们不知道真假”不等于“没有唯一真假”。(4)、(5) 在原书的语境下属于前一种情况。',
                           '(9) 的自我指涉导致矛盾，无法在二值逻辑中保持一致。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 1.2': {'prompt': '先将下面各陈述句中出现的原子命题符号化，并指出它们的真值，然后再写出这些陈述。\n'
                     '(1) $\\sqrt{2}$ 是有理数是不对的。\n'
                     '(2) 2 是偶素数。\n'
                     '(3) 2 或 4 是素数。\n'
                     '(4) 如果 2 是素数，则 3 也是素数。\n'
                     '(5) 2 是素数当且仅当 3 也是素数。',
           'solution': '设 $p$：$\\sqrt{2}$ 是有理数；$q$：2 是素数；$r$：2 是偶数；$s$：3 是素数；$t$：4 是素数。\n'
                       '$p,t$ 的真值为 0，$q,r,s$ 的真值为 1。\n'
                       '五句依次写为：(1) 非 $p$；(2) $q$ 并且 $r$；(3) $q$ 或 $t$；(4) 如果 $q$ 则 $s$；(5) $q$ 当且仅当 $s$。\n'
                       '使用逻辑联结词可写为 $\\neg p$、$q\\land r$、$q\\lor t$、$q\\to s$、$q\\leftrightarrow s$。',
           'explanation': ['先把每个不能再分的事实拆出；“偶素数”同时要求“偶数”和“素数”，所以含两个原子命题。',
                           '判断原子命题：根号 2 是无理数，4 是合数，故 $p=t=0$；2 是偶素数，3 是素数，故另外三个取 1。',
                           '最后按句子的连接方式组合。先符号化原子命题，再连成复合命题，可以避免把原子命题的否定混进定义。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 1.3': {'prompt': '将下列命题符号化。\n'
                     '(1) 吴颖既用功又聪明。\n'
                     '(2) 吴颖不但用功而且聪明。\n'
                     '(3) 吴颖虽然聪明，但不用功。\n'
                     '(4) 张辉与王丽都是三好生。\n'
                     '(5) 张辉与王丽是同学。',
           'solution': '设 $p$：吴颖用功；$q$：吴颖聪明；$r$：张辉是三好生；$s$：王丽是三好生。\n'
                       '(1) $p\\land q$。\n'
                       '(2) $p\\land q$。\n'
                       '(3) $q\\land\\neg p$。\n'
                       '(4) $r\\land s$。\n'
                       '(5) 是不可按主语中的“与”拆开的原子命题，设 $t$：张辉与王丽是同学，则符号化为 $t$。',
           'explanation': ['“既……又……”“不但……而且……”都表示两件事同时成立，统一用合取。',
                           '“虽然……但……”表达语气上的转折，在命题逻辑中仍要求两个分句都成立；“不用功”使 $p$ 前加否定。',
                           '(4) 可以拆成两个人各自是三好生；(5) 描述两人之间的同学关系，不能拆成“张辉是同学”和“王丽是同学”。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 1.4': {'prompt': '将下列命题符号化。\n(1) 张晓静爱唱歌或爱听音乐。\n(2) 张晓静只能挑选 202 或 203 房间。\n(3) 张晓静是江西人或安徽人。',
           'solution': '(1) 设 $p$：张晓静爱唱歌；$q$：张晓静爱听音乐。这里的“或”可相容，符号化为 $p\\lor q$。\n'
                       '(2) 设 $r$：张晓静挑选 202 房间；$s$：张晓静挑选 203 房间。只允许选一个，符号化为 $(r\\land\\neg s)\\lor(\\neg '
                       'r\\land s)$。\n'
                       '(3) 设 $t$：张晓静是江西人；$u$：张晓静是安徽人。排斥或可写为 $(t\\land\\neg u)\\lor(\\neg t\\land '
                       'u)$。按原书此题“籍贯不能同时为两地”的语境，$t,u$ 不可能同时为真，也可简写为 $t\\lor u$。',
           'explanation': ['先判断“或”是否允许两件事同时成立。爱唱歌和爱听音乐可以兼有，因此直接用析取。',
                           '“只能挑选一个房间”排除两个都选，也排除两个都不选；用两个合取式列出仅有的两种合法情况，再将它们析取。',
                           '(3) 的简写依赖语境给出的互斥前提，不能把普通析取 $t\\lor u$ 一概当作排斥或。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 1.5': {'prompt': '将下列命题符号化，并指出它们的真值。\n'
                     '(1) 如果 $3+3=6$，则雪是白色的。\n'
                     '(2) 如果 $3+3\\ne6$，则雪是白色的。\n'
                     '(3) 如果 $3+3=6$，则雪不是白色的。\n'
                     '(4) 如果 $3+3\\ne6$，则雪不是白色的。\n'
                     '(5) 只要 $a$ 能被 4 整除，则 $a$ 一定能被 2 整除。\n'
                     '(6) $a$ 能被 4 整除，仅当 $a$ 能被 2 整除。\n'
                     '(7) 除非 $a$ 能被 2 整除，$a$ 才能被 4 整除。\n'
                     '(8) 除非 $a$ 能被 2 整除，否则 $a$ 不能被 4 整除。\n'
                     '(9) 只有 $a$ 能被 2 整除，$a$ 才能被 4 整除。\n'
                     '(10) 只有 $a$ 能被 4 整除，$a$ 才能被 2 整除。\n'
                     '其中 $a$ 是一个给定的正整数。',
           'solution': '设 $p$：$3+3=6$，$q$：雪是白色的，二者真值均为 1。\n'
                       '(1) $p\\to q$，真值 1。\n'
                       '(2) $\\neg p\\to q$，真值 1。\n'
                       '(3) $p\\to\\neg q$，真值 0。\n'
                       '(4) $\\neg p\\to\\neg q$，真值 1。\n'
                       '再设 $r$：$a$ 能被 4 整除；$s$：$a$ 能被 2 整除。\n'
                       '(5)～(9) 均为 $r\\to s$，真值均为 1。\n'
                       '(10) 为 $s\\to r$，其真值取决于 $a$。例如 $a=8$ 时为真，$a=6$ 时为假。',
           'explanation': ['蕴含 $A\\to B$ 只在前件真、后件假时为假；前件为假时，无论后件真假，蕴含都为真。代入 $p=q=1$ 即得前四题。',
                           '“只要 A 就 B”把 A 作为充分条件，写 $A\\to B$；“只有 B 才 A”“A 仅当 B”把 B 作为必要条件，同样写 $A\\to B$。',
                           '被 4 整除一定被 2 整除，所以 $r\\to s$ 不会出现前真后假。反向命题不总成立，例如 6 是偶数但不是 4 的倍数。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 1.6': {'prompt': '将下列命题符号化，并讨论它们的真值。\n'
                     '(1) $\\sqrt{3}$ 是无理数当且仅当加拿大位于亚洲。\n'
                     '(2) $2+3=5$ 的充要条件是 $\\sqrt{3}$ 是无理数。\n'
                     '(3) 若两圆 $O_1,O_2$ 的面积相等，则它们的半径相等；反之亦然。\n'
                     '(4) 当王小红心情愉快时，她就唱歌；反之，当她唱歌时，一定心情愉快。',
           'solution': '设 $p$：$\\sqrt{3}$ 是无理数；$q$：加拿大位于亚洲；$r$：$2+3=5$。\n'
                       '(1) $p\\leftrightarrow q$，因 $p=1,q=0$，真值为 0。\n'
                       '(2) $r\\leftrightarrow p$，因 $r=p=1$，真值为 1。\n'
                       '(3) 设 $s$：两圆面积相等；$t$：两圆半径相等。符号化为 $s\\leftrightarrow t$，真值为 1。\n'
                       '(4) 设 $u$：王小红心情愉快；$v$：王小红唱歌。符号化为 $u\\leftrightarrow v$，真值由具体情况决定。',
           'explanation': ['“当且仅当”“充要条件”“若……则……；反之亦然”都要求两个方向的蕴含，统一用等价联结词。',
                           '等价式只有两边真值相同时为真；前两题直接代入已知真值。',
                           '圆的面积为 $\\pi R^2$，半径非负，所以面积相等与半径相等互相推出，无论这两个具体圆是否一样大，等价式始终为真。',
                           '(4) 的形式可以确定，但题目没有给出具体生活事实，不能凭常识强行指定它的真值。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 1.7': {'prompt': '令 $p$：北京比天津人口多；$q$：$2+2=4$；$r$：乌鸦是白色的。求下列复合命题的真值。\n'
                     '(1) $((\\neg p\\land q)\\lor(p\\land\\neg q))\\to r$。\n'
                     '(2) $(q\\lor r)\\to(p\\to\\neg r)$。\n'
                     '(3) $(\\neg p\\lor r)\\leftrightarrow(p\\land\\neg r)$。',
           'solution': '按原书取值，$p,q,r$ 的真值依次为 1、1、0。三个复合命题的真值依次为 1、1、0。',
           'explanation': ['(1) 的前件为 $(0\\land1)\\lor(1\\land0)=0$，后件为 0，因此得到 $0\\to0=1$。',
                           '(2) 左侧 $q\\lor r=1$，右侧 $p\\to\\neg r=1\\to1=1$，故全式为 $1\\to1=1$。',
                           '(3) 左侧 $\\neg p\\lor r=0$，右侧 $p\\land\\neg r=1$，两侧不同，等价式为 0。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 1.8': {'prompt': '写出下列公式的真值表，并求它们的成真赋值和成假赋值。\n'
                     '(1) $(\\neg p\\land q)\\to\\neg r$。\n'
                     '(2) $(p\\land\\neg p)\\leftrightarrow(q\\land\\neg q)$。\n'
                     '(3) $\\neg(p\\to q)\\land q\\land r$。\n'
                     '赋值按 $p,q,r$（不含 $r$ 的公式按 $p,q$）的顺序记为二进制串。',
           'solution': '(1) 成假赋值只有 011，其余 000、001、010、100、101、110、111 均为成真赋值。\n'
                       '\n'
                       '| $p$ | $q$ | $r$ | $\\neg p$ | $\\neg r$ | $\\neg p\\land q$ | 全式 |\n'
                       '|---|---|---|---|---|---|---|\n'
                       '|0|0|0|1|1|0|1|\n'
                       '|0|0|1|1|0|0|1|\n'
                       '|0|1|0|1|1|1|1|\n'
                       '|0|1|1|1|0|1|0|\n'
                       '|1|0|0|0|1|0|1|\n'
                       '|1|0|1|0|0|0|1|\n'
                       '|1|1|0|0|1|0|1|\n'
                       '|1|1|1|0|0|0|1|\n'
                       '\n'
                       '(2) 00、01、10、11 均为成真赋值，无成假赋值。\n'
                       '\n'
                       '| $p$ | $q$ | $p\\land\\neg p$ | $q\\land\\neg q$ | 全式 |\n'
                       '|---|---|---|---|---|\n'
                       '|0|0|0|0|1|\n'
                       '|0|1|0|0|1|\n'
                       '|1|0|0|0|1|\n'
                       '|1|1|0|0|1|\n'
                       '\n'
                       '(3) 无成真赋值；000、001、010、011、100、101、110、111 均为成假赋值。\n'
                       '\n'
                       '| $p$ | $q$ | $r$ | $p\\to q$ | $\\neg(p\\to q)$ | $\\neg(p\\to q)\\land q$ | 全式 |\n'
                       '|---|---|---|---|---|---|---|\n'
                       '|0|0|0|1|0|0|0|\n'
                       '|0|0|1|1|0|0|0|\n'
                       '|0|1|0|1|0|0|0|\n'
                       '|0|1|1|1|0|0|0|\n'
                       '|1|0|0|0|1|0|0|\n'
                       '|1|0|1|0|1|0|0|\n'
                       '|1|1|0|1|0|0|0|\n'
                       '|1|1|1|1|0|0|0|',
           'explanation': ['先找出所有命题变项，按二进制顺序列齐 $2^n$ 个赋值，再依联结词优先级计算各列。',
                           '(1) 蕴含为假必须前真后假，因此 $\\neg p\\land q=1$ 且 $\\neg r=0$，唯一可能是 $pqr=011$。',
                           '(2) 两个合取式都是矛盾式，永远为 0，所以它们的等价式永远为 1。',
                           '(3) $\\neg(p\\to q)$ 等价于 $p\\land\\neg q$，再与 $q$ 合取就同时要求 $q$ 和 $\\neg q$，故最后一列全为 '
                           '0。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 1.9': {'prompt': '下列各公式均含两个命题变项 $p,q$，它们中哪些具有相同的真值表？\n'
                     '(1) $p\\to q$。\n'
                     '(2) $p\\leftrightarrow q$。\n'
                     '(3) $\\neg(p\\land\\neg q)$。\n'
                     '(4) $(p\\to q)\\land(q\\to p)$。\n'
                     '(5) $\\neg q\\lor p$。',
           'solution': '(1) 与 (3) 具有相同的真值表；(2) 与 (4) 具有相同的真值表；(5) 与其余公式不同。\n'
                       '\n'
                       '| $p$ | $q$ | (1) | (2) | (3) | (4) | (5) |\n'
                       '|---|---|---|---|---|---|---|\n'
                       '|0|0|1|1|1|1|1|\n'
                       '|0|1|1|0|1|0|0|\n'
                       '|1|0|0|0|0|0|1|\n'
                       '|1|1|1|1|1|1|1|',
           'explanation': ['必须按同一种赋值顺序排列各公式的真值表，才能逐行比较。',
                           '(3) 用德摩根律化为 $\\neg p\\lor q$，正好是 $p\\to q$ 的等价形式。',
                           '(4) 同时要求两个方向的蕴含，正好表示 $p,q$ 互为充分必要条件，与等价式 (2) 相同。',
                           '(5) 等价于 $q\\to p$，它是 (1) 的逆命题；逆命题一般不与原命题等值。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 1.10': {'prompt': '下列各公式中，哪些具有相同的真值表？\n'
                      '(1) $p\\to q$。\n'
                      '(2) $\\neg q\\lor r$。\n'
                      '(3) $(\\neg p\\lor q)\\land((p\\land r)\\to p)$。\n'
                      '(4) $(q\\to r)\\land(p\\to p)$。',
            'solution': '将四个公式统一看成含 $p,q,r$ 的公式，其中未实际出现的变项为哑元。(1) 与 (3) 的真值表相同，(2) 与 (4) 的真值表相同。\n'
                        '\n'
                        '| $p$ | $q$ | $r$ | (1) | (2) | (3) | (4) |\n'
                        '|---|---|---|---|---|---|---|\n'
                        '|0|0|0|1|1|1|1|\n'
                        '|0|0|1|1|1|1|1|\n'
                        '|0|1|0|1|0|1|0|\n'
                        '|0|1|1|1|1|1|1|\n'
                        '|1|0|0|0|1|0|1|\n'
                        '|1|0|1|0|1|0|1|\n'
                        '|1|1|0|1|0|1|0|\n'
                        '|1|1|1|1|1|1|1|',
            'explanation': ['先把四个公式的变项统一为 $p,q,r$；(1) 不依赖 $r$，所以改变 $r$ 不会改变它的值，(2) 同理不依赖 $p$。',
                            '$(p\\land r)\\to p$ 是重言式：若 $p\\land r$ 真，则 $p$ 必真；若前件假，蕴含仍真。故 (3) 化为 $\\neg '
                            'p\\lor q$，等价于 (1)。',
                            '$p\\to p$ 永真，故 (4) 化为 $q\\to r$，再化为 $\\neg q\\lor r$，等价于 (2)。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 2.13': {'prompt': '二进制半加器和二进制全加器。\n'
                      "半加器输入为两个被加数 $x,y$，输出为半和 $h$ 和半进位 $d$；全加器输入为 $x,y$ 及上一位进位 $c'$，输出和 $s$、进位 "
                      '$c$。由真值表求它们的主析取范式，并说明如何由半加器构造全加器。',
            'solution': '半加器：$h=(\\neg x\\land y)\\lor(x\\land\\neg y)$，$d=x\\land y$。\n'
                        '\n'
                        '|$x$|$y$|$h$|$d$|\n'
                        '|---|---|---|---|\n'
                        '|0|0|0|0|\n'
                        '|0|1|1|0|\n'
                        '|1|0|1|0|\n'
                        '|1|1|0|1|\n'
                        '\n'
                        '全加器：\n'
                        "$s=(\\neg x\\land\\neg y\\land c')\\lor(\\neg x\\land y\\land\\neg "
                        "c')\\lor(x\\land\\neg y\\land\\neg c')\\lor(x\\land y\\land c')$。\n"
                        "$c=(\\neg x\\land y\\land c')\\lor(x\\land\\neg y\\land c')\\lor(x\\land "
                        "y\\land\\neg c')\\lor(x\\land y\\land c')$。\n"
                        '\n'
                        "|$x$|$y$|$c'$|$s$|$c$|\n"
                        '|---|---|---|---|---|\n'
                        '|0|0|0|0|0|\n'
                        '|0|0|1|1|0|\n'
                        '|0|1|0|1|0|\n'
                        '|0|1|1|0|1|\n'
                        '|1|0|0|1|0|\n'
                        '|1|0|1|0|1|\n'
                        '|1|1|0|0|1|\n'
                        '|1|1|1|1|1|\n'
                        '\n'
                        "化简为 $s=(h\\land\\neg c')\\lor(\\neg h\\land c')$，$c=(h\\land c')\\lor "
                        'd$。因此可用两个半加器和一个或门实现全加器。',
            'explanation': ['逐行将二进制输入相加，和位是总数模 2，进位是总数除以 2 的整数部分；对输出为 1 的行写出极小项。',
                            '第一个半加器输入 $x,y$，产生 $h=x\\oplus y$ 和 $d=xy$。',
                            '第二个半加器输入 $h,c\\prime$，产生最终和 $s=h\\oplus c\\prime$，以及第二路进位 $h\\land c\\prime$。',
                            '两路进位任意一路为 1，就必须向高位进位，因此最终进位是它们的析取。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 2.14': {'prompt': '利用公式的主析取范式，求主合取范式。\n'
                      '(1) $A\\Leftrightarrow m_1\\lor m_2$，$A$ 中含两个命题变项 $p,q$。\n'
                      '(2) $B\\Leftrightarrow m_1\\lor m_2\\lor m_3$，$B$ 中含三个命题变项 $p,q,r$。',
            'solution': '(1) 未出现在主析取范式中的极小项为 $m_0,m_3$，故 $A\\Leftrightarrow M_0\\land M_3$。\n'
                        '(2) 未出现的极小项为 $m_0,m_4,m_5,m_6,m_7$，故 $B\\Leftrightarrow M_0\\land M_4\\land '
                        'M_5\\land M_6\\land M_7$。',
            'explanation': ['主析取范式列出使公式为真的赋值编号，主合取范式列出使公式为假的赋值编号。',
                            '两个变项共有 $2^2=4$ 个编号 0、1、2、3，补去 1、2 后剩 0、3。',
                            '三个变项共有 0 至 7 八个编号，补去 1、2、3 后剩 0、4、5、6、7。注意是补编号，不是把同编号的小写 $m$ 直接换成大写 $M$。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 6.1': {'prompt': '$A=\\{1,2,3\\}$，将 $A$ 的子集分类。',
           'solution': '0 元子集：$\\varnothing$。\n'
                       '1 元子集：$\\{1\\},\\{2\\},\\{3\\}$。\n'
                       '2 元子集：$\\{1,2\\},\\{1,3\\},\\{2,3\\}$。\n'
                       '3 元子集：$\\{1,2,3\\}$。\n'
                       '总计 $1+3+3+1=8=2^3$ 个。一般 $n$ 元集的 $m$ 元子集有 $C(n,m)$ 个，子集总数为 $\\sum_{m=0}^n '
                       'C(n,m)=2^n$。',
           'explanation': ['按子集的元素个数从 0 到 3 分层列举，可以避免漏掉空集和全集。',
                           '每个元素都可选择“放入”或“不放入”子集，3 个元素独立选择得到 $2^3$ 种结果。',
                           '区分空集 $\\varnothing$ 和只含空集的集合 $\\{\\varnothing\\}$：后者不是本题的子集，因为 '
                           '$\\varnothing\\notin A$。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 6.2': {'prompt': '设 '
                     '$A=\\{\\{a,b,c\\},\\{a,c,d\\},\\{a,e,f\\}\\}$，$B=\\{\\{a\\}\\}$，$C=\\{a,\\{c,d\\}\\}$。给出它们的广义并；并比较广义交。',
           'solution': '$\\bigcup A=\\{a,b,c,d,e,f\\}$，$\\bigcup B=\\{a\\}$，$\\bigcup '
                       'C=a\\cup\\{c,d\\}$，$\\bigcup\\varnothing=\\varnothing$。\n'
                       '对应的广义交为 $\\bigcap A=\\{a\\}$，$\\bigcap B=\\{a\\}$，$\\bigcap '
                       'C=a\\cap\\{c,d\\}$。原书不在无全集限定的集合论语境中定义 $\\bigcap\\varnothing$。',
           'explanation': ['广义并把一个集合族里各成员集合的元素收集起来；$A$ 的三组元素中，出现过一次就保留，重复只计一次。',
                           '$B$ 只有一个成员 $\\{a\\}$，对单成员集合族做广义并或广义交，都得到这个唯一成员。',
                           '$C$ 的成员是 $a$ 与 $\\{c,d\\}$，不能擅自把 $a$ 当成普通单个元素代换；按原书的集合论表达，结果保留为 '
                           '$a\\cup\\{c,d\\}$ 或 $a\\cap\\{c,d\\}$。',
                           '广义交要求元素属于每个成员集合，$A$ 中共同出现的只有 $a$。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.5': {'prompt': '设 '
                     '$R=\\{\\langle1,2\\rangle,\\langle1,3\\rangle,\\langle2,4\\rangle,\\langle4,3\\rangle\\}$，求它的定义域、值域和域。',
           'solution': '$\\operatorname{dom}R=\\{1,2,4\\}$，$\\operatorname{ran}R=\\{2,3,4\\}$，$\\operatorname{fld}R=\\{1,2,3,4\\}$。',
           'explanation': ['收集所有有序对的第一分量，去掉重复，得到定义域。', '收集所有第二分量，去掉重复，得到值域。', '域是定义域和值域的并集；有序对的先后位置不能交换。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.6': {'prompt': '设 $F=\\{\\langle3,3\\rangle,\\langle6,2\\rangle\\}$，$G=\\{\\langle2,3\\rangle\\}$，求 '
                     '$F^{-1}$、$F\\circ G$、$G\\circ F$。本书采用右复合：先经过左侧关系，再经过右侧关系。',
           'solution': '$F^{-1}=\\{\\langle3,3\\rangle,\\langle2,6\\rangle\\}$，$F\\circ '
                       'G=\\{\\langle6,3\\rangle\\}$，$G\\circ F=\\{\\langle2,3\\rangle\\}$。',
           'explanation': ['逆关系逐对交换两个分量，所以 $\\langle6,2\\rangle$ 变为 $\\langle2,6\\rangle$，自环 '
                           '$\\langle3,3\\rangle$ 不变。',
                           '计算 $F\\circ G$ 时寻找 $F$ 的第二分量等于 $G$ 第一分量的接点：只有 '
                           '$6\\xrightarrow{F}2\\xrightarrow{G}3$。',
                           '计算 $G\\circ F$ 时有 $2\\xrightarrow{G}3\\xrightarrow{F}3$，所以得到 '
                           '$\\langle2,3\\rangle$。',
                           '有的教材对复合顺序作相反约定。本题明确沿用原书，不能套用其他书的顺序。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 8.3': {'prompt': '设 $f:\\mathbb N\\to\\mathbb N$，\n'
                     '$$f(x)=\\begin{cases}x/2,&x\\text{ 为偶数},\\\\x+1,&x\\text{ 为奇数}.\\end{cases}$$\n'
                     '令 $A=\\{0,1\\}$，$B=\\{2\\}$，求 $f(A)$ 与 $f^{-1}(B)$。',
           'solution': '$f(A)=\\{f(0),f(1)\\}=\\{0,2\\}$；$f^{-1}(B)=\\{1,4\\}$。',
           'explanation': ['像集把 $A$ 中每个输入代入，$f(0)=0/2=0$，$f(1)=1+1=2$，再把输出组成集合。',
                           '原像要求解所有满足 $f(x)=2$ 的自然数，按奇偶两个分支分别求解。',
                           '偶数分支 $x/2=2$ 得 $x=4$，确为偶数；奇数分支 $x+1=2$ 得 $x=1$，确为奇数。因此两者都保留。',
                           '$f^{-1}(B)$ 表示集合的原像，不要求 $f$ 有反函数。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 8.6': {'prompt': '对下列集合 $A,B$ 构造双射函数 $f:A\\to B$。\n'
                     '(1) $A=P(\\{1,2,3\\})$，$B=\\{0,1\\}^{\\{1,2,3\\}}$（从 $\\{1,2,3\\}$ 到 $\\{0,1\\}$ '
                     '的全体函数）。\n'
                     '(2) $A=[0,1]$，$B=[1/4,1/2]$。\n'
                     '(3) $A=\\mathbb Z$，$B=\\mathbb N$。\n'
                     '(4) $A=[\\pi/2,3\\pi/2]$，$B=[-1,1]$。',
           'solution': '(1) 按 '
                       '$\\varnothing,\\{1\\},\\{2\\},\\{3\\},\\{1,2\\},\\{1,3\\},\\{2,3\\},\\{1,2,3\\}$ '
                       '的次序，分别对应函数 $f_0,\\ldots,f_7$；$f_i$ 在输入 1、2、3 处的取值依次为 $i$ 的三位二进制表示。例如 '
                       '$f_0=(0,0,0)$、$f_1=(0,0,1)$、$f_7=(1,1,1)$。这给出原书的一种双射。\n'
                       '(2) $f(x)=(x+1)/4$。\n'
                       '(3) $f(x)=2x$（$x\\ge0$），$f(x)=-2x-1$（$x<0$）。它使 $0,-1,1,-2,2,-3,3,\\ldots$ 依次对应 '
                       '$0,1,2,3,4,5,6,\\ldots$。\n'
                       '(4) $f(x)=\\sin x$。',
           'explanation': ['(1) 两边各有 8 个元素，原书将两边逐一排好并一一配对。也可以把每个子集映到其特征函数，得到另一种合法双射。',
                           '(2) 线性函数把端点 0、1 分别送到 $1/4,1/2$，严格递增，故既不重复也不漏掉区间内的值。',
                           '(3) 非负整数送到非负偶数，负整数送到正奇数；两部分不交，且覆盖所有自然数。',
                           '(4) 正弦在 $[\\pi/2,3\\pi/2]$ 上严格递减，由 1 变为 -1，所以每个目标值恰好对应一个输入。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 9.1': {'prompt': '二元运算的实例。判断以下通常运算是否为所给集合上的二元运算：自然数集上的加、减、乘、除；整数集上的加、减、乘、除；非零实数集上的加、减、乘、除；固定阶实矩阵上的加与乘；幂集上的并、交、相对补、对称差；同一集合上函数的复合。',
           'solution': '(1) $\\mathbb N$ 上加法、乘法是二元运算，减法、除法不是。\n'
                       '(2) $\\mathbb Z$ 上加法、减法、乘法是二元运算，除法不是。\n'
                       '(3) $\\mathbb R^*$ 上乘法、除法是二元运算，加法、减法不是。\n'
                       '(4) 固定 $n\\ge2$，$M_n(\\mathbb R)$ 上矩阵加法、乘法都是二元运算。\n'
                       '(5) 任意集合 $S$ 的幂集 $P(S)$ 上，$\\cup,\\cap,-,\\oplus$ 都是二元运算。\n'
                       '(6) $S^S$ 为 $S$ 上全体函数，函数复合是 $S^S$ 上的二元运算。',
           'explanation': ['二元运算必须是定义在整个 $S\\times S$ 上、且结果仍落在 $S$ 内的函数；既要处处可算，也要封闭。',
                           '自然数减法可得负数，整数除法可得非整数，且在含 0 的集合上除以 0 无定义。',
                           '非零实数相加或相减可能得 0，因而不封闭；乘除则仍为非零实数。',
                           '同阶矩阵相加、相乘仍同阶；子集的上述运算仍是 $S$ 的子集；两个 $S\\to S$ 的函数复合仍为 $S\\to S$。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 9.3': {'prompt': '一元运算的实例：取相反数、取倒数、取共轭、集合补、双射的逆函数、矩阵转置。分别说明它们适用的集合。',
           'solution': '(1) 取相反数是 $\\mathbb Z,\\mathbb Q,\\mathbb R$ 上的一元运算。\n'
                       '(2) 取倒数是 $\\mathbb Q^*,\\mathbb R^*$ 上的一元运算。\n'
                       '(3) 取共轭复数是 $\\mathbb C$ 上的一元运算。\n'
                       '(4) 以 $S$ 为全集，取绝对补是 $P(S)$ 上的一元运算。\n'
                       '(5) $A$ 为 $S$ 上全体双射的集合，取反函数是 $A$ 上的一元运算。\n'
                       '(6) 固定 $n\\ge2$，取转置是 $M_n(\\mathbb R)$ 上的一元运算。',
           'explanation': ['一元运算是从集合到自身的函数，检查一个输入能否得到唯一结果并留在原集合。',
                           '取倒数必须排除 0；反函数必须把输入限制为双射，才能保证逆仍是函数。',
                           '取补集必须先固定全集；固定阶方阵的转置仍是同阶方阵。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 9.11': {'prompt': '给出并验证以下同态实例。\n'
                      '(1) $\\langle\\mathbb Z,+\\rangle\\to\\langle\\mathbb '
                      'Z_n,\\oplus\\rangle$，$f(x)=x\\bmod n$。\n'
                      '(2) $\\langle\\mathbb R,+\\rangle\\to\\langle\\mathbb '
                      'R^*,\\cdot\\rangle$，$f(x)=e^x$。\n'
                      '(3) $\\langle\\mathbb Z,+\\rangle$ 上 $f_a(x)=ax$（$a\\in\\mathbb Z$）。',
            'solution': '(1) $f$ 是满同态：\n'
                        '$f(x+y)=(x+y)\\bmod n=(x\\bmod n)\\oplus(y\\bmod n)=f(x)\\oplus f(y)$。\n'
                        '(2) $f$ 是单同态：$f(x+y)=e^{x+y}=e^xe^y=f(x)f(y)$，且指数函数单射。\n'
                        '(3) $f_a$ 是自同态：$f_a(x+y)=a(x+y)=ax+ay=f_a(x)+f_a(y)$。$a=0$ 时为零同态；$a=\\pm1$ '
                        '时为自同构；其他整数 $a$ 给出单自同态。',
            'explanation': ['先核对保运算：源结构的加法，经映射后应等于目标结构中的对应运算，而不一定还是加法。',
                            '(1) 每个剩余类 $0,\\ldots,n-1$ 都有整数原像，因此满射；通常多个整数模 $n$ 余数相同，故不单。',
                            '(2) 指数严格递增，故单射；像是正实数，未覆盖负实数，所以在目标 $\\mathbb R^*$ 中不满。',
                            '(3) $a\\ne0$ 时 $ax=ay$ 推出 $x=y$；仅 $a=\\pm1$ 时像为全部整数，故仅这两种为自同构。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.17': {'prompt': '设 $A=\\{a,b,c,d\\}$，给定以下集合族，判断哪些是 $A$ 的划分。\n'
                      '$\\pi_1=\\{\\{a,b,c\\},\\{d\\}\\}$；\n'
                      '$\\pi_2=\\{\\{a,b\\},\\{c\\},\\{d\\}\\}$；\n'
                      '$\\pi_3=\\{\\{a\\},\\{a,b,c,d\\}\\}$；\n'
                      '$\\pi_4=\\{\\{a,b\\},\\{c\\}\\}$；\n'
                      '$\\pi_5=\\{\\varnothing,\\{a,b\\},\\{c,d\\}\\}$；\n'
                      '$\\pi_6=\\{\\{a,\\{a\\}\\},\\{b,c,d\\}\\}$。',
            'solution': '$\\pi_1,\\pi_2$ 是 $A$ 的划分，其他都不是。\n'
                        '$\\pi_3$ 中两个块相交；$\\bigcup\\pi_4\\ne A$，因为漏掉 $d$；$\\pi_5$ 含空块；$\\pi_6$ 的成员 '
                        '$\\{a,\\{a\\}\\}$ 不是 $A$ 的子集，因为 $\\{a\\}\\notin A$。',
            'explanation': ['划分的每个块都必须是 $A$ 的非空子集；这是最先应检查的条件。',
                            '再检查任意两个不同的块是否不相交，最后检查所有块的并是否等于整个 $A$。',
                            '前三个条件分别用“非空、不重、全覆盖”记忆；但还要先保证每个块真的由 $A$ 的元素构成。',
                            '$a$ 与 $\\{a\\}$ 不同，前者是本题的元素，后者是集合；把它们混同会漏掉 $\\pi_6$ 的错误。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 10.1': {'prompt': '判断下列代数系统属于半群、独异点或群中的哪些类型：普通数集的加法；固定阶实矩阵的加法与乘法；幂集上的对称差；模 $n$ 加法；全体自映射的复合；非零实数上定义 '
                      '$x\\circ y=y$ 的运算。',
            'solution': '(1) $\\langle\\mathbb Z^+,+\\rangle,\\langle\\mathbb N,+\\rangle,\\langle\\mathbb '
                        'Z,+\\rangle,\\langle\\mathbb Q,+\\rangle,\\langle\\mathbb '
                        'R,+\\rangle,\\langle\\mathbb C,+\\rangle$ 都是半群。除正整数加法外都是独异点；后四个是群。\n'
                        '(2) $n>1$ 时，$\\langle M_n(\\mathbb R),+\\rangle$ 与 $\\langle M_n(\\mathbb '
                        'R),\\cdot\\rangle$ 都是独异点；加法系统还是群，乘法系统不是群。\n'
                        '(3) $\\langle P(B),\\oplus\\rangle$ 是群。\n'
                        '(4) $\\langle\\mathbb Z_n,\\oplus\\rangle$ 是群。\n'
                        '(5) $\\langle A^A,\\circ\\rangle$ 是独异点；按原书“何时构成群”的提问补充：恰当 $|A|\\le1$ '
                        '时全体自映射都可逆，因而构成群。\n'
                        '(6) $\\langle\\mathbb R^*,\\circ\\rangle$（$x\\circ y=y$）是半群，没有双侧单位元，因而不是独异点、也不是群。',
            'explanation': ['按层次检查：运算封闭且结合得到半群；再有双侧单位元得到独异点；每个元素再有逆元才得到群。',
                            '加法的单位元为 0；正整数集不含 0，自然数集虽含 0 但正整数没有自然数加法逆元。',
                            '矩阵加法的逆是负矩阵；矩阵乘法虽有单位矩阵，但零矩阵等奇异矩阵没有逆。',
                            '对称差的单位元为空集，每个集合与自身对称差为空集；模 $n$ 加法中 $a$ 的逆是 $(-a)\\bmod n$。',
                            '若 $A$ 至少两个元素，就存在非双射常值函数，故全体自映射不能成群。对 (6)，$(x\\circ y)\\circ z=z=x\\circ(y\\circ '
                            'z)$，但 $x\\circ e=e$ 不可能对所有 $x$ 等于 $x$。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 10.2': {'prompt': '设 $G=\\{e,a,b,c\\}$，运算由下表给出，说明它的群结构。\n'
                      '\n'
                      '|运算|$e$|$a$|$b$|$c$|\n'
                      '|---|---|---|---|---|\n'
                      '|$e$|$e$|$a$|$b$|$c$|\n'
                      '|$a$|$a$|$e$|$c$|$b$|\n'
                      '|$b$|$b$|$c$|$e$|$a$|\n'
                      '|$c$|$c$|$b$|$a$|$e$|',
            'solution': '这是 Klein 四元群。$e$ 为单位元；运算可交换；每个元素的逆元都是自身；$a,b,c$ 中任意两个不同元素相乘得到第三个。',
            'explanation': ['单位元所在行和列应分别重现表头与行标，由此可读出 $e$。',
                            '表关于主对角线对称，所以运算可交换；对角线上全是 $e$，所以 $x^2=e$，每个元素自逆。',
                            '结合律不能只凭对称性判断。可将 $e,a,b,c$ 分别对应 $00,10,01,11$，表中运算即逐位模 2 加法；后者满足结合律，从而验证群公理。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 10.3': {'prompt': '设 $\\Sigma$ 是有穷字母表，$\\Sigma_k$ 是其上全部长为 $k$ '
                      '的串构成的集合，$\\Sigma_0=\\{\\lambda\\}$，$\\lambda$ 表示空串。令 '
                      '$\\Sigma^*=\\bigcup_{k=0}^{\\infty}\\Sigma_k$，$\\Sigma^+=\\Sigma^*-\\{\\lambda\\}$。在 '
                      '$\\Sigma^*$ 上定义串的连接运算，说明它构成的代数系统。',
            'solution': '若 $\\omega_1=a_1\\cdots a_m$、$\\omega_2=b_1\\cdots b_n$，则 '
                        '$\\omega_1\\omega_2=a_1\\cdots a_mb_1\\cdots b_n$。\n'
                        '$\\Sigma^*$ 关于连接构成独异点，称为 $\\Sigma$ 上的字代数，单位元是空串 $\\lambda$。$\\Sigma$ 上的形式语言就是 '
                        '$\\Sigma^*$ 的一个子集。',
            'explanation': ['两个有限串连接后仍是有限串，所以封闭。',
                            '三个串无论先连接前两个还是后两个，都得到按同样顺序排列的符号串，因此结合律成立。',
                            '空串连接在任意串左边或右边都不改变该串，所以是双侧单位元。非空串的长度为正，不能通过连接变为空串，通常没有逆元。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 10.8': {'prompt': '设 $G$ 为群、$a\\in G$，令 $H=\\{a^k\\mid k\\in\\mathbb Z\\}$。证明 $H$ 为 $G$ 的子群，并给出整数加群、模 6 '
                      '加群及 Klein 四元群中的实例。',
            'solution': '$H$ 非空，任取 $a^m,a^n\\in H$，有 $a^m(a^n)^{-1}=a^{m-n}\\in H$，由子群判定定理得 $H\\le G$，记为 '
                        '$\\langle a\\rangle$，称为由 $a$ 生成的子群。\n'
                        '整数加群中 $\\langle2\\rangle=\\{2k\\mid k\\in\\mathbb Z\\}=2\\mathbb Z$。\n'
                        '模 6 加群中 $\\langle2\\rangle=\\{0,2,4\\}$。\n'
                        'Klein 四元群中 $\\langle e\\rangle=\\{e\\}$，$\\langle a\\rangle=\\{e,a\\}$，$\\langle '
                        'b\\rangle=\\{e,b\\}$，$\\langle c\\rangle=\\{e,c\\}$。',
            'explanation': ['使用“非空且对 $xy^{-1}$ 封闭”的子群判定，比逐条验证群公理更短。',
                            '指数允许负整数，所以所有逆元也被包含；$m-n$ 仍是整数，证明了所需封闭性。',
                            '在加法记号中，乘法幂应理解为整数倍。模 6 时不断加 2，得到 $0,2,4$ 后循环。',
                            'Klein 群中每个非单位元平方等于单位元，所以它生成的子群仅有两个元素。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 10.16': {'prompt': '设 $S=\\{1,2,\\ldots,8\\}$，置换\n'
                       '$$\\sigma=\\begin{pmatrix}1&2&3&4&5&6&7&8\\\\5&3&6&4&2&1&8&7\\end{pmatrix}.$$\n'
                       '把它分解为不交轮换之积，并进一步写成对换之积。沿用原书置换从左到右作用的顺序。',
             'solution': '由 $1\\mapsto5\\mapsto2\\mapsto3\\mapsto6\\mapsto1$ 得轮换 $(1\\ 5\\ 2\\ 3\\ 6)$。\n'
                         '$4\\mapsto4$ 得 $(4)$，$7\\mapsto8\\mapsto7$ 得 $(7\\ 8)$。\n'
                         '所以 $\\sigma=(1\\ 5\\ 2\\ 3\\ 6)(4)(7\\ 8)=(1\\ 5\\ 2\\ 3\\ 6)(7\\ 8)$。\n'
                         '按原书乘法顺序，可写为 $\\sigma=(1\\ 5)(1\\ 2)(1\\ 3)(1\\ 6)(7\\ 8)$。',
             'explanation': ['从尚未使用的元素出发，持续跟随置换的像，首次回到起点就得到一个轮换。',
                             '标记已经写入轮换的元素，再从剩余元素继续，直到每个元素都用过一次。',
                             '长度为 $k$ 的轮换可拆为 $k-1$ 个对换，本题的五轮换拆成 4 个，再加 $(7\\ 8)$ 共 5 个，所以此置换为奇置换。',
                             '不交轮换可以交换次序，且一阶轮换通常省略；有交的对换不能随意交换次序。'],
             'status': 'reviewed',
             'issues': [],
             'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 10.18': {'prompt': '环的实例：整数、有理数、实数、复数上的普通加乘；固定阶实矩阵的加乘；幂集上的对称差和交；模 $n$ 的加法与乘法。',
             'solution': '(1) $\\mathbb Z,\\mathbb Q,\\mathbb R,\\mathbb C$ 关于普通加法和乘法均构成环。\n'
                         '(2) $n\\ge2$ 时，$M_n(\\mathbb R)$ 关于矩阵加法和乘法构成 $n$ 阶实矩阵环。\n'
                         '(3) $P(B)$ 关于对称差 $\\oplus$ 和交 $\\cap$ 构成环。\n'
                         '(4) $\\mathbb Z_n=\\{0,1,\\ldots,n-1\\}$ 关于模 $n$ 加法 $\\oplus$ 和乘法 $\\otimes$ 构成模 '
                         '$n$ 的整数环。',
             'explanation': ['环要求加法形成交换群、乘法满足结合律、乘法对加法满足左右分配律。乘法可不交换，也不要求每个非零元素有逆元。',
                             '矩阵加法构成交换群，矩阵乘法结合并对加法分配，所以即使乘法不交换，仍然构成环。',
                             '幂集中空集为加法单位元，每个集合是自己的对称差逆元；交对对称差满足分配律。',
                             '模 $n$ 运算继承整数运算的结合与分配性质，同时结果取余后仍落在 $\\mathbb Z_n$。'],
             'status': 'reviewed',
             'issues': [],
             'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 10.20': {'prompt': '区分以下环的性质：$\\mathbb Z,\\mathbb Q,\\mathbb R,\\mathbb C$；偶整数环 $2\\mathbb Z$；$n\\ge2$ '
                       '阶实矩阵环；模 6 整数环。',
             'solution': '(1) $\\mathbb Z,\\mathbb Q,\\mathbb R,\\mathbb C$ 都是交换环、含幺环、无零因子环和整环；其中 $\\mathbb '
                         'Q,\\mathbb R,\\mathbb C$ 是域。\n'
                         '(2) $2\\mathbb Z$ 是交换环、无零因子环，但无乘法单位元，不是含幺环与整环。\n'
                         '(3) $M_n(\\mathbb R)$ 是含幺环，但不是交换环、无零因子环或整环。\n'
                         '(4) $\\mathbb Z_6$ 是交换含幺环，但 $2\\otimes3=0$，存在非零零因子，所以不是整环。一般 $\\mathbb Z_n$ 为域当且仅当 '
                         '$n$ 为素数。',
             'explanation': ['先看乘法是否交换，再看单位元是否在集合内，再检查是否存在两个非零元素乘积为零。',
                             '偶整数中若存在乘法单位元 $e$，由 $2e=2$ 得 $e=1$，但 1 不在偶整数集，所以不存在其他可替代的单位元。',
                             '矩阵单位元是 $I$；例如 $E_{11}E_{22}=0$ 而两个矩阵均非零，说明有零因子。且 '
                             '$E_{11}E_{12}=E_{12}$、$E_{12}E_{11}=0$，说明乘法不交换。',
                             '域还要求每个非零元素可逆，整数 2 在整数环中没有乘法逆元，所以整数环不是域。'],
             'status': 'reviewed',
             'issues': [],
             'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 11.1': {'prompt': '设 $n$ 是正整数，$S_n$ 是 $n$ 的所有正因子的集合，$D$ 为整除关系。说明 $\\langle S_n,D\\rangle$ 构成格。',
            'solution': '对任意 $x,y\\in S_n$，$x\\lor y=\\operatorname{lcm}(x,y)$，$x\\land y=\\gcd(x,y)$。这两个数仍是 '
                        '$n$ 的因子，因此任意两元素都有最小上界与最大下界，构成格。\n'
                        '原书示例：$S_8=\\{1,2,4,8\\}$ 为链；$S_6=\\{1,2,3,6\\}$；$S_{30}=\\{1,2,3,5,6,10,15,30\\}$。',
            'explanation': ['整除偏序中的“上界”是公共倍数，“下界”是公共因子；所以最小上界对应最小公倍数，最大下界对应最大公约数。',
                            '$x,y$ 都整除 $n$，所以它们的最小公倍数仍整除 $n$；最大公约数更是 $n$ 的因子，二者都没有离开 $S_n$。',
                            '不要把整除关系下的上、下界直接理解成数值最大、最小。例如 2 和 3 的上确界是 6，下确界是 1。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 11.3': {'prompt': '设 $G$ 是群，$L(G)=\\{H\\mid H\\le G\\}$ 为它的所有子群的集合。按集合包含关系排序，说明 $L(G)$ 构成格。',
            'solution': '任意 $H_1,H_2\\in L(G)$，交集 $H_1\\cap H_2$ 是子群，且为二者的最大下界；由并集生成的子群 $\\langle H_1\\cup '
                        'H_2\\rangle$ 是二者的最小上界。\n'
                        '所以 $H_1\\land H_2=H_1\\cap H_2$，$H_1\\lor H_2=\\langle H_1\\cup H_2\\rangle$，从而 '
                        '$L(G)$ 构成格，称为 $G$ 的子群格。',
            'explanation': ['交集包含在两个子群中；任何同时包含在二者中的子群也包含在交集中，所以交集是最大下界。',
                            '直接取并集未必对群运算封闭，因此不能一般地将上确界写成并集。',
                            '由并集生成的子群包含 $H_1,H_2$；任何包含二者的子群都必须包含它们所有有限乘积和逆元，也就包含这个生成子群，所以它是最小上界。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 13.1': {'prompt': 'Hanoi 塔：三个柱子 $A,B,C$，初始 $A$ 上有 $n$ 个圆盘，小盘在大盘上。每次只能移动一个圆盘，可借助 $B$，不能把大盘放在小盘上。将全部圆盘由 '
                      '$A$ 移到 $C$，需要多少次移动？给出递归算法及递推式。',
            'solution': '递归算法：若 $n=1$，把唯一圆盘由 $A$ 移到 $C$；否则先把上面 $n-1$ 个盘由 $A$ 借 $C$ 移到 $B$，把最大盘由 $A$ 移到 '
                        '$C$，再把 $B$ 上的 $n-1$ 个盘借 $A$ 移到 $C$。\n'
                        '移动次数满足 $T(1)=1$，$T(n)=2T(n-1)+1$，解为 $T(n)=2^n-1$。\n'
                        '$n=64$ 时需 $2^{64}-1=18\\,446\\,744\\,073\\,709\\,551\\,615$ 次。',
            'explanation': ['最大盘要移动到目标柱前，所有小盘都必须暂时离开它，形成一个规模为 $n-1$ 的同类子问题。',
                            '最大盘移动一次后，还要把这 $n-1$ 个小盘移到它上面，又是同样规模的子问题，所以出现两次 $T(n-1)$。',
                            '用 $T(n)+1=2(T(n-1)+1)$ 将非齐次递推化为等比关系，得 $T(n)+1=2^n$。',
                            '若要证明最少次数，也利用最大盘第一次到达目标柱前后都至少需完成这两次子任务的下界，与递归算法达到的次数相同。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 13.6': {'prompt': '求 Hanoi 塔递推方程 $H(n)=2H(n-1)+1$，初值 $H(1)=1$。',
            'solution': '齐次方程 $H(n)=2H(n-1)$ 的通解为 $c2^n$。\n'
                        '设原方程的常数特解为 $H^*(n)=P$，代入得 $P=2P+1$，所以 $P=-1$。\n'
                        '原方程通解为 $H(n)=c2^n-1$。由 $H(1)=1$ 得 $2c-1=1$，故 $c=1$，最终 $H(n)=2^n-1$。',
            'explanation': ['先忽略常数项求对应齐次方程，其特征根为 2。',
                            '非齐次项是常数，可试常数特解；因为 1 不是齐次特征根，这里不需要再乘 $n$。',
                            '把齐次通解和特解相加，再用初值确定唯一的系数。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 13.20': {'prompt': '给定正整数 $m$，$a_n=P(m,n)$，求数列 $\\{a_n\\}$ 的指数生成函数。',
             'solution': '$$G_e(x)=\\sum_{n=0}^{\\infty}P(m,n)\\frac{x^n}{n!}=\\sum_{n=0}^{m}\\frac{m!}{n!(m-n)!}x^n=\\sum_{n=0}^{m}\\binom '
                         'mn x^n=(1+x)^m.$$\n'
                         '因此 $(1+x)^m$ 既是组合数序列 $\\{C(m,n)\\}$ 的普通生成函数，也是排列数序列 $\\{P(m,n)\\}$ 的指数生成函数。',
             'explanation': ['指数生成函数使用 $a_n/n!$ 作系数，不能漏掉分母 $n!$。',
                             '对 $0\\le n\\le m$，$P(m,n)=m!/(m-n)!$；超过 $m$ 后排列数取 0，所以无限级数实际截到 $m$。',
                             '除以 $n!$ 后恰好得到组合数 $\\binom mn$，最后用二项式定理合并。'],
             'status': 'reviewed',
             'issues': [],
             'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 18.5': {'prompt': '给出长度大于等于 2 的偶圈、长度大于等于 3 的奇圈的边色数。',
            'solution': '偶圈的边色数为 2；奇圈的边色数为 3。',
            'explanation': ['圈上每个顶点关联两条边，相邻边颜色必须不同，所以至少需要两种颜色。',
                            '偶圈沿环交替使用两色，最后一条与第一条仍颜色不同，故两色足够。',
                            '奇圈若交替两色，最后一条必与第一条同色且相邻，产生冲突，所以至少三色；前偶数条边交替两色，最后一条用第三色即可，故正好三色。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 19.11': {'prompt': 'RSA 算例：取 $p=43,q=59,n=pq=2537$，$\\varphi(n)=2436$，加密指数 $w=13$。字母 $a,b,\\ldots,z$ 用 '
                       '$00,01,\\ldots,25$ 表示。加密明文 $m=2106$（vg）；再将收到的密文 0981 解密。',
             'solution': '加密：$13=1+2^2+2^3$。反复平方并取模得\n'
                         '$A_0=2106\\equiv-431$，$A_1\\equiv560$，$A_2\\equiv-988$，$A_3\\equiv-601\\pmod{2537}$。\n'
                         '故 $c=2106^{13}\\bmod2537=(-431)(-988)(-601)\\bmod2537=2321$。\n'
                         '解密指数 $d=13^{-1}\\bmod2436=937$（$13\\cdot937=5\\cdot2436+1$）。\n'
                         '$937=1+2^3+2^5+2^7+2^8+2^9$。\n'
                         '从 $A_0=981$ 开始，逐次平方取模得到 '
                         '$A_1=838,A_2\\equiv-505,A_3=1325,A_4=21,A_5=441,A_6\\equiv-868,A_7\\equiv-65,A_8\\equiv-849,A_9=293$。\n'
                         '因此 '
                         '$981^{937}\\equiv981\\cdot1325\\cdot441\\cdot(-65)\\cdot(-849)\\cdot293\\equiv704\\pmod{2537}$。\n'
                         '补足四位为 0704，按两位一字母解为 he。',
             'explanation': ['模幂不用直接算出巨大整数，先逐次平方，始终把数压缩为模 2537 的余数；负余数也可使用，只要同余即可。',
                             '把指数写成二进制，只乘二进制为 1 的位对应的幂。例如 13 的二进制是 1101，取 $A_0,A_2,A_3$。',
                             '解密指数是加密指数在模 $\\varphi(n)$ 下的乘法逆元，而不是模 $n$ 的逆元。',
                             '解密结果须保留前导 0，否则无法按约定的两位编码分割。'],
             'status': 'reviewed',
             'issues': [],
             'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 2.1': {'prompt': '判断 $\\neg(p\\lor q)$ 与 $\\neg p\\land\\neg q$ 是否等值。',
           'solution': '两式等值，即 $\\neg(p\\lor q)\\Leftrightarrow\\neg p\\land\\neg q$。\n'
                       '\n'
                       '|$p$|$q$|$\\neg(p\\lor q)$|$\\neg p\\land\\neg q$|两式的等价式|\n'
                       '|---|---|---|---|---|\n'
                       '|0|0|1|1|1|\n'
                       '|0|1|0|0|1|\n'
                       '|1|0|0|0|1|\n'
                       '|1|1|0|0|1|',
           'explanation': ['列齐两个变项的四种赋值，分别求两式的值。',
                           '两列逐行一致，所以它们的等价式在所有赋值下均真，说明两式等值。',
                           '这就是德摩根律：否定一个析取，相当于分别否定各项后改用合取。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 2.2': {'prompt': '判断下列各组公式是否等值。\n'
                     '(1) $p\\to(q\\to r)$ 与 $(p\\land q)\\to r$。\n'
                     '(2) $(p\\to q)\\to r$ 与 $(p\\land q)\\to r$。',
           'solution': '(1) 等值；(2) 不等值。\n'
                       '\n'
                       '|$pqr$|$p\\to(q\\to r)$|$(p\\land q)\\to r$|$(p\\to q)\\to r$|\n'
                       '|---|---|---|---|\n'
                       '|000|1|1|0|\n'
                       '|001|1|1|1|\n'
                       '|010|1|1|0|\n'
                       '|011|1|1|1|\n'
                       '|100|1|1|1|\n'
                       '|101|1|1|1|\n'
                       '|110|0|0|0|\n'
                       '|111|1|1|1|',
           'explanation': ['第一式 $p\\to(q\\to r)$ 化为 $\\neg p\\lor\\neg q\\lor r$；第二式 $(p\\land q)\\to r$ '
                           '同样化为 $\\neg p\\lor\\neg q\\lor r$，因此等值。',
                           '$(p\\to q)\\to r$ 则化为 $(p\\land\\neg q)\\lor r$，与前式不同。',
                           '取赋值 $pqr=000$，后者为 0，而 $(p\\land q)\\to r$ 为 1，找到一个反例就足以证明不等值。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 2.3': {'prompt': '用等值演算法验证 $(p\\lor q)\\to r\\Leftrightarrow(p\\to r)\\land(q\\to r)$。',
           'solution': '从右边出发：\n'
                       '$(p\\to r)\\land(q\\to r)$\n'
                       '$\\Leftrightarrow(\\neg p\\lor r)\\land(\\neg q\\lor r)$（蕴含等值式）\n'
                       '$\\Leftrightarrow(\\neg p\\land\\neg q)\\lor r$（分配律）\n'
                       '$\\Leftrightarrow\\neg(p\\lor q)\\lor r$（德摩根律）\n'
                       '$\\Leftrightarrow(p\\lor q)\\to r$（蕴含等值式）。',
           'explanation': ['先消去蕴含，把两边都转为只含否定、合取、析取的形式。',
                           '右式中重复出现的 $r$ 可按分配律提取出来，剩下 $\\neg p\\land\\neg q$。',
                           '将两项否定的合取按德摩根律合并，再识别为蕴含式，就到达左边。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 2.4': {'prompt': '证明 $(p\\to q)\\to r$ 与 $p\\to(q\\to r)$ 不等值。',
           'solution': '令 $A=(p\\to q)\\to r$，$B=p\\to(q\\to r)$。\n'
                       '$A\\Leftrightarrow\\neg(\\neg p\\lor q)\\lor r\\Leftrightarrow(p\\land\\neg q)\\lor '
                       'r$。\n'
                       '$B\\Leftrightarrow\\neg p\\lor(\\neg q\\lor r)\\Leftrightarrow\\neg p\\lor\\neg '
                       'q\\lor r$。\n'
                       '赋值 000 或 010 均使 $A=0,B=1$，故两式不等值。',
           'explanation': ['要证明等值需覆盖所有赋值；证明不等值只需找到一个赋值让两边不同。',
                           '消去蕴含后，$r=0$ 时两式分别为 $p\\land\\neg q$ 和 $\\neg p\\lor\\neg q$。',
                           '取 $p=0$，前式必假、后式必真，而 $q$ 可任取，所以得到 000、010 两个反例。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 2.5': {'prompt': '用等值演算法判断公式的类型。\n'
                     '(1) $((p\\to q)\\land p)\\to q$。\n'
                     '(2) $\\neg(p\\to(p\\lor q))\\land r$。\n'
                     '(3) $p\\land(((p\\lor q)\\land\\neg p)\\to q)$。',
           'solution': '(1) 是重言式：\n'
                       '$((p\\to q)\\land p)\\to q\\Leftrightarrow\\neg((\\neg p\\lor q)\\land p)\\lor '
                       'q\\Leftrightarrow\\neg(p\\land q)\\lor q\\Leftrightarrow\\neg p\\lor\\neg q\\lor '
                       'q\\Leftrightarrow1$。\n'
                       '(2) 是矛盾式：\n'
                       '$\\neg(p\\to(p\\lor q))\\land r\\Leftrightarrow\\neg(\\neg p\\lor p\\lor q)\\land '
                       'r\\Leftrightarrow\\neg1\\land r\\Leftrightarrow0$。\n'
                       '(3) 等值于 $p$：\n'
                       '$p\\land(((p\\lor q)\\land\\neg p)\\to q)\\Leftrightarrow p\\land((q\\land\\neg '
                       'p)\\to q)\\Leftrightarrow p\\land(\\neg q\\lor p\\lor q)\\Leftrightarrow p$。\n'
                       '故 (3) 是非重言式的可满足式，成假赋值为 00、01，成真赋值为 10、11（按 $p,q$）。',
           'explanation': ['先消去最外层蕴含，再用分配律、吸收律和互补律化简。',
                           '(1) 的前件已包含 $p\\to q$ 与 $p$，不可能前件真而 $q$ 假；化简结果为 1，验证了假言推理。',
                           '(2) 内层 $p\\to(p\\lor q)$ 永真，否定后为假，再合取任何 $r$ 都为假。',
                           '(3) 中 $(q\\land\\neg p)\\to q$ 永真，所以只剩 $p$；分类时不能因为公式最后不含 $q$ 就把原赋值长度改为 1。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 2.6': {'prompt': '三人判断王教授籍贯：甲说“不是苏州人，是上海人”；乙说“不是上海人，是苏州人”；丙说“既不是上海人，也不是杭州人”。王教授说三人中一人全对、一人一半对、一人全错。用逻辑演算确定王教授是哪里人。',
           'solution': '设 $p,q,r$ 依次表示“王教授是苏州人、上海人、杭州人”。\n'
                       '甲的两句为 $\\neg p,q$；乙为 $\\neg q,p$；丙为 $\\neg q,\\neg r$。\n'
                       '记三人的全对、一半对、全错分别为 $B_i,C_i,D_i$（$i=1,2,3$ 表示全对、半对、全错）。则\n'
                       '$B_1=\\neg p\\land q$，$B_2=(\\neg p\\land\\neg q)\\lor(p\\land q)$，$B_3=p\\land\\neg '
                       'q$；\n'
                       '$C_1=p\\land\\neg q$，$C_2=(p\\land q)\\lor(\\neg p\\land\\neg q)$，$C_3=\\neg p\\land '
                       'q$；\n'
                       '$D_1=\\neg q\\land\\neg r$，$D_2=(\\neg q\\land r)\\lor(q\\land\\neg r)$，$D_3=q\\land '
                       'r$。\n'
                       '“一人全对、一人半对、一人全错”共六种排列，将六个相应合取式析取，化简得\n'
                       '$E\\Leftrightarrow(\\neg p\\land q\\land\\neg r)\\lor(p\\land\\neg q\\land r)$。\n'
                       '王教授不可能同时为苏州和杭州人，故第二项排除，得 $\\neg p\\land q\\land\\neg r$。\n'
                       '王教授是上海人；甲全对，丙一半对，乙全错。',
           'explanation': ['每个人有两个判断，“一半对”表示两个分句真值相反，不能直接等同于整句合取为假。',
                           '把“全对、半对、全错”分别写成真值条件，再列出三种身份在三人之间的六个分配。',
                           '逻辑公式还应加入籍贯互斥的语境约束；若只计算六种排列而不加约束，会多保留 $p=r=1$ 的不合题意情况。',
                           '最后回代：上海人使甲的“非苏州、上海”均真；乙的“非上海、苏州”均假；丙的“非上海、非杭州”一假一真。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 2.7': {'prompt': '求 $(p\\to q)\\leftrightarrow r$ 的析取范式与合取范式。',
           'solution': '先消去等价与蕴含：\n'
                       '$(p\\to q)\\leftrightarrow r\\Leftrightarrow((\\neg p\\lor q)\\to '
                       'r)\\land(r\\to(\\neg p\\lor q))$\n'
                       '$\\Leftrightarrow((p\\land\\neg q)\\lor r)\\land(\\neg p\\lor q\\lor\\neg r)$。\n'
                       '合取范式为 $(p\\lor r)\\land(\\neg q\\lor r)\\land(\\neg p\\lor q\\lor\\neg r)$。\n'
                       '析取范式为 $(p\\land\\neg q\\land\\neg r)\\lor(\\neg p\\land r)\\lor(q\\land r)$。',
           'explanation': ['先把 $A\\leftrightarrow B$ 换成 $(A\\to B)\\land(B\\to A)$，再全部消去蕴含。',
                           '求合取范式时，目标是若干析取子句的合取，使用析取对合取的分配律展开 $(p\\land\\neg q)\\lor r$。',
                           '求析取范式时，目标是若干合取项的析取，向相反方向分配并删去同时含 $p$ 与 $\\neg p$ 等矛盾的项。',
                           '普通范式不要求每一项含全体变项，主范式才要求，因此这里两项可以只有两个文字。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 2.8': {'prompt': '求 $(p\\to q)\\leftrightarrow r$ 的主析取范式与主合取范式（按 $p,q,r$ 编号）。',
           'solution': '由例 2.7 的析取范式：\n'
                       '$(p\\land\\neg q\\land\\neg r)\\lor(\\neg p\\land r)\\lor(q\\land r)$。\n'
                       '$\\neg p\\land r\\Leftrightarrow(\\neg p\\land\\neg q\\land r)\\lor(\\neg p\\land '
                       'q\\land r)=m_1\\lor m_3$；\n'
                       '$q\\land r\\Leftrightarrow(\\neg p\\land q\\land r)\\lor(p\\land q\\land r)=m_3\\lor '
                       'm_7$。\n'
                       '第一项为 $m_4$，删去重复后，主析取范式为 $m_1\\lor m_3\\lor m_4\\lor m_7$。\n'
                       '由合取范式补足变量：$p\\lor r\\Leftrightarrow M_0\\land M_2$，$\\neg q\\lor r\\Leftrightarrow '
                       'M_2\\land M_6$，第三项为 $M_5$。\n'
                       '主合取范式为 $M_0\\land M_2\\land M_5\\land M_6$。',
           'explanation': ['主析取范式每项必须含 $p,q,r$；缺 $q$ 就乘 $q\\lor\\neg q$，缺 $p$ 就乘 $p\\lor\\neg p$，展开后得到极小项。',
                           '极小项编号来自唯一成真赋值；例如 $p\\land\\neg q\\land\\neg r$ 对应 100，即编号 4。',
                           '主合取范式每个子句也要含全体变项；缺变量就借助 $x\\land\\neg x=0$ 后分配补足。',
                           '最后作交叉检查：真编号为 1、3、4、7，假编号正好为其余 0、2、5、6，合计覆盖 0 至 7。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 2.9': {'prompt': '求命题公式 $p\\to q$ 的主析取范式与主合取范式。',
           'solution': '$p\\to q\\Leftrightarrow\\neg p\\lor q=M_2$，这已经是主合取范式。\n'
                       '补足极小项：\n'
                       '$\\neg p\\lor q\\Leftrightarrow(\\neg p\\land(\\neg q\\lor q))\\lor((\\neg p\\lor '
                       'p)\\land q)$\n'
                       '$\\Leftrightarrow(\\neg p\\land\\neg q)\\lor(\\neg p\\land q)\\lor(p\\land q)$。\n'
                       '主析取范式为 $m_0\\lor m_1\\lor m_3$。',
           'explanation': ['公式含两个变项，所以极小项或极大项中均应恰有两个文字。',
                           '蕴含仅在 $p=1,q=0$ 时假，即编号 2，所以主合取范式只有 $M_2$。',
                           '其余三个赋值 00、01、11 都使公式真，所以主析取范式依次收录 $m_0,m_1,m_3$。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 2.10': {'prompt': '用公式的主析取范式判断下述公式的类型。\n'
                      '(1) $\\neg(p\\to q)\\land q$。\n'
                      '(2) $p\\to(p\\lor q)$。\n'
                      '(3) $(p\\lor q)\\to r$。',
            'solution': '(1) $\\neg(p\\to q)\\land q\\Leftrightarrow(p\\land\\neg q)\\land '
                        'q\\Leftrightarrow0$，无极小项，为矛盾式。\n'
                        '(2) $p\\to(p\\lor q)\\Leftrightarrow\\neg p\\lor p\\lor '
                        'q\\Leftrightarrow1\\Leftrightarrow m_0\\lor m_1\\lor m_2\\lor m_3$，为重言式。\n'
                        '(3) $(p\\lor q)\\to r\\Leftrightarrow(\\neg p\\land\\neg q)\\lor r\\Leftrightarrow '
                        'm_0\\lor m_1\\lor m_3\\lor m_5\\lor m_7$，是非重言式的可满足式。',
            'explanation': ['含 $n$ 个变项的公式共有 $2^n$ 个极小项；全部出现是重言式，一个也不出现是矛盾式，介于二者之间就是非重言式的可满足式。',
                            '(1) 同时要求 $q$ 与 $\\neg q$，所以立即化为 0。',
                            '(2) 含 $p\\lor\\neg p$，立即化为 1；虽然表达式已简成常数，写主范式时仍按原题两个变项列全四项。',
                            '(3) 当 $r=1$ 时四种 $p,q$ 均可；当 $r=0$ 时必须 $p=q=0$，因此共有五个成真赋值。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 2.11': {'prompt': '判断两组公式是否等值。\n'
                      '(1) $p$ 与 $(p\\land q)\\lor(p\\land\\neg q)$。\n'
                      '(2) $(p\\to q)\\to r$ 与 $(p\\land q)\\to r$。',
            'solution': '(1) 两式的主析取范式均为 $m_2\\lor m_3$，所以等值。\n'
                        '(2) $(p\\to q)\\to r\\Leftrightarrow m_1\\lor m_3\\lor m_4\\lor m_5\\lor m_7$；\n'
                        '$(p\\land q)\\to r\\Leftrightarrow m_0\\lor m_1\\lor m_2\\lor m_3\\lor m_4\\lor '
                        'm_5\\lor m_7$。\n'
                        '两者主析取范式不同，因而不等值。',
            'explanation': ['比较主范式前必须统一命题变项及其顺序；(1) 里 $p$ 要作为含 $p,q$ 两个变项的公式来处理。',
                            '$p=p\\land(q\\lor\\neg q)$，分配后正好得到另一式，所以 (1) 等值。',
                            '(2) 两个公式的真编号集合相差 0 和 2；取赋值 000 或 010 就能直接看出一个假、另一个真。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 2.12': {'prompt': '某科研所要从 $A,B,C$ 三名科研骨干中挑选 1～2 名出国进修，要求：(1) 若 $A$ 去，则 $C$ 同去；(2) 若 $B$ 去，则 $C$ 不能去；(3) '
                      '若 $C$ 不去，则 $A$ 或 $B$ 可以去。有哪些选派方案？',
            'solution': '设 $p,q,r$ 分别表示选派 $A,B,C$。条件合取为\n'
                        '$(p\\to r)\\land(q\\to\\neg r)\\land(\\neg r\\to(p\\lor q))$。\n'
                        '其主析取范式为\n'
                        '$(\\neg p\\land\\neg q\\land r)\\lor(\\neg p\\land q\\land\\neg '
                        'r)\\lor(p\\land\\neg q\\land r)=m_1\\lor m_2\\lor m_5$。\n'
                        '因此三种方案为：只派 $C$；只派 $B$；派 $A,C$。',
            'explanation': ['将每一条条件先翻译成蕴含，再用合取表示这些条件必须同时成立。',
                            '找使合取式为真的赋值，按 1 表示“去”、0 表示“不去”还原成人员集合。',
                            '001、010、101 依次对应 $\\{C\\}$、$\\{B\\}$、$\\{A,C\\}$；每种均满足题设派出 1～2 人的数量限制。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 2.15': {'prompt': '用消解法判断下列公式是否可满足。\n'
                      '(1) $(\\neg p\\lor q)\\land(p\\lor q)\\land\\neg q$。\n'
                      '(2) $p\\land(p\\lor q)\\land(p\\lor\\neg q)\\land(q\\lor\\neg r)\\land(q\\lor r)$。',
            'solution': '(1) 子句 $\\neg p\\lor q$ 与 $p\\lor q$ 消解得到 $q$；$q$ 再与 $\\neg q$ 消解得到空子句 '
                        '$\\lambda$，所以不可满足。\n'
                        '(2) $q\\lor\\neg r$ 与 $q\\lor r$ 消解得到 $q$；其他可能的新消解式包括 $p\\lor r$、$p\\lor\\neg '
                        'r$，继续消解不再产生新子句且没有空子句，因此可满足。例如 $p=q=1$，$r$ 任取。',
            'explanation': ['将合取范式视作子句集合。若一对子句含互补文字，如 $p$ 与 $\\neg p$，可删除这对文字并把余下文字析取成消解式。',
                            '(1) 得到互相冲突的单位子句 $q$ 与 $\\neg q$，它们的消解式为空，证明原条件无法同时为真。',
                            '(2) 不应把“这一步没推出空子句”直接当成可满足；需完成到不再产生新子句，或直接给出满足赋值。这里 $p=q=1$ 就是可核验的满足证据。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 6.3': {'prompt': '设 $A=\\{\\{a\\},\\{a,b\\}\\}$，计算 $\\bigcup\\bigcup A$、$\\bigcap\\bigcap A$ 和 '
                     '$(\\bigcap\\bigcup A)\\cup((\\bigcup\\bigcup A)-(\\bigcup\\bigcap A))$。',
           'solution': '$\\bigcup A=\\{a,b\\}$，$\\bigcap A=\\{a\\}$。\n'
                       '所以 $\\bigcup\\bigcup A=a\\cup b$，$\\bigcap\\bigcap A=a$。\n'
                       '第三式为 $(a\\cap b)\\cup((a\\cup b)-a)=(a\\cap b)\\cup(b-a)=b$。',
           'explanation': ['同类广义运算从右往左计算，先算最靠近 $A$ 的广义并、广义交。',
                           '注意 $a,b$ 在集合论表达中本身也是集合。$\\bigcup\\{a,b\\}=a\\cup b$，但 $\\bigcap\\{a\\}=a$。',
                           '第三式中 $b$ 被分成位于 $a$ 内的 $a\\cap b$ 和位于 $a$ 外的 $b-a$，两部分并回去正好为 $b$。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 6.4': {'prompt': '调查 24 名会外语的科技人员，会英语、日语、德语、法语的分别有 13、5、10、9 人。英语和日语都会的有 2 人；英、德、法三语中每两种都会的均为 4 '
                     '人。会日语者既不懂法语也不懂德语。求只会英、法、德、日中一种的人数，以及同时会三种语言的人数。',
           'solution': '设 $x$ 为同时会英、法、德三语的人数；$y_1,y_2,y_3$ 分别为只会英语、法语、德语的人数。每个“恰会英法、英德、法德两语”的区域都是 '
                       '$4-x$；只会日语的有 $5-2=3$ 人。\n'
                       '有\n'
                       '$y_1+2(4-x)+x+2=13$，\n'
                       '$y_2+2(4-x)+x=9$，\n'
                       '$y_3+2(4-x)+x=10$，\n'
                       '$y_1+y_2+y_3+3(4-x)+x=19$。\n'
                       '解得 $x=1,y_1=4,y_2=2,y_3=3$。\n'
                       '所以只会英、法、德、日语的人数依次为 4、2、3、3，同时会三种的为 1 人。',
           'explanation': ['“同时会两种”通常包含也会第三种的人，因此每个两语交集 4 人不能直接当作只会两语人数，应先减三语人数 $x$。',
                           '日语与法语、德语没有交集，只与英语交 2 人，所以日语区域可以独立确定。',
                           '总人数 24 去掉全部 5 名会日语者后剩 19，正好用于最后一个方程；英语方程还要保留与日语的 2 人。',
                           '解出后可回代检查：三语 1 人，恰两语每类 3 人，英语单语 4 人加 6 名恰两语、1 名三语、2 名英日，合为 13。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 6.5': {'prompt': '求 1 到 1000（含端点）之间，不能被 5、6、8 中任何一个整除的整数个数。',
           'solution': '令 $A,B,C$ 分别为区间中可被 5、6、8 整除的数集。\n'
                       '$|A|=200,|B|=166,|C|=125$；\n'
                       '$|A\\cap B|=\\lfloor1000/30\\rfloor=33$，\n'
                       '$|A\\cap C|=\\lfloor1000/40\\rfloor=25$，\n'
                       '$|B\\cap C|=\\lfloor1000/24\\rfloor=41$，\n'
                       '$|A\\cap B\\cap C|=\\lfloor1000/120\\rfloor=8$。\n'
                       '由容斥，所求为 $1000-(200+166+125)+(33+25+41)-8=600$。',
           'explanation': ['先计算至少能被其中一个数整除的坏情况，再从 1000 个整数中扣除。',
                           '同时被两个数整除等价于被它们的最小公倍数整除，不应一律直接相乘，例如 $\\operatorname{lcm}(6,8)=24$。',
                           '单集合相加会重复计数二重交集，需减掉；三重交集在前两轮中少计，需加回。取补集后正负号整体反向。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 6.6': {'prompt': '利用容斥原理求欧拉函数的计算公式。$\\varphi(n)$ 表示 $\\{0,1,\\ldots,n-1\\}$ 中与 $n$ 互素的数的个数，规定 '
                     '$\\varphi(1)=1$。并计算 $\\varphi(60)$。',
           'solution': '设 $n=p_1^{\\alpha_1}\\cdots p_k^{\\alpha_k}$，其中 $p_i$ 为不同素因子。令 $A_i$ 为 '
                       '$\\{0,\\ldots,n-1\\}$ 中被 $p_i$ 整除的数集。\n'
                       '$|A_i|=n/p_i$，$|A_i\\cap A_j|=n/(p_ip_j)$，一般任意若干集合的交集大小为 $n$ 除以相应不同素数之积。\n'
                       '容斥得\n'
                       '$$\\varphi(n)=n-\\sum_i\\frac n{p_i}+\\sum_{i<j}\\frac '
                       'n{p_ip_j}-\\cdots=n\\prod_{i=1}^k\\left(1-\\frac1{p_i}\\right).$$\n'
                       '$\\varphi(60)=60(1-1/2)(1-1/3)(1-1/5)=16$。\n'
                       '这些互素正整数为 $1,7,11,13,17,19,23,29,31,37,41,43,47,49,53,59$。',
           'explanation': ['与 $n$ 不互素，当且仅当至少被 $n$ 的一个素因子整除。因此坏情况正好是所有 $A_i$ 的并集。',
                           '在 $0$ 到 $n-1$ 内，每个素因子的倍数恰有 $n/p_i$ 个；这里包含 0，因此不是 $\\lfloor(n-1)/p_i\\rfloor$。',
                           '不同素数互素，交集中要求同时整除，其最小公倍数就是这些素数的乘积。',
                           '将容斥展开式因式分解，得到乘积公式；只需不同素因子，不必按幂指数重复乘。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 6.7': {'prompt': '错位排列：$n$ 人领取被打乱的 $n$ 顶帽子，每人恰取一顶。证明每个人都未领到自己帽子的排列数为\n'
                     '$$D_n=n!\\left(1-\\frac1{1!}+\\frac1{2!}-\\cdots+(-1)^n\\frac1{n!}\\right).$$',
           'solution': '设 $S$ 是全部排列的集合，$A_i$ 是第 $i$ 人领到自己帽子的排列集合。\n'
                       '$|S|=n!$，固定任意 $k$ 人领到自己的帽子后，剩下 $n-k$ 人的帽子可任意排列，所以相应交集大小为 $(n-k)!$。\n'
                       '由容斥，\n'
                       '$$D_n=\\sum_{k=0}^n(-1)^k\\binom nk(n-k)!=n!\\sum_{k=0}^n\\frac{(-1)^k}{k!}.$$\n'
                       '当 $n$ 很大时，错位排列占全部排列的比例接近 $e^{-1}$。',
           'explanation': ['用“不存在任何固定点”描述所有人均拿错，正好转为对 $A_1\\cup\\cdots\\cup A_n$ 取补。',
                           '选定哪 $k$ 个人拿对有 $\\binom nk$ 种；固定他们的帽子之后，其余人不加限制，仍可有拿对者，计为 $(n-k)!$。',
                           '容斥负责修正这些重叠，不应在交集计算时再要求其余人也拿错。',
                           '用 $\\binom nk(n-k)!=n!/k!$ 逐项化简，即得所需公式。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 6.8': {'prompt': '证明 $A-(B\\cup C)=(A-B)\\cap(A-C)$。',
           'solution': '任意元素 $x$，\n'
                       '$x\\in A-(B\\cup C)$\n'
                       '$\\Leftrightarrow x\\in A\\land\\neg(x\\in B\\lor x\\in C)$\n'
                       '$\\Leftrightarrow x\\in A\\land x\\notin B\\land x\\notin C$\n'
                       '$\\Leftrightarrow(x\\in A\\land x\\notin B)\\land(x\\in A\\land x\\notin C)$\n'
                       '$\\Leftrightarrow x\\in(A-B)\\cap(A-C)$。\n'
                       '故两集合相等。',
           'explanation': ['把“属于差集”写成“属于前一个集合且不属于后一个集合”。',
                           '对“不属于 $B\\cup C$”应用德摩根律，得到既不属于 $B$ 又不属于 $C$。',
                           '按两个差集所需的结构复制 $x\\in A$ 条件并分组；任意元素两边属于关系等价，就证明集合相等。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 6.9': {'prompt': '设 $E$ 为全集，证明 $A\\cap E=A$。',
           'solution': '对全集内任意 $x$，$x\\in A\\cap E\\Leftrightarrow x\\in A\\land x\\in E\\Leftrightarrow '
                       'x\\in A$，因为 $x\\in E$ 恒真。因此 $A\\cap E=A$。',
           'explanation': ['交集要求同时属于两个集合；但 $A\\subseteq E$，属于 $A$ 已保证属于 $E$。',
                           '集合等式可通过任意元素的双向归属等价来证明，不能只证明 $A\\cap E\\subseteq A$ 就结束。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 6.10': {'prompt': '假设已知原书式 (6.1)～(6.14)，用集合运算法则证明吸收律 $A\\cup(A\\cap B)=A$。',
            'solution': '$A\\cup(A\\cap B)$\n'
                        '$=(A\\cap E)\\cup(A\\cap B)$（同一律）\n'
                        '$=A\\cap(E\\cup B)$（分配律）\n'
                        '$=A\\cap(B\\cup E)$（交换律）\n'
                        '$=A\\cap E$（零律）\n'
                        '$=A$（同一律）。',
            'explanation': ['先把单独的 $A$ 写成 $A\\cap E$，使两个并项具有相同的因子 $A$。',
                            '逆用分配律提取公共因子，再利用任何集合与全集的并都是全集。',
                            '本题要求依据较早建立的法则，不能直接引用待证明的吸收律作为中间一步。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 6.11': {'prompt': '证明 $A-B=A\\cap\\overline B$，其中补集相对于固定全集 $E$。',
            'solution': '任意 $x$，\n'
                        '$x\\in A-B\\Leftrightarrow x\\in A\\land x\\notin B$\n'
                        '$\\Leftrightarrow x\\in A\\land x\\in\\overline B$\n'
                        '$\\Leftrightarrow x\\in A\\cap\\overline B$。\n'
                        '故 $A-B=A\\cap\\overline B$。',
            'explanation': ['相对补 $A-B$ 同时限制“在 $A$ 内”和“不在 $B$ 内”。',
                            '固定全集后，不属于 $B$ 就可改为属于其绝对补集 $\\overline B$。',
                            '这个转换能把含差集的等式统一改写为交、并、补，便于使用集合代数定律。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 6.12': {'prompt': '证明 $(A-B)\\cup B=A\\cup B$。',
            'solution': '$(A-B)\\cup B=(A\\cap\\overline B)\\cup B$\n'
                        '$=(A\\cup B)\\cap(\\overline B\\cup B)$\n'
                        '$=(A\\cup B)\\cap E$\n'
                        '$=A\\cup B$。',
            'explanation': ['先把相对补改写成与补集的交，使分配律可以直接使用。',
                            '把 $B$ 分配进去，出现互补项 $\\overline B\\cup B=E$。',
                            '直观上，先从 $A$ 中去掉属于 $B$ 的部分，再把完整的 $B$ 加回来，与直接取 $A\\cup B$ 相同。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 6.13': {'prompt': '证明 $A\\cup B=B\\Longleftrightarrow A\\subseteq B\\Longleftrightarrow A\\cap '
                      'B=A\\Longleftrightarrow A-B=\\varnothing$。',
            'solution': '依次证明四个条件循环蕴含。\n'
                        '若 $A\\cup B=B$，则 $x\\in A\\Rightarrow x\\in A\\cup B=B$，故 $A\\subseteq B$。\n'
                        '若 $A\\subseteq B$，则任意 $x\\in A$ 也属于 $B$，故 $A\\subseteq A\\cap B$；结合 $A\\cap '
                        'B\\subseteq A$ 得 $A\\cap B=A$。\n'
                        '若 $A\\cap B=A$，则 $A-B=A\\cap\\overline B=(A\\cap B)\\cap\\overline '
                        'B=A\\cap(B\\cap\\overline B)=\\varnothing$。\n'
                        '若 $A-B=\\varnothing$，由例 6.12 得 $A\\cup B=(A-B)\\cup B=\\varnothing\\cup B=B$。',
            'explanation': ['多个命题等价不必两两证明；把它们连成一个闭环，每个条件能推出下一个，便能保证任意两者互推。',
                            '前两步使用元素法，把包含关系解释成“属于 $A$ 就属于 $B$”。',
                            '第三、四步使用集合代数和已证明的等式，避免重复做元素讨论。',
                            '这四种形式都是 $A$ 被 $B$ 包含的不同表达，可用于化简或证明集合包含。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 6.14': {'prompt': '化简 $((A\\cup B\\cup C)\\cap(A\\cup B))-((A\\cup(B-C))\\cap A)$。',
            'solution': '因 $A\\cup B\\subseteq A\\cup B\\cup C$，第一部分为 $A\\cup B$。\n'
                        '又 $A\\subseteq A\\cup(B-C)$，第二部分为 $A$。\n'
                        '原式 $=(A\\cup B)-A=B-A$。',
            'explanation': ['先找“一个集合与它的超集取交”的结构，利用 $X\\subseteq Y\\Rightarrow X\\cap Y=X$。',
                            '把两个大括号分别化简，避免直接展开所有差、并、交导致表达式膨胀。',
                            '最后从 $A\\cup B$ 去掉 $A$，只剩 $B$ 中不属于 $A$ 的元素，即 $B-A$。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 6.15': {'prompt': '已知 $A\\oplus B=A\\oplus C$，证明 $B=C$（$\\oplus$ 为对称差）。',
            'solution': '对等式两边再与 $A$ 作对称差：\n'
                        '$A\\oplus(A\\oplus B)=A\\oplus(A\\oplus C)$。\n'
                        '由结合律，$(A\\oplus A)\\oplus B=(A\\oplus A)\\oplus C$。\n'
                        '因为 $A\\oplus A=\\varnothing$，且 $\\varnothing\\oplus X=X$，得到 $B=C$。',
            'explanation': ['普通并集没有这种消去律，不能直接划掉两边的 $A$；必须依据对称差的特殊运算法则。',
                            '对称差中同一个集合出现两次会抵消，因此在两边再作用一次 $A$。',
                            '用结合律将两个 $A$ 放到一起，化为空集后消去，得到所求。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.1': {'prompt': '已知 $\\langle x+2,4\\rangle=\\langle5,2x+y\\rangle$，求 $x,y$。',
           'solution': '有序对相等当且仅当对应分量相等，所以 $x+2=5$、$2x+y=4$。解得 $x=3,y=-2$。',
           'explanation': ['先把有序对等式拆为两个普通等式，第一分量与第一分量对应，不能交叉。', '由第一个方程得 $x=3$，代入第二个方程得 $6+y=4$，所以 $y=-2$。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.2': {'prompt': '设 $A=\\{1,2\\}$，求 $P(A)\\times A$。',
           'solution': '$P(A)=\\{\\varnothing,\\{1\\},\\{2\\},\\{1,2\\}\\}$。\n'
                       '$P(A)\\times '
                       'A=\\{\\langle\\varnothing,1\\rangle,\\langle\\varnothing,2\\rangle,\\langle\\{1\\},1\\rangle,\\langle\\{1\\},2\\rangle,\\langle\\{2\\},1\\rangle,\\langle\\{2\\},2\\rangle,\\langle\\{1,2\\},1\\rangle,\\langle\\{1,2\\},2\\rangle\\}$。',
           'explanation': ['先枚举 $A$ 的所有子集，它们才是 $P(A)$ 的元素，所以第一分量本身是集合。',
                           '将每个第一分量分别与 1、2 配对，得到 $4\\times2=8$ 个有序对。',
                           '空集是幂集的一个元素，必须产生两对；$\\{1\\}$ 与数 1 也不能混写。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.3': {'prompt': '设 $A,B,C,D$ 为任意集合，判断下列命题真假并说明理由。\n'
                     '(1) $A\\times B=A\\times C\\Rightarrow B=C$。\n'
                     '(2) $A-(B\\times C)=(A-B)\\times(A-C)$。\n'
                     '(3) $A=B\\land C=D\\Rightarrow A\\times C=B\\times D$。\n'
                     '(4) 存在集合 $A$，使 $A\\subseteq A\\times A$。',
           'solution': '(1) 假。取 $A=\\varnothing,B=\\{1\\},C=\\{2\\}$，两个积都为空，但 $B\\ne C$。\n'
                       '(2) 假。取 $A=B=\\{1\\},C=\\{2\\}$，左边为 $\\{1\\}$，右边为 '
                       '$\\varnothing\\times\\{1\\}=\\varnothing$。\n'
                       '(3) 真，由等量代入立即得到。\n'
                       '(4) 真，取 $A=\\varnothing$，则 $\\varnothing\\subseteq\\varnothing\\times\\varnothing$。',
           'explanation': ['遇到“任意集合”先检查空集这种边界情况；笛卡儿积任一因子为空，积就为空，因此一般不能消去一个空因子。',
                           '(2) 把普通元素集合与有序对集合相减，不能套用只对同类集合运算成立的分配关系；一个具体反例即可否定全称命题。',
                           '存在命题只需给出一个合法例子，空集也是合法集合，不能排除。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.4': {'prompt': '设 $A=\\{1,2,3,4\\}$，以下均定义 $A$ 上关系，用列元素法表示。\n'
                     '(1) $R=\\{\\langle x,y\\rangle\\mid x\\text{ 是 }y\\text{ 的倍数}\\}$。\n'
                     '(2) $R=\\{\\langle x,y\\rangle\\mid(x-y)^2\\in A\\}$。\n'
                     '(3) $R=\\{\\langle x,y\\rangle\\mid x/y\\text{ 是素数}\\}$。\n'
                     '(4) $R=\\{\\langle x,y\\rangle\\mid x\\ne y\\}$。',
           'solution': '(1) '
                       '$\\{\\langle1,1\\rangle,\\langle2,1\\rangle,\\langle2,2\\rangle,\\langle3,1\\rangle,\\langle3,3\\rangle,\\langle4,1\\rangle,\\langle4,2\\rangle,\\langle4,4\\rangle\\}$。\n'
                       '(2) '
                       '$\\{\\langle1,2\\rangle,\\langle1,3\\rangle,\\langle2,1\\rangle,\\langle2,3\\rangle,\\langle2,4\\rangle,\\langle3,1\\rangle,\\langle3,2\\rangle,\\langle3,4\\rangle,\\langle4,2\\rangle,\\langle4,3\\rangle\\}$。\n'
                       '(3) $\\{\\langle2,1\\rangle,\\langle3,1\\rangle,\\langle4,2\\rangle\\}$。\n'
                       '(4) $A\\times A-I_A$，即 '
                       '$\\{\\langle1,2\\rangle,\\langle1,3\\rangle,\\langle1,4\\rangle,\\langle2,1\\rangle,\\langle2,3\\rangle,\\langle2,4\\rangle,\\langle3,1\\rangle,\\langle3,2\\rangle,\\langle3,4\\rangle,\\langle4,1\\rangle,\\langle4,2\\rangle,\\langle4,3\\rangle\\}$。',
           'explanation': ['先记住每个分量必须都属于 $A$，只需检查 $4^2=16$ 个有序对。',
                           '(1) 相等时也满足倍数关系，四个自环不能漏掉。',
                           '(2) 两数差的平方只能是 0、1、4、9，其中落在 $A$ 中的只有 1、4，因此保留差的绝对值为 1 或 2 的对。',
                           '(3) 商必须恰是素数，商为 1、4、分数均不合；(4) 从 16 对中去掉四个相等对，剩 12 对。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.7': {'prompt': '设 '
                     '$R=\\{\\langle1,2\\rangle,\\langle1,3\\rangle,\\langle2,2\\rangle,\\langle2,4\\rangle,\\langle3,2\\rangle\\}$，求 '
                     '$R$ 在 $\\{1\\},\\varnothing,\\{2,3\\}$ 上的限制，以及 '
                     '$R[\\{1\\}],R[\\varnothing],R[\\{3\\}]$。',
           'solution': '$R\\upharpoonright\\{1\\}=\\{\\langle1,2\\rangle,\\langle1,3\\rangle\\}$。\n'
                       '$R\\upharpoonright\\varnothing=\\varnothing$。\n'
                       '$R\\upharpoonright\\{2,3\\}=\\{\\langle2,2\\rangle,\\langle2,4\\rangle,\\langle3,2\\rangle\\}$。\n'
                       '$R[\\{1\\}]=\\{2,3\\}$，$R[\\varnothing]=\\varnothing$，$R[\\{3\\}]=\\{2\\}$。',
           'explanation': ['限制只保留第一分量属于指定集合的有序对，不要求第二分量也在指定集合里。',
                           '像集收集这些保留有序对的第二分量，去重后组成普通集合。',
                           '空集没有任何合法第一分量，所以限制与像都为空集。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.8': {'prompt': '设 $A=\\{a,b,c,d\\}$，$R=\\{\\langle a,b\\rangle,\\langle b,a\\rangle,\\langle '
                     'b,c\\rangle,\\langle c,d\\rangle\\}$，求 $R$ 的各次幂，用矩阵和关系图表示。',
           'solution': '以 $a,b,c,d$ 为行列次序：\n'
                       '$$M_R=\\begin{pmatrix}0&1&0&0\\\\1&0&1&0\\\\0&0&0&1\\\\0&0&0&0\\end{pmatrix},\\quad '
                       'M_{R^0}=I_4.$$\n'
                       '$$M_{R^2}=\\begin{pmatrix}1&0&1&0\\\\0&1&0&1\\\\0&0&0&0\\\\0&0&0&0\\end{pmatrix},\\quad '
                       'M_{R^3}=\\begin{pmatrix}0&1&0&1\\\\1&0&1&0\\\\0&0&0&0\\\\0&0&0&0\\end{pmatrix}.$$\n'
                       '$R^4=R^2$，从而 $R^{2k}=R^2$（$k\\ge1$），$R^{2k+1}=R^3$（$k\\ge1$）。\n'
                       '关系图的文字表示：$R^0$ 在四点各有自环；$R$ 的边为题设四条；$R^2$ 的边为 $a\\to a,a\\to c,b\\to b,b\\to d$；$R^3$ '
                       '的边为 $a\\to b,a\\to d,b\\to a,b\\to c$。',
           'explanation': ['$R^n$ 的边表示恰有长度 $n$ 的有向路径可连接两端，不是长度小于等于 $n$ 的可达关系。',
                           '关系矩阵采用布尔乘法：乘法为“且”、加法为“或”，因此多条路径仍只记录 1。',
                           '计算到 $R^4=R^2$ 后，每次右复合 $R$ 都保持相等，所以从第二次幂开始以 2 为周期循环。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.9': {'prompt': '设 $A=\\{a,b,d,e,f\\}$，$R=\\{\\langle a,b\\rangle,\\langle b,a\\rangle,\\langle '
                     'd,e\\rangle,\\langle e,f\\rangle,\\langle f,d\\rangle\\}$。求最小自然数 $m<n$，使 $R^m=R^n$。',
           'solution': '$a,b$ 构成长度为 2 的循环，$d,e,f$ 构成长度为 3 的循环。整体周期为 $\\operatorname{lcm}(2,3)=6$。\n'
                       '故 $R^{m+6}=R^m$，最小可取 $m=0,n=6$。',
           'explanation': ['两部分互不连接，可以分别观察点经过一次、两次等作用后何时回到原位。',
                           '整体变换相同必须同时满足差 $n-m$ 为 2 和 3 的倍数，最小正差为 6。',
                           '该关系为循环置换，没有暂态；自然数按本书含 0，故最早从 $R^0=I_A$ 就开始重复。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.10': {'prompt': '设 '
                      '$A=\\{1,2,3\\}$，$R_1=\\{\\langle1,1\\rangle,\\langle2,2\\rangle\\}$，$R_2=\\{\\langle1,1\\rangle,\\langle2,2\\rangle,\\langle3,3\\rangle,\\langle1,2\\rangle\\}$，$R_3=\\{\\langle1,3\\rangle\\}$。判断自反性、反自反性。',
            'solution': '$R_2$ 自反但不反自反；$R_3$ 反自反但不自反；$R_1$ 既不自反也不反自反。',
            'explanation': ['自反要求所有 $x\\in A$ 的 $\\langle x,x\\rangle$ 都存在；$R_1$ 缺 '
                            '$\\langle3,3\\rangle$，所以不自反。',
                            '反自反要求所有自环都不存在；$R_1$ 已有两个自环，因此也不反自反。',
                            '自反与反自反不是互补判断，存在“两者都不是”的情况。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.11': {'prompt': '设 '
                      '$A=\\{1,2,3\\}$，$R_1=\\{\\langle1,1\\rangle,\\langle2,2\\rangle\\}$，$R_2=\\{\\langle1,1\\rangle,\\langle1,2\\rangle,\\langle2,1\\rangle\\}$，$R_3=\\{\\langle1,2\\rangle,\\langle1,3\\rangle\\}$，$R_4=\\{\\langle1,2\\rangle,\\langle2,1\\rangle,\\langle1,3\\rangle\\}$。判断对称性、反对称性。',
            'solution': '$R_1$ 既对称又反对称；$R_2$ 对称但不反对称；$R_3$ 反对称但不对称；$R_4$ 既不对称也不反对称。',
            'explanation': ['对称要求每条边都具有反向边；自环的反向仍是自身，因此 $R_1$ 自动满足。',
                            '反对称只禁止两个不同顶点间同时存在双向边，允许自环；所以仅有自环的 $R_1$ 同样反对称。',
                            '$R_2,R_4$ 都有 $1\\leftrightarrow2$，因此不反对称；$R_3,R_4$ 都有 $1\\to3$ 而无 '
                            '$3\\to1$，因此不对称。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.12': {'prompt': '设 '
                      '$A=\\{1,2,3\\}$，$R_1=\\{\\langle1,1\\rangle,\\langle2,2\\rangle\\}$，$R_2=\\{\\langle1,2\\rangle,\\langle2,3\\rangle\\}$，$R_3=\\{\\langle1,3\\rangle\\}$。判断三者是否传递。',
            'solution': '$R_1,R_3$ 是传递关系；$R_2$ 不是传递关系。',
            'explanation': ['传递要求任意两条可首尾相接的边 $x\\to y,y\\to z$ 都有直接边 $x\\to z$。',
                            '$R_1$ 的可连接路径只有各自的自环重复，相应直接边已存在。',
                            '$R_2$ 有 $1\\to2\\to3$，却没有 $1\\to3$，所以有反例。',
                            '$R_3$ 中没有两条可首尾连接的边，传递条件的前提从未成立，因此真空成立，仍是传递关系。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.13': {'prompt': '设 $R_1,R_2$ 为集合 $A$ 上的关系，证明：\n'
                      '(1) 若二者都自反且对称，则 $R_1\\cup R_2$ 也自反且对称。\n'
                      '(2) 若二者都传递，则 $R_1\\cap R_2$ 也传递。',
            'solution': '(1) 自反性给出 $I_A\\subseteq R_1$ 且 $I_A\\subseteq R_2$，所以 $I_A\\subseteq R_1\\cup '
                        'R_2$。\n'
                        '对称性给出 $R_i^{-1}=R_i$，于是 $(R_1\\cup R_2)^{-1}=R_1^{-1}\\cup R_2^{-1}=R_1\\cup '
                        'R_2$，故并关系对称。\n'
                        '(2) 若 $x(R_1\\cap R_2)y$ 且 $y(R_1\\cap R_2)z$，则这两条关系在 $R_1,R_2$ 中均成立；由各自传递性，$xR_1z$ '
                        '且 $xR_2z$，所以 $x(R_1\\cap R_2)z$，即交关系传递。',
            'explanation': ['自反可改写为包含全体自环，取并自然不会丢掉它们。',
                            '对称可用逆关系保持原集合来表达；逆运算对并分配，因此很快得到结论。',
                            '交关系中的前提同时属于两个原关系，所以可以分别使用两个传递性，再将结论取交。',
                            '同样的证明不能用于传递性的并保持，因为两条连续边可能分别来自不同的关系。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.14': {'prompt': '判断图 7.3 三个关系的自反、反自反、对称、反对称和传递性质。图完整转写为边集，顶点均为 $\\{1,2,3\\}$：\n'
                      '(a) '
                      '$\\{\\langle1,1\\rangle,\\langle1,2\\rangle,\\langle2,1\\rangle,\\langle1,3\\rangle,\\langle3,1\\rangle\\}$。\n'
                      '(b) $\\{\\langle2,1\\rangle,\\langle3,1\\rangle\\}$。\n'
                      '(c) '
                      '$\\{\\langle1,1\\rangle,\\langle2,2\\rangle,\\langle3,3\\rangle,\\langle2,1\\rangle,\\langle1,3\\rangle,\\langle3,2\\rangle\\}$。',
            'solution': '|关系|自反|反自反|对称|反对称|传递|\n'
                        '|---|---|---|---|---|---|\n'
                        '|(a)|否|否|是|否|否|\n'
                        '|(b)|否|是|否|是|是|\n'
                        '|(c)|是|否|否|是|否|',
            'explanation': ['(a) 仅顶点 1 有自环，所以既非自反也非反自反；非自环边均成对，故对称而不反对称；$3\\to1\\to3$ 缺 $3\\to3$，不传递。',
                            '(b) 没有自环、没有非自环双向边，所以反自反且反对称；所有边终止在 1，而 1 无出边，因此没有长度 2 的路径，传递性真空成立。',
                            '(c) 三点均有自环，所以自反；三条非自环边组成单向循环，反对称而不对称；$2\\to1\\to3$ 缺 $2\\to3$，所以不传递。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.15': {'prompt': '设 $A=\\{a,b,c,d\\}$，$R=\\{\\langle a,b\\rangle,\\langle b,a\\rangle,\\langle '
                      'b,c\\rangle,\\langle c,d\\rangle,\\langle d,b\\rangle\\}$，求自反闭包 $r(R)$、对称闭包 '
                      '$s(R)$、传递闭包 $t(R)$。',
            'solution': '$r(R)=R\\cup I_A$，即加上四个自环。\n'
                        '$s(R)=R\\cup R^{-1}$，即双向边 $a\\leftrightarrow b,b\\leftrightarrow '
                        'c,c\\leftrightarrow d,b\\leftrightarrow d$。\n'
                        '$t(R)=A\\times A$，即全部 16 个有序对。\n'
                        '以 $a,b,c,d$ 排序，矩阵分别为\n'
                        '$$M_{r(R)}=\\begin{pmatrix}1&1&0&0\\\\1&1&1&0\\\\0&0&1&1\\\\0&1&0&1\\end{pmatrix},\\quad '
                        'M_{s(R)}=\\begin{pmatrix}0&1&0&0\\\\1&0&1&1\\\\0&1&0&1\\\\0&1&1&0\\end{pmatrix},\\quad '
                        'M_{t(R)}=\\begin{pmatrix}1&1&1&1\\\\1&1&1&1\\\\1&1&1&1\\\\1&1&1&1\\end{pmatrix}.$$\n'
                        '按 Warshall 算法，可依次允许 $a,b,c,d$ 作中间点，将所有可达顶点对置为 1，最终同样得到全 1 矩阵。',
            'explanation': ['闭包只增加达到指定性质必需的边，不删除原边；自反闭包补自环，对称闭包补反向边。',
                            '传递闭包记录所有长度至少为 1 的可达路径。原图中 $b\\to c\\to d\\to b$ 成环，且 $a$ 与 $b$ 双向连接，所以任意两点互相可达。',
                            '每点还可沿一个非空回路回到自身，因此传递闭包也包含全部自环，最终为全域关系。',
                            '布尔矩阵算法的更新为 $M_{ij}\\leftarrow M_{ij}\\lor(M_{ik}\\land M_{kj})$，它表示已有路径或可经过中间点 '
                            '$k$。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.16': {'prompt': '设 $A=\\{1,2,\\ldots,8\\}$，$R=\\{\\langle x,y\\rangle\\mid x,y\\in A,\\ x\\equiv '
                      'y\\pmod3\\}$。说明它是等价关系，给出等价类与商集。',
            'solution': '同余具有自反、对称、传递性，所以 $R$ 为等价关系。\n'
                        '$[1]=[4]=[7]=\\{1,4,7\\}$；\n'
                        '$[2]=[5]=[8]=\\{2,5,8\\}$；\n'
                        '$[3]=[6]=\\{3,6\\}$。\n'
                        '商集为 $A/R=\\{\\{1,4,7\\},\\{2,5,8\\},\\{3,6\\}\\}$。\n'
                        '原图的文字表示：同一个等价类内任意两点双向连接且每点有自环，不同类之间没有边。',
            'explanation': ['$x\\equiv y\\pmod3$ 表示 3 整除 $x-y$。$x-x=0$、差取负、差相加仍被 3 整除，依次证明三种性质。',
                            '按除以 3 的余数分类，余数为 1、2、0 的元素分别构成三个等价类。',
                            '商集的元素是这些等价类本身；同一类用不同代表元命名仍只算商集中的一个元素。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.18': {'prompt': '给出 $A=\\{1,2,3\\}$ 上所有等价关系。',
            'solution': '令 '
                        '$I_A=\\{\\langle1,1\\rangle,\\langle2,2\\rangle,\\langle3,3\\rangle\\}$。全部五个等价关系为：\n'
                        '$A\\times A$；\n'
                        '$I_A\\cup\\{\\langle2,3\\rangle,\\langle3,2\\rangle\\}$；\n'
                        '$I_A\\cup\\{\\langle1,3\\rangle,\\langle3,1\\rangle\\}$；\n'
                        '$I_A\\cup\\{\\langle1,2\\rangle,\\langle2,1\\rangle\\}$；\n'
                        '$I_A$。\n'
                        '它们对应的划分依次为 '
                        '$\\{\\{1,2,3\\}\\}$、$\\{\\{1\\},\\{2,3\\}\\}$、$\\{\\{2\\},\\{1,3\\}\\}$、$\\{\\{3\\},\\{1,2\\}\\}$、$\\{\\{1\\},\\{2\\},\\{3\\}\\}$。',
            'explanation': ['等价关系与集合划分一一对应，所以先枚举划分，再恢复关系，能保证不重不漏。',
                            '按块数分类：一块 1 种，两块时选择单独元素有 3 种，三块 1 种，合计 5 种。',
                            '同块中的任意两元素有关，不同块间无关系；每个元素与自身有关，因此每一种都包含 $I_A$。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.19': {'prompt': '画出偏序集 $\\langle\\{1,2,\\ldots,9\\},R_{整除}\\rangle$ 和 $\\langle '
                      'P(\\{a,b,c\\}),\\subseteq\\rangle$ 的哈斯图。',
            'solution': '第一个哈斯图的覆盖边（由下到上）为：$1\\prec2,1\\prec3,1\\prec5,1\\prec7,2\\prec4,2\\prec6,3\\prec6,3\\prec9,4\\prec8$。\n'
                        '第二个哈斯图按集合大小分四层：底层 $\\varnothing$；第二层 $\\{a\\},\\{b\\},\\{c\\}$；第三层 '
                        '$\\{a,b\\},\\{a,c\\},\\{b,c\\}$；顶层 $\\{a,b,c\\}$。两层相邻集合之间，当且仅当上面的集合比下面多一个元素时连接。',
            'explanation': ['哈斯图删除所有自环和可由传递性推出的边，仅保留覆盖关系。',
                            '整除图中例如 $1\\mid4$，但中间有 $1\\mid2\\mid4$，所以不直接连 1 与 4；2 与 6 之间无其他本集合元素，故直接连边。',
                            '幂集包含序中，覆盖等价于恰增加一个元素；按基数分层就自然得到立方体形的图。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.20': {'prompt': '原书图 7.8 的哈斯图转写：有孤立点 $a$；$b,c$ 均在 $d,e$ 下方，$d,e$ 均在 $f$ 下方；另有独立链 $g\\prec h$。求集合 $A$ '
                      '和关系 $R$ 的表达式。',
            'solution': '$A=\\{a,b,c,d,e,f,g,h\\}$。\n'
                        '$$R=I_A\\cup\\{\\langle b,d\\rangle,\\langle b,e\\rangle,\\langle '
                        'b,f\\rangle,\\langle c,d\\rangle,\\langle c,e\\rangle,\\langle c,f\\rangle,\\langle '
                        'd,f\\rangle,\\langle e,f\\rangle,\\langle g,h\\rangle\\}.$$',
            'explanation': ['先把所有点，包括孤立点 $a$，列入集合 $A$。',
                            '恢复偏序关系时，哈斯图省去的所有自环都必须补回；上升路径表示传递关系，如 $b\\prec d\\prec f$ 需补 $bRf$。',
                            '没有上升路径连接的点不可比，例如 $d,e$，以及不同连通分支中的点，不能擅自加边。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.21': {'prompt': '对例 7.20 的偏序集（原书图 7.8），求极小元、最小元、极大元和最大元。',
            'solution': '极小元：$a,b,c,g$。\n极大元：$a,f,h$。\n不存在最小元，也不存在最大元。',
            'explanation': ['极小元只要求它下面没有更小元素，对应哈斯图无向下连接的点；极大元对应没有向上连接的点。',
                            '孤立点 $a$ 同时没有更大与更小的其他点，所以既极小又极大。',
                            '最小元必须小于等于所有元素，最大元必须大于等于所有元素；本图有多个互不可比的分支，因此均不存在。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.22': {'prompt': '设 $X$ 为有限集，$A=(P(X)-\\{\\varnothing\\})-\\{X\\}$，$A\\ne\\varnothing$，且 $|X|=n$。对包含偏序 '
                      '$\\langle A,\\subseteq\\rangle$：\n'
                      '(1) 是否有最大元？(2) 是否有最小元？(3) 极大元、极小元的一般形式是什么？',
            'solution': '由 $A\\ne\\varnothing$ 知 $n\\ge2$。\n'
                        '没有最大元、最小元。\n'
                        '极小元为全部单元素集 $\\{x\\}$（$x\\in X$）；极大元为全部 $X-\\{x\\}$（$x\\in X$），即 $n-1$ 元子集。',
            'explanation': ['完整幂集格的底层为空集、顶层为 $X$；本题恰好删去这两层，所以整体最小、最大元消失。',
                            '任一至少含两个元素的非空子集，还能删掉一个元素保持非空，所以不极小；单元素集则再无合法更小元素。',
                            '任一少于 $n-1$ 个元素的真子集，还能加一个元素而不等于 $X$，所以不极大；$n-1$ 元子集再加就达到被删掉的 $X$。',
                            '当 $n=2$ 时单元素集同时是极小元与极大元，但两个单元素集互不可比，仍无最小元和最大元。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 7.23': {'prompt': '两台相同机器安排六项任务 $T=\\{t_1,\\ldots,t_6\\}$，全部截止时间为 7。原图任务时长为 '
                      '$l(t_1)=1,l(t_2)=2,l(t_3)=1,l(t_4)=2,l(t_5)=1,l(t_6)=1$。\n'
                      '先后约束转写为 $t_6\\to t_3,t_6\\to t_2,t_5\\to t_3,t_5\\to t_2,t_4\\to t_2,t_3\\to '
                      't_1,t_2\\to t_1$，箭头前任务必须先完成。给出可行调度并找最短完工时间。',
            'solution': '原书给出两个可行方案。以区间 $[开始,结束)$ 表示占用：\n'
                        '\n'
                        '|方案|机器1|机器2|完工时间|\n'
                        '|---|---|---|---|\n'
                        '|一|$t_6:[0,1),t_4:[1,3),t_2:[3,5),t_1:[5,6)$|$t_5:[0,1),t_3:[1,2)$|6|\n'
                        '|二|$t_4:[0,2),t_2:[2,4),t_1:[4,5)$|$t_6:[0,1),t_5:[1,2),t_3:[2,3)$|5|\n'
                        '\n'
                        '方案二最优，因为链 $t_4\\to t_2\\to t_1$ 必须顺序执行，累计时长 $2+2+1=5$，任何方案均不可能在 5 之前完成。',
            'explanation': ['可行性需同时检查每项任务不超过截止时间、每台机器不重叠加工、所有先修任务在后继开始前完成。',
                            '方案二在时间 2 开始 $t_2$ 时，$t_4,t_5,t_6$ 均已完成；时间 4 开始 $t_1$ 时，$t_2,t_3$ 均已完成，所以满足全部约束。',
                            '找到一个短方案还不能证明最优，需再给出下界。最长先后链至少耗时 5，而方案二达到 5，上下界吻合，最优性成立。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 8.1': {'prompt': '设 $F_1=\\{\\langle x_1,y_1\\rangle,\\langle x_2,y_1\\rangle,\\langle '
                     'x_3,y_2\\rangle\\}$，$F_2=\\{\\langle x_1,y_1\\rangle,\\langle '
                     'x_1,y_2\\rangle\\}$。按原例的不同下标元素互异，判断它们是否为函数。',
           'solution': '$F_1$ 是函数；$F_2$ 不是函数，因为同一输入 $x_1$ 对应两个不同输出 $y_1,y_2$。',
           'explanation': ['函数要求每个定义域内输入恰有一个输出，并不要求不同输入的输出不同。',
                           '$F_1$ 中 $x_1,x_2$ 同为 $y_1$ 不会违反函数定义；这只影响单射性。',
                           '$F_2$ 的问题是同一个输入分叉，而不是两个不同输入汇合。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 8.2': {'prompt': '设 $A=\\{1,2,3\\}$，$B=\\{a,b\\}$，求 $B^A$（从 $A$ 到 $B$ 的全部函数）。',
           'solution': '以三元组 $(f(1),f(2),f(3))$ 完整表示函数，$B^A$ 中八个函数依次为\n'
                       '$(a,a,a),(a,a,b),(a,b,a),(a,b,b),(b,a,a),(b,a,b),(b,b,a),(b,b,b)$。\n'
                       '例如 $(a,a,b)$ 对应 '
                       '$\\{\\langle1,a\\rangle,\\langle2,a\\rangle,\\langle3,b\\rangle\\}$。\n'
                       '所以 $|B^A|=2^3=8$。',
           'explanation': ['三个输入每一个均有两个输出选择，且不同输入之间不受单射或满射要求限制，故用乘法原理。',
                           '按三个位置的二进制次序逐项列出，可以确保不重不漏。',
                           '$B^A$ 的元素是完整函数，不是某一个输出值；用取值三元组只是对这八个函数作等价的紧凑表示。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 8.4': {'prompt': '判断下列函数是否为单射、满射、双射。\n'
                     '(1) $f:\\mathbb R\\to\\mathbb R$，$f(x)=-x^2+2x-1$。\n'
                     '(2) $f:\\mathbb Z^+\\to\\mathbb R$，$f(x)=\\ln x$。\n'
                     '(3) $f:\\mathbb R\\to\\mathbb Z$，$f(x)=\\lfloor x\\rfloor$。\n'
                     '(4) $f:\\mathbb R\\to\\mathbb R$，$f(x)=2x+1$。\n'
                     '(5) $f:\\mathbb R^+\\to\\mathbb R^+$，$f(x)=(x^2+1)/x$。',
           'solution': '|题号|单射|满射|双射|\n'
                       '|---|---|---|---|\n'
                       '|(1)|否|否|否|\n'
                       '|(2)|是|否|否|\n'
                       '|(3)|否|是|否|\n'
                       '|(4)|是|是|是|\n'
                       '|(5)|否|否|否|\n'
                       '\n'
                       '(1) $f(x)=-(x-1)^2$，像为 $(-\\infty,0]$，且 $f(0)=f(2)$。\n'
                       '(2) 严格递增，但像只有 $\\{\\ln1,\\ln2,\\ldots\\}$。\n'
                       '(3) 每个整数 $k$ 都是 $f(k)$，但 $f(1.2)=f(1.5)=1$。\n'
                       '(4) 任意 $y$ 都有唯一原像 $(y-1)/2$。\n'
                       '(5) $f(x)=x+1/x\\ge2$，像为 $[2,\\infty)$，且 $f(2)=f(1/2)$。',
           'explanation': ['单射看是否存在两个不同输入给出同一输出；满射看实际像是否覆盖题目指定的整个目标集合。',
                           '严格单调常可用于证明单射，但非单调本身不应代替反例；这里用具体相等值更直接。',
                           '判断满射不能只看解析式，还必须读清目标集合，例如取整函数到整数集是满射，到实数集就不是。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 8.5': {'prompt': '判定下列是否构成 $f:A\\to B$；若构成，判断单射、满射、双射，并完成计算。\n'
                     '(1) '
                     '$A=\\{1,2,3,4,5\\},B=\\{6,7,8,9,10\\}$，$f=\\{\\langle1,8\\rangle,\\langle3,9\\rangle,\\langle4,10\\rangle,\\langle2,6\\rangle,\\langle5,9\\rangle\\}$。\n'
                     '(2) $A,B$ 同 '
                     '(1)，$f=\\{\\langle1,7\\rangle,\\langle2,6\\rangle,\\langle4,5\\rangle,\\langle1,9\\rangle,\\langle5,10\\rangle\\}$。\n'
                     '(3) $A,B$ 同 '
                     '(1)，$f=\\{\\langle1,8\\rangle,\\langle3,10\\rangle,\\langle2,6\\rangle,\\langle4,9\\rangle\\}$。\n'
                     '(4) $A=B=\\mathbb R$，$f(x)=x^3$。\n'
                     '(5) $A=B=\\mathbb R^+$，$f(x)=x/(x^2+1)$。\n'
                     '(6) $A=B=\\mathbb R\\times\\mathbb R$，$f(\\langle x,y\\rangle)=\\langle '
                     'x+y,x-y\\rangle$。令 $L=\\{\\langle x,y\\rangle\\mid x,y\\in\\mathbb R,\\ y=x+1\\}$，求 '
                     '$f(L)$。\n'
                     '(7) $A=\\mathbb N\\times\\mathbb N,B=\\mathbb N$，$f(\\langle x,y\\rangle)=|x^2-y^2|$。求 '
                     '$f(\\mathbb N\\times\\{0\\})$ 和 $f^{-1}(\\{0\\})$。',
           'solution': '(1) 是函数，但不单射（$f(3)=f(5)=9$），不满射（7 无原像），所以不双射。\n'
                       '(2) 不是 $A\\to B$ 的函数，同一输入 1 有输出 7 和 9；且还存在输出 5 不在 $B$、输入 3 缺失的问题。\n'
                       '(3) 不是 $A\\to B$ 的函数，定义域缺少 5。\n'
                       '(4) 是双射。\n'
                       '(5) 是函数，既不单射也不满射；在 $x=1$ 达最大值 $1/2$，像为 $(0,1/2]$，且 $f(2)=f(1/2)$。\n'
                       '(6) 是双射。$f(L)=\\{\\langle2x+1,-1\\rangle\\mid x\\in\\mathbb R\\}=\\mathbb '
                       'R\\times\\{-1\\}$。\n'
                       '(7) 是函数，既不单射（例如 $f(1,1)=f(2,2)=0$）也不满射（2 无原像）。\n'
                       '$f(\\mathbb N\\times\\{0\\})=\\{n^2\\mid n\\in\\mathbb '
                       'N\\}$；$f^{-1}(\\{0\\})=\\{\\langle n,n\\rangle\\mid n\\in\\mathbb N\\}$。',
           'explanation': ['先检查函数存在性：每个 $A$ 中输入恰有一个输出且输出属于 $B$，再谈单射与满射。',
                           '(4) 立方严格递增，且每个实数 $y$ 都有立方根，故双射。',
                           '(6) 给定输出 $\\langle u,v\\rangle$，唯一可解出 $x=(u+v)/2,y=(u-v)/2$，证明双射；求直线的像时直接代入 '
                           '$y=x+1$。',
                           '(7) 平方数模 4 仅为 0 或 1，两平方之差不可能绝对值为 2；求 0 的原像时 $x^2=y^2$，自然数非负，故 $x=y$。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 8.7': {'prompt': '设 $A=\\{1,\\ldots,n\\}$，$B=\\{1,\\ldots,m\\}$（$n,m\\ge1$），从 $A$ 到 $B$ 的所有函数中，有多少个满射？',
           'solution': '若 $n<m$，不存在满射。\n'
                       '一般利用容斥，满射数为\n'
                       '$$\\sum_{i=0}^{m}(-1)^i\\binom mi(m-i)^n.$$\n'
                       '证明：全部函数数为 $m^n$；令 $A_i$ 为未取到目标值 $i$ 的函数集合，则 $|A_i|=(m-1)^n$，任意 $k$ 个此类集合的交集有 '
                       '$(m-k)^n$ 个函数。对全部坏集合取并并用容斥取补，即得公式。',
           'explanation': ['满射要求每个目标值至少被取一次；最方便数其反面：“某一个目标值从未出现”。',
                           '固定漏掉 $k$ 个目标值后，每个输入还有 $m-k$ 种选择，所以为 $(m-k)^n$，再乘选择漏掉哪些值的 $\\binom mk$。',
                           '不同漏值事件可重叠，必须使用交替加减的容斥，不能只用 $m^n-m(m-1)^n$。',
                           '若输入比输出少，每个输入只有一个输出，无法覆盖所有目标值，这是最先可判定的零计数情况。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 8.8': {'prompt': '原书列出常用函数，按增长阶由高到低排列，并写出其中的等阶关系。对数按原书算法计阶约定以 2 为底。',
           'solution': '从高到低为\n'
                       '$$2^{2^n},\\ (n+1)!,\\ n!,\\ n2^n,\\ (3/2)^n,$$\n'
                       '$$(\\log n)^{\\log n}=\\Theta(n^{\\log\\log n}),\\quad(\\log n)!,$$\n'
                       '$$n^3,\\quad n^2=\\Theta(4^{\\log n}),\\quad n\\log n=\\Theta(\\log(n!)),$$\n'
                       '$$n=\\Theta(2^{\\log n}),\\quad(\\sqrt2)^{\\log n},\\quad2^{\\sqrt{\\log n}},$$\n'
                       '$$(\\log n)^2,\\quad\\log n,\\quad\\sqrt{\\log n},\\quad\\log\\log n,$$\n'
                       '$$n^{1/\\log n}=\\Theta(1).$$',
           'explanation': ['双指数快于阶乘，阶乘快于固定底数指数，固定底数指数又快于任何固定次幂多项式；比较的是 $n$ 趋大后的增长阶。',
                           '把幂改写成以 2 '
                           '为底的指数常能统一比较：$4^{\\log_2n}=n^2$，$(\\sqrt2)^{\\log_2n}=n^{1/2}$，$n^{1/\\log_2n}=2$。',
                           '$(\\log n)^{\\log n}$ 的对数为 $(\\log n)(\\log\\log n)$，所以等于 $n^{\\log\\log '
                           'n}$；它最终快于任意固定次多项式。',
                           '利用阶乘的对数增长 $\\log(n!)=\\Theta(n\\log n)$ 可比较相关项；原书 $(\\log n)!$ 在阶乘参数取整数的尺度上理解，例如 '
                           '$n$ 为 2 的幂时。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 8.9': {'prompt': '设 $f,g:\\mathbb R\\to\\mathbb R$，$f(x)=x^2$（$x\\ge3$），$f(x)=-2$（$x<3$）；$g(x)=x+2$。求 '
                     '$f\\circ g,g\\circ f$，并在存在时求反函数。沿用本书右复合：$(f\\circ g)(x)=g(f(x))$。',
           'solution': '$$(f\\circ g)(x)=\\begin{cases}x^2+2,&x\\ge3,\\\\0,&x<3.\\end{cases}$$\n'
                       '$$(g\\circ f)(x)=\\begin{cases}(x+2)^2,&x\\ge1,\\\\-2,&x<1.\\end{cases}$$\n'
                       '$f$ 不是双射，没有反函数；$g$ 为双射，$g^{-1}(x)=x-2$。',
           'explanation': ['本书复合顺序与某些高等数学教材相反，先算写在左边的函数，后算右边的函数。',
                           '$f\\circ g$ 先分 $x\\ge3$ 或 $x<3$，再把结果加 2，阈值不变。',
                           '$g\\circ f$ 先把输入变为 $x+2$，是否采用平方分支取决于 $x+2\\ge3$，所以新阈值是 $x\\ge1$。',
                           '$f$ 在整个 $x<3$ 区间取同一值，无法单射；$g$ 可由 $y=x+2$ 唯一解出 $x=y-2$。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 8.10': {'prompt': '构造双射证明以下集合等势（$\\mathbb N$ 含 0）：\n'
                      '(1) $\\mathbb Z\\approx\\mathbb N$。\n'
                      '(2) $\\mathbb N\\times\\mathbb N\\approx\\mathbb N$。\n'
                      '(3) $\\mathbb N\\approx\\mathbb Q$。\n'
                      '(4) $(0,1)\\approx\\mathbb R$。\n'
                      '(5) $[0,1]\\approx(0,1)$。\n'
                      '(6) 任意 $a<b$，$[0,1]\\approx[a,b]$。',
            'solution': '(1) $f(x)=2x$（$x\\ge0$），$f(x)=-2x-1$（$x<0$）。\n'
                        '(2) 按 $m+n$ 从小到大、同一斜线上按 $m$ 从小到大列出 $\\langle m,n\\rangle$，得到双射\n'
                        '$f(\\langle m,n\\rangle)=(m+n)(m+n+1)/2+m$。\n'
                        '序列开头为 $(0,0),(0,1),(1,0),(0,2),(1,1),(2,0),\\ldots$，分别对应 $0,1,2,3,4,5,\\ldots$。\n'
                        '(3) 将所有 $p/q$（$p\\in\\mathbb Z,q\\in\\mathbb '
                        'Z^+$）排成二维表，按对角方式依次遍历，遇到先前已经出现过的有理数就跳过；得到每个有理数恰出现一次的无穷序列，将第 $n$ 个数对应于 $n$。\n'
                        '(4) $f(x)=\\tan(\\pi(2x-1)/2)$。\n'
                        '(5) 令 $f(0)=1/2,f(1)=1/4$，对 $n\\ge1$ 令 $f(1/2^n)=1/2^{n+2}$，其余 $x$ 令 $f(x)=x$。\n'
                        '(6) $f(x)=(b-a)x+a$；同样的一次函数也可证明 $(0,1)\\approx(a,b)$。',
            'explanation': ['(1) 将非负整数映到偶数、负整数映到奇数，两个部分不重叠且覆盖整个自然数集。',
                            '(2) 前面所有斜线共有 $1+2+\\cdots+(m+n)$ 个点，再加当前斜线上前面的 $m$ 个点，即得编号；有限位置必被遍历，故不遗漏。',
                            '(3) 只遍历分数表示还不够，因为 $1/1,2/2,3/3$ 是同一个有理数；必须去掉重复值才是双射。',
                            '(4) 正切在 $(-\\pi/2,\\pi/2)$ 严格递增且覆盖全部实数，线性变换把输入区间变到这个区间。',
                            '(5) 把 $0,1,1/2,1/4,\\ldots$ 这一条无穷链整体向后移，腾出两端点的位置；其余点保持原值，从而并未丢失任何开区间内的值。',
                            '(6) 线性函数严格递增，端点分别对应 $a,b$，所以在指定闭区间之间为双射。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 8.11': {'prompt': '设 $A$ 为任意集合，证明 $P(A)\\approx\\{0,1\\}^A$。',
            'solution': "构造 $F:P(A)\\to\\{0,1\\}^A$，令 $F(A')=\\chi_{A'}$，即 $\\chi_{A'}(x)=1$ 当且仅当 $x\\in "
                        "A'$，其余为 0。\n"
                        "若 $A'\\ne A''$，至少有元素属于一者而不属于另一者，所以两个特征函数不同，$F$ 单射。\n"
                        '任意 $g:A\\to\\{0,1\\}$，令 $B=\\{x\\in A\\mid g(x)=1\\}$，则 $\\chi_B=g$，从而 $F(B)=g$，$F$ '
                        '满射。\n'
                        '故 $F$ 为双射，两集合等势。',
            'explanation': ['把“一个元素是否属于子集”的二选一信息，编码为 0、1 值函数。',
                            '单射需要证明不同子集一定给出不同函数：从对称差里挑一个元素就能让函数值不同。',
                            '满射需要从任意 0、1 函数恢复子集：取它值为 1 的全部输入，恢复结果再编码就回到原函数。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 8.12': {'prompt': '求下列集合的基数。\n'
                      '(1) $T=\\{x\\mid x\\text{ 是单词 BASEBALL 中的字母}\\}$。\n'
                      '(2) $B=\\{x\\in\\mathbb R\\mid x^2=9\\land2x=8\\}$。\n'
                      '(3) $C=P(A)$，$A=\\{1,3,7,11\\}$。',
            'solution': '(1) $T=\\{B,A,S,E,L\\}$，$\\operatorname{card}T=5$。\n'
                        '(2) 两个方程无公共实根，$B=\\varnothing$，$\\operatorname{card}B=0$。\n'
                        '(3) $|A|=4$，所以 $\\operatorname{card}P(A)=2^4=16$。',
            'explanation': ['集合不计重复，BASEBALL 虽有 8 个字母位置，但只出现 5 种不同字母。',
                            '合取要求两个方程同时成立；$2x=8$ 给 $x=4$，不满足 $x^2=9$，所以不能把两个方程的解取并。',
                            '幂集大小为 $2^{|A|}$，因为每个元素可独立选择属于或不属于某个子集。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 8.13': {'prompt': '设 $\\operatorname{card}A=\\aleph_0$，$\\operatorname{card}B=n$，其中自然数 $n\\ne0$，求 '
                      '$\\operatorname{card}(A\\times B)$。',
            'solution': '写 $A=\\{a_0,a_1,\\ldots\\}$，$B=\\{b_0,\\ldots,b_{n-1}\\}$，定义 $f:A\\times '
                        'B\\to\\mathbb N$ 为 $f(\\langle a_i,b_j\\rangle)=in+j$。\n'
                        '此函数为双射，所以 $\\operatorname{card}(A\\times B)=\\aleph_0$。',
            'explanation': ['每个自然数 $k$ 除以正整数 $n$ 都有唯一的商 $i$ 和余数 $j$，$0\\le j<n$。',
                            '唯一的商余式 $k=in+j$ 同时证明：不同有序对不会同号，每个自然数都有对应的有序对。',
                            '有限非空集合与可数无穷集合的积仍可数无穷；非空条件不可丢，若 $B=\\varnothing$，积就是空集。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 9.2': {'prompt': '在实数集上定义二元运算 $x*y=x$。计算 $3*4$、$(-5)*0.2$、$0*(1/2)$。',
           'solution': '$3*4=3$，$(-5)*0.2=-5$，$0*(1/2)=0$。',
           'explanation': ['新运算符 $*$ 不代表普通乘法，必须严格使用题给定义。', '它总返回左侧输入，右侧值不影响结果，因此三式直接保留左操作数即可。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 9.4': {'prompt': '设 $S=\\{1,2\\}$，给出 $P(S)$ 上绝对补运算与对称差运算的运算表，全集为 $S$。',
           'solution': '补运算表：\n'
                       '\n'
                       '|$A$|$\\overline A$|\n'
                       '|---|---|\n'
                       '|$\\varnothing$|$\\{1,2\\}$|\n'
                       '|$\\{1\\}$|$\\{2\\}$|\n'
                       '|$\\{2\\}$|$\\{1\\}$|\n'
                       '|$\\{1,2\\}$|$\\varnothing$|\n'
                       '\n'
                       '对称差表：\n'
                       '\n'
                       '|$\\oplus$|$\\varnothing$|$\\{1\\}$|$\\{2\\}$|$\\{1,2\\}$|\n'
                       '|---|---|---|---|---|\n'
                       '|$\\varnothing$|$\\varnothing$|$\\{1\\}$|$\\{2\\}$|$\\{1,2\\}$|\n'
                       '|$\\{1\\}$|$\\{1\\}$|$\\varnothing$|$\\{1,2\\}$|$\\{2\\}$|\n'
                       '|$\\{2\\}$|$\\{2\\}$|$\\{1,2\\}$|$\\varnothing$|$\\{1\\}$|\n'
                       '|$\\{1,2\\}$|$\\{1,2\\}$|$\\{2\\}$|$\\{1\\}$|$\\varnothing$|',
           'explanation': ['幂集的四个元素都必须作为运算对象，不能只把 1、2 当作行列。',
                           '补集保留全集中未出现的元素；对称差保留恰属于两者之一的元素，共有部分全部删除。',
                           '对称差表关于对角线对称，且主对角线全为空集，分别反映交换律与 $A\\oplus A=\\varnothing$。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 9.5': {'prompt': '设 $S=\\{1,2,3,4\\}$，定义 $x\\circ y=(xy)\\bmod5$。求运算表。',
           'solution': '|$\\circ$|1|2|3|4|\n'
                       '|---|---|---|---|---|\n'
                       '|1|1|2|3|4|\n'
                       '|2|2|4|1|3|\n'
                       '|3|3|1|4|2|\n'
                       '|4|4|3|2|1|',
           'explanation': ['先做普通乘法，再除以 5 取余，例如 $2\\circ3=6\\bmod5=1$，$4\\circ4=16\\bmod5=1$。',
                           '所得余数都为 1 至 4，没有 0，因为 5 是素数而两个因子均不是 5 的倍数，所以运算确实在 $S$ 上封闭。',
                           '表的第一行、第一列都重现标签，说明 1 为单位元；表关于对角线对称，说明运算可交换。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 9.6': {'prompt': '对下列集合上的二元运算，说明交换、结合、幂等、消去性质，求单位元、零元及所有可逆元素的逆元。\n'
                     '(1) $\\mathbb Z^+$ 上 $x*y=\\operatorname{lcm}(x,y)$。\n'
                     '(2) $\\mathbb Q$ 上 $x*y=x+y-xy$。\n'
                     '消去律沿用原书定义：被消去的元素不得为该运算的零元。',
           'solution': '(1) 可交换、可结合、幂等，不满足消去律。单位元为 1，无零元。仅 1 可逆，其逆元为自身。\n'
                       '(2) 可交换、可结合、不幂等，满足原书约定的消去律。单位元为 0，零元为 1；每个 $x\\ne1$ 均可逆，$x^{-1}=x/(x-1)$，元素 1 不可逆。\n'
                       '结合性验证：$(x*y)*z=x*(y*z)=x+y+z-xy-xz-yz+xyz$。\n'
                       '消去：若 $x*y=x*z$ 且 $x\\ne1$，则 $(1-x)(y-z)=0$，故 $y=z$；交换性给出右消去。\n'
                       '逆元由 $x+y-xy=0$ 解得 $y=x/(x-1)$。',
           'explanation': ['(1) 最小公倍数的对称性、结合性与 $\\operatorname{lcm}(x,x)=x$ 分别给出三种性质；但 $2*1=2*2=2$，不能消去 2。',
                           '正整数最小公倍数的单位元是 1；若有零元 $z$，它必须是所有正整数的公倍数，不存在这样的有限正整数。要乘得单位元 1，两个数只能都为 1。',
                           '(2) $2*2=0\\ne2$ 说明不幂等；$x*0=x$ 说明 0 为单位元，$x*1=1$ 说明 1 为零元，不要按数字名字混淆角色。',
                           '原书消去律排除零元 1；若不排除它，$1*y=1*z=1$ 对任何 $y,z$ 都成立，因此不能无条件消去 1。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 9.7': {'prompt': '设 $A=\\{a,b,c\\}$，三种二元运算如下。判断交换、结合、消去、幂等性质，并求单位元、零元、所有逆元。\n'
                     '\n'
                     '|$*$|$a$|$b$|$c$|\n'
                     '|---|---|---|---|\n'
                     '|$a$|$a$|$b$|$c$|\n'
                     '|$b$|$b$|$c$|$a$|\n'
                     '|$c$|$c$|$a$|$b$|\n'
                     '\n'
                     '|$\\circ$|$a$|$b$|$c$|\n'
                     '|---|---|---|---|\n'
                     '|$a$|$a$|$b$|$c$|\n'
                     '|$b$|$b$|$b$|$b$|\n'
                     '|$c$|$c$|$b$|$c$|\n'
                     '\n'
                     '|$\\cdot$|$a$|$b$|$c$|\n'
                     '|---|---|---|---|\n'
                     '|$a$|$a$|$b$|$c$|\n'
                     '|$b$|$a$|$b$|$c$|\n'
                     '|$c$|$a$|$b$|$c$|',
           'solution': '|运算|交换|结合|消去|幂等|单位元|零元|逆元|\n'
                       '|---|---|---|---|---|---|---|---|\n'
                       '|$*$|是|是|是|否|$a$|无|$a^{-1}=a,b^{-1}=c,c^{-1}=b$|\n'
                       '|$\\circ$|是|是|否|是|$a$|$b$|仅 $a^{-1}=a$|\n'
                       '|$\\cdot$|否|是|否|是|无|无|无|',
           'explanation': ['$*$ 表可把 $a,b,c$ 分别对应 0、1、2，运算就是模 3 加法，故交换、结合、可消去；$b*b=c\\ne b$ 说明不幂等。',
                           '$\\circ$ 相当于链 $a<c<b$ 上取较大者，因此交换、结合、幂等；但 $c\\circ a=c\\circ c=c$ 且 $a\\ne '
                           'c$，所以不消去。',
                           '$\\cdot$ 始终返回右操作数，故 $(x\\cdot y)\\cdot z=z=x\\cdot(y\\cdot z)$，结合而不交换；$x\\cdot '
                           'x=x$，故幂等。',
                           '单位元须同时满足左、右单位条件，零元同样须两侧吸收；右投影运算虽有单侧性质，却无双侧单位元或零元。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 9.8': {'prompt': '设 $V=\\langle\\mathbb Z,+,0\\rangle$，$n\\mathbb Z=\\{nz\\mid z\\in\\mathbb Z\\}$，其中 '
                     '$n$ 为自然数。证明 $n\\mathbb Z$ 是 $V$ 的子代数。',
           'solution': '任取 $nz_1,nz_2\\in n\\mathbb Z$，有 $nz_1+nz_2=n(z_1+z_2)\\in n\\mathbb Z$，所以对加法封闭。\n'
                       '且常元 $0=n\\cdot0\\in n\\mathbb Z$。\n'
                       '因此 $n\\mathbb Z$ 构成 $V$ 的子代数。$n=1$ 与 $n=0$ 时分别为整个 $\\mathbb Z$ 与 '
                       '$\\{0\\}$，是平凡子代数；$n\\ge2$ 时为非平凡真子代数。',
           'explanation': ['子代数不仅要对二元运算封闭，还必须包含原系统指定的全部常元。',
                           '任意两个 $n$ 的整数倍相加仍是 $n$ 的整数倍，给出封闭性的一般证明。',
                           '用 $0=n\\cdot0$ 证明常元归属，不能只验证加法而漏掉签名中的 0。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 9.9': {'prompt': '设 $V_1,V_2$ 分别为模 3 加法、模 2 加法的代数系统，给出积代数 $V_1\\times V_2$ 的运算表，说明交换性、结合性以及单位元。',
           'solution': '积运算逐分量进行：$\\langle x_1,y_1\\rangle\\oplus\\langle '
                       'x_2,y_2\\rangle=\\langle(x_1+x_2)\\bmod3,(y_1+y_2)\\bmod2\\rangle$。\n'
                       '\n'
                       '|$\\oplus$|$\\langle0,0\\rangle$|$\\langle0,1\\rangle$|$\\langle1,0\\rangle$|$\\langle1,1\\rangle$|$\\langle2,0\\rangle$|$\\langle2,1\\rangle$|\n'
                       '|---|---|---|---|---|---|---|\n'
                       '|$\\langle0,0\\rangle$|$\\langle0,0\\rangle$|$\\langle0,1\\rangle$|$\\langle1,0\\rangle$|$\\langle1,1\\rangle$|$\\langle2,0\\rangle$|$\\langle2,1\\rangle$|\n'
                       '|$\\langle0,1\\rangle$|$\\langle0,1\\rangle$|$\\langle0,0\\rangle$|$\\langle1,1\\rangle$|$\\langle1,0\\rangle$|$\\langle2,1\\rangle$|$\\langle2,0\\rangle$|\n'
                       '|$\\langle1,0\\rangle$|$\\langle1,0\\rangle$|$\\langle1,1\\rangle$|$\\langle2,0\\rangle$|$\\langle2,1\\rangle$|$\\langle0,0\\rangle$|$\\langle0,1\\rangle$|\n'
                       '|$\\langle1,1\\rangle$|$\\langle1,1\\rangle$|$\\langle1,0\\rangle$|$\\langle2,1\\rangle$|$\\langle2,0\\rangle$|$\\langle0,1\\rangle$|$\\langle0,0\\rangle$|\n'
                       '|$\\langle2,0\\rangle$|$\\langle2,0\\rangle$|$\\langle2,1\\rangle$|$\\langle0,0\\rangle$|$\\langle0,1\\rangle$|$\\langle1,0\\rangle$|$\\langle1,1\\rangle$|\n'
                       '|$\\langle2,1\\rangle$|$\\langle2,1\\rangle$|$\\langle2,0\\rangle$|$\\langle0,1\\rangle$|$\\langle0,0\\rangle$|$\\langle1,1\\rangle$|$\\langle1,0\\rangle$|\n'
                       '运算满足交换律、结合律，单位元为 $\\langle0,0\\rangle$。',
           'explanation': ['积代数的每个元素是一个有序对，第一分量只能取 0、1、2，第二分量只能取 0、1，共六个元素。',
                           '例如 '
                           '$\\langle1,1\\rangle\\oplus\\langle2,1\\rangle=\\langle0,0\\rangle$，两个分量分别对不同的模数取余，不能统一模 '
                           '6 相加。',
                           '各分量的运算都交换且结合，逐分量验证即可得到积运算的对应性质；两个分量单位元组成整体单位元。'],
           'status': 'reviewed',
           'issues': [],
           'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 9.10': {'prompt': '设 $\\mathbb Z_n=\\{0,1,\\ldots,n-1\\}$，$V_1=\\langle\\mathbb '
                      'Z_4,\\otimes_4\\rangle$、$V_2=\\langle\\mathbb Z_3,\\otimes_3\\rangle$ 分别采用模 4、模 3 '
                      '乘法。考察积代数的消去律。原书称两个因子都满足消去律，再展示积代数不满足；请连同这处前提错误一起辨析。',
            'solution': '积代数确实不满足消去律：\n'
                        '$\\langle2,0\\rangle\\otimes\\langle0,2\\rangle=\\langle0,0\\rangle=\\langle2,0\\rangle\\otimes\\langle0,0\\rangle$。\n'
                        '被消去元素 $\\langle2,0\\rangle$ 并非零元，而右侧两个因子不同，故不能消去。\n'
                        '原书前提需要勘误：模 4 乘法本身也不满足消去律，因为 $2\\otimes_4 0=2\\otimes_4 2=0$，但 $0\\ne2$ 且 $2$ 并非零元 '
                        '0。模 3 乘法在排除零元作为被消去项后可以消去。\n'
                        '因此本例的积代数计算成立，但不能按原文把它当作“两个都可消去的系统，其积不可消去”的有效反例。',
            'explanation': ['先按题中原有模数逐分量计算，确认积系统里确有消去失败。',
                            '验证论证还要逐一检查前提：$\\mathbb Z_4$ 中 2 是非零零因子，已经导致因子系统消去失败。',
                            '这不是 OCR 将数字识错：已对原书图像核对确为模 4，所以保留原系统并明确勘误，而不静默换一个模数。'],
            'status': 'reviewed',
            'issues': ['原书例 9.10 关于模 4 乘法满足消去律的前提有误；文字题解已明确区分原书主张与数学勘误。'],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 9.12': {'prompt': '设 $V=\\langle\\mathbb Z_n,\\oplus\\rangle$，其中 $\\oplus$ 为模 $n$ 加法。证明 $V$ 恰有 $n$ 个自同态。',
            'solution': '对每个 $p\\in\\mathbb Z_n$，定义 $f_p(x)=px\\bmod n$。有\n'
                        '$f_p(x\\oplus y)=(p(x+y))\\bmod n=f_p(x)\\oplus f_p(y)$，故为自同态。$n\\ge2$ 时 '
                        '$f_p(1)=p$，不同 $p$ 给出不同函数，已构造 $n$ 个。\n'
                        '反之任意自同态 $f$ 满足 $f(0)=0$，并由 $p=f(1)$ 及 $x=1\\oplus\\cdots\\oplus1$（$x$ 次），得到 '
                        '$f(x)=px\\bmod n$，所以必为某个 $f_p$，无其他自同态。\n'
                        '$n=1$ 时只有单元素集上的唯一映射，结论仍成立。',
            'explanation': ['先构造至少 $n$ 个，再证明最多 $n$ 个，两部分缺一不可。',
                            '模加法同态由生成元 1 的像完全决定；像可任选 $n$ 个元素中的一个，便对应一个自同态。',
                            '$f(0)=f(0\\oplus0)=f(0)\\oplus f(0)$，在模加群里消去一项可得 $f(0)=0$。',
                            '单元素边界 $n=1$ 不含元素 1，所以应单独处理，不能直接引用 $f(1)$。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'},
 '例 9.13': {'prompt': '进程代数描述实例：一个自动售货机只提供咖啡、茶。输入动作 $coin,coffee,tea$ '
                      '分别表示接收硬币、取走咖啡、取走茶；带横线的互补输出动作分别表示投入硬币、提供咖啡、提供茶。用 CCS 描述机器与只买咖啡的顾客的交互。',
            'solution': '设机器进程 $M=\\,!coin.(\\overline{coffee}+\\overline{tea})$，顾客进程 '
                        '$C=\\,!\\overline{coin}.coffee$。\n'
                        '两者并行：\n'
                        '$$M\\mid '
                        'C=\\,!coin.(\\overline{coffee}+\\overline{tea})\\mid\\,!\\overline{coin}.coffee.$$\n'
                        '硬币投入与接收同步后，转为\n'
                        '$$(\\overline{coffee}+\\overline{tea})\\mid\\,!coin.(\\overline{coffee}+\\overline{tea})\\mid '
                        'coffee\\mid\\,!\\overline{coin}.coffee.$$\n'
                        '随后提供咖啡与取走咖啡同步，系统恢复为 $M\\mid C$。重复算子 $!$ 保留可再次服务、再次购买的进程。\n'
                        '可加限制 $(new\\ coin,coffee,tea)(M\\mid C)$，使这些通道的动作只能在系统内部交互。\n'
                        '所用基本算子为：0（停止）、点号（顺序执行）、$+$（二选一）、$\\mid$（并行）、$new$（限制通道）及 '
                        '$!$（重复）。输入与同名互补输出可同步，产生外部不可见动作 $\\tau$。',
            'explanation': ['区分动作的方向：机器接收硬币、提供饮料；顾客投入硬币、取走饮料，所以对应动作必须互补，横线不能漏掉。',
                            '点号表示先做前面的动作，再进入后续进程；加号表示售货机可选提供咖啡或茶，但一次选择只执行一个分支。',
                            '并行进程中，机器的 $coin$ 与顾客的 $\\overline{coin}$ 同步，分别消去双方已完成的动作前缀，留下可选饮料输出和等待取咖啡的输入。',
                            '第二次同步完成一轮服务。由于双方均带重复算子，后续仍能开始同样交互；通道限制则阻止外部进程在这些通道上插入通信。'],
            'status': 'reviewed',
            'issues': [],
            'ocr_method': 'visual-source-checked-and-math-retyped'}}

def build(items, texts, resolution):
    out=[]
    for item in items:
        prompt='\n'.join(texts[cache_key(s)] for s in item['segments']).strip()
        prompt=re.sub(r'^例\s*\d+(?:\s*[.．]\s*\d+)?\s*', '', prompt)
        solution='\n'.join(texts[cache_key(s)] for s in item['answer_segments']).strip()
        solution=re.sub(r'^(?:解|证明|证)\s*[”"：:]?\s*', '', solution)
        issues=['数学符号、上下标、表格与题解边界尚未逐项人工复核；此文本不能用于自动判分。']
        if not item['answer_segments']:
            issues.append('原书例题的题干和演示结果未由“解/证明”标题分开，待复核拆分。')
        if re.search(r'如图|见图|图\s*\d|图中|下图', prompt+solution):
            issues.append('包含图形引用，图的结构尚未可靠转写为文字。')
        if item.get('context_needed'):
            issues.append('可能依赖上文或前例条件，需核对题干的独立完整性。')
        record={'id':item['id'],'title':item['title'],'prompt':prompt,'solution':solution,'explanation':[],'status':'ocr_needs_review','issues':issues,'source_pages':sorted({s['page'] for s in item['segments']+item['answer_segments']}),'chapter':item['chapter'],'section_id':item['section_id'],'knowledge_ids':item['knowledge_ids'],'ocr_method':resolution,'counted_as_mastery':False,'scoring':'reference_only'}
        if item['title'] in REVIEWED:
            record.update(REVIEWED[item['title']])
        out.append(record)
    data={'version':17,'book_id':'DM2T','items':out,'audit':{'indexed_examples':len(items),'text_records':len(out),'reviewed':sum(i['status']=='reviewed' for i in out),'needs_review':sum(i['status']!='reviewed' for i in out),'with_solution_text':sum(bool(i['solution']) for i in out),'source':'用户提供的《离散数学 第2版》扫描教材；页码为 PDF 物理页。','statement':'全部已索引例题已生成文字记录；OCR 待复核项不是可靠答案，图形与公式仍有识别限制。'}}
    temporary=TARGET.with_suffix('.building.json')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    temporary.replace(TARGET)
    print(json.dumps(data['audit'], ensure_ascii=False), flush=True)

if __name__=='__main__':
    items=examples()
    segments={cache_key(s):s for item in items for s in item['segments']+item['answer_segments']}
    texts={key:(ARGS.cache/(key+'.txt')).read_text() if (ARGS.cache/(key+'.txt')).exists() else low_resolution(segment) for key,segment in segments.items()}
    build(items,texts,'tesseract-216dpi-crop-with-145dpi-fallback')
    if ARGS.high_resolution:
        with concurrent.futures.ThreadPoolExecutor(max_workers=ARGS.workers) as pool:
            pending={pool.submit(high_resolution,segment):key for key,segment in segments.items()}
            done=0
            for future in concurrent.futures.as_completed(pending):
                key=pending[future]
                try:
                    texts[key]=future.result()
                except Exception as exc:
                    print('OCR fallback',key,type(exc).__name__,flush=True)
                done+=1
                if done%30==0:
                    print(f'OCR {done}/{len(pending)}',flush=True)
        build(items,texts,'tesseract-216dpi-crop')
