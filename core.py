"""منطق التراخيص والإعدادات (يستخدمه الـ API وبوت تيليجرام معاً)."""
from __future__ import annotations

import base64
import hashlib
import os
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from store import get_store

DURATIONS = {"week": 7, "month": 30, "2.5months": 75}
KEY_RE = re.compile(r"^[A-Z0-9][A-Z0-9_-]{5,63}$")
DEVICE_RE = re.compile(r"^[A-Za-z0-9_-]{8,128}$")
INDEX = "licenses"
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # بدون أحرف متشابهة (0/O, 1/I)
ACTIONS = {"ban", "unban", "reset_devices", "extend", "delete"}


class LicenseError(Exception):
    def __init__(self, message: str, status: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status = status


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


def normalize(key: object) -> str:
    return str(key or "").strip().upper()


def generate_key() -> str:
    return "VIP-" + "-".join("".join(secrets.choice(ALPHABET) for _ in range(4)) for _ in range(3))


def ver_tuple(v: str) -> tuple:
    parts = re.findall(r"\d+", str(v or ""))
    return tuple(int(p) for p in parts[:4]) or (0,)


def find_hash(data: dict) -> Optional[str]:
    """يحدد الترخيص بواسطة key أو id (أول 8+ خانات من البصمة)."""
    if data.get("key"):
        return hash_key(normalize(data["key"]))
    lic_id = str(data.get("id", "")).lower().strip()
    if len(lic_id) >= 8:
        matches = [h for h in get_store().smembers(INDEX) if h.startswith(lic_id)]
        if len(matches) == 1:
            return matches[0]
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
        "recoverable": bool(lic.get("enc")),
    }



# ------------------------------------------------------------ حفظ مشفّر للأكواد (اختياري)
def _fernet():
    """يعمل فقط إذا ضُبط KEY_VAULT_SECRET في Vercel (24 حرفاً فأكثر)؛ وإلا لا يُحفظ أي شيء قابل للاسترجاع."""
    secret = os.environ.get("KEY_VAULT_SECRET", "")
    if len(secret) < 24:
        return None
    from cryptography.fernet import Fernet
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(f"vault:{secret}".encode()).digest()))


def vault_enabled() -> bool:
    return _fernet() is not None


def reveal_key(data: dict) -> str:
    h = find_hash(data)
    lic = get_store().get(f"lic:{h}") if h else None
    if not lic:
        raise LicenseError("الترخيص غير موجود.", 404)
    f = _fernet()
    if not lic.get("enc"):
        raise LicenseError("هذا الكود أُنشئ قبل تفعيل الحفظ المشفّر، ولا يمكن استرجاعه.", 410)
    if f is None:
        raise LicenseError("KEY_VAULT_SECRET غير مضبوط في Vercel.", 503)
    try:
        return f.decrypt(lic["enc"].encode()).decode()
    except Exception:
        raise LicenseError("تعذر فك التشفير (هل تغيّر KEY_VAULT_SECRET؟).", 500)

# ------------------------------------------------------------ التراخيص
def create_licenses(data: dict) -> list[dict]:
    dtype = str(data.get("type", "week"))
    days = DURATIONS.get(dtype)
    if days is None:
        try:
            days = int(data.get("days", 0))
        except (TypeError, ValueError):
            days = 0
        if not 1 <= days <= 3650:
            raise LicenseError(f"type غير معروف. المتاح: {', '.join(DURATIONS)} أو days (1-3650).")
        dtype = f"{days}days"

    try:
        count = int(data.get("count", 1))
        max_devices = int(data.get("max_devices", 1))
    except (TypeError, ValueError):
        raise LicenseError("count/max_devices يجب أن تكون أرقاماً.")
    if not (1 <= count <= 50 and 1 <= max_devices <= 10):
        raise LicenseError("count (1-50) و max_devices (1-10).")

    custom = normalize(data.get("key")) if data.get("key") else None
    if custom and (count != 1 or not KEY_RE.match(custom)):
        raise LicenseError("الكود المخصص: واحد فقط، 6-64 حرفاً (A-Z 0-9 - _).")

    db = get_store()
    vault = _fernet()
    now = utcnow()
    expiry = iso(now + timedelta(days=days))
    created: list[dict] = []
    for _ in range(count):
        key = custom or generate_key()
        h = hash_key(key)
        if db.get(f"lic:{h}"):
            if custom:
                raise LicenseError("هذا الكود موجود مسبقاً.", 409)
            continue
        record = {
            "type": dtype, "status": "active", "expiry": expiry, "created": iso(now),
            "devices": [], "max_devices": max_devices, "checks": 0,
            "last_seen": None, "note": str(data.get("note", ""))[:100],
        }
        if vault:
            record["enc"] = vault.encrypt(key.encode()).decode()
        db.set(f"lic:{h}", record)
        db.sadd(INDEX, h)
        created.append({"key": key, "id": h[:12], "expires_at": expiry})
    return created


def list_licenses(limit: int = 500) -> list[dict]:
    db = get_store()
    hashes = db.smembers(INDEX)[:limit]
    rows = []
    for h, lic in zip(hashes, db.mget([f"lic:{h}" for h in hashes])):
        if lic:
            rows.append(public_view(h, lic))
    return rows


