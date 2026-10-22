"""Retain the twelve earlier detailed solutions; add question-specific pitfalls."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
TIPS={
 'SRC-DM2T-E001-002':[r'“刘红与魏欣是同学”是一个关系命题，“与”连接人名，不能拆成两命题合取。',r'圆面积中的平方、乘法是数值运算，不是命题联结词；符号须代表整句。'],
 'SRC-DM2T-E001-003':[r'否定“√25不是无理数”要取消这层“不是”，所得“是无理数”为假。',r'ln1=0且0是整数；“整数”不能误读成“正整数”。'],
 'SRC-DM2T-E001-004':[r'“3是偶素数”同时要求偶数与素数，只有素数为真仍使合取为假。',r'“4既不是素数也不是偶数”为两个否定的合取，不能写成对“素数且偶数”的整体否定。'],
 'SRC-DM2T-E001-005':[r'“2或4是偶数”允许两项同真，本题相容析取为真，不是排他或。',r'最后一问“3不是素数”和“4不是偶数”都假，析取才为假；要先判断原句再各自取反。'],
 'SRC-LA7-E001-001':[r'第（1）问要减去反向乘积和−12，得到−16−(−12)=−4。',r'第（3）差积改变方向须同时计算符号；第（4）的混合立方项恰好相消，不可漏掉最后的系数−2。',r'对角线法则只用于本题三阶式，不能照搬到四阶。'],
 'SRC-LA7-E001-002':[r'逆序按前大后小的数对计数，不是看有几个元素不在原位。',r'第（6）除奇数段与偶数段之间的逆序外，还要加偶数递减段内部的n(n−1)/2，不能沿用第（5）答案。'],
 'SRC-LA7-E001-003':[r'第3列已由a₂₃使用，第三、四行只能配剩下第2、4列，不能再选a₃₃。',r'1324有1个逆序，1342有2个逆序，因此两个允许项符号分别负、正，不是都正。'],
 'SRC-PS3-E001-001':[r'样本号码仅1至50，事件“一位数”不能加入盒里没有的0。',r'“不超过20”包括20；3的倍数到48止，51已超出样本空间。'],
 'SRC-PS3-E001-002':[r'两次抛硬币区分先后，（正，反）与（反，正）是不同样本点。',r'呼叫次数包括0且是整数；灯泡寿命是非负实数，不能把两种样本空间混成同一类。',r'寿命“之间”的开闭端点要说明；集合可不同，即使连续模型中的概率相同。'],
 'SRC-PS3-E001-003':[r'“至少一个正面”包括两、三个正面；“不多于一个”还包括全反。',r'三枚硬币先编号，用8个有序三位串，不能把一正二反的三种位置合并成一个样本点。'],
 'SRC-PS3-E001-004':[r'有放回时同色对子都可能；不放回且每色只有1珠时，三个同色对子全部必须删除。',r'“两次没有白珠”要求两次都不白，只排除一次白不够；“有红”则允许红红。'],
 'SRC-PS3-E002-001':[r'交事件AC的补是补A与补C的并，含8个号码；补A交补C只有{5,7,9}，两问不同。',r'C为号码小于5，不含5；A−C是从偶数集中删2、4，不是数值相减。']
}

def main():
    old=set(json.loads((ROOT/'data/detailed-solutions-audit-v33.json').read_text())['complete'])
    assert set(TIPS)==old
    for book in ['DM2T','LA7','PS3']:
        p=ROOT/'data'/f'exercises-{book}-v20.json';doc=json.loads(p.read_text())
        for q in doc['items']:
            if q['id'] not in TIPS:continue
            q['common_mistakes']=TIPS[q['id']]
            q['common_mistakes_basis']={'status':'question_specific','question_id':q['id'],'individual_derivation_verified':True,'derivation_review_source':'detailed-solutions-audit-v33.json'}
        p.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
