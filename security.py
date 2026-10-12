"""المصادقة وتحديد المعدل."""
from __future__ import annotations

import hmac
import os
from functools import wraps

from flask import jsonify, request

from store import get_store


def client_ip() -> str:
    fwd = request.headers.get("X-Forwarded-For", "")
    return (fwd.split(",")[0].strip() or request.headers.get("X-Real-IP") or request.remote_addr or "unknown")


def rate_limit(bucket: str, limit: int, window: int) -> bool:
    """True = مسموح. عند فشل التخزين لا نمنع المستخدمين الشرعيين."""
    try:
        return get_store().hit(f"rl:{bucket}", window) <= limit
    except Exception:
        return True


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        expected = os.environ.get("ADMIN_TOKEN", "")
        if len(expected) < 24:
            return jsonify(success=False, message="ADMIN_TOKEN غير مضبوط على السيرفر (24 حرفاً على الأقل)."), 503

        ip = client_ip()
        if not rate_limit(f"admin:{ip}", 60, 60):
            return jsonify(success=False, message="Too many requests."), 429

        auth = request.headers.get("Authorization", "")
        supplied = auth[7:] if auth.lower().startswith("bearer ") else request.headers.get("X-Admin-Token", "")
        if not hmac.compare_digest(supplied.encode(), expected.encode()):
            return jsonify(success=False, message="Unauthorized."), 401
        return fn(*args, **kwargs)

    return wrapper
