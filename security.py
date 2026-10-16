"""المصادقة وتحديد المعدل."""
from __future__ import annotations

import hmac
import os
from functools import wraps

from flask import g, jsonify, request

import iplog

from store import get_store


def client_ip() -> str:
    """عنوان العميل كما يراه السيرفر (Vercel يضبط هذه الترويسات بنفسه ولا يثق بما يرسله العميل)."""
    for name in ("X-Vercel-Forwarded-For", "X-Real-IP"):
        v = request.headers.get(name, "").split(",")[0].strip()
        if v:
            return v
    fwd = request.headers.get("X-Forwarded-For", "")
    return fwd.split(",")[0].strip() or request.remote_addr or "unknown"


def user_agent() -> str:
    return request.headers.get("User-Agent", "")


def _supplied() -> str:
    auth = request.headers.get("Authorization", "")
    return auth[7:] if auth.lower().startswith("bearer ") else request.headers.get("X-Admin-Token", "")


def role_of(supplied: str):
    """'owner' لتوكن المالك (OWNER_TOKEN)، 'admin' لتوكن المشرفين (ADMIN_TOKEN)، وإلا None."""
    owner = os.environ.get("OWNER_TOKEN", "")
    admin = os.environ.get("ADMIN_TOKEN", "")
    data = supplied.encode()
    if len(owner) >= 24 and hmac.compare_digest(data, owner.encode()):
        return "owner"
    if len(admin) >= 24 and hmac.compare_digest(data, admin.encode()):
        return "admin"
    return None


def rate_limit(bucket: str, limit: int, window: int) -> bool:
    """True = مسموح. عند فشل التخزين لا نمنع المستخدمين الشرعيين."""
    try:
        return get_store().hit(f"rl:{bucket}", window) <= limit
    except Exception:
        return True


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if len(os.environ.get("ADMIN_TOKEN", "")) < 24:
            return jsonify(success=False, message="ADMIN_TOKEN غير مضبوط على السيرفر (24 حرفاً على الأقل)."), 503

        ip = client_ip()
        if not rate_limit(f"admin:{ip}", 60, 60):
            return jsonify(success=False, message="Too many requests."), 429

        role = role_of(_supplied())
        if role is None:
            iplog.record("admin_fail", "", ip, user_agent())
            return jsonify(success=False, message="Unauthorized."), 401
        g.role = role
        iplog.record(role, "", ip, user_agent())
        return fn(*args, **kwargs)

    return wrapper


def owner_required(fn):
    """للمالك فقط. أي توكن آخر يحصل على 404 كأن المسار غير موجود."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        ip = client_ip()
        if not rate_limit(f"owner:{ip}", 30, 60):
            return jsonify(success=False, message="Too many requests."), 429
        supplied = _supplied()
        if role_of(supplied) != "owner":
            if supplied:
                iplog.record("owner_fail", "", ip, user_agent())
            return jsonify(status="error", message="Not found."), 404
        iplog.record("owner", "", ip, user_agent())
        return fn(*args, **kwargs)

    return wrapper
