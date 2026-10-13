"""إدارة المشتركين عبر بوت تيليجرام (Webhook).

المتغيرات في Vercel:
  TELEGRAM_BOT_TOKEN : توكن البوت من @BotFather
  TELEGRAM_ADMIN_IDS : معرّفات المسموح لهم (أرقام) مفصولة بفاصلة، مثال: 123456789,987654321

بعد ضبطهما افتح لوحة /admin ← الإعدادات ← تيليجرام ← «ربط البوت».
"""
from __future__ import annotations

import hashlib
import html
import logging
import os
from typing import Optional

import requests

import core
from core import LicenseError

log = logging.getLogger("telegram")
ICONS = {"active": "🟢", "expired": "🟠", "banned": "🔴"}
STATUS_AR = {"active": "نشط", "expired": "منتهي", "banned": "محظور"}

HELP = """<b>أوامر الإدارة</b>

<b>الأكواد</b>
/add month 3 أحمد  ← ينشئ 3 أكواد شهرية باسم «أحمد»
  المدد: week | month | 2.5months | رقم أيام (مثل 45)
/list  أو  /list active|expired|banned
/info ID
/extend ID 30
/reset ID  ← إعادة ضبط الجهاز
/ban ID  ·  /unban ID
/delete ID نعم
/stats

<b>الباتش والتطبيق</b>
/settings  ← عرض الإعدادات الحالية
/link https://…  ← رابط الباتش
/version 5  ← رقم الباتش (غيّره عند كل تحديث)
/force on|off  ← تحديث الباتش الإلزامي
/notice نص الإعلان  (أو /notice off)
/maintenance on|off"""


# ------------------------------------------------------------ إعدادات
def token() -> str:
    return os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()


def admin_ids() -> set[int]:
    ids = set()
    for part in os.environ.get("TELEGRAM_ADMIN_IDS", "").replace(";", ",").split(","):
        part = part.strip()
        if part.lstrip("-").isdigit():
            ids.add(int(part))
    return ids


def configured() -> bool:
    return bool(token())


def webhook_secret() -> str:
    """سر الـ webhook مشتق من توكن البوت؛ لا حاجة لمتغير إضافي."""
    return hashlib.sha256(f"wh:{token()}".encode()).hexdigest()[:48]


# ------------------------------------------------------------ Telegram API
def call(method: str, **payload) -> dict:
    r = requests.post(f"https://api.telegram.org/bot{token()}/{method}", json=payload, timeout=5)
    try:
        return r.json()
    except ValueError:
        return {"ok": False, "description": f"HTTP {r.status_code}"}


def send(chat_id: int, text: str) -> None:
    try:
        call("sendMessage", chat_id=chat_id, text=text[:4000], parse_mode="HTML",
             disable_web_page_preview=True)
    except Exception:
        log.exception("telegram send failed")


def notify(text: str) -> None:
    """إشعار لكل المشرفين (يُتجاهل بصمت إن لم يُضبط البوت)."""
    if not configured():
        return
    for uid in admin_ids():
        send(uid, text)


def setup_webhook(host: str) -> tuple[bool, str]:
    if not configured():
        return False, "TELEGRAM_BOT_TOKEN غير مضبوط في Vercel."
    me = call("getMe")
    if not me.get("ok"):
        return False, "توكن البوت غير صحيح."
    res = call("setWebhook", url=f"https://{host}/api/telegram/webhook", secret_token=webhook_secret(),
               allowed_updates=["message"], drop_pending_updates=True)
    if not res.get("ok"):
        return False, res.get("description", "فشل ربط الـ webhook.")
    if not admin_ids():
        return True, f"تم الربط مع @{me['result']['username']} لكن TELEGRAM_ADMIN_IDS فارغ؛ لن يرد البوت على أحد."
    return True, f"تم الربط مع @{me['result']['username']}"


# ------------------------------------------------------------ مساعدات العرض
def _esc(s: object) -> str:
    return html.escape(str(s), quote=False)


