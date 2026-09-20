/* ============================================================
   交互逻辑：滚动揭示、导航高亮、两个在线实验台
   ============================================================ */

// ---- 滚动揭示 ----
var io = new IntersectionObserver(function(entries){
  entries.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target);} });
},{threshold:.12});
document.querySelectorAll('.reveal').forEach(function(el){ io.observe(el); });

// ---- 导航高亮 ----
var sections = ['overview','knowledge','task1','task2','thinking','pitfalls','summary']
  .map(function(id){ return document.getElementById(id); });
var navAs = document.querySelectorAll('#navlinks a');
window.addEventListener('scroll', function(){
  var pos = window.scrollY + 120, current = 0;
  sections.forEach(function(s,i){ if(s && s.offsetTop <= pos) current = i; });
  navAs.forEach(function(a,i){ a.classList.toggle('active', i === current); });
},{passive:true});

// ---- 工具：两位小数（与 printf %.2f 对齐，HALF_UP） ----
function fmt2(x){
  var s = (Math.round((x + Number.EPSILON) * 100) / 100).toFixed(2);
  return s;
}

// ================= 实验台 1：成绩计算器 =================
function fillGrade(n,id,u,l,e){
  document.getElementById('g-name').value = n;
  document.getElementById('g-id').value = id;
  document.getElementById('g-usual').value = u;
  document.getElementById('g-lab').value = l;
  document.getElementById('g-exam').value = e;
  runGrade();
}
function runGrade(){
  var name = document.getElementById('g-name').value;
  var sid  = document.getElementById('g-id').value;
  var u = parseFloat(document.getElementById('g-usual').value);
  var l = parseFloat(document.getElementById('g-lab').value);
  var e = parseFloat(document.getElementById('g-exam').value);
  var out = document.getElementById('g-out');
  var L = [];
  L.push('请输入姓名：' + name);
  L.push('请输入学号：' + sid);
  L.push('请输入平时表现成绩(0~100)：' + (isNaN(u)?'<非数字>':u));
  L.push('请输入实验成绩(0~100)：' + (isNaN(l)?'<非数字>':l));
  L.push('请输入期末考试成绩(0~100)：' + (isNaN(e)?'<非数字>':e));
  if(isNaN(u) || isNaN(l) || isNaN(e)){
    L.push('<span style="color:#ff8178">输入成绩不合法（成绩必须是 0~100 的数字）</span>');
    out.innerHTML = L.join('\n'); return;
  }
  if(u < 0 || u > 100 || l < 0 || l > 100 || e < 0 || e > 100){
    L.push('<span style="color:#ff8178">输入成绩不合法</span>');
    out.innerHTML = L.join('\n'); return;
  }
  var USUAL=0.10, LAB=0.30, EXAM=0.60;
  var fg = u*USUAL + l*LAB + e*EXAM;
  var level;
  if(fg>=90) level='优秀'; else if(fg>=80) level='良好';
  else if(fg>=70) level='中等'; else if(fg>=60) level='及格'; else level='不及格';
  L.push('姓名：' + name);
  L.push('学号：' + sid);
  L.push('平时成绩：' + fmt2(u) + '，实验成绩：' + fmt2(l) + '，期末成绩：' + fmt2(e));
  L.push('总评成绩：<span style="color:#7ee0a6;font-weight:700">' + fmt2(fg) + '</span>，等级：<span style="color:#ffd479;font-weight:700">' + level + '</span>');
  L.push('<span style="color:#566173">// 计算明细：' + u + '×0.1 + ' + l + '×0.3 + ' + e + '×0.6 = ' + fmt2(fg) + '</span>');
  out.innerHTML = L.join('\n');
}

