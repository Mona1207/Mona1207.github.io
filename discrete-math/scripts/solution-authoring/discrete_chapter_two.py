"""Explicitly reviewed solutions for every independent exercise in DM chapter 2."""
import manual_solutions as author

add = author.add

def put(number, steps, errors, check):
    add('DM2T', f'002-{number:03}', steps, errors, check)

put(1, [
 r'先逐层求 $A=p\to q=\neg p\lor q$、$B=p\land\neg q$。由德摩根律，$\neg A=\neg(\neg p\lor q)=p\land\neg q=B$，但题目要求真值表，仍须把四组赋值全部列出。',
 r'在 $pq=00,01,10,11$ 四行中，A列为1、1、0、1，B列为0、0、1、0；所以 $A\lor B$ 四行均为1，$\neg(A\lor B)$ 四行均为0。',
 r'分别取否定得到 $\neg A$ 列0、0、1、0和 $\neg B$ 列1、1、0、1，两列每一行都不能同时为1，故 $\neg A\land\neg B$ 四行均为0。答案表的最后两列逐行相同，验证了本题给定A、B的德摩根等值式。',
 r'本题A、B互为否定，所以两边恰为恒假；一般的德摩根律并不要求A、B互补，也不要求两边都恒假。不要从本题的特殊真值反推一般公式只能为0。'
], [r'否定整个 $A\lor B$ 后要把析取换为合取，并分别否定A、B。',r'A列在pq=00时为1；不能把假前件的蕴涵算成0。'], '核对四行的A、B、否定和两个目标列。')

put(2, [
 r'沿用第1题，按00、01、10、11列出 $A=1,1,0,1$、$B=0,0,1,0$。每行的A、B都是由原变项p、q计算出来，不能另当作独立任意输入增加行数。',
 r'计算 $A\to B$：00、01、11三行都是前件A真、后件B假，结果为0；10行是前件假、后件真，结果为1，所以目标列为0、0、1、0。',
 r'再独立计算 $\neg A\lor B$：$\neg A$ 的列为0、0、1、0，B恰与其相同，析取列仍为0、0、1、0。两个目标列在全部四行一致，故等值关系成立。',
 r'这个检查也说明蕴涵的改写规则：要否定整个前件A，后件B保持原样，外层换成析取；不是 $A\lor\neg B$。'
], [r'箭头前件是整个A，不是只对其中的p取否定。',r'本题目标列只有pq=10时为1，不要误套第1题的恒假结论。'], '逐行核对目标列0、0、1、0。')

put(3, [
 r'第（1）式先展开双条件：$((p\land q)\leftrightarrow q)\equiv[(p\land q)\to q]\land[q\to(p\land q)]$。前因子为1，后因子 $\equiv\neg q\lor(p\land q)\equiv(\neg q\lor p)\land(\neg q\lor q)\equiv p\lor\neg q$。因此原式 $\equiv\neg(p\lor\neg q)\equiv\neg p\land q$，仅pq=01成真，是可满足而非重言式。',
 r'第（2）式先化第一个析取项：$p\to(p\lor q)\equiv\neg p\lor p\lor q\equiv1$。整个公式 $\equiv1\lor(p\to r)\equiv1$，所以为重言式。无需对后一个析取项附加条件。',
 r'第（3）式消去蕴涵并用德摩根律：$(p\lor q)\to(p\land r)\equiv\neg(p\lor q)\lor(p\land r)\equiv(\neg p\land\neg q)\lor(p\land r)$。第一项给p=q=0而r任意，得到000、001；第二项给p=r=1而q任意，得到101、111。',
 r'第（3）式在010时为假，所以不是重言式；上一步又给出四组成真赋值，故是非重言的可满足式。下方真值表依次列出各个中间子式，对第（1）、（3）问要求的成真赋值逐行作全量核验。'
], [r'第（1）问最外层还有否定，不能把内层 $p\lor\neg q$ 直接当最终式。',r'第（3）问化简后未出现的自由变项须取0、1两种值，不可漏掉001或111。'], '等值演算判断类型，并与全真值表交叉核对。')

put(4, [
 r'第（1）式从右边开始，用分配律提取p：$(p\land q)\lor(p\land\neg q)\equiv p\land(q\lor\neg q)\equiv p\land1\equiv p$。三步分别用了分配律、排中律和同一律，得到左边。',
 r'第（2）式消去两处蕴涵：$(p\to q)\land(p\to r)\equiv(\neg p\lor q)\land(\neg p\lor r)$。用分配律反向合并公共项 $\neg p$，得 $\neg p\lor(q\land r)$，再按蕴涵等值式还原成 $p\to(q\land r)$。',
 r'第（3）式左边先写双条件的两方向：$\neg(p\leftrightarrow q)\equiv\neg[(\neg p\lor q)\land(\neg q\lor p)]\equiv(p\land\neg q)\lor(q\land\neg p)$。这里外层否定先把合取变成析取，再对每个析取项用德摩根律。',
 r'第（3）式右边化为 $(p\lor q)\land(\neg p\lor\neg q)$，分配展开为 $(p\land\neg p)\lor(p\land\neg q)\lor(q\land\neg p)\lor(q\land\neg q)$。两个互补合取项为0，留下与左边相同的两项，因此两边等值。',
 r'第（4）式左边正是第（3）式得到的两项（合取交换律允许交换q与否定p的顺序），右边相同。直接反用上一段的展开过程，就从左边得到右边；没有只凭两边“形式相近”作结论。'
], [r'$\neg(p\leftrightarrow q)$ 表示恰一项真，不能写成 $\neg p\leftrightarrow\neg q$。',r'分配展开有四项，须明确其中两项为什么为0。'], '为四个等值关系逐步列出使用的定律。')

