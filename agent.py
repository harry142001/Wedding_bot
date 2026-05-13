"""
Wedding Vendor AI Agent — SerpAPI Edition
==========================================
Uses SerpAPI free tier (100 searches/month = plenty for weekly runs).
Searches Google Maps for Montreal wedding vendors.
Saves top-rated results into vendors.json automatically.

Run once:    python agent.py
Run weekly:  python agent.py --schedule
"""

import json, os, time, random, argparse, logging, schedule, requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(format="%(asctime)s - AGENT - %(levelname)s - %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
CITY        = "Montreal"
DB_PATH     = os.path.join(os.path.dirname(__file__), "data", "vendors.json")

SEARCHES = [
    ("Photography",   "wedding photographer Montreal"),
    ("Venue",         "wedding venue Montreal"),
    ("Florist",       "wedding florist Montreal"),
    ("DJ & Music",    "wedding DJ Montreal"),
    ("Wedding Cake",  "wedding cake Montreal"),
    ("Catering",      "wedding catering Montreal"),
    ("Hair & Makeup", "wedding hair makeup Montreal"),
    ("Videography",   "wedding videographer Montreal"),
]

COMMISSION = {"Photography":10,"Venue":8,"Florist":12,"DJ & Music":10,"Wedding Cake":12,"Catering":8,"Hair & Makeup":12,"Videography":10}
PRICE_FROM = {"Photography":2500,"Venue":8000,"Florist":1200,"DJ & Music":1800,"Wedding Cake":700,"Catering":4000,"Hair & Makeup":800,"Videography":2000}

def search_vendors(query, category):
    """Call SerpAPI Google Maps search and return vendor list."""
    log.info(f"Searching: {query}")
    params = {
        "engine":   "google_maps",
        "q":        query,
        "type":     "search",
        "api_key":  SERPAPI_KEY,
        "hl":       "en",
        "gl":       "ca",
    }
    try:
        resp = requests.get("https://serpapi.com/search", params=params, timeout=15)
        data = resp.json()
    except Exception as e:
        log.error(f"Request failed: {e}")
        return []

    if "error" in data:
        log.error(f"SerpAPI error: {data['error']}")
        return []

    results = data.get("local_results", [])
    log.info(f"  Found {len(results)} results")

    vendors = []
    for place in results:
        rating  = place.get("rating", 0)
        reviews = place.get("reviews", 0)
        if rating < 3.5 or reviews < 3:
            continue

        name      = place.get("title", "")
        place_id  = place.get("place_id", "")
        address   = place.get("address", "")
        phone     = place.get("phone", "")
        website   = place.get("website", "")
        thumbnail = place.get("thumbnail", "")

        vendor_id = f"sp_{place_id[:12]}" if place_id else f"sp_{abs(hash(name)) % 100000}"

        vendors.append({
            "id":             vendor_id,
            "name":           name,
            "category":       category,
            "city":           CITY,
            "description":    f"{category} service in {CITY}. Rated {rating}/5 from {reviews} Google reviews.",
            "price_from":     PRICE_FROM.get(category, 1000),
            "price_currency": "CAD",
            "languages":      ["English", "French"],
            "instagram":      "",
            "contact_email":  "",
            "contact_phone":  phone,
            "website":        website,
            "google_rating":  rating,
            "google_reviews": reviews,
            "google_address": address,
            "thumbnail":      thumbnail,
            "active":         True,
            "featured":       rating >= 4.5 and reviews >= 20,
            "commission_pct": COMMISSION.get(category, 10),
            "source":         "serpapi",
            "scraped_at":     datetime.utcnow().isoformat(),
        })

    vendors.sort(key=lambda v: (v["google_rating"], v["google_reviews"]), reverse=True)
    top = vendors[:10]
    log.info(f"  Kept top {len(top)} for {category}")
    return top

def load_db():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def run_agent():
    log.info("=" * 50)
    log.info(f"Agent starting — {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    if not SERPAPI_KEY:
        log.error("No SERPAPI_KEY found in .env file!")
        return

    all_vendors = []
    for category, query in SEARCHES:
        vendors = search_vendors(query, category)
        all_vendors.extend(vendors)
        time.sleep(random.uniform(2, 4))  # be polite to the API

    if not all_vendors:
        log.warning("No vendors found. Check your SERPAPI_KEY in .env")
        return

    # Merge: keep manual vendors, replace auto ones with fresh data
    data   = load_db()
    manual = [v for v in data["vendors"] if v.get("source") not in ("serpapi", "google_places", "auto_scraped")]
    merged = manual + all_vendors
    data["vendors"] = merged
    save_db(data)

    log.info(f"Done! {len(all_vendors)} vendors saved. Total in bot: {len(merged)}")
    for category, _ in SEARCHES:
        cat_vendors = [v for v in all_vendors if v["category"] == category]
        if cat_vendors:
            top = cat_vendors[0]
            log.info(f"  {category}: {len(cat_vendors)} vendors — top: {top['name']} ({top['google_rating']}★)")
    log.info("=" * 50)

def run_scheduled():
    log.info("Scheduler on. Runs every Monday at 8:00 AM.")
    run_agent()
    schedule.every().monday.at("08:00").do(run_agent)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", action="store_true", help="Run weekly automatically")
    args = parser.parse_args()
    run_scheduled() if args.schedule else run_agent()
