"""صفحة المالك: سجل عناوين IP اليومي (تعمل فقط بـ OWNER_TOKEN، وغير مرتبطة بلوحة /admin)."""
import re

from admin_page import ADMIN_HTML

_CSS = re.search(r"<style>(.*?)</style>", ADMIN_HTML, re.S).group(1)

OWNER_HTML = r"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#06080f">
<title>سجل الدخول</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&family=Orbitron:wght@600;800&display=swap">
<style>""" + _CSS + r"""
.wrap{max-width:1100px}
.tbl-wrap{overflow-x:auto;border:1px solid var(--rule);border-radius:var(--r);background:var(--plate)}
table{width:100%;border-collapse:collapse;font-size:13.5px;min-width:760px}
th,td{padding:9px 12px;text-align:start;white-space:nowrap}
th{position:sticky;top:0;background:var(--plate2);color:var(--mut);font-weight:700;font-size:12.5px;border-bottom:1px solid var(--rule)}
tr.day td{background:#0a0f20;color:var(--cyan);font-weight:800;border-top:1px solid #19e3ff33;font-family:"Orbitron","Tajawal",sans-serif;font-size:13px}
tr.r td{border-top:1px solid #121a33}
tr.r:hover td{background:#19e3ff0a}
td.ip{font-family:ui-monospace,Menlo,Consolas,monospace;direction:ltr;text-align:start;color:var(--cyan)}
td.ua{max-width:240px;overflow:hidden;text-overflow:ellipsis;color:var(--mut);direction:ltr;text-align:start}
.k{font-size:12px;font-weight:700;padding:1px 9px;border-radius:99px;border:1px solid currentColor}
.k-user{color:var(--green)}.k-invalid{color:var(--amber)}.k-admin{color:var(--violet)}.k-owner{color:var(--cyan)}
.k-admin_fail,.k-owner_fail{color:var(--pink)}
.flag{color:var(--pink);font-weight:800}
</style>
</head>
<body>

<section id="login" class="login">
  <div class="login-box">
    <svg class="mark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"><path d="M12 2.5l8 3v6c0 5-3.4 9.2-8 10.5-4.6-1.3-8-5.5-8-10.5v-6z"/><circle cx="12" cy="11" r="2.2"/></svg>
    <h1>سجل الدخول</h1>
    <p class="mut">توكن المالك فقط.</p>
    <label for="tk">التوكن</label>
    <input id="tk" type="password" class="ltr" autocomplete="off" autocapitalize="off" spellcheck="false">
    <button id="go" class="btn-main btn-block" style="margin-top:16px">دخول</button>
    <div id="msg" class="err" role="alert"></div>
  </div>
</section>

<div id="app" class="hide">
  <header class="bar"><div class="bar-in">
    <div class="brand"><div><b>سجل الدخول</b><small id="meta">…</small></div></div>
    <button id="out" class="btn-ghost btn-sm">خروج</button>
  </div></header>
  <main class="wrap">
    <div class="strip">
      <div><b id="sRows" class="num">0</b><span>سجلات</span></div>
      <div><b id="sIps" class="num">0</b><span>عناوين مختلفة</span></div>
      <div><b id="sUsers" class="num">0</b><span>أكواد ظهرت</span></div>
      <div><b id="sFlag" class="num">0</b><span>كود من 3 عناوين فأكثر</span></div>
    </div>
    <div class="tools">
      <input id="q" type="text" placeholder="ابحث بالعنوان أو المعرّف أو الاسم" aria-label="بحث">
      <select id="kind" aria-label="النوع">
        <option value="">كل الأنواع</option><option value="user">مستخدمون</option><option value="invalid">أكواد خاطئة</option>
        <option value="admin">دخول المشرفين</option><option value="owner">دخولك أنت</option><option value="fail">توكن خاطئ</option>
      </select>
      <select id="days" aria-label="المدة">
        <option value="7">7 أيام</option><option value="30" selected>30 يوماً</option><option value="90">90 يوماً</option>
      </select>
      <button id="csv" class="btn-main">تحميل CSV</button>
    </div>
    <div class="tbl-wrap"><table id="tbl"><thead><tr>
      <th>الوقت (آخر ظهور)</th><th>النوع</th><th>المعرّف</th><th>الاسم</th><th>العنوان IP</th><th>الحالة</th><th>مرات</th><th>أول ظهور</th><th>الجهاز</th><th>المتصفح / التطبيق</th>
    </tr></thead><tbody id="body"></tbody></table></div>
    <p class="hint">التواريخ مجمّعة حسب يوم UTC والأوقات بتوقيت جهازك. العنوان هو ما يراه السيرفر؛ من يستخدم VPN يظهر عنوان الـ VPN.
      تُحذف السجلات تلقائياً بعد <span id="ret">90</span> يوماً.</p>
  </main>
</div>
<div id="toast" class="toast" role="status"></div>

<script>
(()=>{
const $=s=>document.querySelector(s);
const KT='owner_tk';
let token='', rows=[];
const KIND={user:'مستخدم',invalid:'كود خاطئ',admin:'مشرف',owner:'المالك',admin_fail:'توكن خاطئ',owner_fail:'محاولة مالك'};
const STATUS={active:'نشط',expired:'منتهي',banned:'محظور',device_limit:'جهاز آخر'};
function h(tag,props={},...kids){const e=document.createElement(tag);for(const [k,v] of Object.entries(props||{})){if(v==null)continue;if(k==='class')e.className=v;else e.setAttribute(k,v);}
  for(const c of kids.flat()){if(c==null)continue;e.append(c.nodeType?c:document.createTextNode(c));}return e;}
let tt;function toast(t){const el=$('#toast');el.textContent=t;el.classList.add('show');clearTimeout(tt);tt=setTimeout(()=>el.classList.remove('show'),2400);}
const fmt=s=>s?new Date(s).toLocaleString('ar-EG-u-nu-latn',{dateStyle:'short',timeStyle:'medium'}):'';

async function load(){
  const r=await fetch('/api/owner/logs?days='+$('#days').value,{headers:{Authorization:'Bearer '+token}});
  if(r.status!==200)return r.status;
  const d=await r.json();rows=d.rows||[];$('#ret').textContent=d.retention_days;render();return 200;
}
function view(){
  const q=$('#q').value.trim().toLowerCase(),k=$('#kind').value;
  return rows.filter(r=>(!k||(k==='fail'?r.kind.endsWith('_fail'):r.kind===k))&&(!q||[r.ip,r.who,r.note,r.dev,r.ua].join(' ').toLowerCase().includes(q)));
}
function render(){
  const v=view();
  // كود ظهر من 3 عناوين فأكثر في أيام مختلفة أو نفس اليوم (مؤشر مشاركة الكود)
  const per={};rows.filter(r=>r.kind==='user').forEach(r=>{(per[r.who]=per[r.who]||new Set()).add(r.ip);});
  const flagged=new Set(Object.keys(per).filter(k=>per[k].size>=3));
  $('#sRows').textContent=v.length;$('#sIps').textContent=new Set(v.map(r=>r.ip)).size;
  $('#sUsers').textContent=Object.keys(per).length;$('#sFlag').textContent=flagged.size;
  $('#meta').textContent=rows.length?`آخر تحديث ${new Date().toLocaleTimeString('ar-EG-u-nu-latn')}`:'لا توجد بيانات بعد';
  const b=$('#body');b.replaceChildren();let day='';
  if(!v.length){b.append(h('tr',{},h('td',{colspan:10,style:'text-align:center;color:var(--mut);padding:30px'},'لا توجد سجلات.')));return;}
  v.forEach(r=>{
    if(r.day!==day){day=r.day;b.append(h('tr',{class:'day'},h('td',{colspan:10},day)));}
    b.append(h('tr',{class:'r'},h('td',{class:'num'},fmt(r.last)),h('td',{},h('span',{class:'k k-'+r.kind},KIND[r.kind]||r.kind)),
      h('td',{class:'ip'},r.who||'—'),h('td',{},r.note||'—'),h('td',{class:'ip'},r.ip),
      h('td',{},STATUS[r.status]||r.status||'—'),h('td',{class:'num'},r.count,flagged.has(r.who)&&r.kind==='user'?h('span',{class:'flag',title:'هذا الكود ظهر من 3 عناوين أو أكثر'},' ⚑'):null),
      h('td',{class:'num'},fmt(r.first)),h('td',{class:'ip'},r.dev||'—'),h('td',{class:'ua',title:r.ua},r.ua||'—')));
  });
}
function csv(){
  const v=view();if(!v.length){toast('لا توجد بيانات للتحميل');return;}
  const esc=x=>{let s=String(x??'');if(/^[=+\-@]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';};
  const head=['اليوم (UTC)','آخر ظهور','أول ظهور','النوع','المعرّف','الاسم','IP','الحالة','عدد المرات','الجهاز','المتصفح'];
  const lines=[head,...v.map(r=>[r.day,r.last,r.first,KIND[r.kind]||r.kind,r.who,r.note,r.ip,STATUS[r.status]||r.status,r.count,r.dev,r.ua])].map(a=>a.map(esc).join(','));
  const blob=new Blob(['\ufeff'+lines.join('\r\n')],{type:'text/csv;charset=utf-8'});
  const a=h('a',{href:URL.createObjectURL(blob),download:`ip-log-${new Date().toISOString().slice(0,10)}.csv`});
  document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),2000);
}
async function login(){
  const t=$('#tk').value.trim();if(!t)return;$('#go').disabled=true;$('#msg').textContent='';
  token=t;
  try{const st=await load();
    if(st===200){sessionStorage.setItem(KT,t);$('#login').classList.add('hide');$('#app').classList.remove('hide');}
    else $('#msg').textContent=st===429?'محاولات كثيرة، انتظر دقيقة.':'التوكن غير صحيح.';}
  catch{$('#msg').textContent='تعذر الاتصال بالسيرفر.';}
  finally{$('#go').disabled=false;}
}
$('#go').onclick=login;$('#tk').addEventListener('keydown',e=>{if(e.key==='Enter')login();});
$('#out').onclick=()=>{sessionStorage.removeItem(KT);location.reload();};
$('#q').addEventListener('input',render);$('#kind').addEventListener('change',render);
$('#days').addEventListener('change',load);$('#csv').onclick=csv;
(async()=>{const s=sessionStorage.getItem(KT);if(!s)return;token=s;
  try{if(await load()===200){$('#login').classList.add('hide');$('#app').classList.remove('hide');}}catch{}})();
})();
</script>
</body>
</html>
"""
