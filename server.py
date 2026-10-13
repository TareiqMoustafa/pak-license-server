"""سيرفر التراخيص - Flask على Vercel."""
from __future__ import annotations

import hashlib
import logging
import os
import re
import secrets
from datetime import datetime, timedelta, timezone

from flask import Flask, jsonify, make_response, request

from admin_page import ADMIN_HTML
from security import admin_required, client_ip, rate_limit
from store import get_store

app = Flask(__name__)
app.json.sort_keys = False
app.json.ensure_ascii = False
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("license")

DURATIONS = {"week": 7, "month": 30, "2.5months": 75}
KEY_RE = re.compile(r"^[A-Z0-9][A-Z0-9_-]{5,63}$")
DEVICE_RE = re.compile(r"^[A-Za-z0-9_-]{8,128}$")
INDEX = "licenses"
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # بدون أحرف متشابهة (0/O, 1/I)


# ------------------------------------------------------------ أدوات
def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def hash_key(key: str) -> str:
    """نخزّن بصمة الكود فقط؛ لا يُحفظ الكود الأصلي أبداً."""
    pepper = os.environ.get("KEY_PEPPER", "")
    return hashlib.sha256(f"{pepper}{key}".encode()).hexdigest()


def normalize(key: str) -> str:
    return str(key or "").strip().upper()


def generate_key() -> str:
    return "VIP-" + "-".join("".join(secrets.choice(ALPHABET) for _ in range(4)) for _ in range(3))


def reply(status: str, message: str, code: int = 200, **extra):
    return jsonify(status=status, message=message, **extra), code


def find_hash(data: dict) -> str | None:
    """يحدد الترخيص بواسطة key أو id (أول 12 خانة من البصمة)."""
    if data.get("key"):
        return hash_key(normalize(data["key"]))
    lic_id = str(data.get("id", "")).lower()
    if len(lic_id) >= 8:
        for h in get_store().smembers(INDEX):
            if h.startswith(lic_id):
                return h
    return None


def public_view(h: str, lic: dict) -> dict:
    expired = parse(lic["expiry"]) <= utcnow()
    return {
        "id": h[:12],
        "type": lic["type"],
        "status": "expired" if expired and lic["status"] == "active" else lic["status"],
        "expires_at": lic["expiry"],
        "created": lic.get("created"),
        "devices": len(lic["devices"]),
        "max_devices": lic["max_devices"],
        "checks": lic.get("checks", 0),
        "last_seen": lic.get("last_seen"),
        "note": lic.get("note", ""),
    }


# ------------------------------------------------------------ عام
@app.get("/")
@app.get("/api/health")
def health():
    return jsonify(ok=True, storage=get_store().kind, time=iso(utcnow()))


@app.post("/api/verify")
def verify():
    if not rate_limit(f"verify:{client_ip()}", 20, 60):
        return reply("rate_limited", "محاولات كثيرة، حاول بعد دقيقة.", 429)

    data = request.get_json(silent=True) or {}
    key = normalize(data.get("key"))
    device = str(data.get("device_id", "")).strip()
    if not KEY_RE.match(key) or not DEVICE_RE.match(device):
        return reply("invalid", "بيانات غير صالحة.", 400)

    db = get_store()
    h = hash_key(key)
    lic = db.get(f"lic:{h}")
    if not lic:
        log.info("verify invalid ip=%s", client_ip())
        return reply("invalid", "الكود غير صحيح.", 404)

    if lic["status"] == "banned":
        return reply("banned", "هذا الكود محظور.", 403)

    expiry = parse(lic["expiry"])
    now = utcnow()
    if now >= expiry:
        return reply("expired", "انتهى الاشتراك، يرجى التجديد.", 403)

    if device not in lic["devices"]:
        if len(lic["devices"]) >= lic["max_devices"]:
            return reply("device_limit", "هذا الكود مرتبط بجهاز آخر. تواصل مع الدعم لإعادة الضبط.", 403)
        lic["devices"].append(device)

    lic["checks"] = lic.get("checks", 0) + 1
    lic["last_seen"] = iso(now)
    db.set(f"lic:{h}", lic)

    remaining = expiry - now
    extra = {
        "type": lic["type"],
        "expires_at": lic["expiry"],
        "remaining_days": remaining.days,
        "remaining_hours": remaining.seconds // 3600,
    }
    # رابط الباتش يُرسل فقط للأكواد الصالحة (يُضبط من متغير بيئة)
    patch_url = os.environ.get("PATCH_URL")
    if patch_url:
        extra["download_url"] = patch_url
    # اسم ملف الباتش وحزمة اللعبة (تتغيران مع تحديثات اللعبة والمناطق) بدون إعادة بناء التطبيق
    for env_name, field in (("PATCH_FILE_NAME", "target_file_name"), ("GAME_PACKAGE", "game_package")):
        if os.environ.get(env_name):
            extra[field] = os.environ[env_name]
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
        "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
        "connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
    )
    return resp


