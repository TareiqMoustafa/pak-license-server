"""لوحة التحكم: صفحة واحدة (HTML+CSS+JS) تُخدَّم من /admin وتتصل بنفس واجهات /api/admin.

لا يوجد أي سر داخل الصفحة؛ التوكن يُكتب عند الدخول ويُحفظ في المتصفح فقط.
"""

ADMIN_HTML = r"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#12141a">
<title>لوحة تحكم التراخيص</title>
<style>
:root{--bg:#12141a;--card:#1c1f27;--line:#2c313c;--txt:#eceef3;--mut:#9aa1b2;--amber:#ffd740;--red:#c62828;--green:#43a047;--orange:#fb8c00}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{margin:0;background:var(--bg);color:var(--txt);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Tahoma,sans-serif;padding:max(14px,env(safe-area-inset-top)) 14px 40px}
.wrap{max-width:760px;margin:0 auto}
h1{font-size:19px;margin:0;color:var(--amber)}
h2{font-size:16px;margin:0 0 12px}
.top{display:flex;align-items:center;justify-content:space-between;gap:8px;margin:6px 0 14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px;margin-bottom:14px}
label{display:block;font-size:12.5px;color:var(--mut);margin:0 0 4px}
input,select{width:100%;background:#12141a;color:var(--txt);border:1px solid var(--line);border-radius:10px;padding:11px 12px;font-size:15px;font-family:inherit}
input:focus,select:focus{outline:2px solid var(--amber);outline-offset:0}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.full{grid-column:1/-1}
button{font-family:inherit;font-size:14px;border:0;border-radius:10px;padding:10px 14px;cursor:pointer;color:#fff;background:#3a4050}
button:active{transform:scale(.97)}
button:disabled{opacity:.5}
.primary{background:var(--red);font-size:15px;padding:12px;width:100%;font-weight:700}
.amber{background:var(--amber);color:#111}
.ghost{background:transparent;border:1px solid var(--line);color:var(--txt)}
.danger{background:#7f1d1d}
.small{padding:7px 10px;font-size:13px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:14px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 6px;text-align:center}
.stat b{display:block;font-size:20px}
.stat span{font-size:11.5px;color:var(--mut)}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0}
.chip{background:transparent;border:1px solid var(--line);color:var(--mut);padding:6px 12px;border-radius:99px;font-size:13px}
.chip.on{background:var(--amber);color:#111;border-color:var(--amber)}
.lic{border:1px solid var(--line);border-radius:14px;padding:12px;margin-top:10px;background:#171a21}
.lic .row{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}
.key{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:15px;direction:ltr;word-break:break-all;color:var(--amber)}
.meta{color:var(--mut);font-size:12.5px;margin-top:4px}
.badge{font-size:12px;padding:3px 10px;border-radius:99px;color:#fff}
.b-active{background:var(--green)}.b-expired{background:var(--orange)}.b-banned{background:var(--red)}
.acts{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
.result{background:#10251a;border:1px solid #1f5130;border-radius:12px;padding:12px;margin-top:12px}
.result .key{margin:6px 0}
.msg{color:#ff8a80;font-size:13px;min-height:18px;margin-top:8px}
.toast{position:fixed;bottom:18px;left:50%;transform:translateX(-50%);background:#fff;color:#111;padding:10px 18px;border-radius:99px;font-size:14px;max-width:90vw;opacity:0;pointer-events:none;transition:.25s;z-index:9}
.toast.show{opacity:1}
.hide{display:none!important}
.mut{color:var(--mut);font-size:12.5px}
a.lnk{color:var(--mut);cursor:pointer;text-decoration:underline;font-size:12.5px}
.check{display:flex;gap:8px;align-items:center;margin-top:10px;color:var(--mut);font-size:13px}
.check input{width:auto}
</style>
</head>
<body>
<div class="wrap">

<!-- تسجيل الدخول -->
<section id="login" class="card" style="margin-top:12vh">
  <h1 style="margin-bottom:6px">🔐 لوحة التحكم</h1>
  <p class="mut" style="margin-top:0">أدخل ADMIN_TOKEN للدخول.</p>
  <label for="tokenInput">التوكن</label>
  <input id="tokenInput" type="password" autocomplete="off" autocapitalize="off" spellcheck="false" dir="ltr">
  <label class="check"><input id="remember" type="checkbox"> تذكّرني على هذا الجهاز</label>
  <button id="loginBtn" class="primary" style="margin-top:12px">دخول</button>
  <div id="loginMsg" class="msg"></div>
</section>

<!-- التطبيق -->
<main id="app" class="hide">
  <div class="top">
    <h1>🛡️ إدارة التراخيص</h1>
    <div style="display:flex;gap:6px">
      <button id="refreshBtn" class="ghost small">تحديث</button>
      <button id="logoutBtn" class="ghost small">خروج</button>
    </div>
  </div>

  <div class="stats">
    <div class="stat"><b id="sTotal">0</b><span>الكل</span></div>
    <div class="stat"><b id="sActive" style="color:var(--green)">0</b><span>نشط</span></div>
    <div class="stat"><b id="sExpired" style="color:var(--orange)">0</b><span>منتهي</span></div>
    <div class="stat"><b id="sBanned" style="color:#ef5350">0</b><span>محظور</span></div>
  </div>

  <section class="card">
    <h2>➕ إنشاء أكواد جديدة</h2>
    <div class="grid">
      <div>
        <label for="dur">المدة</label>
        <select id="dur">
          <option value="week">أسبوع (7 أيام)</option>
          <option value="month" selected>شهر (30 يوم)</option>
          <option value="2.5months">شهران ونصف (75 يوم)</option>
          <option value="custom">مدة مخصصة…</option>
        </select>
      </div>
      <div id="daysBox" class="hide">
        <label for="days">عدد الأيام</label>
        <input id="days" type="number" min="1" max="3650" value="30" inputmode="numeric">
      </div>
      <div>
        <label for="count">عدد الأكواد</label>
        <input id="count" type="number" min="1" max="50" value="1" inputmode="numeric">
      </div>
      <div>
        <label for="maxdev">الأجهزة المسموحة</label>
        <input id="maxdev" type="number" min="1" max="10" value="1" inputmode="numeric">
      </div>
      <div class="full">
        <label for="note">اسم العميل / ملاحظة</label>
        <input id="note" maxlength="100" placeholder="مثال: أحمد - واتساب">
      </div>
      <div class="full">
        <label for="ckey">كود مخصص (اختياري، لكود واحد فقط)</label>
        <input id="ckey" dir="ltr" autocapitalize="characters" placeholder="مثال: TARE-VIP">
      </div>
      <div class="full"><button id="createBtn" class="primary">إنشاء</button></div>
    </div>
    <div id="result" class="result hide"></div>
  </section>

  <section class="card">
    <h2>📋 الأكواد</h2>
    <input id="search" placeholder="بحث بالكود أو الاسم…">
    <div class="chips" id="chips"></div>
    <div id="list"></div>
    <p class="mut" style="margin-bottom:0">الأكواد تُحفظ على السيرفر بصيغة مشفّرة، وتظهر هنا فقط الأكواد التي أنشأتها من هذا الجهاز.
      <a class="lnk" id="clearVault">مسح الأكواد المحفوظة محلياً</a></p>
  </section>
</main>
</div>
<div id="toast" class="toast"></div>

<script>
(()=>{
const $=s=>document.querySelector(s);
const K_VAULT='pak_vault', K_TOKEN='pak_token';
let token='', rows=[], filter='all';

/* ---------- أدوات ---------- */
function h(tag,props={},...kids){
  const e=document.createElement(tag);
  for(const [k,v] of Object.entries(props)){
    if(k==='class')e.className=v;
    else if(k.startsWith('on'))e.addEventListener(k.slice(2),v);
    else e.setAttribute(k,v);
  }
  for(const c of kids.flat()){ if(c==null||c===false)continue; e.append(c.nodeType?c:document.createTextNode(c)); }
  return e;
}
let toastT;
function toast(t){const el=$('#toast');el.textContent=t;el.classList.add('show');clearTimeout(toastT);toastT=setTimeout(()=>el.classList.remove('show'),2600);}
async function copy(text){
  try{await navigator.clipboard.writeText(text);}
  catch{const t=h('textarea',{style:'position:fixed;opacity:0'});t.value=text;document.body.append(t);t.select();document.execCommand('copy');t.remove();}
  toast('تم النسخ ✅');
}
const vault=()=>{try{return JSON.parse(localStorage.getItem(K_VAULT)||'{}')}catch{return {}}};
const saveVault=v=>localStorage.setItem(K_VAULT,JSON.stringify(v));

async function api(path,method='GET',body){
  const r=await fetch(path,{method,headers:{'Authorization':'Bearer '+token,'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});
  let d={};try{d=await r.json()}catch{}
  if(r.status===401){logout('انتهت الجلسة أو التوكن غير صحيح');throw new Error('Unauthorized');}
  if(r.status===429)throw new Error('محاولات كثيرة، انتظر دقيقة');
  if(!r.ok||d.success===false)throw new Error(d.message||('خطأ '+r.status));
  return d;
}

/* ---------- الدخول ---------- */
function showApp(){$('#login').classList.add('hide');$('#app').classList.remove('hide');}
function logout(msg){
  token='';sessionStorage.removeItem(K_TOKEN);localStorage.removeItem(K_TOKEN);
  $('#app').classList.add('hide');$('#login').classList.remove('hide');
  $('#tokenInput').value='';$('#loginMsg').textContent=msg||'';
}
async function tryToken(t){
  const r=await fetch('/api/admin/list',{headers:{Authorization:'Bearer '+t}});
  return r.status;
}
async function login(){
  const raw=$('#tokenInput').value.trim(), msg=$('#loginMsg');
  if(!raw){msg.textContent='أدخل التوكن';return;}
  $('#loginBtn').disabled=true;msg.textContent='';
  try{
    // يجرّب كما كُتب، ثم بعد حذف المسافات (أخطاء النسخ الشائعة)
    for(const c of new Set([raw,raw.replace(/\s+/g,'')])){
      const st=await tryToken(c);
      if(st===200){
        token=c;
        ($('#remember').checked?localStorage:sessionStorage).setItem(K_TOKEN,c);
        showApp();await load();return;
      }
      if(st===503){msg.textContent='ADMIN_TOKEN غير مضبوط على السيرفر (24 حرفاً على الأقل).';return;}
      if(st===429){msg.textContent='محاولات كثيرة، انتظر دقيقة.';return;}
    }
    msg.textContent='التوكن غير صحيح.';
  }catch{msg.textContent='تعذر الاتصال بالسيرفر.';}
  finally{$('#loginBtn').disabled=false;}
}

/* ---------- البيانات ---------- */
async function load(){
  try{const d=await api('/api/admin/list');rows=(d.licenses||[]).sort((a,b)=>(b.created||'').localeCompare(a.created||''));render();}
  catch(e){if(e.message!=='Unauthorized')toast(e.message);}
}
function render(){
  const c={all:rows.length,active:0,expired:0,banned:0};
  rows.forEach(r=>c[r.status]=(c[r.status]||0)+1);
  $('#sTotal').textContent=c.all;$('#sActive').textContent=c.active;$('#sExpired').textContent=c.expired;$('#sBanned').textContent=c.banned;

  const chips=$('#chips');chips.replaceChildren(...[['all','الكل'],['active','نشط'],['expired','منتهي'],['banned','محظور']]
    .map(([k,t])=>h('button',{class:'chip'+(filter===k?' on':''),onclick:()=>{filter=k;render();}},`${t} (${c[k]||0})`)));

  const q=$('#search').value.trim().toLowerCase(), v=vault();
  const view=rows.filter(r=>(filter==='all'||r.status===filter)&&(!q||(r.id+' '+(v[r.id]||'')+' '+(r.note||'')).toLowerCase().includes(q)));
  const list=$('#list');list.replaceChildren();
  if(!view.length){list.append(h('p',{class:'mut'},'لا توجد أكواد.'));return;}
  view.forEach(r=>list.append(card(r,v[r.id])));
}
const STATUS={active:'نشط',expired:'منتهي',banned:'محظور'};
function card(r,key){
  const exp=new Date(r.expires_at), days=Math.ceil((exp-Date.now())/864e5);
  const left=r.status==='banned'?'':(days>0?`متبقي ${days} يوم`:`انتهى منذ ${-days} يوم`);
  const act=(label,cls,fn)=>h('button',{class:'small '+cls,onclick:fn},label);
  return h('div',{class:'lic'},
    h('div',{class:'row'},
      h('div',{class:'key'},key||('ID: '+r.id)),
      h('span',{class:'badge b-'+r.status},STATUS[r.status]||r.status)),
    h('div',{class:'meta'},`${r.note?r.note+' • ':''}${r.type} • ينتهي ${r.expires_at.slice(0,10)} ${left?'('+left+')':''}`),
    h('div',{class:'meta'},`الأجهزة ${r.devices}/${r.max_devices} • عدد التحققات ${r.checks}${r.last_seen?' • آخر ظهور '+r.last_seen.replace('T',' ').slice(0,16):''}`),
    h('div',{class:'acts'},
      key&&act('نسخ الكود','amber',()=>copy(key)),
      key&&act('نسخ رسالة للعميل','ghost',()=>copy(`كود التفعيل: ${key}\nصالح حتى: ${r.expires_at.slice(0,10)}`)),
      act('إعادة ضبط الجهاز','ghost',()=>doControl(r,'reset_devices')),
      act('تمديد','ghost',()=>{const d=parseInt(prompt('كم يوماً تريد إضافة؟','30'),10);if(d>0)doControl(r,'extend',{days:d});}),
      r.status==='banned'?act('فك الحظر','ghost',()=>doControl(r,'unban')):act('حظر','danger',()=>doControl(r,'ban')),
      act('حذف','danger',()=>{if(confirm('حذف هذا الكود نهائياً؟'))doControl(r,'delete');})));
}
async function doControl(r,action,extra={}){
  try{const d=await api('/api/admin/control','POST',{id:r.id,action,...extra});toast(d.message||'تم');
    if(action==='delete'){const v=vault();delete v[r.id];saveVault(v);}
    await load();}
  catch(e){if(e.message!=='Unauthorized')toast(e.message);}
}

/* ---------- الإنشاء ---------- */
async function create(){
  const body={}, type=$('#dur').value;
  if(type==='custom')body.days=parseInt($('#days').value,10);else body.type=type;
  body.count=parseInt($('#count').value,10)||1;
  body.max_devices=parseInt($('#maxdev').value,10)||1;
  const note=$('#note').value.trim(), ck=$('#ckey').value.trim();
  if(note)body.note=note; if(ck)body.key=ck;
  $('#createBtn').disabled=true;
  try{
    const d=await api('/api/admin/add','POST',body);
    const v=vault();d.keys.forEach(k=>v[k.id]=k.key);saveVault(v);
    const box=$('#result');box.classList.remove('hide');
    box.replaceChildren(
      h('b',{},`تم إنشاء ${d.keys.length} كود ✅`),
      ...d.keys.map(k=>h('div',{class:'row',style:'display:flex;justify-content:space-between;align-items:center;gap:8px'},
        h('div',{class:'key'},k.key),h('button',{class:'small amber',onclick:()=>copy(k.key)},'نسخ'))),
      d.keys.length>1?h('button',{class:'small ghost',style:'margin-top:8px',onclick:()=>copy(d.keys.map(k=>k.key).join('\n'))},'نسخ الكل'):null);
    $('#ckey').value='';$('#note').value='';
    await load();
  }catch(e){if(e.message!=='Unauthorized')toast(e.message);}
  finally{$('#createBtn').disabled=false;}
}

/* ---------- ربط الأحداث ---------- */
$('#loginBtn').onclick=login;
$('#tokenInput').addEventListener('keydown',e=>{if(e.key==='Enter')login();});
$('#logoutBtn').onclick=()=>logout('');
$('#refreshBtn').onclick=load;
$('#createBtn').onclick=create;
$('#search').addEventListener('input',render);
$('#dur').onchange=()=>$('#daysBox').classList.toggle('hide',$('#dur').value!=='custom');
$('#clearVault').onclick=()=>{if(confirm('مسح الأكواد المحفوظة على هذا الجهاز؟ (لا يؤثر على السيرفر)')){localStorage.removeItem(K_VAULT);render();toast('تم المسح');}};

/* ---------- البدء ---------- */
(async()=>{
  const saved=sessionStorage.getItem(K_TOKEN)||localStorage.getItem(K_TOKEN);
  if(!saved)return;
  try{if(await tryToken(saved)===200){token=saved;showApp();await load();}else logout('');}catch{}
})();
})();
</script>
</body>
</html>
"""
