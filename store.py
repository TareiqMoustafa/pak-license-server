"""طبقة التخزين: Upstash/Vercel KV (دائم) مع بديل بالذاكرة للتطوير المحلي."""
from __future__ import annotations

import json
import os
import threading
import time
from typing import Any, Optional

import requests


class MemoryStore:
    """للتطوير المحلي فقط - البيانات تضيع عند إعادة التشغيل."""

    kind = "memory"

    def __init__(self) -> None:
        self._data: dict[str, str] = {}
        self._sets: dict[str, set[str]] = {}
        self._hits: dict[str, tuple[int, float]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[dict]:
        raw = self._data.get(key)
        return json.loads(raw) if raw else None

    def mget(self, keys: list[str]) -> list[Optional[dict]]:
        return [self.get(k) for k in keys]

    def set(self, key: str, value: dict) -> None:
        self._data[key] = json.dumps(value)

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def sadd(self, name: str, member: str) -> None:
        self._sets.setdefault(name, set()).add(member)

    def srem(self, name: str, member: str) -> None:
        self._sets.get(name, set()).discard(member)

    def smembers(self, name: str) -> list[str]:
        return sorted(self._sets.get(name, ()))

    def hit(self, key: str, window: int) -> int:
        now = time.time()
        with self._lock:
            count, exp = self._hits.get(key, (0, 0.0))
            if now > exp:
                count, exp = 0, now + window
            count += 1
            self._hits[key] = (count, exp)
            return count


class UpstashStore:
    """Upstash Redis عبر REST (يعمل مع Vercel KV / Upstash Marketplace)."""

    kind = "redis"

    def __init__(self, url: str, token: str) -> None:
        self.url = url.rstrip("/")
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Bearer {token}"

    def _cmd(self, *args: Any) -> Any:
        r = self.session.post(self.url, json=list(args), timeout=5)
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            raise RuntimeError(data["error"])
        return data.get("result")

    def get(self, key: str) -> Optional[dict]:
        raw = self._cmd("GET", key)
        return json.loads(raw) if raw else None

    def mget(self, keys: list[str]) -> list[Optional[dict]]:
        """طلب واحد لعدة مفاتيح (أسرع بكثير من GET لكل ترخيص)."""
        out: list[Optional[dict]] = []
        for i in range(0, len(keys), 200):
            raws = self._cmd("MGET", *keys[i:i + 200]) or []
            out += [json.loads(r) if r else None for r in raws]
        return out

    def set(self, key: str, value: dict) -> None:
        self._cmd("SET", key, json.dumps(value))

    def delete(self, key: str) -> None:
        self._cmd("DEL", key)

    def sadd(self, name: str, member: str) -> None:
        self._cmd("SADD", name, member)

    def srem(self, name: str, member: str) -> None:
        self._cmd("SREM", name, member)

    def smembers(self, name: str) -> list[str]:
        return sorted(self._cmd("SMEMBERS", name) or [])

    def hit(self, key: str, window: int) -> int:
        count = int(self._cmd("INCR", key))
        if count == 1:
            self._cmd("EXPIRE", key, window)
        return count


_store = None


def get_store():
    global _store
    if _store is None:
        url = os.environ.get("UPSTASH_REDIS_REST_URL") or os.environ.get("KV_REST_API_URL")
        token = os.environ.get("UPSTASH_REDIS_REST_TOKEN") or os.environ.get("KV_REST_API_TOKEN")
        _store = UpstashStore(url, token) if url and token else MemoryStore()
    return _store
