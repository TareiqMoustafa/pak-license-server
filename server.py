"""سيرفر التراخيص - Flask على Vercel."""
from __future__ import annotations

import hmac
import logging

from flask import Flask, jsonify, make_response, request

import core
import iplog
import telegram_bot as tg
from admin_page import ADMIN_HTML
from owner_page import OWNER_HTML
from core import DEVICE_RE, KEY_RE, LicenseError, hash_key, iso, normalize, parse, utcnow
from security import admin_required, client_ip, owner_required, rate_limit, user_agent
from store import get_store

app = Flask(__name__)
app.json.sort_keys = False
app.json.ensure_ascii = False
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("license")


def reply(status: str, message: str, code: int = 200, **extra):
    resp = jsonify(status=status, message=message, **extra)
    resp.headers["Cache-Control"] = "no-store"
    return resp, code


def fail(ex: LicenseError):
    return jsonify(success=False, message=ex.message), ex.status


# ------------------------------------------------------------ عام
@app.get("/")
@app.get("/api/health")
def health():
    return jsonify(ok=True, storage=get_store().kind, time=iso(utcnow()))


@app.get("/api/app-config")
def app_config():
    """معلومات عامة للتطبيق قبل إدخال الكود (بدون رابط الباتش)."""
    s = core.get_settings()
    resp = jsonify(
        maintenance=s["maintenance"], notice=s["notice"], support_url=s["support_url"],
        min_app_version=s["min_app_version"], update_url=s["update_url"], patch_version=s["patch_version"],
    )
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.post("/api/verify")
def verify():
    if not rate_limit(f"verify:{client_ip()}", 20, 60):
        return reply("rate_limited", "محاولات كثيرة، حاول بعد دقيقة.", 429)

    data = request.get_json(silent=True) or {}
    key = normalize(data.get("key"))
    device = str(data.get("device_id", "")).strip()
    app_version = str(data.get("app_version", "")).strip()[:20]
    if not KEY_RE.match(key) or not DEVICE_RE.match(device):
        return reply("invalid", "بيانات غير صالحة.", 400)

    settings = core.get_settings()
    if settings["maintenance"]:
        return reply("maintenance", settings["notice"] or "السيرفر تحت الصيانة، حاول لاحقاً.", 503)
    min_ver = settings["min_app_version"]
    if min_ver and core.ver_tuple(app_version or "0") < core.ver_tuple(min_ver):
        return reply("update_required", "يجب تحديث التطبيق للمتابعة.", 426,
                     update_url=settings["update_url"], min_app_version=min_ver)

    db = get_store()
    h = hash_key(key)
    lic = db.get(f"lic:{h}")
    ip, ua = client_ip(), user_agent()
    if not lic:
        log.info("verify invalid ip=%s", ip)
        iplog.record("invalid", "", ip, ua, dev=device[:8])
        return reply("invalid", "الكود غير صحيح.", 404)

    def seen(status: str) -> None:
        iplog.record("user", h[:12], ip, ua, note=lic.get("note", ""), status=status, dev=device[:8])

    if lic["status"] == "banned":
        seen("banned")
        return reply("banned", "هذا الكود محظور.", 403)

    expiry = parse(lic["expiry"])
    now = utcnow()
    if now >= expiry:
        seen("expired")
        return reply("expired", "انتهى الاشتراك، يرجى التجديد.", 403)

    new_device = False
    if device not in lic["devices"]:
        if len(lic["devices"]) >= lic["max_devices"]:
            seen("device_limit")
            return reply("device_limit", "هذا الكود مرتبط بجهاز آخر. تواصل مع الدعم لإعادة الضبط.", 403)
        lic["devices"].append(device)
        new_device = True

    lic["checks"] = lic.get("checks", 0) + 1
    lic["last_seen"] = iso(now)
    db.set(f"lic:{h}", lic)

    seen("active")
    if new_device:
        tg.notify(f"🔔 تفعيل جديد\n<code>{h[:12]}</code> • {tg._esc(lic['type'])}"
                  + (f" • {tg._esc(lic['note'])}" if lic.get("note") else "")
                  + f"\nالأجهزة {len(lic['devices'])}/{lic['max_devices']}")

    remaining = expiry - now
    try:
        total_days = max(1, (expiry - parse(lic["created"])).days)
    except (KeyError, TypeError, ValueError):
        total_days = max(1, remaining.days)

    extra = {
        "type": lic["type"],
        "expires_at": lic["expiry"],
        "remaining_days": remaining.days,
        "remaining_hours": remaining.seconds // 3600,
        "total_days": total_days,
        "patch_version": settings["patch_version"],
        "force_update": settings["force_patch_update"],
        "notice": settings["notice"],
        "support_url": settings["support_url"],
        "patch_sha256": settings["patch_sha256"],
        "patch_notes": settings["patch_notes"],
    }
    # رابط الباتش وبياناته تُرسل فقط للأكواد الصالحة
    for field in ("patch_url", "patch_file_name", "game_package"):
        if settings[field]:
            extra[{"patch_url": "download_url", "patch_file_name": "target_file_name",
                   "game_package": "game_package"}[field]] = settings[field]
    return reply("active", f"مفعّل! المتبقي {remaining.days} يوم و{remaining.seconds // 3600} ساعة.", **extra)


