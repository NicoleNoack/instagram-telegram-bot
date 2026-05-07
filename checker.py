import os
from datetime import datetime, timedelta, timezone
from apify_client import ApifyClient


def check_new_posts(accounts: list[str]) -> dict:
    client = ApifyClient(os.environ["APIFY_TOKEN"])
    since = datetime.now(timezone.utc) - timedelta(hours=25)
    results = {u: {"posts": [], "error": None} for u in accounts}

    run_input = {
        "directUrls": [f"https://www.instagram.com/{u}/" for u in accounts],
        "resultsType": "posts",
        "resultsLimit": 5,
    }

    try:
        run = client.actor("apify/instagram-scraper").call(run_input=run_input)
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
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
