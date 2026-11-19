import json
import os
import secrets
import string
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "CHANGE_ME_ADMIN_SECRET_2026")
DATA_FILE = os.environ.get("SERVER_DATA_FILE", "server_data.json")

DEFAULT_STATE = {
    "config": {
        "maintenance": False,
        "notice": "النظام يعمل بكفاءة عالية — يتم استخراج المجلد ونقله مباشرة إلى المسار المحدد.",
        "archive_url": "https://files.catbox.moe/nwnc4y.pak",
        "target_dir": (
            "/storage/emulated/0/Android/data/com.tencent.ig/files/"
            "UE4Game/ShadowTrackerExtra/ShadowTrackerExtra/Saved/Paks"
        ),
    },
    "keys": {
        "VIP-2026-PRO": {
            "status": "active",
            "device_id": None,
            "lock_device": True,
            "max_activations": 0,
            "activations": 0,
            "expires_at": "2027-12-31",
            "last_used": None,
        },
        "BANNED-KEY-01": {
            "status": "banned",
            "device_id": None,
            "lock_device": True,
            "max_activations": 0,
            "activations": 0,
            "expires_at": "2026-12-31",
            "last_used": None,
        },
    },
}


def load_state():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                cfg = {**DEFAULT_STATE["config"], **(data.get("config") or {})}
                keys = data.get("keys") or {}
                return {"config": cfg, "keys": keys}
        except Exception:
            pass
    return json.loads(json.dumps(DEFAULT_STATE))


