"""سجل عناوين IP اليومي (للمالك فقط). يُحفظ يومياً ويُحذف تلقائياً بعد RETENTION_DAYS يوم.

كل سجل = (النوع، المعرّف، العنوان) في اليوم الواحد، مع أول/آخر ظهور وعدد المرات.
أنواع: user (تحقق من كود) · invalid (كود خاطئ) · admin (دخول اللوحة بتوكن المشرفين)
       · owner (دخول المالك) · admin_fail / owner_fail (توكن خاطئ)
"""
from __future__ import annotations

import logging
from datetime import timedelta

from core import iso, parse, utcnow
from store import get_store

log = logging.getLogger("iplog")
RETENTION_DAYS = 90
INDEX = "iplog_days"
THROTTLE_KINDS = {"admin", "owner", "admin_fail", "owner_fail"}  # لا نكتب أكثر من مرة كل 5 دقائق
MAX_ROWS = 5000


def record(kind: str, who: str, ip: str, ua: str = "", note: str = "", status: str = "", dev: str = "") -> None:
    """يسجّل الحدث. لا يرفع أي استثناء أبداً حتى لا يعطّل التحقق أو اللوحة."""
    try:
        db = get_store()
        now = utcnow()
        day = now.strftime("%Y-%m-%d")
        key = f"iplog:{day}"
        data = db.get(key)
        fresh = data is None
        data = data or {}
        ek = f"{kind}|{who}|{ip}"
        e = data.get(ek)
        if e:
            if kind in THROTTLE_KINDS and (now - parse(e["last"])) < timedelta(minutes=5):
                return
            e["last"] = iso(now)
            e["count"] += 1
            e["status"] = status or e.get("status", "")
            e["dev"] = dev or e.get("dev", "")
            e["note"] = note or e.get("note", "")
        else:
            data[ek] = {"kind": kind, "who": who, "ip": ip, "note": note, "status": status, "dev": dev,
                        "ua": ua[:120], "first": iso(now), "last": iso(now), "count": 1}
        db.set(key, data)
        if fresh:
            db.sadd(INDEX, day)
            cutoff = (now - timedelta(days=RETENTION_DAYS)).strftime("%Y-%m-%d")
            for d in db.smembers(INDEX):
                if d < cutoff:
                    db.delete(f"iplog:{d}")
                    db.srem(INDEX, d)
    except Exception:  # noqa: BLE001
        log.exception("iplog failed")


def read(days: int = 30) -> list[dict]:
    db = get_store()
    cutoff = (utcnow() - timedelta(days=max(1, days))).strftime("%Y-%m-%d")
    wanted = sorted((d for d in db.smembers(INDEX) if d >= cutoff), reverse=True)
    rows: list[dict] = []
    for day, data in zip(wanted, db.mget([f"iplog:{d}" for d in wanted])):
        for e in sorted((data or {}).values(), key=lambda x: x["last"], reverse=True):
            rows.append({"day": day, **e})
    return rows[:MAX_ROWS]