# These tasks explicitly ask for truth tables or principal forms. The computed
# tables retained by manual_solutions.main contain every intermediate column.
PRINCIPAL_NOTES = {
 5: [r'第（1）式 $\neg p\to q\equiv p\lor q$，再消去外层蕴涵，得到 $\neg(p\lor q)\lor\neg q\lor p\equiv\neg q\lor p$，所以只在pq=01时假。',r'第（2）式 $\equiv(p\lor q)\land q\land r\equiv q\land r$，p可任意，故仅011、111为真。第（3）式的前件若真，则p或q、r同时真，必有后件 $p\lor q\lor r$ 为真；因此全部八行成真。'],
 6: [r'第（1）式 $\neg(q\to\neg p)\land\neg p\equiv q\land p\land\neg p\equiv0$，因此四行全部成假。',r'第（2）式用分配律得 $(p\land q)\lor\neg p\lor r\equiv(\neg p\lor q)\lor r$，仅p=1、q=r=0时为假，即100。第（3）式第一析取项 $p\to(p\lor q)$ 恒真，因此全式恒真，无成假赋值。'],
 7: [r'第（1）式 $(p\land q)\lor r$：r=1时四行全部成真，另加r=0且p=q=1这一行，得到001、011、101、110、111。其余三行为假。',r'第（2）式 $(p\to q)\land(q\to r)$ 要同时排除p真q假与q真r假。成真仅000、001、011、111；010、100、101、110分别违反至少一条蕴涵。'],
 8: [r'第（1）式 $(p\land q)\to q$ 的前件只要真，q就真；前件假时蕴涵也真，所以四行全真。',r'第（2）式 $(p\leftrightarrow q)\to r$ 成假恰在p=q且r=0，即000、110。第（3）式 $\neg(r\to p)\land p\land q\equiv r\land\neg p\land p\land q\equiv0$，八行全假。'],
 9: [r'第（1）式 $(p\lor q)\lor(\neg p\land r)\equiv p\lor q\lor r$，因为 $p\lor(\neg p\land r)\equiv(p\lor\neg p)\land(p\lor r)\equiv p\lor r$。所以仅000为假。',r'第（2）式先算 $p\to q$ 和 $p\leftrightarrow\neg q$ 两列：00时为1、0，目标为0；01时为1、1，目标为1；10时为0、1，目标为1；11时为1、0，目标为0。成真正是01、10。'],
 10:[r'第（1）式r=1时恒真；r=0时只在p=q=1时真。按pqr从000到111得0、1、0、1、0、1、1、1，因此成假下标为0、2、4。',r'第（2）式两条蕴涵同时真，等于要求p≤q≤r，故成真下标0、1、3、7，成假下标2、4、5、6。下方中间列逐行检查这些限制。'],
 11:[r'第（1）式r必须为1且p、q至少一真，所以成真为011、101、111，其余五行成假。',r'第（2）式前件p若真，后件析取就真；p若假，蕴涵自动真，故全部八行成真。第（3）式 $\neg(q\to\neg p)\land\neg p\equiv q\land p\land\neg p\equiv0$，只涉及p、q，四行全假。']
}
for n, notes in PRINCIPAL_NOTES.items():
    put(n, [
      r'固定变项顺序：含r的问按p、q、r排列；只含p、q的问按p、q排列。下标是赋值按该顺序组成的二进制数。极小项在指定行为1，极大项在指定行为0；二者的否定位置恰好相反。',
      *notes,
      r'按下方完整真值表，把每个真行逐一写成含全部变项的极小项，再析取得主析取范式；把每个假行逐一写成极大项，再合取得主合取范式。譬如三变项011给 $m_3=\neg p\land q\land r$，而 $M_3=p\lor\neg q\lor\neg r$。答案的下标式和下方展开式一一对应。',
      r'若没有真行，主析取范式为0；没有假行，主合取范式为1。求其中一种范式后可用互补下标得到另一种：全部下标只属于真行或假行之一，不能重叠或遗漏。'
    ], [r'极小项对真行写，极大项对假行写，否定位置不能混用。',r'先确定该小问实际含几个变项；二变项只有4行，三变项才有8行。'], '逐小问独立化简和真值穷举一致，并核对所有范式项及赋值。')

put(12, [
 r'三变项按p、q、r排列，全赋值为000、001、010、011、100、101、110、111。题给真行为000、011、110，对应十进制下标0、3、6；不在这三行中的001、010、100、101、111都是假行，下标1、2、4、5、7。',
 r'为每个真行写极小项：000给 $\neg p\land\neg q\land\neg r$，011给 $\neg p\land q\land r$，110给 $p\land q\land\neg r$。所以主析取范式为三者析取，即 $m_0\lor m_3\lor m_6$。',
 r'为每个假行写极大项：001给 $p\lor q\lor\neg r$，010给 $p\lor\neg q\lor r$，100给 $\neg p\lor q\lor r$，101给 $\neg p\lor q\lor\neg r$，111给 $\neg p\lor\neg q\lor\neg r$。主合取范式为这五项的合取，即 $M_1\land M_2\land M_4\land M_5\land M_7$。',
 r'核验：任一给定真行恰好使一个极小项为1，并使所有五个极大项为1；任一假行使三个极小项都为0，且使自己的极大项为0。故两个范式都准确恢复题设八行。'
], [r'由成真下标求主合取范式须先取下标补集，不能沿用0、3、6。',r'极大项中位为1时写否定，极小项规则相反。'], '逐项展开3个极小项、5个极大项并检验全8行。')

