import instaloader
from datetime import datetime, timedelta, timezone


def check_new_posts(accounts: list[str]) -> dict:
    L = instaloader.Instaloader(
        quiet=True,
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        save_metadata=False,
    )
    since = datetime.now(timezone.utc) - timedelta(hours=25)
    results = {}

    for username in accounts:
        results[username] = {"posts": [], "error": None}
        try:
            profile = instaloader.Profile.from_username(L.context, username)
            for post in profile.get_posts():
                if post.date_utc < since:
                    break
                results[username]["posts"].append({
                    "type": "Video" if post.is_video else "Bild/Foto",
                    "date": post.date_local,
                    "url": f"https://www.instagram.com/p/{post.shortcode}/",
                    "caption": (post.caption or "").strip()[:120],
                    "likes": post.likes,
                })
        except Exception as e:
            results[username]["error"] = str(e)

    return results
