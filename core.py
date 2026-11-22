"""منطق التراخيص والإعدادات وOTA (يستخدمه الـ API وبوت تيليجرام معاً)."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from store import get_store

DURATIONS = {"week": 7, "month": 30, "2.5months": 75, "year": 365, "day": 1}
KEY_RE = re.compile(r"^[A-Z0-9][A-Z0-9_-]{5,63}$")
DEVICE_RE = re.compile(r"^[A-Za-z0-9_-]{8,128}$")
INDEX = "licenses"
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
ACTIONS = {"ban", "unban", "reset_devices", "extend", "delete", "set_note", "set_max_devices"}


class LicenseError(Exception):
    def __init__(self, message: str, status: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status = status


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
    now = utcnow()
    expiry = parse(lic["expiry"])
    expired = expiry <= now
    remaining = max(0, (expiry - now).days) if not expired else 0
    status = "expired" if expired and lic["status"] == "active" else lic["status"]
    return {
        "id": h[:12],
        "type": lic["type"],
        "status": status,
        "expires_at": lic["expiry"],
        "created": lic.get("created"),
        "devices": len(lic.get("devices") or []),
        "max_devices": lic.get("max_devices", 1),
        "checks": lic.get("checks", 0),
        "last_seen": lic.get("last_seen"),
        "note": lic.get("note", ""),
        "recoverable": bool(lic.get("enc")),
        "remaining_days": remaining,
        "soon": status == "active" and remaining <= 3,
    }


def _fernet():
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
            "type": dtype,
            "status": "active",
            "expiry": expiry,
            "created": iso(now),
            "devices": [],
            "max_devices": max_devices,
            "checks": 0,
            "last_seen": None,
            "note": str(data.get("note", ""))[:100],
        }
        if vault:
            record["enc"] = vault.encrypt(key.encode()).decode()
        db.set(f"lic:{h}", record)
        db.sadd(INDEX, h)
        created.append({"key": key, "id": h[:12], "expires_at": expiry})
    return created


def list_licenses(
    limit: int = 500,
    *,
    status: str = "",
    q: str = "",
    soon_only: bool = False,
) -> list[dict]:
    db = get_store()
    hashes = db.smembers(INDEX)
    rows: list[dict] = []
    q_norm = (q or "").strip().lower()
    status_norm = (status or "").strip().lower()
    for h, lic in zip(hashes, db.mget([f"lic:{h}" for h in hashes])):
        if not lic:
            continue
        view = public_view(h, lic)
        if status_norm and view["status"] != status_norm:
            continue
        if soon_only and not view.get("soon"):
            continue
        if q_norm:
            hay = f"{view['id']} {view.get('note', '')} {view.get('type', '')}".lower()
            if q_norm not in hay:
                continue
        rows.append(view)
    rows.sort(key=lambda r: r.get("created") or "", reverse=True)
    return rows[: max(1, min(limit, 2000))]


def license_stats() -> dict:
    rows = list_licenses(limit=2000)
    counts = {"active": 0, "expired": 0, "banned": 0, "total": len(rows), "soon": 0, "checks": 0}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        counts["checks"] += int(r.get("checks") or 0)
        if r.get("soon"):
            counts["soon"] += 1
    return counts


def control_license(data: dict) -> tuple[str, Optional[dict]]:
    action = str(data.get("action", "")).lower()
    action = {"block": "ban", "unblock": "unban"}.get(action, action)
    if action not in ACTIONS:
        raise LicenseError(
            "action: ban | unban | reset_devices | extend | delete | set_note | set_max_devices"
        )

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
        base = max(parse(lic["expiry"]), utcnow())
        lic["expiry"] = iso(base + timedelta(days=days))
    elif action == "set_note":
        lic["note"] = str(data.get("note", ""))[:100]
    elif action == "set_max_devices":
        try:
            md = int(data.get("max_devices", 1))
        except (TypeError, ValueError):
            md = 0
        if not 1 <= md <= 10:
            raise LicenseError("max_devices (1-10).")
        lic["max_devices"] = md

    db.set(f"lic:{h}", lic)
    return f"تم تنفيذ {action}.", public_view(h, lic)


def cleanup_expired(older_than_days: int = 30) -> int:
    if not 1 <= older_than_days <= 3650:
        raise LicenseError("older_than_days (1-3650).")
    db = get_store()
    cutoff = utcnow() - timedelta(days=older_than_days)
    removed = 0
    hashes = db.smembers(INDEX)
    for h, lic in zip(hashes, db.mget([f"lic:{h}" for h in hashes])):
        if not lic:
            db.srem(INDEX, h)
            continue
        try:
            exp = parse(lic["expiry"])
        except (KeyError, TypeError, ValueError):
            continue
        if exp < cutoff and lic.get("status") != "banned":
            db.delete(f"lic:{h}")
            db.srem(INDEX, h)
            removed += 1
    return removed


def bulk_extend(data: dict) -> dict:
    try:
        days = int(data.get("days", 0))
    except (TypeError, ValueError):
        days = 0
    if not 1 <= days <= 3650:
        raise LicenseError("days (1-3650).")
    ids = data.get("ids") or []
    if isinstance(ids, str):
        ids = [x.strip() for x in ids.replace(",", " ").split() if x.strip()]
    status_filter = str(data.get("status", "")).lower().strip()
    rows = list_licenses(limit=2000)
    targets = []
    if ids:
        id_set = {i.lower() for i in ids}
        targets = [r for r in rows if r["id"] in id_set or any(r["id"].startswith(i) for i in id_set)]
    elif status_filter in ("active", "expired", "banned"):
        targets = [r for r in rows if r["status"] == status_filter]
    else:
        raise LicenseError("حدد ids أو status (active|expired|banned).")
    ok, fail = 0, 0
    for r in targets[:200]:
        try:
            control_license({"id": r["id"], "action": "extend", "days": days})
            ok += 1
        except LicenseError:
            fail += 1
    return {"extended": ok, "failed": fail, "days": days}


# ------------------------------------------------------------ إعدادات الباتش والتطبيق وOTA
SETTINGS_KEY = "settings"
FILE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,100}\.(pak|zip)$", re.IGNORECASE)
PKG_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$")
VERSION_RE = re.compile(r"^[A-Za-z0-9._-]{0,32}$")
APPVER_RE = re.compile(r"^\d+(\.\d+){0,3}$")
URL_RE = re.compile(r"^https?://[^\s]{4,500}$")

DEFAULTS: dict = {
    "patch_url": "",
    "patch_file_name": "",
    "game_package": "",
    "patch_version": "1",
    "patch_sha256": "",
    "patch_notes": "",
    "deploy_mode": "auto",
    "force_patch_update": False,
    "min_app_version": "",
    "latest_app_version": "",
    "update_url": "",
    "update_message": "",
    "ota_version": "1.0.0",
    "ota_notes": "",
    "ota_activate_label": "",
    "ota_install_label": "",
    "notice": "",
    "support_url": "",
    "maintenance": False,
}
ENV_FALLBACK = {"patch_url": "PATCH_URL", "patch_file_name": "PATCH_FILE_NAME", "game_package": "GAME_PACKAGE"}
BOOL_FIELDS = {"force_patch_update", "maintenance"}


def get_stored_settings() -> dict:
    try:
        return get_store().get(SETTINGS_KEY) or {}
    except Exception:
        return {}


def get_settings() -> dict:
    out = dict(DEFAULTS)
    for field, env in ENV_FALLBACK.items():
        out[field] = os.environ.get(env, "").strip()
    stored = get_stored_settings()
    for field, value in stored.items():
        if field in DEFAULTS and value not in ("", None):
            out[field] = value
    return out


def build_ota_bundle() -> dict:
    s = get_settings()
    payload: dict = {}
    if s.get("ota_notes"):
        payload["notes"] = s["ota_notes"]
    if s.get("notice"):
        payload["notice"] = s["notice"]
    if s.get("support_url"):
        payload["support_url"] = s["support_url"]
    if s.get("ota_activate_label"):
        payload["activate_label"] = s["ota_activate_label"]
    if s.get("ota_install_label"):
        payload["install_label"] = s["ota_install_label"]

    canonical = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    digest = hashlib.sha256(canonical).hexdigest()
    return {
        "ota_version": s.get("ota_version") or "1.0.0",
        "payload": payload,
        "sha256": digest,
    }


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
            raise LicenseError("اسم الملف يجب أن ينتهي بـ .pak أو .zip ويحتوي أحرفاً إنجليزية وأرقاماً فقط.")
        elif field == "game_package" and value and not PKG_RE.match(value):
            raise LicenseError("حزمة اللعبة غير صحيحة (مثال: com.tencent.ig).")
        elif field in ("patch_version", "ota_version") and value and not VERSION_RE.match(value):
            raise LicenseError("رقم الإصدار: أحرف وأرقام ونقطة وشرطة فقط (حتى 32).")
        elif field in ("min_app_version", "latest_app_version") and value and not APPVER_RE.match(value):
            raise LicenseError("نسخة التطبيق بالشكل 2.1.0")
        elif field in ("notice", "update_message", "ota_notes") and len(value) > 400:
            raise LicenseError("النص أطول من 400 حرف.")
        elif field in ("ota_activate_label", "ota_install_label") and len(value) > 40:
            raise LicenseError("نص الزر أطول من 40 حرفاً.")
        elif field == "patch_notes" and len(value) > 600:
            raise LicenseError("ملاحظات الباتش أطول من 600 حرف.")
        elif field == "patch_sha256" and value and not re.fullmatch(r"[A-Fa-f0-9]{64}", value):
            raise LicenseError("بصمة SHA-256 يجب أن تكون 64 خانة (0-9 و a-f).")
        elif field == "deploy_mode":
            value = value.lower() if value else "auto"
            if value not in ("auto", "pak", "folder"):
                raise LicenseError("deploy_mode: auto | pak | folder")
        clean[field] = value
    return clean


def save_settings(data: dict) -> dict:
    clean = validate_settings(data)
    stored = get_stored_settings()
    stored.update(clean)
    get_store().set(SETTINGS_KEY, stored)
    return get_settings()