put(13, [
 r'题给四个假行010、011、110、111，对应下标2、3、6、7；其余000、001、100、101为真行，下标0、1、4、5。观察这四个假行的共同特点是q=1，与p、r无关。',
 r'按真行构造主析取范式：$$(\neg p\land\neg q\land\neg r)\lor(\neg p\land\neg q\land r)\lor(p\land\neg q\land\neg r)\lor(p\land\neg q\land r).$$即 $m_0\lor m_1\lor m_4\lor m_5$。',
 r'按假行构造主合取范式：$$(p\lor\neg q\lor r)\land(p\lor\neg q\lor\neg r)\land(\neg p\lor\neg q\lor r)\land(\neg p\lor\neg q\lor\neg r).$$即 $M_2\land M_3\land M_6\land M_7$。',
 r'把主析取范式按p配对、r配对，得到 $\neg q\land(\neg p\lor p)\land(\neg r\lor r)\equiv\neg q$，与第一步观察一致。注意 $\neg q$ 是简化式，因不含p、r，本身不是三变项的主范式。'
], [r'化简为 $\neg q$ 后仍须给出题目要求的含全部变项的主范式。',r'真、假下标各4个且应覆盖0至7。'], '完整展开两种主范式，再化简为q的否定核对。')

put(14, [
 r'n个变项共有 $2^n$ 组赋值。主合取范式的构造是：对每个使A为0的赋值写一个极大项，再把所有这些项合取。',
 r'题设没有成假赋值，因此没有任何极大项应被选入，所得是空合取。合取的单位元为1，所以空合取定义为1；这与空析取为0不同。',
 r'从真值直接检查：没有成假赋值表示每个赋值都使A为1，故A为重言式，恰与常量1等值。因此主合取范式为1，不是“所有极大项的合取”。'
], [r'全部极大项的合取恒假，恰与本题恒真相反。',r'空合取为1，不能因没有项就写0。'], '由主合取范式构造及恒真语义双重确认。')

put(15, [
 r'主析取范式唯一性要求比较时使用同一变项顺序和同一变项集合。第（1）问统一用p、q、r。第一式 $\neg(\neg p\lor q)\lor r\equiv(p\land\neg q)\lor r$：r=1给下标1、3、5、7，r=0且p=1、q=0给下标4，故PDNF为 $m_1\lor m_3\lor m_4\lor m_5\lor m_7$。',
 r'第（1）问第二式 $q\to(p\to r)\equiv\neg q\lor\neg p\lor r$，仅110为假，PDNF为 $m_0\lor m_1\lor m_2\lor m_3\lor m_4\lor m_5\lor m_7$。它比第一式多下标0、2，所以不等值。取000反查，第一式为0、第二式为1。',
 r'第（2）问统一按p、q，$\neg(p\land q)$ 只在11时假，PDNF为 $m_0\lor m_1\lor m_2$；$\neg(p\lor q)$ 只在00时真，PDNF为 $m_0$。范式不同，所以也不等值。',
 r'可具体展开第（2）问：前式为 $(\neg p\land\neg q)\lor(\neg p\land q)\lor(p\land\neg q)$，后式为 $\neg p\land\neg q$。赋值01使前真后假，作为独立反例验证。'
], [r'逻辑等值要所有赋值一致，一个反例就能否定，但单个相同行不能证明等值。',r'第（1）问箭头的括号位置不同，不能都当作 $p\to(q\to r)$。'], '依题意分别求唯一PDNF，并用反例检查不等值结论。')

put(16, [
 r'统一按p、q、r。第（1）问第一式 $p\to(q\to r)\equiv\neg p\lor\neg q\lor r$，只有110为假，所以PCNF为 $M_6=\neg p\lor\neg q\lor r$。第二式用德摩根律也等于这个三文字析取，假行相同、PCNF相同，故等值。',
 r'第（2）问第一式仍是 $M_6$。第二式 $(p\to q)\to r\equiv(p\land\neg q)\lor r$，假行是r=0且不是p=1、q=0，即000、010、110。因此PCNF为 $M_0\land M_2\land M_6$。',
 r'第二式PCNF展开为 $(p\lor q\lor r)\land(p\lor\neg q\lor r)\land(\neg p\lor\neg q\lor r)$。它与仅含 $M_6$ 的第一式不相同；在000时第一式为1、第二式为0，故不等值。',
 r'此题也体现蕴涵不满足结合律：$p\to(q\to r)$ 与 $(p\to q)\to r$ 的括号不能任意移动。比较范式时须先固定括号再计算。'
], [r'PCNF用假行下标；不能把真行当作极大项来源。',r'不能删除蕴涵括号或套用合取、析取的结合律。'], '逐式求PCNF并以反例验证第二对不同。')

