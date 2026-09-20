var S1 = `<!-- ===== 知识储备 ===== -->
<section class="block" id="knowledge" style="background:linear-gradient(180deg,#f3f5f8,var(--bg))">
  <div class="wrap">
    <div class="sec-head reveal">
      <span class="sec-tag">02 · KNOWLEDGE</span>
      <h2>知识储备：12 个核心知识点</h2>
      <p>动手写代码前，先把这 12 个知识点过一遍。它们正是本次实验报告思考题、也是后面答题网站的全部考点。</p>
    </div>
    <div class="grid-2">
      <!-- KP01 -->
      <div class="kp reveal">
        <div class="kp-head"><span class="kp-idx">KP 01</span><h3>程序基本结构与编译运行</h3></div>
        <p class="body">Java 程序以<b>类</b>为基本单位，<code class="inline">public class</code> 的名字必须与源文件名完全一致（区分大小写）；程序从固定写法的 <code class="inline">main</code> 方法开始执行。</p>
        <div class="build-flow">
          <div class="build-node">
            <div class="bn-ico"><svg width="26" height="26" viewBox="0 0 24 24" fill="none"><path d="M6 3h9l4 4v14H6z" stroke="currentColor" stroke-width="1.7" /><path d="M9 12h7M9 16h7M9 8h3" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" /></svg></div>
            <div class="bn-t">源文件</div><div class="bn-d">GradeCalculator.java<br>源代码文本</div>
          </div>
          <div class="build-arrow">→<span class="cmd">javac</span></div>
          <div class="build-node">
            <div class="bn-ico"><svg width="26" height="26" viewBox="0 0 24 24" fill="none"><path d="M8 6l-5 6 5 6M16 6l5 6-5 6" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" /></svg></div>
            <div class="bn-t">字节码</div><div class="bn-d">GradeCalculator.class<br>跨平台中间码</div>
          </div>
          <div class="build-arrow">→<span class="cmd">java</span></div>
          <div class="build-node">
            <div class="bn-ico"><svg width="26" height="26" viewBox="0 0 24 24" fill="none"><rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor" stroke-width="1.7" /><path d="M7 9l3 3-3 3M13 15h4" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" /></svg></div>
            <div class="bn-t">JVM 运行</div><div class="bn-d">解释执行字节码<br>控制台输入输出</div>
          </div>
        </div>
        <div class="console"><span class="dim"># 编译（生成 .class）</span>
<span class="prompt">javac GradeCalculator.java</span>
<span class="dim"># 运行（注意：不带 .class 后缀）</span>
<span class="prompt">java GradeCalculator</span></div>
        <div class="callout warn" style="margin-bottom:0">
          <svg viewBox="0 0 24 24" fill="none"><path d="M12 3 2 20h20L12 3z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" /><path d="M12 10v4M12 17h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" /></svg>
          常见低级错误：运行时写成 <code class="inline">java GradeCalculator.class</code>；文件名与 <code class="inline">public class</code> 名不一致；每条语句末尾漏掉分号 <code class="inline">;</code>。
        </div>
      </div>
      <!-- KP02 -->
      <div class="kp reveal">
        <div class="kp-head"><span class="kp-idx">KP 02</span><h3>变量与命名规范</h3></div>
        <p class="body">变量先声明、后使用：<code class="inline">类型 变量名 = 初始值;</code>。实验明确要求<b>变量名要有含义</b>，禁止用 a、b、c 这类无意义名字。</p>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>标识符规则（硬性）</th><th>命名惯例（可读性）</th></tr></thead>
            <tbody>
              <tr><td>字母、下划线 <code class="inline">_</code>、<code class="inline">$</code> 开头</td><td>变量 / 方法：小驼峰 <code class="inline">usualScore</code></td></tr>
              <tr><td>不能以数字开头（<code class="inline">2score</code> 非法）</td><td>类名：大驼峰 <code class="inline">GradeCalculator</code></td></tr>
              <tr><td>不能使用关键字（<code class="inline">final</code>、<code class="inline">int</code>）</td><td>常量：全大写 + 下划线 <code class="inline">EXAM_WEIGHT</code></td></tr>
              <tr><td>区分大小写、不能含空格</td><td>名字体现业务含义，能望文知义</td></tr>
            </tbody>
          </table>
        </div>
        <div class="callout tip" style="margin-bottom:0">
          <svg viewBox="0 0 24 24" fill="none"><path d="M5 12l4 4L19 7" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" /></svg>
          <code class="inline">usualScore / labScore / examScore / finalGrade</code> 一看就知道是「平时、实验、期末、总评」，这就是本实验要求的见名知意。
        </div>
      </div>
      <!-- KP03 -->
      <div class="kp reveal">
        <div class="kp-head"><span class="kp-idx">KP 03</span><h3>final 常量：权重必须定义为常量</h3></div>
        <p class="body">用 <code class="inline">final</code> 修饰的变量只能赋值一次，习惯写成 <code class="inline">static final</code> 类常量、名字全大写。任务书明确要求三个权重<b>必须定义为命名常量</b>，不能在算式里直接写 0.1、0.3、0.6（那叫「魔法数字」）。</p>
        <div class="code-card">
          <div class="code-bar"><span class="dots"><i></i><i></i><i></i></span><span class="fname">GradeCalculator.java</span><span class="tag">CONSTANTS</span></div>
<pre class="code" data-raw><span class="tok-kw">private</span> <span class="tok-kw">static</span> <span class="tok-kw">final</span> <span class="tok-type">double</span> USUAL_WEIGHT = <span class="tok-num">0.10</span>;  <span class="tok-com">// 平时 10%</span>
<span class="tok-kw">private</span> <span class="tok-kw">static</span> <span class="tok-kw">final</span> <span class="tok-type">double</span> LAB_WEIGHT   = <span class="tok-num">0.30</span>;  <span class="tok-com">// 实验 30%</span>
<span class="tok-kw">private</span> <span class="tok-kw">static</span> <span class="tok-kw">final</span> <span class="tok-type">double</span> EXAM_WEIGHT  = <span class="tok-num">0.60</span>;  <span class="tok-com">// 期末 60%</span></pre>
        </div>
        <p class="small">好处：① 语义清晰；② 权重调整时只改一处，不会漏改；③ 编译器阻止误修改。</p>
      </div>
      <!-- KP04 -->
      <div class="kp reveal">
        <div class="kp-head"><span class="kp-idx">KP 04</span><h3>基本数据类型与 String</h3></div>
        <p class="body">Java 有 8 种基本类型，本实验用到其中三种；注意 <code class="inline">String</code> 首字母大写，它是<b>类（引用类型）</b>，不是基本类型。</p>
        <div class="type-grid">
          <div class="type-cell"><div class="tname">int</div><div class="tdesc">整数：边长、周长</div></div>
          <div class="type-cell"><div class="tname">double</div><div class="tdesc">小数：成绩、面积</div></div>
          <div class="type-cell"><div class="tname">boolean</div><div class="tdesc">true / false：isRight</div></div>
          <div class="type-cell"><div class="tname">char</div><div class="tdesc">单个字符</div></div>
          <div class="type-cell"><div class="tname">byte</div><div class="tdesc">1 字节整数</div></div>
          <div class="type-cell"><div class="tname">short</div><div class="tdesc">短整数</div></div>
          <div class="type-cell"><div class="tname">long</div><div class="tdesc">长整数</div></div>
          <div class="type-cell"><div class="tname">float</div><div class="tdesc">单精度小数</div></div>
          <div class="type-cell ref" style="grid-column:1/-1"><div class="tname">String</div><div class="tdesc">引用类型（类）：姓名 name、学号 studentId、等级 level</div></div>
        </div>
      </div>
      <!-- KP05 -->
      <div class="kp reveal">
        <div class="kp-head"><span class="kp-idx">KP 05</span><h3>类型转换与整数除法陷阱</h3></div>
        <p class="body"><b>自动拓宽</b>：小类型 → 大类型自动完成，如 <code class="inline">int</code> 参与 <code class="inline">double</code> 运算时自动转成 double；<b>强制窄化</b>：<code class="inline">(int) 3.9</code> 直接截断小数得 3，可能丢精度。</p>
        <div class="callout warn">
          <svg viewBox="0 0 24 24" fill="none"><path d="M12 3 2 20h20L12 3z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" /><path d="M12 10v4M12 17h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" /></svg>
          <b>本实验最容易踩的坑：</b>两个 <code class="inline">int</code> 相除，结果仍是 int，小数部分被直接丢弃：<code class="inline">5 / 2 == 2</code>。海伦公式求半周长必须写 <code class="inline">perimeter / 2.0</code>，让运算在 double 下进行。
        </div>
        <div class="code-card">
          <div class="code-bar"><span class="dots"><i></i><i></i><i></i></span><span class="fname">TypeCast.java</span><span class="tag">DEMO</span></div>
<pre class="code" data-raw><span class="tok-type">int</span> perimeter = <span class="tok-num">12</span>;
<span class="tok-type">double</span> p1 = perimeter / <span class="tok-num">2</span>;      <span class="tok-com">// 6.0  —— 整数除法先得 6，再转 double</span>
<span class="tok-type">double</span> p2 = perimeter / <span class="tok-num">2.0</span>;    <span class="tok-com">// 6.0  —— 本题周长恰为偶数</span>
<span class="tok-com">// 换成奇数边，如周长 9：9/2 得 4（错），9/2.0 得 4.5（对）</span></pre>
        </div>
      </div>
      <!-- KP06 -->
      <div class="kp reveal">
        <div class="kp-head"><span class="kp-idx">KP 06</span><h3>运算符：算术 / 关系 / 逻辑 / 三元</h3></div>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>类别</th><th>运算符</th><th>本实验用途</th></tr></thead>
            <tbody>
              <tr><td>算术</td><td class="mono">+ - * / %</td><td>加权求和、平方、周长面积；<code class="inline">%</code> 取余</td></tr>
              <tr><td>关系</td><td class="mono">&lt; &gt; &lt;= &gt;= == !=</td><td>结果必为 boolean，用于成绩 / 边长比较</td></tr>
              <tr><td>逻辑</td><td class="mono">&amp;&amp;　||　!</td><td>组合多个条件</td></tr>
              <tr><td>三元</td><td class="mono">条件 ? a : b</td><td><code class="inline">isRight ? "是" : "否"</code></td></tr>
            </tbody>
          </table>
        </div>
        <div class="callout key" style="margin-bottom:0">
          <svg viewBox="0 0 24 24" fill="none"><path d="M12 2v4M12 18v4M2 12h4M18 12h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" /><circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.8" /></svg>
          <b>短路特性：</b><code class="inline">&amp;&amp;</code> 左边为 false 时右边不再计算；<code class="inline">||</code> 左边为 true 时右边不再计算。多条件合法性判断正是靠 <code class="inline">||</code> 串起来：<b>任意一项</b>越界即非法。
        </div>
      </div>
      <!-- KP07 -->
      <div class="kp reveal">
        <div class="kp-head"><span class="kp-idx">KP 07</span><h3>Scanner 键盘输入</h3></div>
        <p class="body"><code class="inline">Scanner</code> 是 <code class="inline">java.util</code> 包下的输入类，三步使用：<b>导入 → 创建 → 读取</b>，用完 <code class="inline">close()</code>。</p>
        <div class="code-card">
          <div class="code-bar"><span class="dots"><i></i><i></i><i></i></span><span class="fname">Scanner 用法</span><span class="tag">INPUT</span></div>
<pre class="code" data-raw><span class="tok-kw">import</span> java.util.Scanner;          <span class="tok-com">// ① 导入</span>
<span class="tok-type">Scanner</span> scanner = <span class="tok-kw">new</span> <span class="tok-type">Scanner</span>(<span class="tok-type">System</span>.in);  <span class="tok-com">// ② 创建</span>
<span class="tok-type">String</span> name  = scanner.nextLine();    <span class="tok-com">// ③ 读取一整行（姓名、学号）</span>
<span class="tok-type">double</span> score = scanner.nextDouble();  <span class="tok-com">//    读取一个小数（成绩）</span>
<span class="tok-type">int</span> side    = scanner.nextInt();     <span class="tok-com">//    读取一个整数（边长）</span>
scanner.close();                      <span class="tok-com">// ④ 关闭</span></pre>
        </div>
        <div class="callout note" style="margin-bottom:0">
          <svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.8" /><path d="M12 11v5M12 8h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" /></svg>
          <b>混用陷阱：</b><code class="inline">nextInt()/nextDouble()</code> 只取走数字、留下行尾的换行符，紧接着的 <code class="inline">nextLine()</code> 会读到空串。本实验把字符串（姓名学号）放在最前面读取，规避了该问题；若顺序相反，需额外调用一次 <code class="inline">nextLine()</code> 消耗换行。
        </div>
      </div>
      <!-- KP08 -->
      <div class="kp reveal">
        <div class="kp-head"><span class="kp-idx">KP 08</span><h3>printf 格式化输出</h3></div>
        <p class="body">任务要求总评与面积<b>保留两位小数</b>，靠 <code class="inline">System.out.printf</code> 实现；<code class="inline">print</code> 不换行、<code class="inline">println</code> 换行、<code class="inline">printf</code> 按格式串输出。</p>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>格式符</th><th>含义</th><th>示例输出</th></tr></thead>
            <tbody>
              <tr><td class="mono">%.2f</td><td>浮点数保留两位小数</td><td class="mono">87.30</td></tr>
              <tr><td class="mono">%d</td><td>整数</td><td class="mono">12</td></tr>
              <tr><td class="mono">%s</td><td>字符串</td><td class="mono">良好</td></tr>
              <tr><td class="mono">%n</td><td>跨平台换行符</td><td class="mono">↵</td></tr>
              <tr><td class="mono">%%</td><td>输出一个百分号</td><td class="mono">%</td></tr>
            </tbody>
          </table>
        </div>
        <div class="code-card" style="margin-bottom:0">
          <div class="code-bar"><span class="dots"><i></i><i></i><i></i></span><span class="fname">格式串与参数一一对应</span><span class="tag">PRINTF</span></div>
<pre class="code" data-raw><span class="tok-type">System</span>.out.printf(<span class="tok-str">"总评成绩：%.2f，等级：%s%n"</span>, finalGrade, level);
<span class="tok-com">//            格式符 %.2f 对应 finalGrade，%s 对应 level</span></pre>
        </div>
      </div>
      <!-- KP09 -->
      <div class="kp reveal">
        <div class="kp-head"><span class="kp-idx">KP 09</span><h3>选择结构：if 家族与 switch</h3></div>
        <p class="body"><code class="inline">if</code> 条件必须是 boolean 表达式。本实验用到三种形态：单分支（非法即结束）、双分支、多分支链。</p>
        <div class="code-card" style="margin-bottom:12px">
          <div class="code-bar"><span class="dots"><i></i><i></i><i></i></span><span class="fname">Level.java</span><span class="tag">IF-ELSE IF</span></div>
<pre class="code" data-raw><span class="tok-kw">if</span> (finalGrade &gt;= <span class="tok-num">90</span>)      level = <span class="tok-str">"优秀"</span>;   <span class="tok-com">// 从高到低</span>
<span class="tok-kw">else if</span> (finalGrade &gt;= <span class="tok-num">80</span>) level = <span class="tok-str">"良好"</span>;
<span class="tok-kw">else if</span> (finalGrade &gt;= <span class="tok-num">70</span>) level = <span class="tok-str">"中等"</span>;
<span class="tok-kw">else if</span> (finalGrade &gt;= <span class="tok-num">60</span>) level = <span class="tok-str">"及格"</span>;
<span class="tok-kw">else</span>                    level = <span class="tok-str">"不及格"</span>; <span class="tok-com">// 兜底</span></pre>
        </div>
        <div class="callout warn" style="margin-bottom:12px">
          <svg viewBox="0 0 24 24" fill="none"><path d="M12 3 2 20h20L12 3z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" /><path d="M12 10v4M12 17h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" /></svg>
          分支必须<b>从高分到低分</b>排列。若先写 <code class="inline">&gt;=60</code>，90 分也会先命中「及格」，等级直接判错。
        </div>
        <p class="small">补充：<code class="inline">switch</code> 适合「表达式等于若干离散值」的多分支（支持 byte/short/int/char/String/枚举，不支持 double、boolean）；else 总与最近的未配对 if 结合，嵌套时建议加大括号。</p>
      </div>
      <!-- KP10 -->
      <div class="kp reveal">
        <div class="kp-head"><span class="kp-idx">KP 10</span><h3>逻辑表达式与判断顺序</h3></div>
        <p class="body">任务二有五级判断，顺序是程序正确性的核心——<b>先保证数据合法，再谈分类与计算</b>。</p>
        <div class="flow">
          <div class="step"><div class="sn">STEP 1</div><div class="st">范围校验</div><div class="sd">三边是否都在 1~1000</div></div>
          <div class="arrow"><svg viewBox="0 0 24 24" fill="none"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" /></svg></div>
          <div class="step"><div class="sn">STEP 2</div><div class="st">构成判断</div><div class="sd">任意两边之和大于第三边</div></div>
          <div class="arrow"><svg viewBox="0 0 24 24" fill="none"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" /></svg></div>
          <div class="step"><div class="sn">STEP 3</div><div class="st">类型分类</div><div class="sd">等边 → 等腰 → 不等边</div></div>
        </div>
        <div class="flow" style="margin-top:0">
          <div class="step"><div class="sn">STEP 4</div><div class="st">直角判定</div><div class="sd">比较三组平方关系</div></div>
          <div class="arrow"><svg viewBox="0 0 24 24" fill="none"><path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" /></svg></div>
          <div class="step"><div class="sn">STEP 5</div><div class="st">周长面积</div><div class="sd">海伦公式，double 存储</div></div>
          <div class="arrow" style="visibility:hidden"><svg viewBox="0 0 24 24"><path d="M5 12h14" stroke="currentColor" stroke-width="2.2" /></svg></div>
          <div class="step" style="background:var(--brand-soft);border-color:#f3cdb0"><div class="sn">OUTPUT</div><div class="st">格式化输出</div><div class="sd">面积保留两位小数</div></div>
        </div>
      </div>
      <!-- KP11 -->
      <div class="kp reveal">
        <div class="kp-head"><span class="kp-idx">KP 11</span><h3>Math 类与海伦公式</h3></div>
        <p class="body"><code class="inline">Math</code> 是 java.lang 下的数学工具类，无需 import，方法均为静态，直接 <code class="inline">Math.方法名()</code> 调用。</p>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>常用成员</th><th>作用</th></tr></thead>
            <tbody>
              <tr><td class="mono">Math.sqrt(x)</td><td>平方根；x 为负数时返回 <code class="inline">NaN</code>（不是报错！）</td></tr>
              <tr><td class="mono">Math.pow(a,b)</td><td>a 的 b 次方（本题直接用 a*a 求平方）</td></tr>
              <tr><td class="mono">Math.PI</td><td>圆周率常量</td></tr>
              <tr><td class="mono">Math.abs / max / min</td><td>绝对值 / 最大 / 最小</td></tr>
            </tbody>
          </table>
        </div>
        <div class="formula"><span class="cm">// 海伦公式（Heron's formula）</span>
p = (a + b + c) / <span class="op">2.0</span>
S = <span class="op">√</span>( p · (p−a) · (p−b) · (p−c) )</div>
        <p class="small" style="margin-bottom:0">这也是必须先做构成判断的原因：若三边不能构成三角形，根号内的乘积可能为负，<code class="inline">Math.sqrt</code> 会悄悄返回 <code class="inline">NaN</code> 而不是提醒你。</p>
      </div>
      <!-- KP12 -->
      <div class="kp reveal" style="grid-column:1/-1">
        <div class="kp-head"><span class="kp-idx">KP 12</span><h3>== 与 equals：字符串比较（思考题考点）</h3></div>
        <div class="grid-2" style="align-items:start">
          <div>
            <p class="body">对<b>基本类型</b>，<code class="inline">==</code> 比较数值；对<b>引用类型</b>（如 String），<code class="inline">==</code> 比较的是两个引用是否指向<b>同一个对象（内存地址）</b>，而 <code class="inline">equals</code> 才是比较字符串的<b>字符内容</b>。</p>
            <div class="code-card" style="margin-bottom:0">
              <div class="code-bar"><span class="dots"><i></i><i></i><i></i></span><span class="fname">StringCompare.java</span><span class="tag">STRING</span></div>
<pre class="code" data-raw><span class="tok-type">String</span> s1 = <span class="tok-kw">new</span> <span class="tok-type">String</span>(<span class="tok-str">"abc"</span>);
<span class="tok-type">String</span> s2 = <span class="tok-kw">new</span> <span class="tok-type">String</span>(<span class="tok-str">"abc"</span>);
s1 == s2        <span class="tok-com">// false：两个不同对象，地址不同</span>
s1.equals(s2)   <span class="tok-com">// true ：内容都是 abc</span>
s1.equalsIgnoreCase(<span class="tok-str">"ABC"</span>); <span class="tok-com">// true：忽略大小写比内容</span></pre>
            </div>
          </div>
          <div>
            <div class="tbl-wrap" style="margin-top:0">
              <table>
                <thead><tr><th>写法</th><th>比较的是</th><th>适用</th></tr></thead>
                <tbody>
                  <tr><td class="mono">==</td><td>基本类型比值；引用类型比地址</td><td>int/double/boolean</td></tr>
                  <tr><td class="mono">equals()</td><td>字符串字符内容</td><td><b>String 内容比较</b></td></tr>
                  <tr><td class="mono">equalsIgnoreCase()</td><td>内容（忽略大小写）</td><td>验证码等场景</td></tr>
                </tbody>
              </table>
            </div>
            <div class="callout key" style="margin-bottom:0">
              <svg viewBox="0 0 24 24" fill="none"><path d="M12 2v4M12 18v4M2 12h4M18 12h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" /><circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.8" /></svg>
              结论：判断字符串内容<b>永远用 equals 系列</b>。即使 <code class="inline">"abc" == "abc"</code> 因字符串常量池偶尔为 true，也绝不能依赖它——<code class="inline">new</code> 出来的对象立刻现出原形。
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
<!-- ===== 任务一 ===== -->
<section class="block" id="task1">
  <div class="wrap">
    <div class="sec-head reveal">
      <span class="sec-tag">03 · TASK ONE</span>
      <h2>任务一精讲：GradeCalculator 成绩计算器</h2>
      <p>需求 → 流程 → 逐段代码 → 测试用例 → 在线实验台，五步把这个程序讲透。</p>
    </div>
    <div class="card reveal">
      <h3 class="t-h"><span class="n">1</span>需求拆解（对照任务书逐条落实）</h3>
      <div class="grid-3" style="gap:12px">
        <ul class="tick" style="margin:0">
          <li>创建类 <code class="inline">GradeCalculator</code></li>
          <li>输入姓名、学号（字符串）</li>
          <li>输入平时、实验、期末三项成绩</li>
        </ul>
        <ul class="tick" style="margin:0">
          <li>权重 10% / 30% / 60% 定义为<b>命名常量</b></li>
          <li>任一成绩超出 0~100：输出「输入成绩不合法」且<b>不再计算</b></li>
          <li>变量名有含义，禁止 a/b/c</li>
        </ul>
        <ul class="tick" style="margin:0">
          <li>显示姓名、学号、三项原始成绩与总评</li>
          <li>总评成绩<b>保留两位小数</b></li>
          <li>（选做）按分数段输出等级</li>
        </ul>
      </div>
    </div>
    <div class="card reveal" style="margin-top:20px">
      <h3 class="t-h"><span class="n">2</span>加权公式（权重即常量）</h3>
      <div class="weight-bars">
        <div class="wbar"><span class="wl">平时表现</span><div class="wt"><div class="wf" style="width:10%;background:#e8a55c">10%</div></div><span class="wv">× 0.10</span></div>
        <div class="wbar"><span class="wl">实验成绩</span><div class="wt"><div class="wf" style="width:30%;background:#e26a1c">30%</div></div><span class="wv">× 0.30</span></div>
        <div class="wbar"><span class="wl">期末考试</span><div class="wt"><div class="wf" style="width:60%;background:#b8530f">60%</div></div><span class="wv">× 0.60</span></div>
      </div>
      <div class="formula">finalGrade = usualScore × <span class="op">0.10</span> + labScore × <span class="op">0.30</span> + examScore × <span class="op">0.60</span>
<span class="cm"># 例：90×0.1 + 85×0.3 + 88×0.6 = 9.0 + 25.5 + 52.8 = 87.30 → 良好</span></div>
    </div>
    <h3 class="t-h reveal" style="margin-top:34px"><span class="n">3</span>逐段代码讲解</h3>
    <div class="code-explain reveal">
      <div class="code-card" style="margin:0">
        <div class="code-bar"><span class="dots"><i></i><i></i><i></i></span><span class="fname">GradeCalculator.java</span><span class="tag">① 导入·类·常量</span></div>
<pre class="code" data-raw><span class="tok-kw">import</span> java.util.Scanner;
<span class="tok-kw">public</span> <span class="tok-kw">class</span> <span class="tok-type">GradeCalculator</span> {
    <span class="tok-com">// 权重命名常量</span>
    <span class="tok-kw">private</span> <span class="tok-kw">static</span> <span class="tok-kw">final</span> <span class="tok-type">double</span> USUAL_WEIGHT = <span class="tok-num">0.10</span>;
    <span class="tok-kw">private</span> <span class="tok-kw">static</span> <span class="tok-kw">final</span> <span class="tok-type">double</span> LAB_WEIGHT   = <span class="tok-num">0.30</span>;
    <span class="tok-kw">private</span> <span class="tok-kw">static</span> <span class="tok-kw">final</span> <span class="tok-type">double</span> EXAM_WEIGHT  = <span class="tok-num">0.60</span>;</pre>
      </div>
      <div class="notes">
        <h4>这段在做什么</h4>
        <p><code class="inline">import</code> 把 Scanner 引入当前文件；类名与文件名一致。</p>
        <p>三个权重写成 <code class="inline">private static final</code> 类常量，全大写下划线命名——任务书的硬性要求，杜绝魔法数字。</p>
      </div>
    </div>
    <div class="code-explain reveal">
      <div class="code-card" style="margin:0">
        <div class="code-bar"><span class="dots"><i></i><i></i><i></i></span><span class="fname">GradeCalculator.java</span><span class="tag">② main·输入</span></div>
<pre class="code" data-raw>    <span class="tok-kw">public</span> <span class="tok-kw">static</span> <span class="tok-kw">void</span> <span class="tok-type">main</span>(<span class="tok-type">String</span>[] args) {
        <span class="tok-type">Scanner</span> scanner = <span class="tok-kw">new</span> <span class="tok-type">Scanner</span>(<span class="tok-type">System</span>.in);
        <span class="tok-type">System</span>.out.print(<span class="tok-str">"请输入姓名："</span>);
        <span class="tok-type">String</span> name = scanner.nextLine();
        <span class="tok-type">System</span>.out.print(<span class="tok-str">"请输入学号："</span>);
        <span class="tok-type">String</span> studentId = scanner.nextLine();
        <span class="tok-type">System</span>.out.print(<span class="tok-str">"请输入平时表现成绩(0~100)："</span>);
        <span class="tok-type">double</span> usualScore = scanner.nextDouble();
        <span class="tok-type">System</span>.out.print(<span class="tok-str">"请输入实验成绩(0~100)："</span>);
        <span class="tok-type">double</span> labScore = scanner.nextDouble();
        <span class="tok-type">System</span>.out.print(<span class="tok-str">"请输入期末考试成绩(0~100)："</span>);
        <span class="tok-type">double</span> examScore = scanner.nextDouble();</pre>
      </div>
      <div class="notes">
        <h4>这段在做什么</h4>
        <p>提示语用 <code class="inline">print</code>（不换行），让光标停在冒号后等待输入，符合控制台交互习惯。</p>
        <p>姓名、学号用 <code class="inline">nextLine()</code> 读整行；三项成绩可能有小数，用 <code class="inline">double</code> + <code class="inline">nextDouble()</code>。</p>
        <p>字符串输入排在数值输入之前，避开换行残留陷阱。</p>
      </div>
    </div>
    <div class="code-explain reveal">
      <div class="code-card" style="margin:0">
        <div class="code-bar"><span class="dots"><i></i><i></i><i></i></span><span class="fname">GradeCalculator.java</span><span class="tag">③ 合法性校验</span></div>
<pre class="code" data-raw>        <span class="tok-com">// 数据有效性判断：任意一项超出0~100，不再计算总评</span>
        <span class="tok-kw">if</span> (usualScore &lt; <span class="tok-num">0</span> || usualScore &gt; <span class="tok-num">100</span>
                || labScore &lt; <span class="tok-num">0</span> || labScore &gt; <span class="tok-num">100</span>
                || examScore &lt; <span class="tok-num">0</span> || examScore &gt; <span class="tok-num">100</span>) {
            <span class="tok-type">System</span>.out.println(<span class="tok-str">"输入成绩不合法"</span>);
            <span class="tok-kw">return</span>;
        }</pre>
      </div>
      <div class="notes">
        <h4>这段在做什么</h4>
        <p>六个关系表达式用 <code class="inline">||</code> 连接：<b>只要有一项</b>小于 0 或大于 100，条件即成立。</p>
        <p>边界 0 和 100 本身合法（用的是 <code class="inline">&lt;0</code>、<code class="inline">&gt;100</code>）。</p>
        <p><code class="inline">return</code> 直接结束 main 方法，后面的计算与输出一律不执行——精确对应任务书「不再计算」。</p>
      </div>
    </div>
    <div class="code-explain reveal">
      <div class="code-card" style="margin:0">
        <div class="code-bar"><span class="dots"><i></i><i></i><i></i></span><span class="fname">GradeCalculator.java</span><span class="tag">④ 计算·等级·输出</span></div>
<pre class="code" data-raw>        <span class="tok-com">// 按权重计算总评成绩</span>
        <span class="tok-type">double</span> finalGrade = usualScore * USUAL_WEIGHT
                + labScore * LAB_WEIGHT
                + examScore * EXAM_WEIGHT;
        <span class="tok-type">String</span> level;
        <span class="tok-kw">if</span> (finalGrade &gt;= <span class="tok-num">90</span>)      level = <span class="tok-str">"优秀"</span>;
        <span class="tok-kw">else if</span> (finalGrade &gt;= <span class="tok-num">80</span>) level = <span class="tok-str">"良好"</span>;
        <span class="tok-kw">else if</span> (finalGrade &gt;= <span class="tok-num">70</span>) level = <span class="tok-str">"中等"</span>;
        <span class="tok-kw">else if</span> (finalGrade &gt;= <span class="tok-num">60</span>) level = <span class="tok-str">"及格"</span>;
        <span class="tok-kw">else</span>                    level = <span class="tok-str">"不及格"</span>;
        <span class="tok-type">System</span>.out.println(<span class="tok-str">"姓名："</span> + name);
        <span class="tok-type">System</span>.out.println(<span class="tok-str">"学号："</span> + studentId);
        <span class="tok-type">System</span>.out.printf(<span class="tok-str">"平时成绩：%.2f，实验成绩：%.2f，"</span>
                + <span class="tok-str">"期末成绩：%.2f%n"</span>, usualScore, labScore, examScore);
        <span class="tok-type">System</span>.out.printf(<span class="tok-str">"总评成绩：%.2f，等级：%s%n"</span>,
                finalGrade, level);
        scanner.close();
    }
}</pre>
      </div>
      <div class="notes">
        <h4>这段在做什么</h4>
        <p>加权求和时常量名即文档，算式读起来像公式本身。</p>
        <p>等级链从 90 分向下兜底，<code class="inline">else</code> 处理不及格，无遗漏。</p>
        <p><code class="inline">printf</code> 的 <code class="inline">%.2f</code> 保证两位小数，<code class="inline">%s</code> 填等级，<code class="inline">%n</code> 换行；最后关闭 Scanner。</p>
      </div>
    </div>
    <div class="card reveal">
      <h3 class="t-h"><span class="n">4</span>测试记录（真实运行结果）</h3>
      <div class="tbl-wrap">
        <table>
          <thead><tr><th>用例</th><th class="mono">平时</th><th class="mono">实验</th><th class="mono">期末</th><th>实际输出</th><th>结论</th></tr></thead>
          <tbody>
            <tr><td>常规混合</td><td class="mono">90</td><td class="mono">85</td><td class="mono">88</td><td class="mono">总评 87.30，良好</td><td><span class="pass">通过</span></td></tr>
            <tr><td>满分边界</td><td class="mono">100</td><td class="mono">100</td><td class="mono">100</td><td class="mono">总评 100.00，优秀</td><td><span class="pass">通过</span></td></tr>
            <tr><td>零分边界</td><td class="mono">0</td><td class="mono">0</td><td class="mono">0</td><td class="mono">总评 0.00，不及格</td><td><span class="pass">通过</span></td></tr>
            <tr><td>上限越界</td><td class="mono">120</td><td class="mono">85</td><td class="mono">88</td><td class="mono">输入成绩不合法</td><td><span class="pass">通过</span></td></tr>
            <tr><td>负值越界</td><td class="mono">90</td><td class="mono">-5</td><td class="mono">88</td><td class="mono">输入成绩不合法</td><td><span class="pass">通过</span></td></tr>
          </tbody>
        </table>
      </div>
    </div>
    <!-- 在线实验台 1 -->
    <div class="lab reveal" id="lab1">
      <div class="lab-title">在线实验台 · GradeCalculator <span class="live"><i></i>LIVE</span></div>
      <div class="lab-desc">下面是用 JavaScript 复刻的同款逻辑，输入任意数据点「运行」，输出与 Java 程序逐字一致；也可点快捷用例一键填充。</div>
      <div class="lab-grid">
        <div class="lab-form">
          <div class="field-row">
            <div class="field"><label>姓名</label><input id="g-name" type="text" value="张三"></div>
            <div class="field" style="grid-column:span 2"><label>学号</label><input id="g-id" type="text" value="2024001"></div>
          </div>
          <div class="field-row">
            <div class="field"><label>平时成绩 (10%)</label><input id="g-usual" type="number" value="90"></div>
            <div class="field"><label>实验成绩 (30%)</label><input id="g-lab" type="number" value="85"></div>
            <div class="field"><label>期末成绩 (60%)</label><input id="g-exam" type="number" value="88"></div>
          </div>
          <div class="lab-actions">
            <button class="lab-btn run" onclick="runGrade()">运行程序</button>
            <button class="lab-btn" onclick="document.getElementById('g-out').textContent='等待输入…'">清空控制台</button>
          </div>
          <div class="quick">
            <div class="ql">QUICK TEST CASES</div>
            <button onclick="fillGrade('张三','2024001',90,85,88)">90/85/88</button>
            <button onclick="fillGrade('李四','2024002',100,100,100)">100 满分</button>
            <button onclick="fillGrade('王五','2024003',0,0,0)">0 零分</button>
            <button onclick="fillGrade('赵六','2024004',120,85,88)">120 越界</button>
            <button onclick="fillGrade('孙七','2024005',90,-5,88)">-5 负值</button>
          </div>
        </div>
        <div class="lab-out" id="g-out"><span class="ph">点击「运行程序」查看输出…</span></div>
      </div>
    </div>
  </div>
</section>
`;