def _left(v: dict) -> str:
    if v["status"] == "banned":
        return "محظور"
    delta = core.parse(v["expires_at"]) - core.utcnow()
    days = delta.days
    if delta.total_seconds() <= 0:
        return f"انتهى منذ {-days if days < 0 else 0} يوم"
    return f"متبقي {days} يوم" if days else f"متبقي {delta.seconds // 3600} ساعة"


def _line(v: dict) -> str:
    note = f" • {_esc(v['note'])}" if v.get("note") else ""
    return f"{ICONS.get(v['status'], '⚪')} <code>{v['id']}</code> {_esc(v['type'])} • {_left(v)}{note}"


def _find(rows: list[dict], ident: str) -> Optional[dict]:
    ident = ident.lower()
    hits = [r for r in rows if r["id"].startswith(ident)]
    return hits[0] if len(hits) == 1 else None


def _onoff(word: str) -> Optional[bool]:
    w = word.lower()
    if w in ("on", "1", "yes", "تشغيل", "نعم", "فعل"):
        return True
    if w in ("off", "0", "no", "ايقاف", "إيقاف", "لا", "الغاء"):
        return False
    return None


# ------------------------------------------------------------ الأوامر
def cmd_add(args: list[str]) -> str:
    if not args:
        return "الاستخدام: /add month 3 أحمد"
    first, rest = args[0].lower(), args[1:]
    data: dict = {}
    if first in core.DURATIONS:
        data["type"] = first
    elif first.isdigit():
        data["type"], data["days"] = "custom", int(first)
    else:
        return "المدة: week | month | 2.5months | أو عدد الأيام."
    if rest and rest[0].isdigit():
        data["count"] = int(rest[0])
        rest = rest[1:]
    if rest:
        data["note"] = " ".join(rest)
    created = core.create_licenses(data)
    if not created:
        return "لم يُنشأ أي كود، حاول مرة أخرى."
    keys = "\n".join(f"<code>{k['key']}</code>" for k in created)
    return f"✅ تم إنشاء {len(created)} كود (ينتهي {created[0]['expires_at'][:10]})\n\n{keys}\n\nاحفظها الآن؛ لن تظهر مرة أخرى."


def cmd_list(args: list[str]) -> str:
    rows = sorted(core.list_licenses(), key=lambda r: r.get("created") or "", reverse=True)
    if args and args[0].lower() in STATUS_AR:
        rows = [r for r in rows if r["status"] == args[0].lower()]
    if not rows:
        return "لا توجد أكواد."
    body = "\n".join(_line(r) for r in rows[:25])
    more = f"\n… و{len(rows) - 25} أخرى" if len(rows) > 25 else ""
    return f"<b>الأكواد ({len(rows)})</b>\n{body}{more}"


def cmd_info(args: list[str]) -> str:
    if not args:
        return "الاستخدام: /info ID"
    r = _find(core.list_licenses(), args[0])
    if not r:
        return "الترخيص غير موجود."
    seen = r["last_seen"].replace("T", " ")[:16] if r.get("last_seen") else "—"
    return (f"{_line(r)}\n"
            f"ينتهي: {r['expires_at'][:10]}\nالأجهزة: {r['devices']}/{r['max_devices']}\n"
            f"عدد التحققات: {r['checks']}\nآخر ظهور: {seen}")


def cmd_stats(_: list[str]) -> str:
    rows = core.list_licenses()
    c = {"active": 0, "expired": 0, "banned": 0}
    soon = 0
    for r in rows:
        c[r["status"]] = c.get(r["status"], 0) + 1
        if r["status"] == "active" and (core.parse(r["expires_at"]) - core.utcnow()).days < 3:
            soon += 1
    return (f"📊 <b>الإحصائيات</b>\nالكل: {len(rows)}\n🟢 نشط: {c['active']}\n"
            f"🟠 منتهي: {c['expired']}\n🔴 محظور: {c['banned']}\n⏳ ينتهي خلال 3 أيام: {soon}")