put(17, [
 r'目标只允许否定、合取、析取，须依次消掉蕴涵和双条件。第（1）问先把 $q\leftrightarrow(q\land r)$ 写成 $[q\to(q\land r)]\land[(q\land r)\to q]$。后一项恒真，前一项 $\equiv\neg q\lor(q\land r)\equiv\neg q\lor r$。',
 r'于是第（1）式 $\neg[p\to(\neg q\lor r)]\equiv\neg[\neg p\lor\neg q\lor r]\equiv p\land q\land\neg r$，已只含允许的联结词。',
 r'第（2）式 $(p\land q)\lor\neg r$ 原本就只使用允许联结词，直接保留即可。化为目标联结词集合不要求一定改变原式。',
 r'第（3）问令 $X=(q\land r)\lor(\neg q\land\neg r)$ 表示 $q\leftrightarrow r$，则 $p\leftrightarrow X\equiv(p\land X)\lor(\neg p\land\neg X)$。否定X用德摩根律可化为 $(q\land\neg r)\lor(\neg q\land r)$，因此展开后得到答案所列四个合取分支，最终无箭头或双条件残留。'
], [r'外层否定要作用于整个蕴涵，得出前件真、后件假。',r'第（3）问不能在最终式中把X当作新变项而不展开其定义。'], '逐处消去不允许的联结词，并以定义展开核验。')

put(18, [
 r'仅允许 $\{\neg,\land\}$ 时，用 $U\lor V\equiv\neg(\neg U\land\neg V)$ 消去每个析取；若遇蕴涵、双条件，先按定义展开。',
 r'第（1）式将三项析取一次用德摩根律反写：$p\lor\neg q\lor\neg r\equiv\neg(\neg p\land\neg\neg q\land\neg\neg r)\equiv\neg(\neg p\land q\land r)$。',
 r'第（2）式 $p\leftrightarrow r\equiv(p\to r)\land(r\to p)$，而 $p\to r\equiv\neg(p\land\neg r)$、$r\to p\equiv\neg(r\land\neg p)$。保留外层与q的合取即得 $\neg(p\land\neg r)\land\neg(r\land\neg p)\land q$。',
 r'第（3）式先化简：$(p\to(q\land r))\lor p\equiv\neg p\lor(q\land r)\lor p\equiv1$。若目标集合不另允许常量符号，可把1写成 $\neg(p\land\neg p)$，其中只有否定与合取。'
], [r'第（3）式即使化为1，也须注意题目限定是否允许常量，写出允许联结词组成的恒真式最稳妥。',r'双条件要保留两个方向，不能只写 $\neg(p\land\neg r)$。'], '逐式给出仅由否定与合取组成的表达式。')

put(19, [
 r'仅允许 $\{\neg,\lor\}$ 时，用 $U\land V\equiv\neg(\neg U\lor\neg V)$ 消去合取；也可先化简，再对最后的合取用一次德摩根律。',
 r'第（1）式把 $U=\neg p\lor\neg q,V=r$ 代入上述规则，得到 $\neg(\neg(\neg p\lor\neg q)\lor\neg r)$。这保留了原来“前一大项与r都真”的意思。',
 r'第（2）式先消蕴涵：$p\to(q\land\neg p)\equiv\neg p\lor(q\land\neg p)\equiv\neg p$，最后一步是吸收律。故原式 $\equiv\neg p\land q\land r\equiv\neg(p\lor\neg q\lor\neg r)$。',
 r'第（3）式直接由德摩根律反写为 $\neg(\neg p\lor\neg q\lor r)$。检查第（2）、（3）的r：前者要求r真所以内部是 $\neg r$，后者要求r假所以内部是r，不能混用。'
], [r'德摩根律处理三项合取时，外层否定内的每个文字都须取反。',r'第（2）问蕴涵前件为p，不能误写成 $p\lor(q\land\neg p)$。'], '以吸收律和德摩根律消去全部合取与蕴涵。')

put(20, [
 r'目标只允许否定与蕴涵。基本替换为 $U\land V\equiv\neg(U\to\neg V)$、$U\lor V\equiv\neg U\to V$。这些均由 $X\to Y\equiv\neg X\lor Y$ 推出，不能把箭头当作对称运算。',
 r'第（1）式令 $X=p\land q\equiv\neg(p\to\neg q)$，则 $X\lor r\equiv\neg X\to r\equiv(p\to\neg q)\to r$。',
 r'第（2）式对 $U=p\to\neg q,V=r$ 直接用合取替换，得 $\neg((p\to\neg q)\to\neg r)$。',
 r'第（3）式先令 $X=\neg(p\to\neg q)$。双条件为 $(X\to r)\land(r\to X)$，再把这个合取换成 $\neg((X\to r)\to\neg(r\to X))$。最后把每处X展开，得到 $\neg((\neg(p\to\neg q)\to r)\to\neg(r\to\neg(p\to\neg q)))$，仅含允许符号。'
], [r'$U\lor V$ 改成 $\neg U\to V$，不是 $U\to V$。',r'第（3）问临时代号X最终应展开，且各处括号一致。'], '由蕴涵定义推导两个替换公式并逐式应用。')

