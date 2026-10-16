"""لوحة التحكم: صفحة واحدة (HTML+CSS+JS) تُخدَّم من /admin وتتصل بواجهات /api/admin.

لا يوجد أي سر داخل الصفحة؛ التوكن يُكتب عند الدخول ويُحفظ في المتصفح فقط.
"""

ADMIN_HTML = r"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#06080f">
<title>إدارة التراخيص</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&family=Orbitron:wght@600;800&display=swap">
<style>
:root{
  --ink:#06080f;--plate:#0c1020;--plate2:#121832;--rule:#1c2646;
  --text:#e8eeff;--mut:#7f8bb0;
  --cyan:#19e3ff;--violet:#8b5cff;--pink:#ff2e93;--green:#38ffa2;--amber:#ffb020;
  --cyan-ink:#031318;
  --r:10px;
  --glow:0 0 0 1px #19e3ff55,0 0 18px #19e3ff40;
}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html{color-scheme:dark}
body{margin:0;color:var(--text);min-height:100vh;
  font:15px/1.65 "Tajawal","IBM Plex Sans Arabic",system-ui,-apple-system,"Segoe UI",Tahoma,sans-serif;
  background:
    radial-gradient(900px 500px at 85% -10%,#8b5cff26,transparent 60%),
    radial-gradient(700px 480px at -10% 10%,#19e3ff1f,transparent 60%),
    radial-gradient(800px 500px at 50% 120%,#ff2e9318,transparent 60%),
    var(--ink);
  background-attachment:fixed;
  padding-bottom:calc(76px + env(safe-area-inset-bottom))}
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.5;
  background-image:linear-gradient(#ffffff08 1px,transparent 1px),linear-gradient(90deg,#ffffff08 1px,transparent 1px);
  background-size:44px 44px;
  -webkit-mask-image:radial-gradient(ellipse at 50% 0%,#000 10%,transparent 75%);
  mask-image:radial-gradient(ellipse at 50% 0%,#000 10%,transparent 75%)}
#app,#login{position:relative;z-index:1}
button,input,select,textarea{font:inherit;color:inherit}
.hide{display:none!important}
.mut{color:var(--mut)}
.num{font-variant-numeric:tabular-nums}
.ltr{direction:ltr;unicode-bidi:plaintext;text-align:left}
:focus-visible{outline:2px solid var(--cyan);outline-offset:2px}

/* ---------- أزرار وحقول ---------- */
button{border-radius:var(--r);padding:9px 16px;cursor:pointer;background:var(--plate2);
  border:1px solid var(--rule);transition:background .15s,transform .1s,box-shadow .2s,border-color .2s}
button:hover{border-color:#19e3ff66;box-shadow:0 0 14px #19e3ff22}
button:active{transform:scale(.97)}
button:disabled{opacity:.45;cursor:not-allowed;box-shadow:none}
.btn-main{background:linear-gradient(135deg,var(--cyan),#5aa9ff 55%,var(--violet));color:var(--cyan-ink);
  border-color:transparent;font-weight:800;box-shadow:0 0 18px #19e3ff40}
.btn-main:hover{box-shadow:0 0 26px #19e3ff80,0 0 8px #8b5cff80;border-color:transparent;filter:brightness(1.08)}
.btn-danger{color:var(--pink);border-color:#ff2e9344;background:#1a0b17}
.btn-danger:hover{background:#2a0f22;border-color:var(--pink);box-shadow:0 0 14px #ff2e9340}
.btn-solid-danger{background:linear-gradient(135deg,var(--pink),#ff5d5d);border-color:transparent;color:#1a0210;font-weight:800;
  box-shadow:0 0 18px #ff2e9355}
.btn-ghost{background:transparent}
.btn-sm{padding:6px 12px;font-size:13.5px}
.btn-block{width:100%;padding:13px;font-size:16px}
label{display:block;font-size:13px;color:var(--mut);margin:0 0 5px}
input[type=text],input[type=password],input[type=number],input[type=url],select,textarea{
  width:100%;background:#050711;border:1px solid var(--rule);border-radius:var(--r);padding:10px 12px;transition:border-color .2s,box-shadow .2s}
textarea{resize:vertical;min-height:70px}
input:focus,select:focus,textarea:focus{border-color:var(--cyan);outline:none;box-shadow:0 0 0 3px #19e3ff22,0 0 16px #19e3ff30}
.hint{font-size:12.5px;color:var(--mut);margin:5px 0 0}
a{color:var(--cyan)}

/* ---------- الدخول ---------- */
.login{min-height:100vh;display:grid;place-items:center;padding:20px}
.login-box{width:100%;max-width:390px;padding:30px 24px;border-radius:16px;background:#0b1022e6;position:relative;
  border:1px solid #19e3ff44;box-shadow:0 0 40px #8b5cff22,inset 0 0 30px #19e3ff0d}
.login-box::before{content:"";position:absolute;inset:-1px;border-radius:16px;padding:1px;pointer-events:none;
  background:linear-gradient(135deg,var(--cyan),transparent 35%,transparent 65%,var(--pink));
  -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;
  mask:linear-gradient(#000 0 0) content-box exclude,linear-gradient(#000 0 0)}
.mark{width:50px;height:50px;color:var(--cyan);filter:drop-shadow(0 0 8px #19e3ffaa)}
.login h1{font-size:26px;margin:14px 0 4px;font-weight:800;
  background:linear-gradient(90deg,#fff,var(--cyan));-webkit-background-clip:text;background-clip:text;color:transparent}
.login p{margin:0 0 22px}
.remember{display:flex;gap:8px;align-items:center;margin:12px 0 16px;color:var(--mut);font-size:13.5px}
.remember input{width:18px;height:18px;accent-color:var(--cyan)}
.err{color:var(--pink);font-size:13.5px;min-height:22px;margin-top:10px}

/* ---------- الهيكل ---------- */
.bar{position:sticky;top:0;z-index:5;background:#06080fd9;backdrop-filter:blur(12px);
  border-bottom:1px solid #19e3ff33;padding:max(10px,env(safe-area-inset-top)) 16px 10px;
  box-shadow:0 1px 24px #19e3ff12}
.bar-in{max-width:980px;margin:0 auto;display:flex;align-items:center;gap:14px}
.brand{display:flex;align-items:center;gap:10px;margin-inline-end:auto}
.brand .mark{width:32px;height:32px}
.brand b{display:block;font-size:16px;line-height:1.2;font-weight:800}
.brand small{display:block;font-size:12px;color:var(--mut);line-height:1.2}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--green);margin-inline-end:6px;box-shadow:0 0 8px var(--green)}
.dot.bad{background:var(--pink);box-shadow:0 0 8px var(--pink)}.dot.warn{background:var(--amber);box-shadow:0 0 8px var(--amber)}
.tabs{display:flex;gap:4px}
.tab{background:transparent;border:0;border-radius:var(--r);padding:8px 14px;color:var(--mut);display:flex;gap:8px;align-items:center;position:relative;box-shadow:none}
.tab svg{width:18px;height:18px}
.tab:hover{color:var(--text);background:var(--plate);box-shadow:none}
.tab[aria-selected=true]{color:var(--cyan);background:#19e3ff12;text-shadow:0 0 12px #19e3ff99}
.tab[aria-selected=true]::after{content:"";position:absolute;inset-inline:14px;bottom:2px;height:2px;border-radius:2px;
  background:linear-gradient(90deg,var(--cyan),var(--violet));box-shadow:0 0 10px var(--cyan)}
.wrap{max-width:980px;margin:0 auto;padding:18px 16px}
h2{font-size:20px;margin:0 0 4px;font-weight:800}
.sub{color:var(--mut);font-size:13.5px;margin:0 0 16px}

@media (max-width:720px){
  .tabs{position:fixed;inset:auto 0 0 0;z-index:6;background:#070a16f2;backdrop-filter:blur(14px);
    border-top:1px solid #19e3ff33;padding:6px 10px calc(6px + env(safe-area-inset-bottom));justify-content:space-around;gap:0;
    box-shadow:0 -4px 24px #19e3ff12}
  .tab{flex-direction:column;gap:2px;font-size:12px;padding:6px 18px;flex:1}
  .tab svg{width:22px;height:22px}
  .tab[aria-selected=true]::after{bottom:0}
  .bar-in{gap:8px}
}

/* ---------- الإحصاءات ---------- */
.strip{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:18px}
.strip>div{padding:12px 14px;background:linear-gradient(160deg,var(--plate2),var(--plate));border:1px solid var(--rule);
  border-radius:var(--r);position:relative;overflow:hidden}
.strip>div::before{content:"";position:absolute;inset-inline:0;top:0;height:2px;background:currentColor;opacity:.8;box-shadow:0 0 12px currentColor}
.strip>div:nth-child(1){color:var(--green)}.strip>div:nth-child(2){color:var(--cyan)}
.strip>div:nth-child(3){color:var(--amber)}.strip>div:nth-child(4){color:var(--pink)}
.strip b{display:block;font:800 30px/1.1 "Orbitron","Tajawal",sans-serif;text-shadow:0 0 16px currentColor}
.strip span{font-size:12.5px;color:var(--mut)}
.c-moss,.c-sand,.c-rust,.c-crim{color:inherit}
@media (max-width:520px){.strip{gap:8px}.strip b{font-size:22px}.strip>div{padding:10px}}

/* ---------- أدوات القائمة ---------- */
.tools{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}
.tools input{flex:1 1 200px}
.tools select{width:auto;flex:0 0 auto}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}
.chip{border-radius:99px;padding:5px 14px;font-size:13.5px;background:transparent;color:var(--mut)}
.chip[aria-pressed=true]{background:#19e3ff1c;color:var(--cyan);border-color:var(--cyan);font-weight:700;box-shadow:0 0 14px #19e3ff40}

/* ---------- بطاقة الترخيص ---------- */
.lic{background:linear-gradient(160deg,var(--plate2),var(--plate));border:1px solid var(--rule);border-radius:var(--r);margin-bottom:10px;
  border-inline-start:4px solid var(--green);overflow:hidden;transition:border-color .2s,box-shadow .2s}
.lic:hover{border-color:#19e3ff44;border-inline-start-color:var(--green)}
.lic{box-shadow:inset 4px 0 14px -8px var(--green)}
.lic.st-expired{border-inline-start-color:var(--amber);box-shadow:inset 4px 0 14px -8px var(--amber)}
.lic.st-banned{border-inline-start-color:var(--pink);box-shadow:inset 4px 0 14px -8px var(--pink)}
.lic.soon{border-inline-start-color:var(--cyan);box-shadow:inset 4px 0 14px -8px var(--cyan)}
.lic-head{all:unset;box-sizing:border-box;display:flex;width:100%;gap:12px;align-items:center;justify-content:space-between;
  padding:12px 14px;cursor:pointer}
.lic-head:focus-visible{outline:2px solid var(--cyan);outline-offset:-2px}
.lic-head:hover{background:#19e3ff0a}
.who{min-width:0}
.id{font-family:"Orbitron",ui-monospace,Menlo,Consolas,monospace;font-size:14px;letter-spacing:.04em;color:var(--cyan);direction:ltr;display:block;
  overflow-wrap:anywhere;text-shadow:0 0 10px #19e3ff66}
.nm{font-size:13px;color:var(--mut)}
.right{text-align:end;flex:none}
.badge{display:inline-block;font-size:12px;font-weight:700;padding:2px 11px;border-radius:99px;border:1px solid currentColor;box-shadow:0 0 10px -2px currentColor}
.b-active{color:var(--green)}.b-expired{color:var(--amber)}.b-banned{color:var(--pink)}
.left{display:block;font-size:12.5px;color:var(--mut);margin-top:3px}
.meter{height:4px;background:#0a0f20}
.meter i{display:block;height:100%;background:linear-gradient(90deg,var(--green),var(--cyan));box-shadow:0 0 10px var(--green);transition:width .5s}
.st-expired .meter i{background:var(--amber);box-shadow:0 0 10px var(--amber)}
.st-banned .meter i{background:var(--pink);box-shadow:0 0 10px var(--pink)}
.soon .meter i{background:linear-gradient(90deg,var(--cyan),var(--violet));box-shadow:0 0 10px var(--cyan)}
.lic-body{padding:14px;border-top:1px solid var(--rule);background:#080c1b}
.kv{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px 16px;margin:0 0 14px}
.kv dt{font-size:12px;color:var(--mut)}.kv dd{margin:0;font-size:14px}
.acts{display:flex;gap:6px;flex-wrap:wrap}
.empty{border:1px dashed #19e3ff44;border-radius:var(--r);padding:34px 16px;text-align:center;color:var(--mut);background:#19e3ff08}
.empty b{display:block;color:var(--text);margin-bottom:4px}

/* ---------- نماذج ---------- */
.panel{background:linear-gradient(160deg,var(--plate2),var(--plate));border:1px solid var(--rule);border-radius:12px;padding:18px;margin-bottom:16px;position:relative}
.panel::before{content:"";position:absolute;inset-inline:18px;top:-1px;height:1px;background:linear-gradient(90deg,transparent,var(--cyan),transparent);opacity:.7}
.panel h3{margin:0 0 2px;font-size:16px;font-weight:800}
.panel>.sub{margin-bottom:14px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.full{grid-column:1/-1}
@media (max-width:560px){.grid{grid-template-columns:1fr}}
.seg{display:flex;border:1px solid var(--rule);border-radius:var(--r);overflow:hidden}
.seg button{flex:1;border:0;border-radius:0;background:#050711;padding:10px 4px;font-size:14px;color:var(--mut);box-shadow:none}
.seg button+button{border-inline-start:1px solid var(--rule)}
.seg button[aria-pressed=true]{background:linear-gradient(135deg,#19e3ff2a,#8b5cff2a);color:var(--cyan);font-weight:800;text-shadow:0 0 10px #19e3ff99}
.stepper{display:flex;align-items:stretch}
.stepper button{width:44px;padding:0;font-size:20px}
.stepper input{text-align:center;border-radius:0;margin:0 -1px}
.result{margin-top:16px;border:1px solid #38ffa255;background:#06150f;border-radius:var(--r);padding:14px;box-shadow:0 0 24px #38ffa222}
.result .row{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:6px 0;border-top:1px solid #12342a}
.result .row:first-of-type{border-top:0}
.sw{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 0;border-top:1px solid var(--rule)}
.sw:first-of-type{border-top:0}
.sw b{display:block;font-weight:700}
.sw small{color:var(--mut);font-size:12.5px}
.sw input{appearance:none;width:46px;height:26px;flex:none;border-radius:99px;background:#1a2342;position:relative;cursor:pointer;transition:background .2s,box-shadow .2s;margin:0}
.sw input::after{content:"";position:absolute;top:3px;inset-inline-start:3px;width:20px;height:20px;border-radius:50%;background:#cfd8ff;transition:inset-inline-start .2s,background .2s}
.sw input:checked{background:#38ffa233;box-shadow:0 0 14px #38ffa266,inset 0 0 0 1px var(--green)}
.sw input:checked::after{inset-inline-start:23px;background:var(--green);box-shadow:0 0 10px var(--green)}
.pill{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;padding:3px 11px;border-radius:99px;border:1px solid var(--rule);color:var(--mut);font-weight:400}
.savebar{position:sticky;bottom:calc(66px + env(safe-area-inset-bottom));display:flex;gap:10px;align-items:center;justify-content:space-between;
  background:#0d1330f2;border:1px solid var(--cyan);border-radius:var(--r);padding:10px 14px;margin-top:6px;box-shadow:0 0 24px #19e3ff40;backdrop-filter:blur(8px)}
@media (min-width:721px){.savebar{bottom:14px}}
ol.steps{margin:8px 0 0;padding-inline-start:20px;color:var(--mut);font-size:13.5px}
ol.steps li{margin-bottom:4px}
code{direction:ltr;unicode-bidi:isolate;background:#050711;border:1px solid var(--rule);color:var(--cyan);padding:1px 6px;border-radius:5px;font-size:12.5px}

/* ---------- نافذة التأكيد + إشعار ---------- */
.modal{position:fixed;inset:0;z-index:20;background:#02030acc;backdrop-filter:blur(4px);display:grid;place-items:end center;padding:0}
@media (min-width:721px){.modal{place-items:center}}
.sheet{width:100%;max-width:420px;background:var(--plate);border:1px solid #19e3ff55;border-radius:16px 16px 0 0;padding:20px;
  box-shadow:0 0 40px #19e3ff30;animation:up .2s ease-out}
@media (min-width:721px){.sheet{border-radius:14px}}
.sheet h3{margin:0 0 6px;font-size:17px;font-weight:800}
.sheet .acts{margin-top:18px;justify-content:flex-end}
@keyframes up{from{transform:translateY(24px);opacity:0}to{transform:none;opacity:1}}
.toast{position:fixed;left:50%;bottom:calc(84px + env(safe-area-inset-bottom));transform:translate(-50%,10px);background:#0d1330;color:var(--text);
  border:1px solid var(--cyan);box-shadow:0 0 22px #19e3ff55;padding:10px 20px;border-radius:99px;font-size:14px;max-width:90vw;
  opacity:0;pointer-events:none;transition:.25s;z-index:30}
.toast.show{opacity:1;transform:translate(-50%,0)}
.skeleton{height:62px;border-radius:var(--r);background:linear-gradient(90deg,var(--plate),var(--plate2),var(--plate));
  background-size:200% 100%;animation:sk 1.2s infinite;margin-bottom:8px}
@keyframes sk{to{background-position:-200% 0}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
</head>
<body>

<!-- تسجيل الدخول -->
<section id="login" class="login">
  <div class="login-box">
    <svg class="mark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"><path d="M12 2.5l8 3v6c0 5-3.4 9.2-8 10.5-4.6-1.3-8-5.5-8-10.5v-6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/></svg>
    <h1>إدارة التراخيص</h1>
    <p class="mut">ادخل بالتوكن الخاص بالسيرفر (ADMIN_TOKEN).</p>
    <label for="tokenInput">التوكن</label>
    <input id="tokenInput" type="password" class="ltr" autocomplete="off" autocapitalize="off" spellcheck="false">
    <label class="remember"><input id="remember" type="checkbox"> تذكّرني على هذا الجهاز</label>
    <button id="loginBtn" class="btn-main btn-block">دخول</button>
    <div id="loginMsg" class="err" role="alert"></div>
  </div>
</section>

<!-- التطبيق -->
<div id="app" class="hide">
  <header class="bar"><div class="bar-in">
    <div class="brand">
      <svg class="mark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"><path d="M12 2.5l8 3v6c0 5-3.4 9.2-8 10.5-4.6-1.3-8-5.5-8-10.5v-6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/></svg>
      <div><b>إدارة التراخيص</b><small id="srv"><span class="dot warn"></span>جارٍ الفحص…</small></div>
    </div>
    <nav class="tabs" role="tablist" id="tabs">
      <button class="tab" role="tab" data-tab="licenses" aria-selected="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M4 6h16M4 12h16M4 18h10"/></svg>الأكواد</button>
      <button class="tab" role="tab" data-tab="create" aria-selected="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="12" cy="12" r="8.5"/><path d="M12 8v8M8 12h8"/></svg>إنشاء</button>
      <button class="tab" role="tab" data-tab="settings" aria-selected="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><path d="M5 7h9M18 7h1M5 17h1M10 17h9"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/></svg>الإعدادات</button>
    </nav>
    <button id="logoutBtn" class="btn-ghost btn-sm">خروج</button>
  </div></header>

  <main class="wrap">

    <!-- الأكواد -->
    <section id="tab-licenses">
      <div class="strip">
        <div><b id="sActive" class="c-moss num">0</b><span>نشط</span></div>
        <div><b id="sSoon" class="c-sand num">0</b><span>ينتهي خلال 3 أيام</span></div>
        <div><b id="sExpired" class="c-rust num">0</b><span>منتهي</span></div>
        <div><b id="sBanned" class="c-crim num">0</b><span>محظور</span></div>
      </div>
      <div class="tools">
        <input id="search" type="text" placeholder="ابحث بالكود أو اسم العميل" aria-label="بحث">
        <select id="sort" aria-label="الترتيب">
          <option value="new">الأحدث</option>
          <option value="exp">الأقرب انتهاءً</option>
          <option value="seen">آخر ظهور</option>
        </select>
        <button id="refreshBtn" class="btn-ghost">تحديث</button>
      </div>
      <div class="chips" id="chips"></div>
      <div id="list"></div>
      <p class="hint">الأكواد تُحفظ على السيرفر مشفّرة. تظهر نصوص الأكواد هنا فقط لما أنشأتَه من هذا المتصفح، وغيرها يظهر بمعرّفه.
        <a href="#" id="clearVault" class="mut">مسح الأكواد المحفوظة محلياً</a></p>
    </section>

    <!-- إنشاء -->
    <section id="tab-create" class="hide">
      <h2>إنشاء أكواد</h2>
      <p class="sub">الكود يظهر مرة واحدة بعد الإنشاء، انسخه أو أرسله للعميل مباشرة.</p>
      <div class="panel">
        <div class="grid">
          <div class="full">
            <label>مدة الاشتراك</label>
            <div class="seg" id="durSeg">
              <button data-v="week" aria-pressed="false">أسبوع</button>
              <button data-v="month" aria-pressed="true">شهر</button>
              <button data-v="2.5months" aria-pressed="false">75 يوم</button>
              <button data-v="custom" aria-pressed="false">مخصص</button>
            </div>
          </div>
          <div id="daysBox" class="full hide">
            <label for="days">عدد الأيام</label>
            <input id="days" type="number" min="1" max="3650" value="45" inputmode="numeric">
          </div>
          <div>
            <label for="count">عدد الأكواد</label>
            <div class="stepper"><button data-step="count:-1" aria-label="أنقص">−</button><input id="count" type="number" min="1" max="50" value="1" inputmode="numeric"><button data-step="count:1" aria-label="زِد">+</button></div>
          </div>
          <div>
            <label for="maxdev">الأجهزة المسموحة لكل كود</label>
            <div class="stepper"><button data-step="maxdev:-1" aria-label="أنقص">−</button><input id="maxdev" type="number" min="1" max="10" value="1" inputmode="numeric"><button data-step="maxdev:1" aria-label="زِد">+</button></div>
          </div>
          <div class="full">
            <label for="note">اسم العميل أو ملاحظة</label>
            <input id="note" type="text" maxlength="100" placeholder="مثال: أحمد - واتساب">
          </div>
          <div class="full">
            <label for="ckey">كود مخصص (اختياري، لكود واحد فقط)</label>
            <input id="ckey" type="text" class="ltr" autocapitalize="characters" placeholder="مثال: TARE-VIP">
          </div>
          <div class="full"><button id="createBtn" class="btn-main btn-block">إنشاء الأكواد</button></div>
        </div>
        <div id="result" class="result hide"></div>
      </div>
    </section>

    <!-- الإعدادات -->
    <section id="tab-settings" class="hide">
      <h2>الإعدادات</h2>
      <p class="sub">تُطبَّق فوراً على كل المستخدمين بدون إعادة نشر أو بناء للتطبيق.</p>

      <div class="panel">
        <h3>ملف الباتش <span id="patchPill" class="pill"></span></h3>
        <p class="sub">هنا تضع رابط الباتش. يصل للتطبيق بعد التحقق من الكود فقط.</p>
        <div class="grid">
          <div class="full">
            <label for="f_patch_url">رابط التحميل المباشر</label>
            <input id="f_patch_url" data-k="patch_url" type="url" class="ltr" placeholder="https://…" autocomplete="off">
          </div>
          <div>
            <label for="f_patch_version">رقم الباتش</label>
            <input id="f_patch_version" data-k="patch_version" type="text" class="ltr" placeholder="1">
            <p class="hint">غيّر الرقم عند كل باتش جديد ليعرف التطبيق أن هناك تحديثاً.</p>
          </div>
          <div>
            <label for="f_patch_file_name">اسم الملف داخل اللعبة</label>
            <input id="f_patch_file_name" data-k="patch_file_name" type="text" class="ltr" placeholder="اتركه فارغاً للاسم الافتراضي">
          </div>
          <div class="full">
            <label for="f_game_package">حزمة اللعبة</label>
            <input id="f_game_package" data-k="game_package" type="text" class="ltr" placeholder="com.tencent.ig">
          </div>
          <div class="full">
            <div class="sw"><div><b>تحديث الباتش الإلزامي</b><small>عند تغيّر رقم الباتش يحمّله التطبيق ويثبّته تلقائياً عند الفتح.</small></div>
              <input type="checkbox" data-k="force_patch_update" aria-label="تحديث إلزامي"></div>
          </div>
        </div>
      </div>

      <div class="panel">
        <h3>التطبيق والإعلانات</h3>
        <p class="sub">إعلان يظهر أعلى التطبيق، ورابط الدعم، وفرض تحديث التطبيق.</p>
        <div class="grid">
          <div class="full">
            <label for="f_notice">نص الإعلان</label>
            <textarea id="f_notice" data-k="notice" maxlength="300" placeholder="مثال: تم تحديث الباتش للإصدار الجديد."></textarea>
          </div>
          <div class="full">
            <label for="f_support_url">رابط الدعم</label>
            <input id="f_support_url" data-k="support_url" type="url" class="ltr" placeholder="https://t.me/…">
          </div>
          <div>
            <label for="f_min_app_version">أقل نسخة تطبيق مسموحة</label>
            <input id="f_min_app_version" data-k="min_app_version" type="text" class="ltr" placeholder="1.3.0">
            <p class="hint">أي نسخة أقدم تُمنع من التفعيل.</p>
          </div>
          <div>
            <label for="f_update_url">رابط تحميل التطبيق الجديد</label>
            <input id="f_update_url" data-k="update_url" type="url" class="ltr" placeholder="https://…/app.apk">
          </div>
          <div class="full">
            <div class="sw"><div><b>وضع الصيانة</b><small>يوقف التفعيل مؤقتاً ويعرض الإعلان للمستخدمين.</small></div>
              <input type="checkbox" data-k="maintenance" aria-label="وضع الصيانة"></div>
          </div>
        </div>
      </div>

      <div class="savebar hide" id="savebar">
        <span>لديك تغييرات غير محفوظة</span>
        <span style="display:flex;gap:8px"><button id="discardBtn" class="btn-ghost btn-sm">تراجع</button><button id="saveBtn" class="btn-main btn-sm">حفظ</button></span>
      </div>

      <div class="panel">
        <h3>بوت تيليجرام <span id="tgPill" class="pill"></span></h3>
        <p class="sub">أنشئ الأكواد وأدر المشتركين من تيليجرام، وتصلك رسالة عند كل تفعيل جديد.</p>
        <ol class="steps">
          <li>أنشئ بوتاً من <code>@BotFather</code> وانسخ التوكن.</li>
          <li>في Vercel أضف <code>TELEGRAM_BOT_TOKEN</code> و<code>TELEGRAM_ADMIN_IDS</code> (معرّفك الرقمي، ويمكنك معرفته بإرسال /start للبوت)، ثم أعد النشر.</li>
          <li>اضغط «ربط البوت» أدناه، ثم أرسل <code>/help</code> للبوت.</li>
        </ol>
        <div class="acts" style="margin-top:14px"><button id="tgBtn" class="btn-main">ربط البوت</button></div>
      </div>
    </section>
  </main>
</div>

<div id="modal" class="modal hide" role="dialog" aria-modal="true"><div class="sheet" id="sheet"></div></div>
<div id="toast" class="toast" role="status"></div>

<script>
(()=>{
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const K_VAULT='pak_vault', K_TOKEN='pak_token';
const STATUS={active:'نشط',expired:'منتهي',banned:'محظور'};
const TYPES={week:'أسبوع',month:'شهر','2.5months':'75 يوم'};
let token='', rows=[], filter='all', openId=null, dur='month';
let saved={}, dirty=false;

/* ---------- أدوات ---------- */
function h(tag,props={},...kids){
  const e=document.createElement(tag);
  for(const [k,v] of Object.entries(props||{})){
    if(v==null||v===false)continue;
    if(k==='class')e.className=v;
    else if(k.startsWith('on'))e.addEventListener(k.slice(2),v);
    else e.setAttribute(k,v===true?(k.startsWith('aria-')?'true':''):v);
  }
  for(const c of kids.flat()){if(c==null||c===false)continue;e.append(c.nodeType?c:document.createTextNode(c));}
  return e;
}
let toastT;
function toast(t){const el=$('#toast');el.textContent=t;el.classList.add('show');clearTimeout(toastT);toastT=setTimeout(()=>el.classList.remove('show'),2600);}
async function copy(text,msg){
  try{await navigator.clipboard.writeText(text);}
  catch{const t=h('textarea',{style:'position:fixed;opacity:0'});t.value=text;document.body.append(t);t.select();document.execCommand('copy');t.remove();}
  toast(msg||'تم النسخ');
}
const vault=()=>{try{return JSON.parse(localStorage.getItem(K_VAULT)||'{}')}catch{return {}}};
const saveVault=v=>localStorage.setItem(K_VAULT,JSON.stringify(v));
const fmtDate=s=>s?s.slice(0,10):'—';
const fmtSeen=s=>s?s.replace('T',' ').slice(0,16):'لم يظهر بعد';

async function api(path,method='GET',body){
  const r=await fetch(path,{method,headers:{'Authorization':'Bearer '+token,'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});
  let d={};try{d=await r.json()}catch{}
  if(r.status===401){logout('انتهت الجلسة أو التوكن غير صحيح');throw new Error('Unauthorized');}
  if(r.status===429)throw new Error('محاولات كثيرة، انتظر دقيقة');
  if(!r.ok||d.success===false)throw new Error(d.message||('خطأ '+r.status));
  return d;
}
const quiet=e=>{if(e.message!=='Unauthorized')toast(e.message);};

/* نافذة تأكيد بدل confirm/prompt */
function ask({title,body,ok='تأكيد',danger=false,content}){
  return new Promise(res=>{
    const done=v=>{$('#modal').classList.add('hide');$('#sheet').replaceChildren();document.removeEventListener('keydown',esc);res(v);};
    const esc=e=>{if(e.key==='Escape')done(null);};
    const okBtn=h('button',{class:danger?'btn-solid-danger':'btn-main',onclick:()=>done(content?content.value():true)},ok);
    $('#sheet').replaceChildren(h('h3',{},title),body?h('p',{class:'mut',style:'margin:0'},body):null,content?content.el:null,
      h('div',{class:'acts'},h('button',{class:'btn-ghost',onclick:()=>done(null)},'إلغاء'),okBtn));
    $('#modal').classList.remove('hide');document.addEventListener('keydown',esc);
    setTimeout(()=>(content&&content.focus?content.focus():okBtn).focus(),30);
  });
}

/* ---------- الدخول ---------- */
function showApp(){$('#login').classList.add('hide');$('#app').classList.remove('hide');}
function logout(msg){
  token='';sessionStorage.removeItem(K_TOKEN);localStorage.removeItem(K_TOKEN);
  $('#app').classList.add('hide');$('#login').classList.remove('hide');
  $('#tokenInput').value='';$('#loginMsg').textContent=msg||'';
}
const tryToken=async t=>(await fetch('/api/admin/list',{headers:{Authorization:'Bearer '+t}})).status;
async function login(){
  const raw=$('#tokenInput').value.trim(), msg=$('#loginMsg');
  if(!raw){msg.textContent='أدخل التوكن';return;}
  $('#loginBtn').disabled=true;msg.textContent='';
  try{
    for(const c of new Set([raw,raw.replace(/\s+/g,'')])){
      const st=await tryToken(c);
      if(st===200){token=c;($('#remember').checked?localStorage:sessionStorage).setItem(K_TOKEN,c);await enter();return;}
      if(st===503){msg.textContent='ADMIN_TOKEN غير مضبوط على السيرفر (24 حرفاً على الأقل).';return;}
      if(st===429){msg.textContent='محاولات كثيرة، انتظر دقيقة.';return;}
    }
    msg.textContent='التوكن غير صحيح.';
  }catch{msg.textContent='تعذر الاتصال بالسيرفر.';}
  finally{$('#loginBtn').disabled=false;}
}
async function enter(){
  showApp();
  $('#list').replaceChildren(h('div',{class:'skeleton'}),h('div',{class:'skeleton'}),h('div',{class:'skeleton'}));
  checkHealth();load();loadSettings();
}
async function checkHealth(){
  const el=$('#srv');
  try{
    const d=await (await fetch('/api/health')).json();
    el.replaceChildren(h('span',{class:'dot'+(d.storage==='redis'?'':' warn')}),d.storage==='redis'?'السيرفر متصل · تخزين دائم':'تخزين مؤقت! الأكواد ستضيع');
  }catch{el.replaceChildren(h('span',{class:'dot bad'}),'السيرفر لا يستجيب');}
}

/* ---------- التبويبات ---------- */
function tab(name){
  $$('.tab').forEach(b=>b.setAttribute('aria-selected',b.dataset.tab===name));
  ['licenses','create','settings'].forEach(n=>$('#tab-'+n).classList.toggle('hide',n!==name));
  window.scrollTo({top:0});
}
$('#tabs').addEventListener('click',e=>{const b=e.target.closest('.tab');if(b)tab(b.dataset.tab);});

/* ---------- الأكواد ---------- */
async function load(){
  try{const d=await api('/api/admin/list');rows=d.licenses||[];render();}
  catch(e){quiet(e);}
}
const daysLeft=r=>Math.ceil((new Date(r.expires_at)-Date.now())/864e5);
const isSoon=r=>r.status==='active'&&daysLeft(r)<=3;
function leftText(r){
  if(r.status==='banned')return 'موقوف';
  const d=daysLeft(r);
  if(d>1)return `متبقي ${d} يوم`;
  if(d===1)return 'ينتهي غداً';
  if(d===0)return 'ينتهي اليوم';
  return `انتهى منذ ${-d} يوم`;
}
function meterPct(r){
  if(r.status!=='active')return r.status==='banned'?100:0;
  const exp=new Date(r.expires_at), start=r.created?new Date(r.created):null;
  if(!start)return 50;
  return Math.max(2,Math.min(100,(exp-Date.now())/(exp-start)*100));
}
function render(){
  const c={active:0,soon:0,expired:0,banned:0};
  rows.forEach(r=>{c[r.status]=(c[r.status]||0)+1;if(isSoon(r))c.soon++;});
  $('#sActive').textContent=c.active;$('#sSoon').textContent=c.soon;$('#sExpired').textContent=c.expired;$('#sBanned').textContent=c.banned;

  $('#chips').replaceChildren(...[['all','الكل',rows.length],['active','نشط',c.active],['expired','منتهي',c.expired],['banned','محظور',c.banned]]
    .map(([k,t,n])=>h('button',{class:'chip','aria-pressed':filter===k,onclick:()=>{filter=k;render();}},`${t} (${n})`)));

  const q=$('#search').value.trim().toLowerCase(), v=vault(), sort=$('#sort').value;
  let view=rows.filter(r=>(filter==='all'||r.status===filter)&&(!q||(r.id+' '+(v[r.id]||'')+' '+(r.note||'')).toLowerCase().includes(q)));
  view.sort(sort==='exp'?(a,b)=>a.expires_at.localeCompare(b.expires_at)
    :sort==='seen'?(a,b)=>(b.last_seen||'').localeCompare(a.last_seen||'')
    :(a,b)=>(b.created||'').localeCompare(a.created||''));
  const list=$('#list');list.replaceChildren();
  if(!view.length){
    list.append(rows.length?h('div',{class:'empty'},h('b',{},'لا نتائج'),'جرّب بحثاً أو تصنيفاً آخر.')
      :h('div',{class:'empty'},h('b',{},'لا توجد أكواد بعد'),'اذهب إلى «إنشاء» لتصنع أول كود.',h('div',{style:'margin-top:12px'},h('button',{class:'btn-main btn-sm',onclick:()=>tab('create')},'إنشاء كود'))));
    return;
  }
  view.forEach(r=>list.append(card(r,v[r.id])));
}
function card(r,key){
  const open=openId===r.id;
  const act=(label,cls,fn)=>h('button',{class:'btn-sm '+cls,onclick:fn},label);
  const head=h('button',{class:'lic-head','aria-expanded':open,onclick:()=>{openId=open?null:r.id;render();}},
    h('div',{class:'who'},h('span',{class:'id'},key||('ID '+r.id)),h('span',{class:'nm'},r.note||TYPES[r.type]||r.type)),
    h('div',{class:'right'},h('span',{class:'badge b-'+r.status},STATUS[r.status]||r.status),h('span',{class:'left num'},leftText(r))));
  const body=open?h('div',{class:'lic-body'},
    h('dl',{class:'kv'},
      h('div',{},h('dt',{},'المدة'),h('dd',{},TYPES[r.type]||r.type)),
      h('div',{},h('dt',{},'ينتهي في'),h('dd',{class:'num'},fmtDate(r.expires_at))),
      h('div',{},h('dt',{},'الأجهزة'),h('dd',{class:'num'},`${r.devices} من ${r.max_devices}`)),
      h('div',{},h('dt',{},'عدد مرات التحقق'),h('dd',{class:'num'},r.checks)),
      h('div',{},h('dt',{},'آخر ظهور'),h('dd',{class:'num'},fmtSeen(r.last_seen))),
      h('div',{},h('dt',{},'تاريخ الإنشاء'),h('dd',{class:'num'},fmtDate(r.created)))),
    h('div',{class:'acts'},
      key&&act('نسخ الكود','btn-main',()=>copy(key)),
      key&&act('نسخ رسالة للعميل','',()=>copy(`كود التفعيل: ${key}\nصالح حتى: ${fmtDate(r.expires_at)}`)),
      !key&&act('نسخ المعرّف','',()=>copy(r.id)),
      act('تمديد','',()=>extend(r)),
      act('إعادة ضبط الجهاز','',()=>control(r,'reset_devices',{},'إعادة ضبط الجهاز','سيتمكن العميل من تفعيل الكود على جهاز جديد.')),
      r.status==='banned'?act('فك الحظر','',()=>control(r,'unban')):act('حظر','btn-danger',()=>control(r,'ban',{},'حظر الكود','لن يعمل هذا الكود حتى تفك الحظر.',true)),
      act('حذف','btn-danger',()=>control(r,'delete',{},'حذف نهائي','سيُحذف الكود من السيرفر ولا يمكن استرجاعه.',true))))
    :null;
  return h('article',{class:'lic st-'+r.status+(isSoon(r)?' soon':'')},head,
    h('div',{class:'meter'},h('i',{style:`width:${meterPct(r)}%`})),body);
}
async function control(r,action,extra={},title,body,danger){
  if(title&&!(await ask({title,body,ok:title.split(' ')[0],danger})))return;
  try{
    const d=await api('/api/admin/control','POST',{id:r.id,action,...extra});toast(d.message||'تم');
    if(action==='delete'){const v=vault();delete v[r.id];saveVault(v);openId=null;}
    await load();
  }catch(e){quiet(e);}
}
async function extend(r){
  const inp=h('input',{type:'number',min:1,max:3650,value:30,inputmode:'numeric'});
  const chips=h('div',{class:'chips',style:'margin:12px 0 8px'},...[7,30,75].map(n=>h('button',{class:'chip',onclick:()=>{inp.value=n;}},`${n} يوم`)));
  const wrap=h('div',{},chips,h('label',{},'عدد الأيام المضافة'),inp);
  const val=await ask({title:'تمديد الاشتراك',ok:'تمديد',content:{el:wrap,value:()=>parseInt(inp.value,10),focus:()=>inp.select()}});
  if(val>0)control(r,'extend',{days:val});
}

/* ---------- الإنشاء ---------- */
$('#durSeg').addEventListener('click',e=>{
  const b=e.target.closest('button');if(!b)return;dur=b.dataset.v;
  $$('#durSeg button').forEach(x=>x.setAttribute('aria-pressed',x===b));
  $('#daysBox').classList.toggle('hide',dur!=='custom');
});
$$('[data-step]').forEach(b=>b.addEventListener('click',()=>{
  const [id,d]=b.dataset.step.split(':'),el=$('#'+id),min=+el.min,max=+el.max;
  el.value=Math.min(max,Math.max(min,(parseInt(el.value,10)||min)+(+d)));
}));
async function create(){
  const body={};
  if(dur==='custom')body.days=parseInt($('#days').value,10);else body.type=dur;
  body.count=parseInt($('#count').value,10)||1;
  body.max_devices=parseInt($('#maxdev').value,10)||1;
  const note=$('#note').value.trim(), ck=$('#ckey').value.trim();
  if(note)body.note=note;if(ck)body.key=ck;
  $('#createBtn').disabled=true;
  try{
    const d=await api('/api/admin/add','POST',body);
    const v=vault();d.keys.forEach(k=>v[k.id]=k.key);saveVault(v);
    const exp=fmtDate(d.keys[0]&&d.keys[0].expires_at);
    $('#result').classList.remove('hide');
    $('#result').replaceChildren(
      h('b',{},`تم إنشاء ${d.keys.length} كود · ينتهي ${exp}`),
      ...d.keys.map(k=>h('div',{class:'row'},h('span',{class:'id'},k.key),h('span',{class:'acts'},
        h('button',{class:'btn-sm btn-main',onclick:()=>copy(k.key)},'نسخ'),
        h('button',{class:'btn-sm',onclick:()=>copy(`كود التفعيل: ${k.key}\nصالح حتى: ${exp}`,'تم نسخ الرسالة')},'رسالة')))),
      d.keys.length>1?h('div',{style:'margin-top:10px'},h('button',{class:'btn-sm',onclick:()=>copy(d.keys.map(k=>k.key).join('\n'),'تم نسخ كل الأكواد')},'نسخ الكل')):null);
    $('#ckey').value='';$('#note').value='';
    load();
  }catch(e){quiet(e);}
  finally{$('#createBtn').disabled=false;}
}

/* ---------- الإعدادات ---------- */
const fields=()=>$$('[data-k]');
function readForm(){const o={};fields().forEach(el=>{o[el.dataset.k]=el.type==='checkbox'?el.checked:el.value.trim();});return o;}
function fillForm(s){
  fields().forEach(el=>{const v=s[el.dataset.k];if(el.type==='checkbox')el.checked=!!v;else el.value=v==null?'':v;});
  saved=readForm();markDirty();
  const ok=!!s.patch_url;
  $('#patchPill').replaceChildren(h('span',{class:'dot'+(ok?'':' bad')}),ok?'الرابط مضبوط':'الرابط غير مضبوط');
}
function markDirty(){
  const now=readForm();dirty=JSON.stringify(now)!==JSON.stringify(saved);
  $('#savebar').classList.toggle('hide',!dirty);
}
async function loadSettings(){
  try{
    const d=await api('/api/admin/settings');fillForm(d.settings);
    const t=d.telegram||{};
    $('#tgPill').replaceChildren(h('span',{class:'dot'+(t.configured&&t.admins?'':(t.configured?' warn':' bad'))}),
      t.configured?(t.admins?'جاهز':'أضف TELEGRAM_ADMIN_IDS'):'غير مضبوط');
  }catch(e){quiet(e);}
}
async function saveSettings(){
  $('#saveBtn').disabled=true;
  try{const d=await api('/api/admin/settings','POST',readForm());toast('تم حفظ الإعدادات');fillForm(d.settings);}
  catch(e){quiet(e);}
  finally{$('#saveBtn').disabled=false;}
}
async function tgSetup(){
  $('#tgBtn').disabled=true;
  try{const d=await api('/api/admin/telegram/setup','POST');toast(d.message);loadSettings();}
  catch(e){quiet(e);}
  finally{$('#tgBtn').disabled=false;}
}

/* ---------- ربط الأحداث ---------- */
$('#loginBtn').onclick=login;
$('#tokenInput').addEventListener('keydown',e=>{if(e.key==='Enter')login();});
$('#logoutBtn').onclick=()=>logout('');
$('#refreshBtn').onclick=()=>{load();checkHealth();};
$('#createBtn').onclick=create;
$('#search').addEventListener('input',render);
$('#sort').addEventListener('change',render);
$('#saveBtn').onclick=saveSettings;
$('#discardBtn').onclick=()=>fillForm(saved);
$('#tgBtn').onclick=tgSetup;
fields().forEach(el=>el.addEventListener('input',markDirty));
$('#modal').addEventListener('click',e=>{if(e.target.id==='modal'){const b=$('#sheet').querySelector('.btn-ghost');b&&b.click();}});
$('#clearVault').onclick=async e=>{e.preventDefault();
  if(await ask({title:'مسح الأكواد المحفوظة',body:'يمسح النصوص المحفوظة في هذا المتصفح فقط، ولا يؤثر على السيرفر.',ok:'مسح'})){localStorage.removeItem(K_VAULT);render();toast('تم المسح');}};
window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue='';}});

/* ---------- البدء ---------- */
(async()=>{
  const s=sessionStorage.getItem(K_TOKEN)||localStorage.getItem(K_TOKEN);
  if(!s)return;
  try{if(await tryToken(s)===200){token=s;await enter();}else logout('');}catch{}
})();
})();
</script>
</body>
</html>
"""
