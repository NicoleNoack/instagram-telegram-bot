import asyncio
import logging
from datetime import datetime

from telegram import Bot
from telegram.error import TelegramError

from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, INSTAGRAM_ACCOUNTS
from checker import check_new_posts

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def build_message(results: dict) -> str:
    today = datetime.now().strftime("%d.%m.%Y")
    lines = [f"📱 *Instagram Check — {today}*\n"]
    any_new = False

    for username, data in results.items():
        if data["error"]:
            lines.append(f"❌ @{username}: Fehler — `{data['error']}`\n")
            continue

        posts = data["posts"]
        if not posts:
            lines.append(f"😴 *@{username}* — kein neuer Beitrag in den letzten 24h\n")
            continue

        any_new = True
        lines.append(f"🔔 *@{username}* — {len(posts)} neuer Beitrag{'e' if len(posts) > 1 else ''}:")
        for p in posts:
            emoji = "🎥" if p["type"] == "Video" else "🖼"
            date_str = p["date"].strftime("%d.%m. um %H:%M Uhr")
            lines.append(f"  {emoji} {p['type']} · {date_str}")
            lines.append(f"  🔗 {p['url']}")
            if p["caption"]:
                short = p["caption"][:80] + ("…" if len(p["caption"]) > 80 else "")
                lines.append(f"  _{short}_")
            lines.append("")

    if not any_new and not any(d["error"] for d in results.values()):
        lines = [f"✅ *Instagram Check — {today}*\n\nKeine neuen Beiträge in den letzten 24h."]

    return "\n".join(lines)


async def main():
    logger.info("Starte Instagram-Prüfung...")
    results = check_new_posts(INSTAGRAM_ACCOUNTS)
    message = build_message(results)

    bot = Bot(token=TELEGRAM_TOKEN)
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
        logger.info("Nachricht gesendet!")
    except TelegramError as e:
        logger.error(f"Telegram-Fehler: {e}")


if __name__ == "__main__":
    asyncio.run(main())