put(21, [
 r'与非定义为 $p\uparrow q=\neg(p\land q)$，或非定义为 $p\downarrow q=\neg(p\lor q)$。由合取交换律，$\neg(p\land q)\equiv\neg(q\land p)$；由析取交换律，$\neg(p\lor q)\equiv\neg(q\lor p)$。因此两种联结词都满足交换律。',
 r'要否定结合律，只须找一组使两种括号结果不同的赋值，但必须同时算出左右两式。与非取pqr=001：左边先得 $p\uparrow q=\neg0=1$，再得 $1\uparrow1=0$；右边先得 $q\uparrow r=\neg(0\land1)=1$，再得 $0\uparrow1=1$。两边0与1不同，故不等值。',
 r'或非取pqr=100：左边先得 $p\downarrow q=\neg(1\lor0)=0$，再得 $0\downarrow0=1$；右边先得 $q\downarrow r=\neg(0\lor0)=1$，再得 $1\downarrow1=0$。两边1与0不同，故也不等值。',
 r'交换律只交换同一个二元运算的两输入；结合律涉及两层运算和括号。前者成立并不能推出后者成立，这两个反例已分别否定与非、或非的结合律。'
], [r'与非是先“与”再整体否定，或非是先“或”再整体否定。',r'证明不等值须展示同一赋值下左右不同，不能分别用两组赋值。'], '定义证明交换律，逐层计算两个结合律反例。')

put(22, [
 r'先固定表2.8的行顺序为pq=00、01、10、11。该表把四个输出依此作为二进制的从高位到低位来编号：若输出为 $b_0b_1b_2b_3$，下标是 $8b_0+4b_1+2b_2+b_3$；这是本表的编号约定。',
 r'第（1）式与非：合取列为0、0、0、1，整体取反得1、1、1、0；二进制1110为 $8+4+2=14$，故对应 $F_{14}^{(2)}$。',
 r'第（2）式或非：析取列为0、1、1、1，取反得1、0、0、0，编号8，对应 $F_8^{(2)}$。',
 r'第（3）式恰在01、10时真，所以输出0、1、1、0，编号 $4+2=6$，对应 $F_6^{(2)}$。第（4）式 $\neg(p\to q)\equiv p\land\neg q$，仅10时真，输出0、0、1、0，编号2，对应 $F_2^{(2)}$。',
 r'最后逐式反查：与非只在11时假、或非只在00时真、异或在两个不同值时真、否定蕴涵只在10时真。四个输出列和编号都与这些定义一致。'
], [r'真值函数编号取决于表的行顺序和高低位约定，不可自行反转。',r'第（4）式是否定整个蕴涵，不是 $\neg p\to q$。'], '明确表2.8编号约定，逐行计算四个输出并转为十进制。')

put(23, [
 r'定义：$A\Leftrightarrow B$ 表示对全部共同变项的每一赋值v都有 $v(A)=v(B)$。若某变项只出现在一式中，也给它赋值，另一式的值不受其影响；这样比较的赋值集合保持一致。',
 r'自反性：对任意v，数值 $v(A)$ 总等于自身，所以每一行 $v(A)=v(A)$，从而 $A\Leftrightarrow A$。',
 r'对称性：假设 $A\Leftrightarrow B$，任意v下都有 $v(A)=v(B)$。数值等号对称，故 $v(B)=v(A)$；v任意，所以 $B\Leftrightarrow A$。',
 r'传递性：假设 $A\Leftrightarrow B$ 且 $B\Leftrightarrow C$。任取三式全部变项的一组赋值v，有 $v(A)=v(B)$ 和 $v(B)=v(C)$；由数值等号传递性得 $v(A)=v(C)$，故 $A\Leftrightarrow C$。',
 r'三条性质均由“任意赋值下真值相等”推出，不要求A、B、C的书写形式相同，也不是只验证某一组特殊赋值。'
], [r'逻辑等值比较所有赋值的真值，不是要求字符串一样。',r'传递性应在同一共同变项赋值下串接两个等式。'], '依等值定义分别证明等价关系的三性质。')

put(24, [
 r'“当且仅当”分为两个方向。先设 $A\Leftrightarrow B$。任意赋值v下 $v(A)=v(B)$，否定的真值规则是 $v(\neg A)=1-v(A)$，故 $v(\neg A)=1-v(B)=v(\neg B)$。',
 r'由于v任意，得到 $\neg A\Leftrightarrow\neg B$，完成一个方向。这里是对两边同时取否定，不能只否定其中一边。',
 r'反向设 $\neg A\Leftrightarrow\neg B$，则任意v下 $1-v(A)=1-v(B)$。两边同减1再乘−1，得到 $v(A)=v(B)$，故 $A\Leftrightarrow B$。',
 r'等值演算也可表述为：否定式等值后再同时取否定，得到 $\neg\neg A\Leftrightarrow\neg\neg B$，最后用双重否定律还原。两个方向全部成立。'
], [r'充要条件要把反向证明写出。',r'$\neg A\Leftrightarrow B$ 与本题的“两边都否定”等值不是同一个命题。'], '以否定真值运算的可逆性证明两个方向。')

put(25, [
 r'要说明推断“不一定”，构造满足前提而不满足结论的反例即可。统一取 $A=p,B=\neg p$。p=0时A=0、B=1；p=1时A=1、B=0，因此A、B确实不等值。',
 r'第（1）问令 $C=p\lor\neg p$，由排中律C恒真。所以 $A\lor C\equiv A\lor1\equiv1$，$B\lor C\equiv B\lor1\equiv1$，两个析取等值，而A与B不等值。',
 r'第（2）问改令 $C=p\land\neg p$，由矛盾律C恒假。所以 $A\land C\equiv A\land0\equiv0$，$B\land C\equiv B\land0\equiv0$，两个合取等值，A与B仍不等值。',
 r'前一个C把A、B的差异全部用恒真遮蔽，后一个C用恒假遮蔽。因此通常不能从等值式两侧直接“消去相同析取项／合取项”。两个小问允许选不同C。'
], [r'反例必须同时验前提等值和结论不等值，不能只说A、B不同。',r'第（1）问要用恒真C，第（2）问要用恒假C。'], '完整验证两组反例的前提与结论。')

