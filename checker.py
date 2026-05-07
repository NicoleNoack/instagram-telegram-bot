import instaloader
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout


def _fetch_account(username: str, since: datetime) -> dict:
    L = instaloader.Instaloader(
        quiet=True,
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        save_metadata=False,
        request_timeout=15,
    )
    posts = []
    profile = instaloader.Profile.from_username(L.context, username)
    for post in profile.get_posts():
        if post.date_utc < since:
            break
        posts.append({
            "type": "Video" if post.is_video else "Bild/Foto",
            "date": post.date_local,
            "url": f"https://www.instagram.com/p/{post.shortcode}/",
            "caption": (post.caption or "").strip()[:120],
            "likes": post.likes,
        })
    return posts


def check_new_posts(accounts: list[str]) -> dict:
    since = datetime.now(timezone.utc) - timedelta(hours=25)
    results = {}

    for username in accounts:
        results[username] = {"posts": [], "error": None}
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_fetch_account, username, since)
                results[username]["posts"] = future.result(timeout=45)
        except FuturesTimeout:
            results[username]["error"] = "Timeout — Instagram antwortet nicht (möglicherweise blockiert)"
        except Exception as e:
            results[username]["error"] = str(e)

    return results