// ================= 实验台 2：三角形分析器 =================
function fillTri(a,b,c){
  document.getElementById('t-a').value = a;
  document.getElementById('t-b').value = b;
  document.getElementById('t-c').value = c;
  runTri();
}
function runTri(){
  var a = parseInt(document.getElementById('t-a').value, 10);
  var b = parseInt(document.getElementById('t-b').value, 10);
  var c = parseInt(document.getElementById('t-c').value, 10);
  var out = document.getElementById('t-out');
  var L = [];
  L.push('<span style="color:#566173">请输入三条边长…</span>');
  L.push('三边长度：' + (isNaN(a)?'?':a) + '、' + (isNaN(b)?'?':b) + '、' + (isNaN(c)?'?':c));
  if(isNaN(a)||isNaN(b)||isNaN(c)){
    L.push('<span style="color:#ff8178">输入边长不合法（必须输入整数）</span>');
    out.innerHTML = L.join('\n'); return;
  }
  // 闸门1
  L.push('<span style="color:#7e8896">[闸门1] 范围校验 1~1000 …</span>');
  if(a<1||a>1000||b<1||b>1000||c<1||c>1000){
    L.push('<span style="color:#ff8178">  ✗ 存在越界边 → 输入边长不合法，边长应为1~1000</span>');
    L.push('<span style="color:#ff8178">程序结束（return），后续判断不再执行</span>');
    out.innerHTML = L.join('\n'); return;
  }
  L.push('<span style="color:#7ee0a6">  ✓ 三边均在 1~1000</span>');
  // 闸门2
  L.push('<span style="color:#7e8896">[闸门2] 构成判断：任意两边之和 &gt; 第三边 …</span>');
  L.push('<span style="color:#566173">  ' + a + '+' + b + '=' + (a+b) + (a+b>c?' &gt; ':' ≤ ') + c + '　'
       + a + '+' + c + '=' + (a+c) + (a+c>b?' &gt; ':' ≤ ') + b + '　'
       + b + '+' + c + '=' + (b+c) + (b+c>a?' &gt; ':' ≤ ') + a + '</span>');
  if(a+b<=c||a+c<=b||b+c<=a){
    L.push('<span style="color:#ff8178">  ✗ 存在两边之和不大于第三边（含退化情形）→ 三条边不能构成三角形</span>');
    L.push('<span style="color:#ff8178">程序结束（return），不进行分类与计算</span>');
    out.innerHTML = L.join('\n'); return;
  }
  L.push('<span style="color:#7ee0a6">  ✓ 严格不等式全部成立，可以构成三角形</span>');
  // 闸门3
  var type;
  if(a===b&&b===c) type='等边三角形';
  else if(a===b||a===c||b===c) type='等腰三角形';
  else type='不等边三角形';
  L.push('<span style="color:#7e8896">[闸门3] 类型分类（先等边后等腰）→ </span><span style="color:#ffd479;font-weight:700">' + type + '</span>');
  // 闸门4
  var g1=a*a+b*b, g2=a*a+c*c, g3=b*b+c*c;
  var isRight = (g1===c*c)||(g2===b*b)||(g3===a*a);
  L.push('<span style="color:#7e8896">[闸门4] 直角判定：' + a + '²+' + b + '²=' + g1 + (g1===c*c?'=':'≠') + c + '²=' + (c*c) + '；'
       + a + '²+' + c + '²=' + g2 + (g2===b*b?'=':'≠') + b + '²=' + (b*b) + '；'
       + b + '²+' + c + '²=' + g3 + (g3===a*a?'=':'≠') + a + '²=' + (a*a) + '</span>');
  L.push('是否为直角三角形：<span style="color:' + (isRight?'#7ee0a6':'#9fb0c4') + ';font-weight:700">' + (isRight?'是':'否') + '</span>');
  // 闸门5
  var perimeter = a+b+c;
  var p = perimeter/2.0;
  var area = Math.sqrt(p*(p-a)*(p-b)*(p-c));
  L.push('<span style="color:#7e8896">[闸门5] 周长 = ' + a + '+' + b + '+' + c + ' = ' + perimeter +
         '；半周长 p = ' + perimeter + '/2.0 = ' + p + '</span>');
  L.push('周长：<span style="color:#7ee0a6;font-weight:700">' + perimeter + '</span>');
  L.push('面积：<span style="color:#7ee0a6;font-weight:700">' + fmt2(area) + '</span> <span style="color:#566173">// √[' + p + '×' + (p-a) + '×' + (p-b) + '×' + (p-c) + ']</span>');
  out.innerHTML = L.join('\n');
}

// 初始运行一次，让首屏控制台有内容
runGrade();
runTri();