put(26, [
 r'若C为矛盾式，则 $A\lor C\equiv A\lor0\equiv A$，$B\lor C\equiv B$。因此已知两个析取等值可立即推出 $A\Leftrightarrow B$。这是第一个保证消去的充分条件。',
 r'若C为重言式，则 $A\land C\equiv A\land1\equiv A$，$B\land C\equiv B$，所以第二种关系也能消去C。',
 r'若条件只允许约束C，且要对所有A、B保证第一个消去规则，这个条件还是必要的。若C至少在一个赋值为真，取A为恒假式、B=C，则 $A\lor C\equiv C\equiv B\lor C$，但在C为真的赋值A=0、B=1，A、B不等值。故必须让C没有成真赋值，即恒假。',
 r'第二种同理：若C至少能为假，取A为恒真式、B=C，则 $A\land C\equiv C\equiv B\land C$，但在C为假时A、B不同。因此要对任意A、B保证可消去，C必须恒真。若已固定特定A、B，可能另有更弱条件，不能把本题的普遍保证误说成每一特定实例的必要条件。'
], [r'普遍消去时析取需C恒假，合取需C恒真，恰与第25题反例的遮蔽条件相反。',r'“对任意A、B”与“对某一对A、B”不可混淆。'], '证明两个充分条件，并以反例证明普遍消去的必要性。')

put(27, [
 r'“向上”取1，变项顺序为p、q、r。四种亮灯状态分别是001（仅C）、100（仅A）、011（B、C）、110（A、B）。因此成真下标为1、4、3、6，按升序写 $F=m_1\lor m_3\lor m_4\lor m_6$。其余000、010、101、111必须熄灯。',
 r'逐行写出四个极小项，按q配对合并：前两项中p=0、r=1，q任意，给 $\neg p\land r\land(\neg q\lor q)=\neg p\land r$；后两项中p=1、r=0，给 $p\land\neg r$。所以 $F=(\neg p\land r)\lor(p\land\neg r)$，灯亮只取决于A、C是否异态。',
 r'第（b）问用德摩根律消去这个析取，得 $F=\neg[\neg(\neg p\land r)\land\neg(p\land\neg r)]$，只含否定和合取。',
 r'第（c）问令 $U=\neg p\land r,V=p\land\neg r$。因为 $U\lor V\equiv\neg U\to V$，又有 $\neg U=\neg p\to\neg r$、$V=\neg(p\to r)$，得到 $F=(\neg p\to\neg r)\to\neg(p\to r)$，只含否定和蕴涵。',
 r'反查八种状态：p=r时两个合取项都为0；p≠r时恰有一项为1，而q取0、1都不变，正好是题设四行。若按实际继电器／逻辑门实现，可分别将合取接AND门、否定接NOT门；题目未给触点或电源规格，逻辑表达式确定了所要求的布尔功能。'
], [r'“仅C”是001，不是把B、C都置1。',r'化简后q不出现是因两个q状态都被允许，并非漏掉B开关。'], '四行建模，配对化简，分别构造两种目标联结词表达式并验证全8行。')

put(28, [
 r'把输入1解释为该路当前申请；输出1表示选中这路。A最高优先，所以只要A=1，无论B、C如何，都必须选A，得到 $F_A=A$。',
 r'B被选中需要B申请，同时A未申请，两个条件必须同时满足，故 $F_B=\neg A\land B$。C被选中需要C申请且A、B都未申请，故 $F_C=\neg A\land\neg B\land C$。',
 r'证明互斥：$F_A\land F_B$ 与 $F_A\land F_C$ 都含 $A\land\neg A$，恒为0；$F_B\land F_C$ 含 $B\land\neg B$，也恒为0。因此任意输入下最多一个输出为1。',
 r'证明无遗漏：若A=1，选A；若A=0且B=1，选B；若A=B=0且C=1，选C；若A=B=C=0，三输出均0。四类覆盖全部输入，既保证有人申请时按序输出，也保证无人申请时不凭空输出。'
], [r'“同一时刻只能一个输出”是最多一个，不能在000时也强行输出一路。',r'C要同时检查A、B两路均无申请，只检查A不够。'], '从逐级优先条件构造公式，再证明两两互斥及输入覆盖。')