# ------------------------------------------------------------ الأدمن
@app.post("/api/admin/add")
@admin_required
def admin_add():
    data = request.get_json(silent=True) or {}
    dtype = str(data.get("type", "week"))
    days = DURATIONS.get(dtype)
    if days is None:
        try:
            days = int(data.get("days", 0))
        except (TypeError, ValueError):
            days = 0
        if not 1 <= days <= 3650:
            return jsonify(success=False, message=f"type غير معروف. المتاح: {', '.join(DURATIONS)} أو days (1-3650)."), 400
        dtype = f"{days}days"

    try:
        count = int(data.get("count", 1))
        max_devices = int(data.get("max_devices", 1))
    except (TypeError, ValueError):
        return jsonify(success=False, message="count/max_devices يجب أن تكون أرقاماً."), 400
    if not (1 <= count <= 50 and 1 <= max_devices <= 10):
        return jsonify(success=False, message="count (1-50) و max_devices (1-10)."), 400

    custom = normalize(data.get("key")) if data.get("key") else None
    if custom and (count != 1 or not KEY_RE.match(custom)):
        return jsonify(success=False, message="الكود المخصص: واحد فقط، 6-64 حرفاً (A-Z 0-9 - _)."), 400

    db = get_store()
    expiry = iso(utcnow() + timedelta(days=days))
    created = []
    for _ in range(count):
        key = custom or generate_key()
        h = hash_key(key)
        if db.get(f"lic:{h}"):
            if custom:
                return jsonify(success=False, message="هذا الكود موجود مسبقاً."), 409
            continue
        db.set(f"lic:{h}", {
            "type": dtype, "status": "active", "expiry": expiry, "created": iso(utcnow()),
            "devices": [], "max_devices": max_devices, "checks": 0,
            "last_seen": None, "note": str(data.get("note", ""))[:100],
        })
        db.sadd(INDEX, h)
        created.append({"key": key, "id": h[:12], "expires_at": expiry})
    return jsonify(success=True, message=f"تم إنشاء {len(created)} كود. احفظها الآن؛ لن تظهر مرة أخرى.", keys=created)


@app.get("/api/admin/list")
@admin_required
def admin_list():
    db = get_store()
    rows = []
    for h in db.smembers(INDEX)[:500]:
        lic = db.get(f"lic:{h}")
        if lic:
            rows.append(public_view(h, lic))
    return jsonify(success=True, count=len(rows), licenses=rows)


@app.post("/api/admin/control")
@admin_required
def admin_control():
    data = request.get_json(silent=True) or {}
    action = str(data.get("action", "")).lower()
    action = {"block": "ban", "unblock": "unban"}.get(action, action)
    if action not in {"ban", "unban", "reset_devices", "extend", "delete"}:
        return jsonify(success=False, message="action: ban | unban | reset_devices | extend | delete"), 400

    h = find_hash(data)
    db = get_store()
    lic = db.get(f"lic:{h}") if h else None
    if not lic:
        return jsonify(success=False, message="الترخيص غير موجود."), 404

    if action == "delete":
        db.delete(f"lic:{h}")
        db.srem(INDEX, h)
        return jsonify(success=True, message="تم الحذف.")

    if action == "ban":
        lic["status"] = "banned"
    elif action == "unban":
        lic["status"] = "active"
    elif action == "reset_devices":
        lic["devices"] = []
    elif action == "extend":
        try:
            days = int(data.get("days", 0))
        except (TypeError, ValueError):
            days = 0
        if not 1 <= days <= 3650:
            return jsonify(success=False, message="days (1-3650)."), 400
        base = max(parse(lic["expiry"]), utcnow())  # التمديد من الآن إن كان منتهياً
        lic["expiry"] = iso(base + timedelta(days=days))

    db.set(f"lic:{h}", lic)
    return jsonify(success=True, message=f"تم تنفيذ {action}.", license=public_view(h, lic))


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
