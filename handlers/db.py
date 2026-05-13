"""
Simple file-based database using JSON.
When you're ready to scale, swap this for Supabase or SQLite.
"""

import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "vendors.json")

def _load():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(data):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ── Vendor queries ──────────────────────────────────────────────

def get_all_vendors(active_only=True):
    data = _load()
    vendors = data["vendors"]
    if active_only:
        vendors = [v for v in vendors if v.get("active", True)]
    return vendors

def get_vendors_by_category(category):
    return [v for v in get_all_vendors() if v["category"] == category]

def get_vendor_by_id(vendor_id):
    for v in get_all_vendors(active_only=False):
        if v["id"] == vendor_id:
            return v
    return None

def get_categories():
    vendors = get_all_vendors()
    seen = set()
    categories = []
    for v in vendors:
        if v["category"] not in seen:
            seen.add(v["category"])
            categories.append(v["category"])
    return sorted(categories)

def add_vendor(vendor_dict):
    data = _load()
    # Auto-generate ID
    existing_ids = [v["id"] for v in data["vendors"]]
    n = len(existing_ids) + 1
    vendor_dict["id"] = f"v{n:03d}"
    vendor_dict["active"] = True
    data["vendors"].append(vendor_dict)
    _save(data)
    return vendor_dict["id"]

# ── Request (lead) tracking ─────────────────────────────────────

def save_request(couple_user_id, couple_username, couple_name, vendor_id, message=""):
    data = _load()
    vendor = get_vendor_by_id(vendor_id)
    request = {
        "id": f"req_{len(data['requests']) + 1:04d}",
        "timestamp": datetime.utcnow().isoformat(),
        "couple_user_id": couple_user_id,
        "couple_username": couple_username or "unknown",
        "couple_name": couple_name,
        "vendor_id": vendor_id,
        "vendor_name": vendor["name"] if vendor else "Unknown",
        "vendor_category": vendor["category"] if vendor else "Unknown",
        "vendor_price_from": vendor["price_from"] if vendor else 0,
        "commission_pct": vendor.get("commission_pct", 10) if vendor else 10,
        "status": "new",   # new → contacted → booked → paid
        "message": message,
        "commission_earned": 0.0
    }
    data["requests"].append(request)
    _save(data)
    return request

def get_all_requests():
    return _load()["requests"]

def update_request_status(request_id, status, commission_earned=None):
    data = _load()
    for r in data["requests"]:
        if r["id"] == request_id:
            r["status"] = status
            if commission_earned is not None:
                r["commission_earned"] = commission_earned
            break
    _save(data)

def get_stats():
    data = _load()
    requests = data["requests"]
    total = len(requests)
    booked = [r for r in requests if r["status"] == "booked"]
    paid = [r for r in requests if r["status"] == "paid"]
    earned = sum(r.get("commission_earned", 0) for r in paid)
    return {
        "total_requests": total,
        "total_booked": len(booked),
        "total_paid": len(paid),
        "total_earned": earned,
        "active_vendors": len([v for v in data["vendors"] if v.get("active")])
    }