put(29, [
 r'设 $W_B,L_B,D_B$ 分别表示王、李、丁当班长，$W_S,L_S$ 表示王、李当生活委员，$W_X$ 表示王当学习委员。恰对一半是异或，整体条件为 $F=(W_B\oplus L_S)\land(D_B\oplus W_S)\land(L_B\oplus W_X)$，还必须合取“三职与三人一一对应”的约束K。',
 r'用班长的三种可能作等值分支展开：在K下，$F\land K\equiv(W_B\land F\land K)\lor(L_B\land F\land K)\lor(D_B\land F\land K)$。这是因K保证三个班长命题恰一真，不是凭经验漏掉其他分支。每个异或使用 $1\oplus x=\neg x$、$0\oplus x=x$ 化简。',
 r'王当班长分支：K给 $W_S=W_X=D_B=L_B=0$。乙异或 $D_B\oplus W_S=0\oplus0=0$，该分支立即矛盾，整项为0。',
 r'李当班长分支：K给 $L_S=0,W_B=0$。甲异或 $W_B\oplus L_S=0\oplus0=0$，该分支也为0；或者继续由丙得王非学习委员，再推王为生活委员，仍不能满足甲。',
 r'丁当班长分支：$D_B=1,W_B=L_B=0$。甲化为 $L_S$，要求李为生活委员；乙化为 $\neg W_S$，要求王非生活委员；丙化为 $W_X$，要求王为学习委员。三项一致且符合K，故此分支唯一保留。',
 r'结果为丁金生班长、李强生活委员、王小红学习委员。反代三人的两句话，真值分别为（0，1）、（1，0）、（0，1），每人确实恰对一句，且三职各一人。'
], [r'“恰好一半”是异或，普通析取会允许两句都真。',r'必须合取职务一一对应约束，否则逻辑公式会出现无效的多人同职方案。'], '写明全条件，并作穷尽的等值分支展开和最后反代。')

put(30, [
 r'设z、q、s、l、w依次表示赵、钱、孙、李、周去。五个条件逐一为 $z\to q$、$l\lor w$、$q\leftrightarrow\neg s$、$s\leftrightarrow l$、$w\to(z\land q)$。整体是五式合取，每条均须满足。',
 r'由两个双条件，在满足整体条件的赋值中可代入 $q=\neg s,l=s$。消去蕴涵后，剩余等值约束为 $(\neg z\lor\neg s)\land(s\lor w)\land[\neg w\lor(z\land\neg s)]$，并保留上述q、l的替换关系。',
 r'按s展开。s=1时，第一项变为 $\neg z$，第二项恒真，第三项变为 $\neg w$；再有q=0、l=1。因此唯一赋值（z,q,s,l,w）=（0,0,1,1,0），只派孙、李。',
 r's=0时，第一项恒真，第二项变w，第三项变 $\neg w\lor z$。用 $w\land(\neg w\lor z)\equiv w\land z$，得w=z=1；再有q=1、l=0，唯一赋值为（1,1,0,0,1），只派赵、钱、周。',
 r's只能为0或1，两个分支已穷尽。分别反代五条：孙李方案中李、孙同去，钱不去且周、赵不去；赵钱周方案中周的附加条件成立，孙李均不去。两者都满足全部限制，故仅这两套方案。'
], [r'“至少一人”用析取，“恰好一人”用异或，两者不同。',r'周去的后件是赵、钱同时去，须写 $z\land q$。'], '使用双条件代入与s的等值分支展开，穷尽并反查全部方案。')

put(31, [
 r'一次二元消解只选一对互补文字：若 $C_1=l\lor X,C_2=\neg l\lor Y$，消解结果为 $X\lor Y$，再删去重复文字；不能同时删除多对互补文字。',
 r'第（1）问唯一可选互补对是r、$\neg r$。删除它们，合并其余文字得 $\neg p\lor\neg q\lor\neg q\lor s\lor\neg t$，利用析取幂等律去掉重复 $\neg q$，结果为 $\neg p\lor\neg q\lor s\lor\neg t$。',
 r'第（2）问用 $\neg s,s$ 消解，第二个子句删去s后不剩文字，第一个余下 $p\lor\neg q\lor r$，故这就是消解结果。',
 r'第（3）问有两种消解。对 $\neg p,p$ 消解得 $q\lor r\lor\neg r\lor\neg s$，含互补对r、$\neg r$，为重言子句。对r、$\neg r$ 消解得 $\neg p\lor q\lor p\lor\neg s$，含p、$\neg p$，也为重言子句。',
 r'两个重言子句均等值于1，但都不是空子句。若错误地同时删除两对，会得到 $q\lor\neg s$，这不是合法的一次消解结果。'
], [r'一次只能消去一对互补文字。',r'重言子句恒真，空子句恒假，两者方向相反。'], '列出每个合法消解对、保留文字和去重过程。')

put(32, [
 r'消解反证目标是从合取范式的子句集中推出空子句 $\square$。空子句在任何赋值下都假，而每个消解结果都是原子句的逻辑后果，因此推出它就说明原式不可满足。',
 r'第（1）问将五个子句依次标为 $C_1=\neg p\lor q,C_2=\neg p\lor r,C_3=\neg q\lor\neg r,C_4=p\lor\neg r,C_5=r$。由 $C_5,C_3$ 对r消解得 $C_6=\neg q$；由 $C_5,C_4$ 对r消解得 $C_7=p$。',
 r'再由 $C_7,C_1$ 对p消解得 $C_8=q$；最后 $C_8,C_6$ 消解得 $\square$。已取得矛盾；$C_2$ 没被用到并不影响证明，因为原式包含一个不可满足子集就已经不可满足。',
 r'第（2）问原式否定一个蕴涵。用 $\neg(X\to q)\equiv X\land\neg q$，其中 $X=(p\lor q)\land\neg p$，得到子句集 $\{p\lor q,\neg p,\neg q\}$。前两个对p消解得q，再与 $\neg q$ 消解得 $\square$，故也为矛盾式。'
], [r'否定蕴涵时前件保留、后件否定，不能写成 $\neg X\lor q$。',r'不必强行使用所有子句；推出空子句即足够。'], '逐次记录消解来源、枢轴文字及空子句终点。')

