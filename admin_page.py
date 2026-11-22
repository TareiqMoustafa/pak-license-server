"""لوحة تحكم Lader Tareiq: صفحة واحدة (HTML+CSS+JS) تُخدَّم من /admin وتتصل بواجهات /api/admin."""

ADMIN_HTML = r"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#05070E">
<title>Lader Tareiq — إدارة التراخيص وOTA</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&family=Orbitron:wght@600;800&display=swap">
<style>
:root{
  --ink:#05070E;--bg2:#0B1024;--plate:#0C1124;--plate2:#131B38;--rule:#1E2A4F;
  --text:#EEF3FF;--mut:#8693BA;
  --cyan:#19E3FF;--violet:#8B5CFF;--pink:#FF2E93;--green:#38FFA2;--amber:#FFB020;
  --cyan-ink:#031318;
  --r:14px;
  --glow:0 0 0 1px #19e3ff55,0 0 22px #19e3ff38;
}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html{color-scheme:dark}
body{margin:0;color:var(--text);min-height:100vh;
  font:15px/1.65 "Tajawal","IBM Plex Sans Arabic",system-ui,-apple-system,"Segoe UI",Tahoma,sans-serif;
  background:
    radial-gradient(950px 520px at 88% -8%,#8b5cff2c,transparent 62%),
    radial-gradient(760px 500px at -8% 12%,#19e3ff24,transparent 62%),
    radial-gradient(840px 520px at 50% 118%,#ff2e931a,transparent 62%),
    linear-gradient(180deg,var(--ink),var(--bg2));
  background-attachment:fixed;
  padding-bottom:calc(82px + env(safe-area-inset-bottom))}
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.45;
  background-image:linear-gradient(#ffffff08 1px,transparent 1px),linear-gradient(90deg,#ffffff08 1px,transparent 1px);
  background-size:44px 44px;
  -webkit-mask-image:radial-gradient(ellipse at 50% 0%,#000 12%,transparent 78%);
  mask-image:radial-gradient(ellipse at 50% 0%,#000 12%,transparent 78%)}
#app,#login{position:relative;z-index:1}
button,input,select,textarea{font:inherit;color:inherit}
.hide{display:none!important}
.mut{color:var(--mut)}
.num{font-variant-numeric:tabular-nums}
.ltr{direction:ltr;unicode-bidi:plaintext;text-align:left}
:focus-visible{outline:2px solid var(--cyan);outline-offset:2px}

button{border-radius:12px;padding:9px 16px;cursor:pointer;background:var(--plate2);
  border:1px solid var(--rule);transition:background .15s,transform .1s,box-shadow .2s,border-color .2s}
button:hover{border-color:#19e3ff77;box-shadow:0 0 16px #19e3ff26}
button:active{transform:scale(.97)}
button:disabled{opacity:.45;cursor:not-allowed;box-shadow:none}
.btn-main{background:linear-gradient(135deg,var(--cyan),#5aa9ff 52%,var(--violet));color:var(--cyan-ink);
  border-color:transparent;font-weight:800;box-shadow:0 0 22px #19e3ff42}
.btn-main:hover{box-shadow:0 0 28px #19e3ff80,0 0 12px #8b5cff77;border-color:transparent;filter:brightness(1.06)}
.btn-danger{color:var(--pink);border-color:#ff2e934d;background:#1b0b18}
.btn-danger:hover{background:#2b0e24;border-color:var(--pink);box-shadow:0 0 16px #ff2e9344}
.btn-solid-danger{background:linear-gradient(135deg,var(--pink),#ff5d5d);border-color:transparent;color:#1a0210;font-weight:800;
  box-shadow:0 0 20px #ff2e9355}
.btn-ghost{background:transparent}
.btn-sm{padding:6px 12px;font-size:13.5px}
.btn-block{width:100%;padding:13px;font-size:16px}
label{display:block;font-size:13px;color:var(--mut);margin:0 0 5px}
input[type=text],input[type=password],input[type=number],input[type=url],select,textarea{
  width:100%;background:#05070E;border:1px solid var(--rule);border-radius:12px;padding:10px 12px;transition:border-color .2s,box-shadow .2s}
textarea{resize:vertical;min-height:70px}
input:focus,select:focus,textarea:focus{border-color:var(--cyan);outline:none;box-shadow:0 0 0 3px #19e3ff22,0 0 18px #19e3ff30}
.hint{font-size:12.5px;color:var(--mut);margin:5px 0 0}
a{color:var(--cyan)}

.login{min-height:100vh;display:grid;place-items:center;padding:20px}
.login-box{width:100%;max-width:400px;padding:30px 24px;border-radius:18px;background:#0c1124f0;position:relative;
  border:1px solid #19e3ff4d;box-shadow:0 0 42px #8b5cff26,inset 0 0 30px #19e3ff0e}
.login-box::before{content:"";position:absolute;inset:-1px;border-radius:18px;padding:1px;pointer-events:none;
  background:linear-gradient(135deg,var(--cyan),var(--violet) 50%,var(--pink));
  -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;
  mask:linear-gradient(#000 0 0) content-box exclude,linear-gradient(#000 0 0)}
.mark{width:50px;height:50px;color:var(--cyan);filter:drop-shadow(0 0 10px #19e3ffaa)}
.login h1{font-size:25px;margin:14px 0 4px;font-weight:800;
  background:linear-gradient(90deg,#fff,var(--cyan),var(--violet));-webkit-background-clip:text;background-clip:text;color:transparent}
.login p{margin:0 0 22px}
.remember{display:flex;gap:8px;align-items:center;margin:12px 0 16px;color:var(--mut);font-size:13.5px}
.remember input{width:18px;height:18px;accent-color:var(--cyan)}
.err{color:var(--pink);font-size:13.5px;min-height:22px;margin-top:10px}

.bar{position:sticky;top:0;z-index:5;background:#05070ee0;backdrop-filter:blur(14px);
  border-bottom:1px solid #19e3ff33;padding:max(10px,env(safe-area-inset-top)) 16px 10px;
  box-shadow:0 1px 26px #19e3ff14}
.bar-in{max-width:980px;margin:0 auto;display:flex;align-items:center;gap:14px}
.brand{display:flex;align-items:center;gap:10px;margin-inline-end:auto}
.brand .mark{width:34px;height:34px}
.brand b{display:block;font-size:16px;line-height:1.2;font-weight:800;color:var(--text)}
.brand small{display:block;font-size:11.5px;color:var(--mut);line-height:1.25}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--green);margin-inline-end:6px;box-shadow:0 0 8px var(--green)}
.dot.bad{background:var(--pink);box-shadow:0 0 8px var(--pink)}.dot.warn{background:var(--amber);box-shadow:0 0 8px var(--amber)}
.tabs{display:flex;gap:4px}
.tab{background:transparent;border:0;border-radius:12px;padding:8px 14px;color:var(--mut);display:flex;gap:8px;align-items:center;position:relative;box-shadow:none}
.tab svg{width:18px;height:18px}
.tab:hover{color:var(--text);background:var(--plate);box-shadow:none}
.tab[aria-selected=true]{color:var(--cyan);background:#19e3ff14;text-shadow:0 0 12px #19e3ff88}
.tab[aria-selected=true]::after{content:"";position:absolute;inset-inline:14px;bottom:2px;height:2px;border-radius:2px;
  background:linear-gradient(90deg,var(--cyan),var(--violet));box-shadow:0 0 10px var(--cyan)}
.wrap{max-width:980px;margin:0 auto;padding:18px 16px}
h2{font-size:20px;margin:0 0 4px;font-weight:800}
.sub{color:var(--mut);font-size:13.5px;margin:0 0 16px}

@media (max-width:720px){
  .tabs{position:fixed;inset:auto 0 0 0;z-index:6;background:#05070ef5;backdrop-filter:blur(14px);
    border-top:1px solid #19e3ff33;padding:6px 10px calc(6px + env(safe-area-inset-bottom));justify-content:space-around;gap:0;
    box-shadow:0 -4px 24px #19e3ff14}
  .tab{flex-direction:column;gap:2px;font-size:12px;padding:6px 18px;flex:1}
  .tab svg{width:22px;height:22px}
  .tab[aria-selected=true]::after{bottom:0}
  .bar-in{gap:8px}
}

.strip{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:18px}
.strip>div{padding:12px 14px;background:linear-gradient(160deg,var(--plate2),var(--plate));border:1px solid var(--rule);
  border-radius:var(--r);position:relative;overflow:hidden}
.strip>div::before{content:"";position:absolute;inset-inline:0;top:0;height:2px;background:currentColor;opacity:.85;box-shadow:0 0 12px currentColor}
.strip>div:nth-child(1){color:var(--green)}.strip>div:nth-child(2){color:var(--cyan)}
.strip>div:nth-child(3){color:var(--amber)}.strip>div:nth-child(4){color:var(--pink)}
.strip b{display:block;font:800 30px/1.1 "Orbitron","Tajawal",sans-serif;text-shadow:0 0 16px currentColor}
.strip span{font-size:12.5px;color:var(--mut)}
@media (max-width:520px){.strip{gap:8px}.strip b{font-size:22px}.strip>div{padding:10px}}

.tools{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}
.tools input{flex:1 1 200px}
.tools select{width:auto;flex:0 0 auto}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}
.chip{border-radius:99px;padding:5px 14px;font-size:13.5px;background:transparent;color:var(--mut)}
.chip[aria-pressed=true]{background:#19e3ff1c;color:var(--cyan);border-color:var(--cyan);font-weight:700;box-shadow:0 0 14px #19e3ff40}

.lic{background:linear-gradient(160deg,var(--plate2),var(--plate));border:1px solid var(--rule);border-radius:var(--r);margin-bottom:10px;
  border-inline-start:4px solid var(--green);overflow:hidden;transition:border-color .2s,box-shadow .2s}
.lic:hover{border-color:#19e3ff4d;border-inline-start-color:var(--green)}
.lic{box-shadow:inset 4px 0 14px -8px var(--green)}
.lic.st-expired{border-inline-start-color:var(--amber);box-shadow:inset 4px 0 14px -8px var(--amber)}
.lic.st-banned{border-inline-start-color:var(--pink);box-shadow:inset 4px 0 14px -8px var(--pink)}
.lic.soon{border-inline-start-color:var(--cyan);box-shadow:inset 4px 0 14px -8px var(--cyan)}
.lic-head{all:unset;box-sizing:border-box;display:flex;width:100%;gap:12px;align-items:center;justify-content:space-between;
  padding:12px 14px;cursor:pointer}
.lic-head:focus-visible{outline:2px solid var(--cyan);outline-offset:-2px}
.lic-head:hover{background:#19e3ff0c}
.who{min-width:0}
.id{font-family:"Orbitron",ui-monospace,Menlo,Consolas,monospace;font-size:14px;letter-spacing:.04em;color:var(--cyan);direction:ltr;display:block;
  overflow-wrap:anywhere;text-shadow:0 0 10px #19e3ff66}
.nm{font-size:13px;color:var(--mut)}
.right{text-align:end;flex:none}
.badge{display:inline-block;font-size:12px;font-weight:700;padding:2px 11px;border-radius:99px;border:1px solid currentColor;box-shadow:0 0 10px -2px currentColor}
.b-active{color:var(--green)}.b-expired{color:var(--amber)}.b-banned{color:var(--pink)}
.rem{font-size:12.5px;color:var(--mut);margin-top:2px}
.lic-body{display:none;padding:12px 14px 14px;border-top:1px solid var(--rule);background:#070b18a6}
.lic.open .lic-body{display:block}
.meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px 14px;font-size:13.5px;margin-bottom:12px}
.meta small{display:block;color:var(--mut);font-size:12px}
.acts{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.acts input[type=number]{width:84px;padding:6px 8px}

.panel{background:linear-gradient(160deg,var(--plate2),var(--plate));border:1px solid var(--rule);border-radius:18px;padding:18px;margin-bottom:14px;
  box-shadow:0 4px 24px #00000044}
.panel h3{margin:0 0 2px;font-size:16px;font-weight:800}
.panel .sub{margin-bottom:14px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.grid .full{grid-column:1/-1}
@media (max-width:600px){.grid{grid-template-columns:1fr}}
.sw{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 12px;border:1px solid var(--rule);border-radius:12px;background:#05070E}
.sw small{display:block;color:var(--mut);font-size:12.5px}
.sw input[type=checkbox]{width:20px;height:20px;flex:none;accent-color:var(--cyan)}
.pill{display:inline-flex;align-items:center;font-size:12.5px;padding:2px 11px;border-radius:99px;border:1px solid var(--rule);color:var(--mut);margin-inline-start:8px;vertical-align:middle}
.steps{margin:10px 0 14px;padding-inline-start:20px;color:var(--mut);font-size:13.5px}
.steps li{margin:4px 0}
.steps code{color:var(--cyan);background:#05070E;padding:1px 6px;border-radius:6px;border:1px solid var(--rule)}

.result{background:#05070E;border:1px solid var(--cyan);border-radius:14px;padding:14px;margin-top:14px;box-shadow:var(--glow)}
.result .row{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 0;border-bottom:1px solid var(--rule)}
.result .row:last-child{border-bottom:0}
.result .id{font-size:15px}
.empty{text-align:center;color:var(--mut);padding:36px 16px;border:1px dashed var(--rule);border-radius:18px}

.savebar{position:sticky;bottom:14px;z-index:4;display:flex;align-items:center;justify-content:space-between;gap:12px;
  padding:12px 16px;border-radius:14px;background:var(--plate2);border:1px solid var(--cyan);box-shadow:0 8px 30px #0009,var(--glow)}
@media (max-width:720px){.savebar{bottom:calc(72px + env(safe-area-inset-bottom))}}

.toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%) translateY(16px);z-index:20;
  background:var(--plate2);border:1px solid var(--cyan);border-radius:99px;padding:9px 20px;font-size:14px;
  opacity:0;pointer-events:none;transition:opacity .18s,transform .18s;box-shadow:var(--glow);white-space:nowrap}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
@media (max-width:720px){.toast{bottom:calc(76px + env(safe-area-inset-bottom))}}

.dlg{position:fixed;inset:0;z-index:30;display:grid;place-items:center;padding:20px;background:#02040ab8;backdrop-filter:blur(6px)}
.dlg-box{width:100%;max-width:380px;background:var(--plate);border:1px solid var(--rule);border-radius:18px;padding:22px;box-shadow:0 24px 60px #000}
.dlg-box h3{margin:0 0 8px;font-size:17px}
.dlg-box p{margin:0 0 18px;color:var(--mut);font-size:14px;white-space:pre-line}
.dlg-acts{display:flex;gap:8px;justify-content:flex-end}
</style>
</head>
<body>

<section id="login" class="login">
  <div class="login-box">
    <svg class="mark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"><path d="M12 2.5l8 3v6c0 5-3.4 9.2-8 10.5-4.6-1.3-8-5.5-8-10.5v-6z"/><path d="M9 12l2 2 4-4"/></svg>
    <h1>Lader Tareiq</h1>
    <p class="mut">لوحة إدارة التراخيص والباتش وتحديثات OTA.</p>
    <label for="tokenInput">رمز الدخول (ADMIN_TOKEN)</label>
    <input id="tokenInput" type="password" class="ltr" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="••••••••••••">
    <label class="remember"><input id="remember" type="checkbox"> تذكّرني في هذا المتصفح</label>
    <button id="loginBtn" class="btn-main btn-block">دخول</button>
    <div id="loginErr" class="err" role="alert"></div>
  </div>
</section>

<div id="app" class="hide">
  <header class="bar">
    <div class="bar-in">
      <div class="brand">
        <svg class="mark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"><path d="M12 2.5l8 3v6c0 5-3.4 9.2-8 10.5-4.6-1.3-8-5.5-8-10.5v-6z"/><path d="M9 12l2 2 4-4"/></svg>
        <div><b>Lader Tareiq</b><small id="healthTxt"><span class="dot"></span>جاري الفحص…</small></div>
      </div>
      <nav class="tabs" role="tablist">
        <button class="tab" role="tab" aria-selected="true" data-tab="keys">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>
          <span>الأكواد</span>
        </button>
        <button class="tab" role="tab" aria-selected="false" data-tab="add">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 8v8M8 12h8"/></svg>
          <span>إنشاء</span>
        </button>
        <button class="tab" role="tab" aria-selected="false" data-tab="settings">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l-.06-.06a1.65 1.65 0 0 0-.33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
          <span>الإعدادات</span>
        </button>
      </nav>
      <button id="refreshBtn" class="btn-ghost btn-sm" title="تحديث">تحديث</button>
      <button id="logoutBtn" class="btn-ghost btn-sm">خروج</button>
    </div>
  </header>

  <main class="wrap">
    <section id="tab-keys">
      <div class="strip">
        <div><b id="stActive" class="num">0</b><span>نشط</span></div>
        <div><b id="stSoon" class="num">0</b><span>ينتهي قريباً</span></div>
        <div><b id="stExp" class="num">0</b><span>منتهي</span></div>
        <div><b id="stBan" class="num">0</b><span>محظور</span></div>
      </div>
      <div class="tools">
        <input id="q" type="search" placeholder="ابحث بالمعرّف أو الاسم أو الملاحظة…" aria-label="بحث">
        <select id="sort" aria-label="الترتيب">
          <option value="created">الأحدث إنشاءً</option>
          <option value="exp_asc">الأقرب انتهاءً</option>
          <option value="exp_desc">الأبعد انتهاءً</option>
          <option value="checks">الأكثر تحققاً</option>
        </select>
        <button id="bulkBtn" class="btn-sm">تمديد جماعي</button>
      </div>
      <div class="chips" role="group" aria-label="تصفية">
        <button class="chip" data-f="all" aria-pressed="true">الكل</button>
        <button class="chip" data-f="active" aria-pressed="false">نشط</button>
        <button class="chip" data-f="soon" aria-pressed="false">ينتهي خلال 3 أيام</button>
        <button class="chip" data-f="expired" aria-pressed="false">منتهي</button>
        <button class="chip" data-f="banned" aria-pressed="false">محظور</button>
      </div>
      <div id="list"></div>
    </section>

    <section id="tab-add" class="hide">
      <h2>إنشاء أكواد جديدة</h2>
      <p class="sub">يُنشأ الكود وتُحفظ بصمته فقط؛ انسخه للمشترك فور إنشائه.</p>
      <div class="panel">
        <div class="grid">
          <div>
            <label for="dur">المدة</label>
            <select id="dur">
              <option value="day">يوم (1)</option>
              <option value="week">أسبوع (7 أيام)</option>
              <option value="month" selected>شهر (30 يوماً)</option>
              <option value="2.5months">شهرين ونصف (75 يوماً)</option>
              <option value="year">سنة (365 يوماً)</option>
              <option value="custom">عدد أيام مخصص…</option>
            </select>
          </div>
          <div id="customDaysBox" class="hide">
            <label for="customDays">عدد الأيام (1–3650)</label>
            <input id="customDays" type="number" min="1" max="3650" value="14">
          </div>
          <div>
            <label for="count">العدد (1–50)</label>
            <input id="count" type="number" min="1" max="50" value="1">
          </div>
          <div>
            <label for="maxDev">أقصى عدد أجهزة (1–10)</label>
            <input id="maxDev" type="number" min="1" max="10" value="1">
          </div>
          <div>
            <label for="note">اسم المشترك أو ملاحظة</label>
            <input id="note" type="text" maxlength="100" placeholder="مثال: أحمد — VIP">
          </div>
          <div>
            <label for="ckey">كود مخصص (اختياري، لكود واحد)</label>
            <input id="ckey" type="text" maxlength="64" class="ltr" placeholder="VIP-XXXX-YYYY-ZZZZ">
          </div>
          <div class="full">
            <button id="createBtn" class="btn-main btn-block">إنشاء الأكواد</button>
          </div>
        </div>
        <div id="result" class="result hide"></div>
      </div>
    </section>

    <section id="tab-settings" class="hide">
      <h2>إعدادات الباتش وOTA والتطبيق</h2>
      <p class="sub">تُحفظ في قاعدة البيانات وتُطبّق فوراً على تطبيق Lader Tareiq.</p>

      <div class="panel">
        <h3>الباتش والحزمة <span id="patchPill" class="pill"></span></h3>
        <p class="sub">رابط التحميل يُرسل للمستخدمين المفعّلين فقط بعد التحقق من الكود.</p>
        <div class="grid">
          <div class="full">
            <label for="f_patch_url">رابط تحميل الباتش أو الأرشيف (.pak أو .zip)</label>
            <input id="f_patch_url" data-k="patch_url" type="url" class="ltr" placeholder="https://…/patch.pak">
          </div>
          <div>
            <label for="f_patch_file_name">اسم الملف الهدف</label>
            <input id="f_patch_file_name" data-k="patch_file_name" type="text" class="ltr" placeholder="res_pufferpatch.pak">
          </div>
          <div>
            <label for="f_game_package">حزمة اللعبة</label>
            <input id="f_game_package" data-k="game_package" type="text" class="ltr" placeholder="com.tencent.ig">
          </div>
          <div>
            <label for="f_patch_version">رقم إصدار الباتش</label>
            <input id="f_patch_version" data-k="patch_version" type="text" class="ltr" placeholder="1">
          </div>
          <div>
            <label for="f_deploy_mode">وضع النشر</label>
            <select id="f_deploy_mode" data-k="deploy_mode">
              <option value="auto">تلقائي (auto)</option>
              <option value="pak">ملف باتش (pak)</option>
              <option value="folder">مجلد / أرشيف (folder)</option>
            </select>
          </div>
          <div class="full">
            <label for="f_patch_sha256">بصمة SHA-256 للباتش (اختياري — 64 خانة)</label>
            <input id="f_patch_sha256" data-k="patch_sha256" type="text" class="ltr" maxlength="64" placeholder="اتركه فارغاً إن لم يكن مطلوباً">
          </div>
          <div class="full">
            <label for="f_patch_notes">ما الجديد في هذا الباتش</label>
            <textarea id="f_patch_notes" data-k="patch_notes" maxlength="600" placeholder="مثال: تحسين الاستقرار وإصلاحات الأداء."></textarea>
          </div>
          <div class="full">
            <div class="sw">
              <div><b>تحديث الباتش تلقائياً وإلزامياً</b><small>يحمّل الباتش الجديد تلقائياً عند فتح التطبيق.</small></div>
              <input type="checkbox" data-k="force_patch_update" aria-label="تحديث الباتش تلقائياً وإلزامياً">
            </div>
          </div>
        </div>
      </div>

      <div class="panel">
        <h3>التحديث التحسيني OTA وتحديث APK</h3>
        <p class="sub">إرسال تحسينات فورية عن بُعد عبر OTA أو فرض تحديث APK جديد.</p>
        <div class="grid">
          <div>
            <label for="f_ota_version">إصدار OTA التحسيني</label>
            <input id="f_ota_version" data-k="ota_version" type="text" class="ltr" placeholder="1.0.1">
            <p class="hint">ارفع الرقم لإرسال حزمة OTA جديدة دون إعادة تثبيت APK.</p>
          </div>
          <div>
            <label for="f_ota_notes">ملاحظات تحديث OTA</label>
            <input id="f_ota_notes" data-k="ota_notes" type="text" maxlength="400" placeholder="تحسين الإشعارات والروابط عن بُعد.">
          </div>
          <div>
            <label for="f_ota_activate_label">نص زر التفعيل عبر OTA (اختياري)</label>
            <input id="f_ota_activate_label" data-k="ota_activate_label" type="text" maxlength="40" placeholder="تحقق وفعّل VIP">
          </div>
          <div>
            <label for="f_ota_install_label">نص زر التثبيت عبر OTA (اختياري)</label>
            <input id="f_ota_install_label" data-k="ota_install_label" type="text" maxlength="40" placeholder="تثبيت الباتش">
          </div>
          <div>
            <label for="f_min_app_version">أقل نسخة APK مسموحة (إلزامي)</label>
            <input id="f_min_app_version" data-k="min_app_version" type="text" class="ltr" placeholder="2.0.0">
            <p class="hint">أي نسخة أقدم تُمنع من المتابعة.</p>
          </div>
          <div>
            <label for="f_latest_app_version">أحدث نسخة APK (اختياري)</label>
            <input id="f_latest_app_version" data-k="latest_app_version" type="text" class="ltr" placeholder="2.1.0">
            <p class="hint">تظهر عند فحص التحديثات يدوياً.</p>
          </div>
          <div class="full">
            <label for="f_update_url">رابط تحميل APK الجديد</label>
            <input id="f_update_url" data-k="update_url" type="url" class="ltr" placeholder="https://…/LaderTareiq.apk">
          </div>
          <div class="full">
            <label for="f_update_message">رسالة التحديث الكبير (APK)</label>
            <input id="f_update_message" data-k="update_message" type="text" maxlength="400" placeholder="يتوفر إصدار جديد من التطبيق.">
          </div>
        </div>
      </div>

      <div class="panel">
        <h3>الإعلانات والدعم والصيانة</h3>
        <p class="sub">رسالة أعلى التطبيق، رابط الدعم، وحالة الصيانة.</p>
        <div class="grid">
          <div class="full">
            <label for="f_notice">نص الإعلان</label>
            <textarea id="f_notice" data-k="notice" maxlength="400" placeholder="مثال: أهلاً بك في Lader Tareiq."></textarea>
          </div>
          <div class="full">
            <label for="f_support_url">رابط الدعم</label>
            <input id="f_support_url" data-k="support_url" type="url" class="ltr" placeholder="https://t.me/…">
          </div>
          <div class="full">
            <div class="sw">
              <div><b>وضع الصيانة</b><small>يوقف التحقق مؤقتاً ويعرض الإعلان للمستخدمين.</small></div>
              <input type="checkbox" data-k="maintenance" aria-label="وضع الصيانة">
            </div>
          </div>
        </div>
      </div>

      <div class="savebar hide" id="savebar">
        <span>لديك تغييرات غير محفوظة</span>
        <span style="display:flex;gap:8px">
          <button id="discardBtn" class="btn-ghost btn-sm">تراجع</button>
          <button id="saveBtn" class="btn-main btn-sm">حفظ</button>
        </span>
      </div>

      <div class="panel">
        <h3>بوت تيليجرام <span id="tgPill" class="pill"></span></h3>
        <p class="sub">أدر الأكواد وOTA والتحديثات من تيليجرام وتلقّ إشعارات التفعيل.</p>
        <ol class="steps">
          <li>أنشئ بوتاً من <code>@BotFather</code> وانسخ التوكن.</li>
          <li>في Vercel أضف <code>TELEGRAM_BOT_TOKEN</code> و<code>TELEGRAM_ADMIN_IDS</code> ثم أعد النشر.</li>
          <li>اضغط «ربط البوت» أدناه، ثم أرسل <code>/help</code> للبوت.</li>
        </ol>
        <button id="tgBtn" class="btn-sm">ربط البوت</button>
      </div>

      <div class="panel">
        <h3>ذاكرة المتصفح</h3>
        <p class="sub">النسخ الاحتياطية المحلية للأكواد المنشأة في هذا المتصفح فقط.</p>
        <button id="clearVaultBtn" class="btn-danger btn-sm">مسح الأكواد المحفوظة هنا</button>
      </div>
    </section>
  </main>
</div>

<div id="toast" class="toast" role="status"></div>

<div id="dlg" class="dlg hide" role="dialog" aria-modal="true">
  <div class="dlg-box">
    <h3 id="dlgTitle"></h3>
    <p id="dlgBody"></p>
    <div id="dlgExtra"></div>
    <div class="dlg-acts">
      <button id="dlgCancel" class="btn-ghost btn-sm">إلغاء</button>
      <button id="dlgOk" class="btn-main btn-sm">تأكيد</button>
    </div>
  </div>
</div>

<script>
(()=>{
const K_TOKEN='admin_token', K_VAULT='key_vault_v1';
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
let token='', licenses=[], filter='all', saved={}, dirty=false;
const STATUS_AR={active:'نشط',expired:'منتهي',banned:'محظور'};
const vault=()=>{try{return JSON.parse(localStorage.getItem(K_VAULT)||'{}');}catch{return{};}};
const saveVault=o=>{try{localStorage.setItem(K_VAULT,JSON.stringify(o));}catch{}};

function h(tag,props={},...kids){
  const e=document.createElement(tag);
  for(const [k,v] of Object.entries(props||{})){
    if(v==null)continue;
    if(k==='class')e.className=v;
    else if(k.startsWith('on')&&typeof v==='function')e.addEventListener(k.slice(2),v);
    else e.setAttribute(k,v);
  }
  for(const c of kids.flat()){if(c==null)continue;e.append(c.nodeType?c:document.createTextNode(c));}
  return e;
}
let toastTimer;
function toast(msg){
  const t=$('#toast');t.textContent=msg;t.classList.add('show');
  clearTimeout(toastTimer);toastTimer=setTimeout(()=>t.classList.remove('show'),2500);
}
function copy(txt,label='تم النسخ'){
  if(!txt)return;
  navigator.clipboard?.writeText(txt).then(()=>toast(label)).catch(()=>{
    const ta=h('textarea',{value:txt});document.body.append(ta);ta.select();document.execCommand('copy');ta.remove();toast(label);
  });
}
function fmtDate(iso){
  if(!iso)return '—';
  const d=new Date(iso);
  return isNaN(d)?iso:d.toLocaleString('ar-EG-u-nu-latn',{dateStyle:'medium',timeStyle:'short'});
}
function leftText(r){
  if(r.status==='banned')return 'محظور';
  const sec=(new Date(r.expires_at)-Date.now())/1000;
  if(sec<=0)return `انتهى منذ ${Math.max(1,Math.floor(-sec/86400))} يوم`;
  const days=Math.floor(sec/86400);
  return days?`متبقي ${days} يوم`:`متبقي ${Math.max(1,Math.floor(sec/3600))} ساعة`;
}

function confirmDlg({title,body,okText='تأكيد',danger=false,extra=null}){
  return new Promise(res=>{
    $('#dlgTitle').textContent=title;$('#dlgBody').textContent=body;
    const ex=$('#dlgExtra');ex.replaceChildren();if(extra)ex.append(extra);
    const ok=$('#dlgOk'),cancel=$('#dlgCancel'),dlg=$('#dlg');
    ok.textContent=okText;ok.className='btn-sm '+(danger?'btn-solid-danger':'btn-main');
    dlg.classList.remove('hide');ok.focus();
    const close=v=>{dlg.classList.add('hide');ok.onclick=cancel.onclick=null;res(v);};
    ok.onclick=()=>close(true);cancel.onclick=()=>close(false);
  });
}

async function api(path,method='GET',body=null){
  const opt={method,headers:{Authorization:'Bearer '+token}};
  if(body!==null){opt.headers['Content-Type']='application/json';opt.body=JSON.stringify(body);}
  const r=await fetch(path,opt);
  const d=await r.json().catch(()=>({}));
  if(!r.ok)throw new Error(d.message||`خطأ (${r.status})`);
  return d;
}

function logout(msg){
  sessionStorage.removeItem(K_TOKEN);localStorage.removeItem(K_TOKEN);token='';
  $('#app').classList.add('hide');$('#login').classList.remove('hide');
  $('#tokenInput').value='';$('#loginErr').textContent=msg||'';
}
async function tryToken(t){
  const r=await fetch('/api/admin/stats',{headers:{Authorization:'Bearer '+t}});
  return r.status;
}
async function login(){
  const t=$('#tokenInput').value.trim();
  if(!t){$('#loginErr').textContent='أدخل رمز الدخول.';return;}
  $('#loginBtn').disabled=true;$('#loginErr').textContent='';
  try{
    const st=await tryToken(t);
    if(st===200){
      token=t;
      if($('#remember').checked)localStorage.setItem(K_TOKEN,t);
      else sessionStorage.setItem(K_TOKEN,t);
      await enter();
    }else if(st===429){$('#loginErr').textContent='محاولات كثيرة، انتظر دقيقة.';}
    else{$('#loginErr').textContent='رمز الدخول غير صحيح.';}
  }catch{
    $('#loginErr').textContent='تعذر الاتصال بالسيرفر.';
  }finally{$('#loginBtn').disabled=false;}
}
async function enter(){
  $('#login').classList.add('hide');$('#app').classList.remove('hide');
  await Promise.all([load(),loadSettings(),checkHealth()]);
}

async function checkHealth(){
  try{
    const r=await fetch('/api/health');const d=await r.json();
    $('#healthTxt').replaceChildren(h('span',{class:'dot'}),`متصل · ${d.storage} · v${d.version}`);
  }catch{
    $('#healthTxt').replaceChildren(h('span',{class:'dot bad'}),'غير متصل');
  }
}

async function load(){
  try{
    const d=await api('/api/admin/list?limit=1000');
    licenses=d.licenses||[];render();
  }catch(e){toast(e.message);}
}
function filtered(){
  const q=$('#q').value.trim().toLowerCase();
  let rows=licenses.filter(r=>{
    if(filter==='active'&&r.status!=='active')return false;
    if(filter==='soon'&&!r.soon)return false;
    if(filter==='expired'&&r.status!=='expired')return false;
    if(filter==='banned'&&r.status!=='banned')return false;
    if(!q)return true;
    return [r.id,r.note,r.type].join(' ').toLowerCase().includes(q);
  });
  const s=$('#sort').value;
  if(s==='exp_asc')rows=[...rows].sort((a,b)=>new Date(a.expires_at)-new Date(b.expires_at));
  else if(s==='exp_desc')rows=[...rows].sort((a,b)=>new Date(b.expires_at)-new Date(a.expires_at));
  else if(s==='checks')rows=[...rows].sort((a,b)=>(b.checks||0)-(a.checks||0));
  return rows;
}
function render(){
  const active=licenses.filter(r=>r.status==='active').length;
  const soon=licenses.filter(r=>r.soon).length;
  const exp=licenses.filter(r=>r.status==='expired').length;
  const ban=licenses.filter(r=>r.status==='banned').length;
  $('#stActive').textContent=active;$('#stSoon').textContent=soon;$('#stExp').textContent=exp;$('#stBan').textContent=ban;

  const rows=filtered(), box=$('#list'), v=vault();
  if(!rows.length){
    box.replaceChildren(h('div',{class:'empty'},licenses.length?'لا توجد نتائج مطابقة للبحث أو التصفية.':'لا توجد أكواد بعد. ابدأ بإنشاء كود من تبويب «إنشاء».'));
    return;
  }
  box.replaceChildren(...rows.map(r=>{
    const daysInp=h('input',{type:'number',min:1,max:3650,value:30,'aria-label':'عدد الأيام'});
    const knownKey=v[r.id];
    const card=h('article',{class:`lic st-${r.status}${r.soon?' soon':''}`},
      h('button',{class:'lic-head',type:'button',onclick:()=>card.classList.toggle('open')},
        h('div',{class:'who'},
          h('span',{class:'id'},r.id),
          h('span',{class:'nm'},(r.note||'بدون ملاحظة')+' · '+r.type)),
        h('div',{class:'right'},
          h('span',{class:`badge b-${r.status}`},STATUS_AR[r.status]||r.status),
          h('div',{class:'rem'},leftText(r)))),
      h('div',{class:'lic-body'},
        h('div',{class:'meta'},
          h('div',null,h('small',null,'الأجهزة'),`${r.devices} / ${r.max_devices}`),
          h('div',null,h('small',null,'التحققات'),String(r.checks||0)),
          h('div',null,h('small',null,'ينتهي في'),fmtDate(r.expires_at)),
          h('div',null,h('small',null,'آخر ظهور'),fmtDate(r.last_seen))),
        h('div',{class:'acts'},
          knownKey?h('button',{class:'btn-sm btn-main',onclick:()=>copy(knownKey,'تم نسخ الكود')},'نسخ الكود'):null,
          h('button',{class:'btn-sm',onclick:()=>revealKey(r.id)},'إظهار الكود'),
          daysInp,
          h('button',{class:'btn-sm',onclick:()=>act(r.id,'extend',{days:+daysInp.value||30})},'تمديد'),
          h('button',{class:'btn-sm',onclick:()=>act(r.id,'reset_devices')},'فك الأجهزة'),
          r.status==='banned'
            ?h('button',{class:'btn-sm',onclick:()=>act(r.id,'unban')},'إلغاء الحظر')
            :h('button',{class:'btn-sm btn-danger',onclick:()=>act(r.id,'ban')},'حظر'),
          h('button',{class:'btn-sm btn-danger',onclick:()=>delLic(r.id)},'حذف'))));
    return card;
  }));
}
async function revealKey(id){
  const v=vault();if(v[id]){copy(v[id],'تم نسخ الكود');return;}
  try{const d=await api('/api/admin/reveal','POST',{id});v[id]=d.key;saveVault(v);copy(d.key,'تم نسخ الكود');render();}
  catch(e){toast(e.message);}
}
async function act(id,action,extra={}){
  try{const d=await api('/api/admin/control','POST',{id,action,...extra});toast(d.message||'تم');await load();}
  catch(e){toast(e.message);}
}
async function delLic(id){
  if(!await confirmDlg({title:'حذف الترخيص',body:`سيتم حذف ${id} نهائياً.`,okText:'حذف',danger:true}))return;
  await act(id,'delete');
}
async function bulkExtend(){
  const sel=h('select',{},
    h('option',{value:'active'},'كل الأكواد النشطة'),
    h('option',{value:'expired'},'كل الأكواد المنتهية'),
    h('option',{value:'banned'},'كل الأكواد المحظورة'));
  const inp=h('input',{type:'number',min:1,max:3650,value:7,style:'margin-top:8px'});
  const wrap=h('div',null,h('label',null,'الفئة المستهدفة'),sel,h('label',{style:'margin-top:10px'},'إضافة أيام'),inp);
  if(!await confirmDlg({title:'تمديد جماعي',body:'اختر الفئة وعدد الأيام الإضافية:',okText:'تمديد',extra:wrap}))return;
  try{const d=await api('/api/admin/bulk-extend','POST',{status:sel.value,days:+inp.value||7});toast(d.message);await load();}
  catch(e){toast(e.message);}
}

$('#dur').onchange=()=>$('#customDaysBox').classList.toggle('hide',$('#dur').value!=='custom');
async function createKeys(){
  const dur=$('#dur').value, count=+$('#count').value||1, max_devices=+$('#maxDev').value||1;
  const note=$('#note').value.trim(), key=$('#ckey').value.trim();
  const body={count,max_devices};
  if(dur==='custom'){body.type='custom';body.days=+$('#customDays').value||1;}
  else body.type=dur;
  if(note)body.note=note;
  if(key)body.key=key;
  $('#createBtn').disabled=true;
  try{
    const d=await api('/api/admin/add','POST',body);
    const v=vault();d.keys.forEach(k=>{v[k.id]=k.key;});saveVault(v);
    const exp=fmtDate(d.keys[0]&&d.keys[0].expires_at);
    const res=$('#result');res.classList.remove('hide');
    res.replaceChildren(
      h('b',null,`تم إنشاء ${d.keys.length} كود · ينتهي ${exp}`),
      ...d.keys.map(k=>h('div',{class:'row'},
        h('span',{class:'id'},k.key),
        h('span',{class:'acts'},
          h('button',{class:'btn-sm btn-main',onclick:()=>copy(k.key,'تم نسخ الكود')},'نسخ'),
          h('button',{class:'btn-sm',onclick:()=>copy(`كود التفعيل: ${k.key}\nينتهي: ${exp}`,'تم نسخ الرسالة')},'رسالة')))),
      d.keys.length>1?h('div',{style:'margin-top:10px'},
        h('button',{class:'btn-sm',onclick:()=>copy(d.keys.map(k=>k.key).join('\n'),'تم نسخ الكل')},'نسخ الكل')):null);
    $('#ckey').value='';$('#note').value='';
    await load();
  }catch(e){toast(e.message);}
  finally{$('#createBtn').disabled=false;}
}

const fields=()=>$$('[data-k]');
function readForm(){
  const o={};
  fields().forEach(el=>{o[el.dataset.k]=el.type==='checkbox'?el.checked:el.value.trim();});
  return o;
}
function fillForm(s){
  fields().forEach(el=>{
    const v=s[el.dataset.k];
    if(el.type==='checkbox')el.checked=!!v;
    else el.value=v==null?'':v;
  });
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
    $('#tgPill').replaceChildren(
      h('span',{class:'dot'+(t.configured&&t.admins?'':(t.configured?' warn':' bad'))}),
      t.configured?(t.admins?'جاهز':'أضف TELEGRAM_ADMIN_IDS'):'غير مضبوط');
  }catch(e){toast(e.message);}
}
async function saveSettings(){
  $('#saveBtn').disabled=true;
  try{const d=await api('/api/admin/settings','POST',readForm());toast('تم حفظ الإعدادات');fillForm(d.settings);}
  catch(e){toast(e.message);}
  finally{$('#saveBtn').disabled=false;}
}
async function tgSetup(){
  $('#tgBtn').disabled=true;
  try{const d=await api('/api/admin/telegram/setup','POST');toast(d.message);await loadSettings();}
  catch(e){toast(e.message);}
  finally{$('#tgBtn').disabled=false;}
}

$$('.tab').forEach(b=>b.onclick=()=>{
  $$('.tab').forEach(x=>x.setAttribute('aria-selected',x===b));
  ['keys','add','settings'].forEach(t=>$('#tab-'+t).classList.toggle('hide',b.dataset.tab!==t));
});
$$('.chip').forEach(c=>c.onclick=()=>{
  $$('.chip').forEach(x=>x.setAttribute('aria-pressed',x===c));
  filter=c.dataset.f;render();
});
$('#loginBtn').onclick=login;
$('#tokenInput').addEventListener('keydown',e=>{if(e.key==='Enter')login();});
$('#logoutBtn').onclick=()=>logout('');
$('#refreshBtn').onclick=()=>{load();loadSettings();checkHealth();};
$('#q').addEventListener('input',render);
$('#sort').addEventListener('change',render);
$('#bulkBtn').onclick=bulkExtend;
$('#createBtn').onclick=createKeys;
fields().forEach(el=>{el.addEventListener('input',markDirty);el.addEventListener('change',markDirty);});
$('#discardBtn').onclick=()=>fillForm(saved);
$('#saveBtn').onclick=saveSettings;
$('#tgBtn').onclick=tgSetup;
$('#clearVaultBtn').onclick=async()=>{
  if(!await confirmDlg({title:'مسح الأكواد المحفوظة هنا',body:'يمسح الأكواد المحفوظة في هذا المتصفح فقط ولا يؤثر على قاعدة البيانات.',okText:'مسح',danger:true}))return;
  localStorage.removeItem(K_VAULT);render();toast('تم المسح');
};
window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue='';}});

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
