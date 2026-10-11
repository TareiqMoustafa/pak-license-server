from datetime import datetime, timedelta
from flask import Flask, jsonify, request

app = Flask(__name__)

# قاعدة بيانات مؤقتة متوافقة مع الاستضافات السحابية (Serverless)
MEMORY_DB = {
    "VIP-TARIQ-75": {
        "expiry": (datetime.now() + timedelta(days=75)).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "status": "active",
        "type": "2.5months",
    }
}


@app.route("/api/verify", methods=["GET"])
def verify_license():
  key = request.args.get("key")
  if not key or key not in MEMORY_DB:
    return (
        jsonify({"status": "invalid", "message": "Key not found or incorrect."}),
        404,
    )

  lic = MEMORY_DB[key]
  if lic["status"] == "blocked":
    return jsonify({
        "status": "blocked",
        "message": "Access denied. Key has been blocked by admin.",
    })

  try:
    expiry_time = datetime.strptime(lic["expiry"], "%Y-%m-%d %H:%M:%S")
  except ValueError:
    expiry_time = datetime.now()

  now = datetime.now()

  if now > expiry_time:
    lic["status"] = "expired"
    return jsonify({
        "status": "expired",
        "message": "Subscription expired. Please renew.",
    })

  remaining = expiry_time - now
  days = remaining.days
  hours = remaining.seconds // 3600

  return jsonify({
      "status": "active",
      "type": lic["type"],
      "remaining_days": days,
      "remaining_hours": hours,
      "message": f"Active! Remaining: {days} days and {hours} hours.",
  })


@app.route("/api/admin/add", methods=["POST"])
def add_license():
  data = request.json or {}
  key = data.get("key")
  duration_type = data.get("type")  # week, month, 2.5months

  if not key or not duration_type:
    return jsonify({"success": False, "message": "Missing key or type."}), 400

  if duration_type == "week":
    days = 7
  elif duration_type == "month":
    days = 30
  elif duration_type == "2.5months":
    days = 75
  else:
    days = 7

  expiry_date = (datetime.now() + timedelta(days=days)).strftime(
      "%Y-%m-%d %H:%M:%S"
  )

  MEMORY_DB[key] = {
      "expiry": expiry_date,
      "status": "active",
      "type": duration_type,
  }
  return jsonify({
      "success": True,
      "message": f"Key {key} added for {days} days successfully.",
  })


@app.route("/api/admin/control", methods=["POST"])
def admin_control():
  data = request.json or {}
  key = data.get("key")
  action = data.get("action")  # block or unblock

  if not key or not action:
    return jsonify({"success": False, "message": "Missing key or action."}), 400

  if key in MEMORY_DB:
    MEMORY_DB[key]["status"] = "blocked" if action == "block" else "active"
    return jsonify(
        {"success": True, "message": f"Key {key} status changed to {action}."}
    )

  return jsonify({"success": False, "message": "Key not found."}), 404


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