put(33, [
 r'第（1）问初始子句为 $C_1=p,C_2=\neg p\lor\neg q,C_3=q$。由 $C_1,C_2$ 对p消解得到 $C_4=\neg q$；由 $C_3,C_4$ 对q消解得空子句。因此原式不可满足。',
 r'第（2）问由 $C_1=p\lor q$ 与 $C_2=p\lor\neg q$ 对q消解，得到 $p\lor p$，去重为p。再与 $C_3=\neg p\lor r$ 对p消解，得r。因此满足原式必有p=r=1。',
 r'反向验证：若p=r=1，前两个子句因p真而真，第三个因r真而真，q不受限制。因此原式等值于 $p\land r$；全部成真赋值（p,q,r）为101、111。',
 r'这里用一个实际满足赋值完成可满足性的证明。“暂时没有推出空子句”本身不够，必须继续完成消解判定或像本题一样给出并验证模型。'
], [r'同号的两个p只去重为p，不会互相抵消。',r'未见空子句不自动等于已证明可满足，仍需验证模型或完成算法。'], '第一式推出空子句；第二式证明约束必要充分并列出全部模型。')

put(34, [
 r'设两子句可对至少两对不同变项的互补文字消解。可不失一般性写成 $C_1=l\lor k\lor X$、$C_2=\neg l\lor\neg k\lor Y$，其中l、k是不同变项上的文字；X、Y还可含其他文字。',
 r'若选择l、$\neg l$ 消解，得到 $k\lor X\lor\neg k\lor Y$。它包含 $k\lor\neg k$，所以无论赋值如何都是1，即重言子句。',
 r'若选择k、$\neg k$ 消解，得到 $l\lor X\lor\neg l\lor Y$，同样是重言子句。若互补对多于两对，选任意一对消解后至少仍保留另一对，因此结论不变。',
 r'每一种合法的一次消解结果都等值于1，故任意两个结果彼此等值。它们可以包含不同文字、形式不同，但真值函数都恒真。这里没有同时消去多对文字。'
], [r'“多个可选消解对”指一次选择其中一对，不能把所有互补对一齐删去。',r'结果等值不要求结果的文字集合相同。'], '写出一般两互补对形式，证明每个消解结果均为重言式。')

put(35, [
 r'记l对应的变项为p。题设l出现而互补文字不出现，称为纯文字情形。S是所有子句的合取，$S\prime$ 由删除含l的整个子句得到，并非只从这些子句中删一个文字l。',
 r'先证 $S$ 可满足则 $S\prime$ 可满足。取满足S的赋值v，S中每个子句都真。$S\prime$ 的每个子句原来就在S里，因此也全真；同一个v就满足 $S\prime$。',
 r'反向取满足 $S\prime$ 的赋值v，调整p使l为真：若l=p就设p=1，若 $l=\neg p$ 就设p=0，其余变项保持不动。$S\prime$ 既无l（相关子句都已删去），又无互补文字（题设保证），所以根本不含p，这个调整不会改变 $S\prime$ 的真值。',
 r'被删除的每个子句都含l，调整后均因一个真文字而真；保留的子句仍真，所以新赋值满足S。两个方向合起来，S与 $S\prime$ 同时可满足或同时不可满足，即等可满足。',
 r'边界：若所有子句都被删去，$S\prime$ 是空合取1；同样可把纯文字置真来满足S。等可满足不等于等值，例如S=p、$S\prime=1$，p=0时两式真值不同，但两式都存在满足赋值。'
], [r'删的是含l的整个子句，不是从子句中删l本身。',r'反向可以修改赋值；因此证明的是等可满足，而非同一赋值下总相等。'], '给出模型限制与模型延拓两个方向，并处理空子句集。')

put(36, [
 r'定义赋值翻转变换T：对每个属于U的底层变项p，令 $T(v)(p)=1-v(p)$；不属于U的变项保持原值。必须把同一变项的全部出现一致翻转。',
 r'逐文字验证。若p属于U，正文字p被替换为 $\neg p$，在v下取值 $1-v(p)=T(v)(p)$，等于原正文字在T(v)下的值；负文字 $\neg p$ 被替为p，在v下值 $v(p)=1-T(v)(p)$，也等于原负文字在T(v)下的值。若p不属于U，文字和赋值都未改变，等式仍成立。',
 r'每个文字都满足对应真值相等，析取与合取仅按输入真值运算，所以逐子句、逐合取得 $v(R_U(S))=T(v)(S)$。这说明变换后式的满足赋值正对应原式在翻转赋值下的满足赋值。',
 r'再注意 $T(T(v))=v$，故T是赋值集合上的双射。如果S有满足赋值w，取v=T(w)，则 $v(R_U(S))=w(S)=1$；反之R式有满足赋值v，则T(v)满足S。因此两式等可满足。',
 r'它们一般不等值：S=p、U仅含p时，变换得 $\neg p$。两式都可满足，却在每个同一赋值下真值相反；本题的双射联系的是不同赋值，不能省略翻转步骤。'
], [r'U按底层变项决定，正负文字要一起互补，不能只把正文字改成负文字。',r'对应赋值需要翻转，不能据此宣称同一赋值下两式等值。'], '逐正负文字核对后归纳到整式，并用自逆双射证明等可满足。')

if __name__ == '__main__':
    author.main()