def cmd_control(action: str, args: list[str]) -> str:
    if not args:
        return f"الاستخدام: /{action} ID"
    data = {"id": args[0], "action": action}
    if action == "extend":
        if len(args) < 2 or not args[1].isdigit():
            return "الاستخدام: /extend ID 30"
        data["days"] = int(args[1])
    if action == "delete" and (len(args) < 2 or args[1] not in ("نعم", "yes", "confirm")):
        return f"للتأكيد أرسل: /delete {_esc(args[0])} نعم"
    msg, view = core.control_license(data)
    return f"✅ {msg}" + (f"\n{_line(view)}" if view else "")


def cmd_settings(_: list[str]) -> str:
    s = core.get_settings()
    yn = lambda b: "مفعّل" if b else "متوقف"  # noqa: E731
    return (
        "<b>الإعدادات الحالية</b>\n"
        f"رابط الباتش: {_esc(s['patch_url']) or '❌ غير مضبوط'}\n"
        f"رقم الباتش: {_esc(s['patch_version'])}\nتحديث إلزامي: {yn(s['force_patch_update'])}\n"
        f"إعلان: {_esc(s['notice']) or '—'}\nالصيانة: {yn(s['maintenance'])}\n"
        f"أقل نسخة تطبيق: {_esc(s['min_app_version']) or '—'}"
    )


def cmd_set(field: str, args: list[str], label: str) -> str:
    if not args:
        return f"أرسل القيمة بعد الأمر. مثال: /{label} …"
    value: object
    if field in core.BOOL_FIELDS:
        value = _onoff(args[0])
        if value is None:
            return "استخدم on أو off."
    else:
        value = " ".join(args)
        if field == "notice" and value.lower() in ("off", "حذف", "مسح"):
            value = ""
    core.save_settings({field: value})
    shown = ("مفعّل" if value else "متوقف") if isinstance(value, bool) else (_esc(value) or "تم المسح")
    return f"✅ تم حفظ {label}: {shown}"


def run_command(text: str) -> str:
    parts = text.split()
    cmd = parts[0].lstrip("/").split("@")[0].lower()
    args = parts[1:]
    table = {
        "add": lambda: cmd_add(args), "list": lambda: cmd_list(args), "info": lambda: cmd_info(args),
        "stats": lambda: cmd_stats(args), "settings": lambda: cmd_settings(args),
        "ban": lambda: cmd_control("ban", args), "unban": lambda: cmd_control("unban", args),
        "reset": lambda: cmd_control("reset_devices", args), "extend": lambda: cmd_control("extend", args),
        "delete": lambda: cmd_control("delete", args),
        "link": lambda: cmd_set("patch_url", args, "رابط الباتش"),
        "version": lambda: cmd_set("patch_version", args, "رقم الباتش"),
        "force": lambda: cmd_set("force_patch_update", args, "التحديث الإلزامي"),
        "notice": lambda: cmd_set("notice", args, "الإعلان"),
        "maintenance": lambda: cmd_set("maintenance", args, "وضع الصيانة"),
        "start": lambda: HELP, "help": lambda: HELP,
    }
    handler = table.get(cmd)
    if handler is None:
        return "أمر غير معروف. أرسل /help"
    try:
        return handler()
    except LicenseError as ex:
        return f"❌ {_esc(ex.message)}"


def handle_update(update: dict) -> None:
    msg = update.get("message") or {}
    text = (msg.get("text") or "").strip()
    chat_id = (msg.get("chat") or {}).get("id")
    uid = (msg.get("from") or {}).get("id")
    if not chat_id or not text.startswith("/"):
        return
    if uid not in admin_ids():
        send(chat_id, f"غير مصرّح. معرّفك: <code>{uid}</code>\nأضفه إلى TELEGRAM_ADMIN_IDS في Vercel.")
        return
    send(chat_id, run_command(text))