def control_license(data: dict) -> tuple[str, Optional[dict]]:
    action = str(data.get("action", "")).lower()
    action = {"block": "ban", "unblock": "unban"}.get(action, action)
    if action not in ACTIONS:
        raise LicenseError("action: ban | unban | reset_devices | extend | delete")

    h = find_hash(data)
    db = get_store()
    lic = db.get(f"lic:{h}") if h else None
    if not lic:
        raise LicenseError("الترخيص غير موجود.", 404)

    if action == "delete":
        db.delete(f"lic:{h}")
        db.srem(INDEX, h)
        return "تم الحذف.", None

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
            raise LicenseError("days (1-3650).")
        base = max(parse(lic["expiry"]), utcnow())  # التمديد من الآن إن كان منتهياً
        lic["expiry"] = iso(base + timedelta(days=days))

    db.set(f"lic:{h}", lic)
    return f"تم تنفيذ {action}.", public_view(h, lic)


# ------------------------------------------------------------ إعدادات الباتش والتطبيق
SETTINGS_KEY = "settings"
FILE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,100}\.pak$")
PKG_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$")
VERSION_RE = re.compile(r"^[A-Za-z0-9._-]{0,32}$")
APPVER_RE = re.compile(r"^\d+(\.\d+){0,3}$")
URL_RE = re.compile(r"^https?://[^\s]{4,500}$")

DEFAULTS: dict = {
    "patch_url": "",             # رابط تحميل الباتش (يُرسل للتطبيق بعد التحقق من الكود فقط)
    "patch_file_name": "",       # اسم الملف داخل مجلد اللعبة (.pak)
    "game_package": "",          # حزمة اللعبة (مثل com.tencent.ig)
    "patch_version": "1",        # غيّر الرقم عند كل باتش جديد ليعرف التطبيق أن هناك تحديثاً
    "patch_sha256": "",          # بصمة SHA-256 للملف (اختياري) ليتحقق التطبيق من سلامته
    "patch_notes": "",           # ما الجديد في هذا الباتش (يظهر في التطبيق)
    "force_patch_update": False,  # تحديث الباتش تلقائياً وإلزامياً
    "min_app_version": "",       # أقل نسخة تطبيق مسموحة (أي نسخة أقدم تُمنع وتُطلب منها التحديث)
    "update_url": "",            # رابط تحميل APK الجديد
    "notice": "",                # إعلان يظهر في أعلى التطبيق
    "support_url": "",           # رابط الدعم (تيليجرام/واتساب)
    "maintenance": False,        # إيقاف التحقق مؤقتاً
}
ENV_FALLBACK = {"patch_url": "PATCH_URL", "patch_file_name": "PATCH_FILE_NAME", "game_package": "GAME_PACKAGE"}
BOOL_FIELDS = {"force_patch_update", "maintenance"}


def get_stored_settings() -> dict:
    try:
        return get_store().get(SETTINGS_KEY) or {}
    except Exception:
        return {}


def get_settings() -> dict:
    """القيمة المحفوظة من اللوحة أولاً، ثم متغيرات Vercel (PATCH_URL...)، ثم الافتراضي."""
    out = dict(DEFAULTS)
    for field, env in ENV_FALLBACK.items():
        out[field] = os.environ.get(env, "").strip()
    stored = get_stored_settings()
    for field, value in stored.items():
        if field in DEFAULTS and value not in ("", None):
            out[field] = value
    return out


def validate_settings(data: dict) -> dict:
    clean: dict = {}
    for field in DEFAULTS:
        if field not in data:
            continue
        value = data[field]
        if field in BOOL_FIELDS:
            clean[field] = bool(value)
            continue
        value = str(value or "").strip()
        if field in ("patch_url", "update_url", "support_url"):
            if value and not URL_RE.match(value):
                raise LicenseError("الرابط يجب أن يبدأ بـ http:// أو https://")
        elif field == "patch_file_name" and value and not FILE_RE.match(value):
            raise LicenseError("اسم الملف يجب أن ينتهي بـ .pak ويحتوي أحرفاً إنجليزية وأرقاماً فقط.")
        elif field == "game_package" and value and not PKG_RE.match(value):
            raise LicenseError("حزمة اللعبة غير صحيحة (مثال: com.tencent.ig).")
        elif field == "patch_version" and not VERSION_RE.match(value):
            raise LicenseError("رقم الباتش: أحرف وأرقام ونقطة وشرطة فقط (حتى 32).")
        elif field == "min_app_version" and value and not APPVER_RE.match(value):
            raise LicenseError("نسخة التطبيق بالشكل 1.3.0")
        elif field == "notice" and len(value) > 300:
            raise LicenseError("الإعلان أطول من 300 حرف.")
        elif field == "patch_notes" and len(value) > 600:
            raise LicenseError("ملاحظات الباتش أطول من 600 حرف.")
        elif field == "patch_sha256" and value and not re.fullmatch(r"[A-Fa-f0-9]{64}", value):
            raise LicenseError("بصمة SHA-256 يجب أن تكون 64 خانة (0-9 و a-f).")
        clean[field] = value
    return clean


def save_settings(data: dict) -> dict:
    clean = validate_settings(data)
    stored = get_stored_settings()
    stored.update(clean)
    get_store().set(SETTINGS_KEY, stored)
    return get_settings()
