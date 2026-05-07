import os
import time
import requests
from datetime import datetime, timedelta, timezone

APIFY_TOKEN = os.environ["APIFY_TOKEN"]
ACTOR_ID = "apify~instagram-scraper"
BASE_URL = "https://api.apify.com/v2"


def check_new_posts(accounts: list[str]) -> dict:
    since = datetime.now(timezone.utc) - timedelta(hours=25)
    results = {u: {"posts": [], "error": None} for u in accounts}

    run_input = {
        "directUrls": [f"https://www.instagram.com/{u}/" for u in accounts],
        "resultsType": "posts",
        "resultsLimit": 5,
    }

    try:
        r = requests.post(
            f"{BASE_URL}/acts/{ACTOR_ID}/runs",
            params={"token": APIFY_TOKEN},
            json=run_input,
            timeout=30,
        )
        r.raise_for_status()
        run = r.json()["data"]
        run_id = run["id"]
        dataset_id = run["defaultDatasetId"]

        for _ in range(30):
            time.sleep(10)
            status_r = requests.get(
                f"{BASE_URL}/actor-runs/{run_id}",
                params={"token": APIFY_TOKEN},
                timeout=15,
            )
            status = status_r.json()["data"]["status"]
            if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
                break

        items_r = requests.get(
            f"{BASE_URL}/datasets/{dataset_id}/items",
            params={"token": APIFY_TOKEN},
            timeout=30,
        )
        items_r.raise_for_status()

        for item in items_r.json():
            username = item.get("ownerUsername", "")
            if username not in results:
                continue
            timestamp = item.get("timestamp")
            if not timestamp:
                continue
            post_date = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if post_date < since:
                continue
            results[username]["posts"].append({
                "type": "Video" if item.get("type") == "Video" else "Bild/Foto",
                "date": post_date.astimezone().replace(tzinfo=None),
                "url": item.get("url", ""),
                "caption": (item.get("caption") or "").strip()[:120],
                "likes": item.get("likesCount", 0),
            })

    except Exception as e:
        for u in accounts:
            results[u]["error"] = str(e)

    return results
