var S2 = `
<!-- ===== 任务二 ===== -->
<section class="block" id="task2" style="background:linear-gradient(180deg,#f3f5f8,var(--bg))">
  <div class="wrap">
    <div class="sec-head reveal">
      <span class="sec-tag">04 · TASK TWO</span>
      <h2>任务二精讲：TriangleAnalyzer 三角形分析器</h2>
      <p>这是选择结构的综合训练：五级判断环环相扣，<b>判断顺序错一层，结果就全错</b>。先看需求，再看判定流水线，然后逐段过代码。</p>
    </div>

    <div class="card reveal">
      <h3 class="t-h"><span class="n">1</span>需求拆解</h3>
      <div class="grid-3" style="gap:12px">
        <ul class="tick" style="margin:0">
          <li>创建类 <code class="inline">TriangleAnalyzer</code></li>
          <li>键盘输入三条边长（整数）</li>
          <li>边长范围必须在 <code class="inline">1~1000</code></li>
        </ul>
        <ul class="tick" style="margin:0">
          <li>判断能否构成三角形（含退化情形）</li>
          <li>分类：等边 / 等腰 / 不等边</li>
          <li>判断是否为直角三角形</li>
        </ul>
        <ul class="tick" style="margin:0">
          <li>计算周长（int）与面积（海伦公式）</li>
          <li>面积用 <code class="inline">%.2f</code> 保留两位小数</li>
          <li>每一道非法校验都要立即结束</li>
        </ul>
      </div>
    </div>

    <h3 class="t-h reveal" style="margin-top:34px"><span class="n">2</span>五级判定流水线（本程序的灵魂）</h3>
    <div class="pipeline reveal">
      <div class="pl-row">
        <div class="pl-gate"><div class="gname">闸门 1 · 范围</div><div class="gcode">1 &lt;= side &lt;= 1000</div></div>
        <div class="pl-body">三边是否都是 <b>1~1000</b> 的正整数。任一越界 → 打印 <code class="inline">输入边长不合法，边长应为1~1000</code> 并 <code class="inline">return</code>。<span class="no">0、负数、1001 在这里被拦下。</span></div>
      </div>
      <div class="pl-row">
        <div class="pl-gate"><div class="gname">闸门 2 · 构成</div><div class="gcode">a+b&gt;c &amp;&amp; a+c&gt;b &amp;&amp; b+c&gt;a</div></div>
        <div class="pl-body">三角形不等式，必须是<b>严格大于</b>。用否定形式书写：<code class="inline">a+b&lt;=c || a+c&lt;=b || b+c&lt;=a</code> 即不能构成。<span class="no">等号对应退化三角形（三点共线），如 1、2、3。</span></div>
      </div>
      <div class="pl-row">
        <div class="pl-gate"><div class="gname">闸门 3 · 类型</div><div class="gcode">等边 → 等腰 → 不等边</div></div>
        <div class="pl-body">先判三边全等（等边），再判两边相等（等腰），最后兜底不等边。<span class="yes">顺序不能反：等边也满足“两边相等”。</span></div>
      </div>
      <div class="pl-row">
        <div class="pl-gate"><div class="gname">闸门 4 · 直角</div><div class="gcode">a²+b²==c² 三种组合</div></div>
        <div class="pl-body">事先不知道哪条是斜边，三组平方关系<b>都要检查</b>，任一成立即为直角，结果存入 <code class="inline">boolean isRight</code>。</div>
      </div>
      <div class="pl-row">
        <div class="pl-gate"><div class="gname">闸门 5 · 计算</div><div class="gcode">周长 int / 半周长 2.0 / 海伦 double</div></div>
        <div class="pl-body">周长是整数；半周长必须 <code class="inline">perimeter / 2.0</code>；面积 <code class="inline">Math.sqrt(p*(p-a)*(p-b)*(p-c))</code>，两位小数输出。</div>
      </div>
    </div>
    <div class="callout key reveal">
      <svg viewBox="0 0 24 24" fill="none"><path d="M12 2v4M12 18v4M2 12h4M18 12h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.8"/></svg>
      <b>为什么是这个顺序？</b>范围不合法的数据若进入构成判断，0、负数会产生荒谬结论；不能构成三角形的三边若进入海伦公式，根号内可能为负，<code class="inline">Math.sqrt</code> 会返回 <code class="inline">NaN</code> 而不报错。<b>先保证数据有效，再分类，最后计算</b>——这叫「卫语句（guard clause）」写法。
    </div>

    <h3 class="t-h reveal" style="margin-top:34px"><span class="n">3</span>逐段代码讲解</h3>
    <div class="code-explain reveal">
      <div class="code-card" style="margin:0">
        <div class="code-bar"><span class="dots"><i></i><i></i><i></i></span><span class="fname">TriangleAnalyzer.java</span><span class="tag">① 导入·类·常量</span></div>
<pre class="code" data-raw><span class="tok-kw">import</span> java.util.Scanner;
<span class="tok-kw">public</span> <span class="tok-kw">class</span> <span class="tok-type">TriangleAnalyzer</span> {
    <span class="tok-com">// 边长范围命名常量，杜绝魔法数字</span>
    <span class="tok-kw">private</span> <span class="tok-kw">static</span> <span class="tok-kw">final</span> <span class="tok-type">int</span> MIN_SIDE = <span class="tok-num">1</span>;
    <span class="tok-kw">private</span> <span class="tok-kw">static</span> <span class="tok-kw">final</span> <span class="tok-type">int</span> MAX_SIDE = <span class="tok-num">1000</span>;</pre>
      </div>
      <div class="notes">
        <h4>这段在做什么</h4>
        <p>上下限也抽成命名常量，与任务一的权重常量同一套规范。</p>
        <p>边长只可能是整数，用 <code class="inline">int</code>；面积含小数，用 <code class="inline">double</code>。</p>
      </div>
    </div>
    <div class="code-explain reveal">
      <div class="code-card" style="margin:0">
        <div class="code-bar"><span class="dots"><i></i><i></i><i></i></span><span class="fname">TriangleAnalyzer.java</span><span class="tag">② 输入·闸门1</span></div>
<pre class="code" data-raw>    <span class="tok-kw">public</span> <span class="tok-kw">static</span> <span class="tok-kw">void</span> <span class="tok-type">main</span>(<span class="tok-type">String</span>[] args) {
        <span class="tok-type">Scanner</span> scanner = <span class="tok-kw">new</span> <span class="tok-type">Scanner</span>(<span class="tok-type">System</span>.in);
        <span class="tok-type">System</span>.out.print(<span class="tok-str">"请输入第一条边长："</span>);
        <span class="tok-type">int</span> a = scanner.nextInt();
        <span class="tok-type">System</span>.out.print(<span class="tok-str">"请输入第二条边长："</span>);
        <span class="tok-type">int</span> b = scanner.nextInt();
        <span class="tok-type">System</span>.out.print(<span class="tok-str">"请输入第三条边长："</span>);
        <span class="tok-type">int</span> c = scanner.nextInt();
        <span class="tok-com">// 闸门1：范围校验</span>
        <span class="tok-kw">if</span> (a &lt; MIN_SIDE || a &gt; MAX_SIDE
                || b &lt; MIN_SIDE || b &gt; MAX_SIDE
                || c &lt; MIN_SIDE || c &gt; MAX_SIDE) {
            <span class="tok-type">System</span>.out.println(<span class="tok-str">"输入边长不合法，边长应为1~1000"</span>);
            <span class="tok-kw">return</span>;
        }</pre>
      </div>
      <div class="notes">
        <h4>这段在做什么</h4>
        <p>三个 <code class="inline">nextInt()</code> 连续读取整数，不存在换行残留问题（没有混用 nextLine）。</p>
        <p>六个比较用 <code class="inline">||</code> 串联，<b>任意一边</b>越界即非法并立即结束。</p>
      </div>
    </div>
    <div class="code-explain reveal">
      <div class="code-card" style="margin:0">
        <div class="code-bar"><span class="dots"><i></i><i></i><i></i></span><span class="fname">TriangleAnalyzer.java</span><span class="tag">③ 闸门2·闸门3</span></div>
<pre class="code" data-raw>        <span class="tok-com">// 闸门2：构成判断（&lt;= 含退化三角形）</span>
        <span class="tok-kw">if</span> (a + b &lt;= c || a + c &lt;= b || b + c &lt;= a) {
            <span class="tok-type">System</span>.out.println(<span class="tok-str">"三条边不能构成三角形"</span>);
            <span class="tok-kw">return</span>;
        }
        <span class="tok-com">// 闸门3：类型分类，先特殊后一般</span>
        <span class="tok-type">String</span> type;
        <span class="tok-kw">if</span> (a == b &amp;&amp; b == c) {
            type = <span class="tok-str">"等边三角形"</span>;
        } <span class="tok-kw">else if</span> (a == b || a == c || b == c) {
            type = <span class="tok-str">"等腰三角形"</span>;
        } <span class="tok-kw">else</span> {
            type = <span class="tok-str">"不等边三角形"</span>;
        }</pre>
      </div>
      <div class="notes">
        <h4>这段在做什么</h4>
        <p>构成判断用 <code class="inline">&lt;=</code> 而不是 <code class="inline">&lt;</code>：a+b==c 时三点共线，不是三角形。</p>
        <p>等边条件 <code class="inline">a==b &amp;&amp; b==c</code> 写在最前；若先判等腰，等边会被提前归走。</p>
      </div>
    </div>
    <div class="code-explain reveal">
      <div class="code-card" style="margin:0">
        <div class="code-bar"><span class="dots"><i></i><i></i><i></i></span><span class="fname">TriangleAnalyzer.java</span><span class="tag">④ 闸门4·闸门5</span></div>
<pre class="code" data-raw>        <span class="tok-com">// 闸门4：直角判定，三组平方关系</span>
        <span class="tok-type">boolean</span> isRight = (a * a + b * b == c * c)
                || (a * a + c * c == b * b)
                || (b * b + c * c == a * a);
        <span class="tok-com">// 闸门5：周长、半周长、海伦公式</span>
        <span class="tok-type">int</span> perimeter = a + b + c;
        <span class="tok-type">double</span> p = perimeter / <span class="tok-num">2.0</span>;
        <span class="tok-type">double</span> area = <span class="tok-type">Math</span>.sqrt(p * (p - a) * (p - b) * (p - c));
        <span class="tok-type">System</span>.out.println(<span class="tok-str">"三角形类型："</span> + type);
        <span class="tok-type">System</span>.out.println(<span class="tok-str">"是否为直角三角形："</span>
                + (isRight ? <span class="tok-str">"是"</span> : <span class="tok-str">"否"</span>));
        <span class="tok-type">System</span>.out.println(<span class="tok-str">"周长："</span> + perimeter);
        <span class="tok-type">System</span>.out.printf(<span class="tok-str">"面积：%.2f%n"</span>, area);
        scanner.close();
    }
}</pre>
      </div>
      <div class="notes">
        <h4>这段在做什么</h4>
        <p>三组勾股关系覆盖斜边为 c、b、a 三种情况，无需先排序。</p>
        <p><code class="inline">perimeter / 2.0</code> 触发浮点除法；海伦公式连乘后开方，结果天然是 double。</p>
        <p>三元运算符直接把 boolean 转成「是 / 否」输出。</p>
      </div>
    </div>

    <div class="card reveal">
      <h3 class="t-h"><span class="n">4</span>测试记录（真实运行结果）</h3>
      <div class="tbl-wrap">
        <table>
          <thead><tr><th>用例</th><th class="mono">三边</th><th>类型</th><th>直角</th><th class="mono">周长</th><th class="mono">面积</th><th>结论</th></tr></thead>
          <tbody>
            <tr><td>经典勾股</td><td class="mono">3, 4, 5</td><td>不等边三角形</td><td>是</td><td class="mono">12</td><td class="mono">6.00</td><td><span class="pass">通过</span></td></tr>
            <tr><td>等腰非直角</td><td class="mono">5, 5, 6</td><td>等腰三角形</td><td>否</td><td class="mono">16</td><td class="mono">12.00</td><td><span class="pass">通过</span></td></tr>
            <tr><td>等边</td><td class="mono">2, 2, 2</td><td>等边三角形</td><td>否</td><td class="mono">6</td><td class="mono">1.73</td><td><span class="pass">通过</span></td></tr>
            <tr><td>退化情形</td><td class="mono">1, 2, 3</td><td colspan="4">三条边不能构成三角形</td><td><span class="pass">通过</span></td></tr>
            <tr><td>零边</td><td class="mono">0, 3, 4</td><td colspan="4">输入边长不合法，边长应为1~1000</td><td><span class="pass">通过</span></td></tr>
            <tr><td>超上限</td><td class="mono">1001, 5, 5</td><td colspan="4">输入边长不合法，边长应为1~1000</td><td><span class="pass">通过</span></td></tr>
          </tbody>
        </table>
      </div>
      <p class="small" style="margin-bottom:0">手算验证：5,5,6 → p=8，S=√(8×3×3×2)=√144=12.00；2,2,2 → p=3，S=√(3×1×1×1)=√3≈1.73。</p>
    </div>

    <!-- 在线实验台 2 -->
    <div class="lab reveal" id="lab2">
      <div class="lab-title">在线实验台 · TriangleAnalyzer <span class="live"><i></i>LIVE</span></div>
      <div class="lab-desc">JavaScript 复刻的五级判定流水线，控制台会逐道打印闸门通过情况；点快捷用例可复现上表全部场景。</div>
      <div class="lab-grid">
        <div class="lab-form">
          <div class="field-row">
            <div class="field"><label>第一条边 a</label><input id="t-a" type="number" value="3"></div>
            <div class="field"><label>第二条边 b</label><input id="t-b" type="number" value="4"></div>
            <div class="field"><label>第三条边 c</label><input id="t-c" type="number" value="5"></div>
          </div>
          <div class="lab-actions">
            <button class="lab-btn run" onclick="runTri()">运行程序</button>
            <button class="lab-btn" onclick="document.getElementById('t-out').textContent='等待输入…'">清空控制台</button>
          </div>
          <div class="quick">
            <div class="ql">QUICK TEST CASES</div>
            <button onclick="fillTri(3,4,5)">3/4/5 直角</button>
            <button onclick="fillTri(5,5,6)">5/5/6 等腰</button>
            <button onclick="fillTri(2,2,2)">2/2/2 等边</button>
            <button onclick="fillTri(1,2,3)">1/2/3 退化</button>
            <button onclick="fillTri(0,3,4)">0 越界</button>
            <button onclick="fillTri(1001,5,5)">1001 越界</button>
          </div>
        </div>
        <div class="lab-out" id="t-out"><span class="ph">点击「运行程序」查看输出…</span></div>
      </div>
    </div>
  </div>
</section>

<!-- ===== 思考题 ===== -->
<section class="block" id="thinking">
  <div class="wrap">
    <div class="sec-head reveal">
      <span class="sec-tag">05 · THINKING</span>
      <h2>实验思考题解答</h2>
      <p>报告中的思考题，这里给出可直接誊写的完整答案。</p>
    </div>
    <div class="think reveal">
      <div class="qline"><span class="qbadge">Q1</span><div><b>String 类型的数据能用 <code class="inline">==</code> 比较内容是否相等吗？应该用什么？</b></div></div>
      <div class="ans">
        <span class="atag">参考答案</span>
        <p class="body" style="margin:0">不能。对引用类型 String，<code class="inline">==</code> 比较的是两个引用是否指向<b>同一个对象（内存地址）</b>，而不是字符内容；<code class="inline">new String("abc") == new String("abc")</code> 结果为 false。比较内容应使用 <code class="inline">equals()</code>（忽略大小写用 <code class="inline">equalsIgnoreCase()</code>）。只有 int、double、boolean 等基本类型才用 <code class="inline">==</code> 比值。</p>
      </div>
    </div>
    <div class="think reveal">
      <div class="qline"><span class="qbadge">Q2</span><div><b>求半周长时为什么写 <code class="inline">perimeter / 2.0</code>，而不是 <code class="inline">perimeter / 2</code>？</b></div></div>
      <div class="ans">
        <span class="atag">参考答案</span>
        <p class="body" style="margin:0">perimeter 是 int，<code class="inline">2</code> 也是 int，整数除法会直接截断小数部分（如 9/2 得 4），半周长取整后海伦公式面积必然失真。写成 <code class="inline">2.0</code> 后，int 自动提升为 double 进行浮点除法，9/2.0 得 4.5，结果正确。本题周长为偶数时两者数值相同，但 2.0 是通用、安全的写法。</p>
      </div>
    </div>
    <div class="think reveal">
      <div class="qline"><span class="qbadge">Q3</span><div><b>三角形分类时，为什么等边判断必须放在等腰判断之前？合法性判断为什么放在最前？</b></div></div>
      <div class="ans">
        <span class="atag">参考答案</span>
        <p class="body" style="margin:0">if-else if 链自上而下匹配、命中即停。等边三角形三边相等，必然也满足「任意两边相等」的等腰条件，若等腰在前，等边会被提前判成等腰。分支应遵循<b>从特殊到一般</b>的顺序。合法性（范围、构成）放在最前是卫语句思想：非法数据一旦进入分类与开方计算，会产生错误结论甚至 NaN，且任务书要求非法输入立即停止、不再计算。</p>
      </div>
    </div>
    <div class="think reveal">
      <div class="qline"><span class="qbadge">Q4</span><div><b>为什么构成判断通过后才使用海伦公式？<code class="inline">Math.sqrt</code> 对负数开方会报错吗？</b></div></div>
      <div class="ans">
        <span class="atag">参考答案</span>
        <p class="body" style="margin:0">海伦公式根号内的 p(p−a)(p−b)(p−c) 只有在三边能构成三角形时才非负。若三边不能构成三角形，乘积可能为负；Java 中 <code class="inline">Math.sqrt(负数)</code> <b>不会编译报错也不会抛异常</b>，而是返回 <code class="inline">NaN</code>（Not a Number），程序会带着错误结果继续运行，更难排查。因此必须先用三角形不等式拦截。</p>
      </div>
    </div>
  </div>
</section>

<!-- ===== 易错点 ===== -->
<section class="block" id="pitfalls" style="background:linear-gradient(180deg,#f3f5f8,var(--bg))">
  <div class="wrap">
    <div class="sec-head reveal">
      <span class="sec-tag">06 · PITFALLS</span>
      <h2>10 个高频易错点</h2>
      <p>都是初学者在本题上真实丢分的地方，逐条对照自己的代码。</p>
    </div>
    <div class="pit-grid reveal">
      <div class="pit"><h4><span class="x">✗</span>运行命令带 .class 后缀</h4><p>写成 <code class="inline">java GradeCalculator.class</code>，报“找不到或无法加载主类”。</p><span class="fix">java 后面只写主类名：<code class="inline">java GradeCalculator</code>。</span></div>
      <div class="pit"><h4><span class="x">✗</span>文件名与类名不一致</h4><p><code class="inline">public class</code> 名与 .java 文件名不同或大小写不符，编译报错。</p><span class="fix">两者完全一致，类名使用大驼峰。</span></div>
      <div class="pit"><h4><span class="x">✗</span>权重写魔法数字</h4><p>直接在算式里写 0.1、0.3、0.6，不符合任务书硬性要求。</p><span class="fix">定义 <code class="inline">private static final double</code> 常量，全大写命名。</span></div>
      <div class="pit"><h4><span class="x">✗</span>整数除法丢小数</h4><p><code class="inline">perimeter / 2</code> 结果为 int，奇数周长时半周长被截断。</p><span class="fix">写 <code class="inline">perimeter / 2.0</code>，让运算在 double 下进行。</span></div>
      <div class="pit"><h4><span class="x">✗</span>强转当作四舍五入</h4><p>以为 <code class="inline">(int)3.9</code> 得 4，实际直接截断得 3。</p><span class="fix">需要四舍五入用 <code class="inline">Math.round()</code>。</span></div>
      <div class="pit"><h4><span class="x">✗</span>nextLine 读到空串</h4><p>先 nextInt/nextDouble 后 nextLine，换行符残留导致读入空字符串。</p><span class="fix">字符串输入放最前，或额外调一次 nextLine() 消耗换行。</span></div>
      <div class="pit"><h4><span class="x">✗</span>用 == 比较字符串</h4><p><code class="inline">level == "优秀"</code> 比的是对象地址，结果不可靠。</p><span class="fix">内容比较一律用 <code class="inline">.equals()</code>。</span></div>
      <div class="pit"><h4><span class="x">✗</span>等级链从低到高</h4><p>先写 &gt;=60，90 分也会先命中“及格”，等级判错。</p><span class="fix">if-else if 链按 90→80→70→60 从高到低，else 兜底。</span></div>
      <div class="pit"><h4><span class="x">✗</span>边界与退化处理错</h4><p>成绩用 &gt;=100 判非法（100 分被误杀）；构成判断用 a+b&lt;c（漏掉 a+b==c 的退化情形）。</p><span class="fix">闭区间用 &lt;0 || &gt;100；构成用 &lt;= 一次拦住共线。</span></div>
      <div class="pit"><h4><span class="x">✗</span>只验一组勾股 / 分类顺序反</h4><p>只写 a²+b²==c²，5,3,4 这类换序输入判不出直角；等腰写在等边前。</p><span class="fix">三组平方都检查；类型先等边后等腰再不等边。</span></div>
    </div>
  </div>
</section>

<!-- ===== 小结 ===== -->
<section class="block" id="summary">
  <div class="wrap">
    <div class="summary-dark reveal">
      <span class="sec-tag" style="color:#e8873a">07 · SUMMARY</span>
      <h2 style="margin-top:8px">实验小结：你应该带走的 6 个能力</h2>
      <div class="sum-grid">
        <div class="sum-item"><div class="si-n">01</div><h4>完整的工程流程</h4><p>能独立完成建类 → 编码 → javac 编译 → java 运行 → 用例测试的闭环。</p></div>
        <div class="sum-item"><div class="si-n">02</div><h4>常量与命名</h4><p>会用 final 命名常量表达权重、范围等业务规则，变量见名知意。</p></div>
        <div class="sum-item"><div class="si-n">03</div><h4>输入输出规范</h4><p>熟练使用 Scanner 三类读取方法与 printf 格式符，清楚混用陷阱。</p></div>
        <div class="sum-item"><div class="si-n">04</div><h4>类型与运算</h4><p>理解自动/强制类型转换，能主动规避整数除法截断问题。</p></div>
        <div class="sum-item"><div class="si-n">05</div><h4>分支设计</h4><p>会用卫语句处理非法输入，会设计从特殊到一般、从高到低的分支顺序。</p></div>
        <div class="sum-item"><div class="si-n">06</div><h4>健壮性意识</h4><p>先校验后计算、边界与退化情形全覆盖，理解 NaN 等静默错误的危害。</p></div>
      </div>
      <div class="callout tip" style="margin-top:24px;background:rgba(14,124,102,.15);border-color:#2f5a45;color:#bfe8dc">
        <svg viewBox="0 0 24 24" fill="none"><path d="M5 12l4 4L19 7" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        学完本页后，建议到「50 题答题闯关」网站完成自测，目标正确率 90% 以上；错题可回到对应 KP 知识点卡片复习。
      </div>
    </div>
  </div>
</section>
`;