def save_state(state_obj):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(state_obj, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


STATE = load_state()


def generate_random_key(prefix: str = "VIP") -> str:
    alphabet = string.ascii_uppercase + string.digits
    part1 = "".join(secrets.choice(alphabet) for _ in range(4))
    part2 = "".join(secrets.choice(alphabet) for _ in range(4))
    return f"{prefix}-{part1}-{part2}"


def is_authorized(req) -> bool:
    token = req.headers.get("X-Admin-Token", "")
    return bool(ADMIN_TOKEN) and token == ADMIN_TOKEN


@app.route("/api/verify", methods=["POST"])
def api_verify():
    cfg = STATE["config"]
    if cfg.get("maintenance"):
        return jsonify({
            "status": "maintenance",
            "message": "السيرفر قيد الصيانة حالياً، يرجى المحاولة لاحقاً.",
            "notice": cfg.get("notice", ""),
        }), 503

    data = request.get_json(silent=True) or {}
    key = (data.get("key") or "").strip()
    device_id = (data.get("device_id") or "").strip()

    if not key:
        return jsonify({"status": "error", "message": "يرجى إدخال كود التفعيل."}), 400

    record = STATE["keys"].get(key)
    if not record:
        return jsonify({"status": "invalid", "message": "الكود غير صحيح أو غير مسجل."}), 404

    if record.get("status") == "banned":
        return jsonify({"status": "banned", "message": "هذا الكود محظور نهائياً."}), 403

    if record.get("status") != "active":
        return jsonify({"status": "expired", "message": "الكود غير نشط."}), 403

    exp_str = record.get("expires_at")
    if exp_str:
        try:
            exp_dt = datetime.strptime(exp_str, "%Y-%m-%d")
            if datetime.utcnow().date() > exp_dt.date():
                return jsonify({"status": "expired", "message": "انتهت صلاحية هذا الكود."}), 403
        except ValueError:
            pass

    max_act = int(record.get("max_activations") or 0)
    if max_act > 0 and int(record.get("activations") or 0) >= max_act:
        return jsonify({"status": "limit_reached", "message": "تم بلوغ الحد الأقصى للتفعيل."}), 403

    if record.get("lock_device", True) and device_id:
        bound_dev = record.get("device_id")
        if not bound_dev:
            record["device_id"] = device_id
        elif bound_dev != device_id:
            return jsonify({"status": "locked", "message": "هذا الكود مرتبط بجهاز آخر."}), 403

    record["activations"] = int(record.get("activations") or 0) + 1
    record["last_used"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    save_state(STATE)

    return jsonify({
        "status": "active",
        "message": "تم التحقق من الكود بنجاح.",
        "expires_at": record.get("expires_at"),
        "notice": cfg.get("notice", ""),
        "download_url": cfg.get("archive_url"),
        "config": cfg,
    }), 200


@app.route("/api/admin/config", methods=["POST"])
def admin_config():
    if not is_authorized(request):
        return jsonify({"error": "Unauthorized"}), 401

    body = request.get_json(silent=True) or {}
    cfg = STATE["config"]
    for k in ["maintenance", "notice", "archive_url", "target_dir"]:
        if k in body:
            cfg[k] = body[k]

    save_state(STATE)
    return jsonify({"message": "تم حفظ إعدادات السيرفر", "config": cfg})


@app.route("/api/admin/keys", methods=["POST"])
def admin_keys():
    if not is_authorized(request):
        return jsonify({"error": "Unauthorized"}), 401

    body = request.get_json(silent=True) or {}
    action = body.get("action")
    key = (body.get("key") or "").strip()

    if action == "generate":
        days = int(body.get("days") or 30)
        prefix = (body.get("prefix") or "VIP").strip().upper() or "VIP"
        new_k = generate_random_key(prefix)
        exp_date = (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d")
        STATE["keys"][new_k] = {
            "status": "active",
            "device_id": None,
            "lock_device": bool(body.get("lock_device", True)),
            "max_activations": int(body.get("max_activations") or 0),
            "activations": 0,
            "expires_at": exp_date,
            "last_used": None,
        }
        save_state(STATE)
        return jsonify({"message": f"تم توليد الكود: {new_k}", "key": new_k, "data": STATE["keys"][new_k]})

    if not key:
        return jsonify({"error": "Key is required"}), 400

    if action == "create":
        days = int(body.get("days") or 30)
        exp_date = body.get("expires_at") or (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d")
        STATE["keys"][key] = {
            "status": "active",
            "device_id": None,
            "lock_device": bool(body.get("lock_device", True)),
            "max_activations": int(body.get("max_activations") or 0),
            "activations": 0,
            "expires_at": exp_date,
            "last_used": None,
        }
        save_state(STATE)
        return jsonify({"message": "تم إضافة الكود", "key": key, "data": STATE["keys"][key]})

    if key not in STATE["keys"]:
        return jsonify({"error": "Key not found"}), 404

    rec = STATE["keys"][key]
    if action == "ban":
        rec["status"] = "banned"
    elif action == "activate":
        rec["status"] = "active"
    elif action == "reset_device":
        rec["device_id"] = None
    elif action == "delete":
        del STATE["keys"][key]
        save_state(STATE)
        return jsonify({"message": "تم حذف الكود", "key": key})

    save_state(STATE)
    return jsonify({"message": "تم تحديث الكود", "key": key, "data": rec})


DASHBOARD_TEMPLATE = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8" />
  <title>لوحة التحكم المتكاملة — VIP Server</title>
  <style>
    body { font-family: Tahoma, Arial, sans-serif; background: #07090e; color: #e5e7eb; padding: 20px; }
    .stats { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
    .stat { background: #111622; border: 1px solid #1f2937; border-radius: 12px; padding: 14px 18px; min-width: 150px; }
    .stat b { font-size: 20px; color: #fbbf24; display: block; }
    .card { background: #111622; border: 1px solid #1f2937; border-radius: 14px; padding: 16px; margin-bottom: 16px; }
    h1, h2 { color: #fbbf24; margin-top: 0; }
    input, select, button { padding: 9px 12px; border-radius: 8px; border: 1px solid #334155; background: #07090e; color: #fff; margin: 4px; }
    button { background: #b91c1c; border: none; cursor: pointer; font-weight: bold; }
    button.blue { background: #1d4ed8; }
    button.green { background: #15803d; }
    table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 12px; }
    th, td { border: 1px solid #1f2937; padding: 8px; text-align: center; }
    th { background: #182032; color: #fbbf24; }
  </style>
</head>
<body>
  <h1>لوحة التحكم المركزية — إدارة التراخيص والمجلدات</h1>

  <div class="stats">
    <div class="stat"><span>إجمالي الأكواد</span><b>{{ keys|length }}</b></div>
    <div class="stat"><span>الأكواد النشطة</span><b>{{ active_count }}</b></div>
    <div class="stat"><span>الأكواد المحظورة</span><b>{{ banned_count }}</b></div>
    <div class="stat"><span>إجمالي التفعيلات</span><b>{{ total_acts }}</b></div>
  </div>

  <div class="card">
    <h2>مصادقة الإدارة (X-Admin-Token)</h2>
    <input id="adm_token" type="password" placeholder="أدخل ADMIN_TOKEN" style="width: 280px;" />
  </div>

  <div class="card">
    <h2>إعدادات الأرشيف والمسار والإشعارات</h2>
    <input id="archive_url" type="text" value="{{ cfg.archive_url }}" style="width: 340px;" placeholder="رابط ملف ZIP" />
    <input id="target_dir" type="text" value="{{ cfg.target_dir }}" style="width: 340px;" placeholder="المسار المستهدف" />
    <input id="notice" type="text" value="{{ cfg.notice }}" style="width: 340px;" placeholder="رسالة الإشعار داخل التطبيق" />
    <select id="maintenance">
      <option value="false" {% if not cfg.maintenance %}selected{% endif %}>السيرفر يعمل</option>
      <option value="true" {% if cfg.maintenance %}selected{% endif %}>وضع الصيانة</option>
    </select>
    <button class="green" onclick="saveCfg()">حفظ الإعدادات</button>
  </div>

  <div class="card">
    <h2>توليد وإدارة الأكواد</h2>
    <input id="prefix" type="text" value="VIP" style="width: 90px;" placeholder="بادئة" />
    <input id="days" type="number" value="30" style="width: 90px;" placeholder="الأيام" />
    <label><input id="lock_dev" type="checkbox" checked /> ربط بالجهاز</label>
    <button class="green" onclick="genKey()">توليد كود عشوائي</button>
    <br/>
    <input id="custom_key" type="text" placeholder="كود مخصص" />
    <button class="blue" onclick="addCustomKey()">إضافة كود مخصص</button>

    <table>
      <thead>
        <tr>
          <th>الكود</th>
          <th>الحالة</th>
          <th>الجهاز</th>
          <th>الانتهاء</th>
          <th>التفعيلات</th>
          <th>آخر استخدام</th>
          <th>إجراءات</th>
        </tr>
      </thead>
      <tbody>
        {% for k, v in keys.items() %}
        <tr>
          <td><b>{{ k }}</b></td>
          <td>{{ v.status }}</td>
          <td>{{ v.device_id or 'غير مرتبط' }}</td>
          <td>{{ v.expires_at }}</td>
          <td>{{ v.activations }}</td>
          <td>{{ v.last_used or '-' }}</td>
          <td>
            <button onclick="actKey('ban', '{{ k }}')">حظر</button>
            <button class="blue" onclick="actKey('activate', '{{ k }}')">تفعيل</button>
            <button class="blue" onclick="actKey('reset_device', '{{ k }}')">فك الجهاز</button>
            <button onclick="actKey('delete', '{{ k }}')">حذف</button>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

  <script>
    function headers() {
      return {
        "Content-Type": "application/json",
        "X-Admin-Token": document.getElementById("adm_token").value
      };
    }
    async function saveCfg() {
      const r = await fetch("/api/admin/config", {
        method: "POST",
        headers: headers(),
        body: JSON.stringify({
          archive_url: document.getElementById("archive_url").value,
          target_dir: document.getElementById("target_dir").value,
          notice: document.getElementById("notice").value,
          maintenance: document.getElementById("maintenance").value === "true"
        })
      });
      const j = await r.json();
      alert(j.message || j.error);
      location.reload();
    }
    async function genKey() {
      const r = await fetch("/api/admin/keys", {
        method: "POST",
        headers: headers(),
        body: JSON.stringify({
          action: "generate",
          prefix: document.getElementById("prefix").value,
          days: parseInt(document.getElementById("days").value || "30", 10),
          lock_device: document.getElementById("lock_dev").checked
        })
      });
      const j = await r.json();
      alert(j.message || j.error);
      location.reload();
    }
    async function addCustomKey() {
      const r = await fetch("/api/admin/keys", {
        method: "POST",
        headers: headers(),
        body: JSON.stringify({
          action: "create",
          key: document.getElementById("custom_key").value,
          days: parseInt(document.getElementById("days").value || "30", 10),
          lock_device: document.getElementById("lock_dev").checked
        })
      });
      const j = await r.json();
      alert(j.message || j.error);
      location.reload();
    }
    async function actKey(action, key) {
      const r = await fetch("/api/admin/keys", {
        method: "POST",
        headers: headers(),
        body: JSON.stringify({ action, key })
      });
      const j = await r.json();
      alert(j.message || j.error);
      location.reload();
    }
  </script>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def home():
    keys = STATE["keys"]
    active_c = sum(1 for v in keys.values() if v.get("status") == "active")
    banned_c = sum(1 for v in keys.values() if v.get("status") == "banned")
    total_a = sum(int(v.get("activations") or 0) for v in keys.values())
    return render_template_string(
        DASHBOARD_TEMPLATE,
        cfg=STATE["config"],
        keys=keys,
        active_count=active_c,
        banned_count=banned_c,
        total_acts=total_a,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
