import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

INSTAGRAM_ACCOUNTS = [
    "sarah.heck.vibes",
    "netcoo",
    "pm_powermutti",
]

CHECK_HOUR = 9
CHECK_MINUTE = 0
TIMEZONE = "Europe/Berlin"
