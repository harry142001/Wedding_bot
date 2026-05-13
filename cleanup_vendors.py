"""
One-time cleanup script for vendors.json
Run once: python cleanup_vendors.py
"""

import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "vendors.json")

# Fake vendors to remove
FAKE_IDS = {"v001", "v002", "v003", "v004", "v005"}

# Name fixes — too long for bot buttons
NAME_FIXES = {
    "Rob Malo Films | Montreal Wedding Videographer | Vidéaste Mariage Montréal": "Rob Malo Films",
    "Back to Basics Entertainment - DJ MAJD Montreal": "DJ MAJD - Back to Basics",
    "Uptown Xpress - Montreal Wedding MC and DJ Specialist": "Uptown Xpress DJ & MC",
    "Eventure Group | Event Planner | Catering Services in Montreal": "Eventure Group Catering",
    "West Island & Montreal catering by Gini": "Catering by Gini",
    "LiMon Pâtisserie Powered by Katy's Cake Montreal": "LiMon Pâtisserie",
    "Nicolas Abou Photographer / Videographer | Montreal | Commercial and Events": "Nicolas Abou Photo & Video",
    "Hossi Beauty Montreal Makeup Artist & Hairstylist": "Hossi Beauty",
    "Lisa Sim Makeup Artist / SIM Minerals": "Lisa Sim Makeup Artist",
    "Pâtisserie Gourmets-Crafts ( Pre-order only)": "Pâtisserie Gourmets-Crafts",
    "Makeup Artist | Andrea Blancas": "Andrea Blancas Makeup",
    "Suvana's Sweets(Homebase Business)": "Suvana's Sweets",
}

# Category fixes
CATEGORY_FIXES = {
    "sp_ChIJn0dH-pUR": "Videography",  # Rob Malo Films — was in Photography
}

def cleanup():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    vendors = data["vendors"]
    before = len(vendors)

    cleaned = []
    removed = []
    renamed = []
    recategorized = []

    for v in vendors:
        # Remove fake vendors
        if v["id"] in FAKE_IDS:
            removed.append(v["name"])
            continue

        # Fix long names
        if v["name"] in NAME_FIXES:
            renamed.append(f"{v['name'][:40]}... → {NAME_FIXES[v['name']]}")
            v["name"] = NAME_FIXES[v["name"]]

        # Fix wrong categories
        if v["id"] in CATEGORY_FIXES:
            old_cat = v["category"]
            v["category"] = CATEGORY_FIXES[v["id"]]
            recategorized.append(f"{v['name']}: {old_cat} → {v['category']}")

        cleaned.append(v)

    data["vendors"] = cleaned

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Report
    print("=" * 50)
    print("CLEANUP COMPLETE")
    print("=" * 50)
    print(f"\nVendors before: {before}")
    print(f"Vendors after:  {len(cleaned)}")

    print(f"\n✅ Removed {len(removed)} fake vendors:")
    for n in removed:
        print(f"   - {n}")

    print(f"\n✅ Shortened {len(renamed)} long names:")
    for n in renamed:
        print(f"   - {n}")

    print(f"\n✅ Fixed {len(recategorized)} wrong categories:")
    for n in recategorized:
        print(f"   - {n}")

    print(f"\n{'='*50}")
    print("Your vendors.json is clean and ready!")
    print("Restart your bot: python bot.py")

if __name__ == "__main__":
    cleanup()