# ------------------------------------------------------------ لوحة التحكم (واجهة فقط؛ الحماية في الـ API)
@app.get("/admin")
def admin_page():
    resp = make_response(ADMIN_HTML)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["X-Robots-Tag"] = "noindex, nofollow"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Content-Security-Policy"] = (
        "default-src 'none'; script-src 'unsafe-inline'; "
        "style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; "
        "connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
    )
    return resp


# ------------------------------------------------------------ الأدمن
@app.post("/api/admin/add")
@admin_required
def admin_add():
    try:
        created = core.create_licenses(request.get_json(silent=True) or {})
    except LicenseError as ex:
        return fail(ex)
    return jsonify(success=True, message=f"تم إنشاء {len(created)} كود. احفظها الآن؛ لن تظهر مرة أخرى.",
                   keys=created)


@app.get("/api/admin/list")
@admin_required
def admin_list():
    rows = core.list_licenses()
    return jsonify(success=True, count=len(rows), licenses=rows)


@app.post("/api/admin/control")
@admin_required
def admin_control():
    try:
        message, view = core.control_license(request.get_json(silent=True) or {})
    except LicenseError as ex:
        return fail(ex)
    return jsonify(success=True, message=message, license=view)


@app.post("/api/admin/reveal")
@admin_required
def admin_reveal():
    try:
        key = core.reveal_key(request.get_json(silent=True) or {})
    except LicenseError as ex:
        return fail(ex)
    log.info("admin revealed a key ip=%s", client_ip())
    resp = jsonify(success=True, key=key)
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.get("/api/admin/settings")
@admin_required
def admin_settings_get():
    return jsonify(success=True, settings=core.get_settings(),
                   telegram={"configured": tg.configured(), "admins": len(tg.admin_ids())},
                   vault=core.vault_enabled())


@app.post("/api/admin/settings")
@admin_required
def admin_settings_set():
    try:
        settings = core.save_settings(request.get_json(silent=True) or {})
    except LicenseError as ex:
        return fail(ex)
    return jsonify(success=True, message="تم حفظ الإعدادات.", settings=settings)


@app.post("/api/admin/telegram/setup")
@admin_required
def admin_telegram_setup():
    try:
        ok, message = tg.setup_webhook(request.host)
    except Exception as ex:  # noqa: BLE001
        log.exception("telegram setup failed")
        return jsonify(success=False, message=f"تعذر الاتصال بتيليجرام: {ex.__class__.__name__}"), 502
    return jsonify(success=ok, message=message), (200 if ok else 400)


# ------------------------------------------------------------ المالك فقط (سجل IP)
@app.get("/owner")
def owner_page():
    resp = make_response(OWNER_HTML)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["X-Robots-Tag"] = "noindex, nofollow"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Content-Security-Policy"] = (
        "default-src 'none'; script-src 'unsafe-inline'; "
        "style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; "
        "connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
    )
    return resp


@app.get("/api/owner/logs")
@owner_required
def owner_logs():
    try:
        days = min(90, max(1, int(request.args.get("days", 30))))
    except ValueError:
        days = 30
    resp = jsonify(success=True, retention_days=iplog.RETENTION_DAYS, rows=iplog.read(days))
    resp.headers["Cache-Control"] = "no-store"
    return resp


# ------------------------------------------------------------ تيليجرام
@app.post("/api/telegram/webhook")
def telegram_webhook():
    if not tg.configured():
        return "", 404
    sent = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if not hmac.compare_digest(sent.encode(), tg.webhook_secret().encode()):
        return "", 403
    try:
        tg.handle_update(request.get_json(silent=True) or {})
    except Exception:  # noqa: BLE001  (نرد 200 دائماً كي لا يعيد تيليجرام الإرسال)
        log.exception("telegram update failed")
    return "", 200


# ------------------------------------------------------------ أخطاء JSON
@app.errorhandler(404)
def _404(_):
    return jsonify(status="error", message="Not found."), 404


@app.errorhandler(405)
def _405(_):
    return jsonify(status="error", message="Method not allowed."), 405


@app.errorhandler(413)
def _413(_):
    return jsonify(status="error", message="Payload too large."), 413


@app.errorhandler(Exception)
def _500(ex):
    log.exception("unhandled: %s", ex)
    return jsonify(status="error", message="خطأ داخلي في السيرفر."), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
