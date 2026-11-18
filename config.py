import os
import secrets
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()}

TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL", "")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")

# Majburiy obuna kanali. "-100..." raqamli ID yoki "@kanal_username" bo'lishi mumkin.
_channel_id_raw = os.getenv("CHANNEL_ID", "").strip()
try:
    CHANNEL_ID: object = int(_channel_id_raw)
except ValueError:
    CHANNEL_ID = _channel_id_raw or None

# Obuna bo'lish tugmasi uchun havola. "@username" yoki oddiy "username" tarzida
# yozilgan bo'lsa ham, to'g'ri https://t.me/... havolasiga avtomatik aylantiriladi.
# Berilmagan bo'lsa, CHANNEL_ID "@username" bo'lsa shundan hosil qilinadi.
CHANNEL_URL = os.getenv("CHANNEL_URL", "").strip()
if CHANNEL_URL and not CHANNEL_URL.startswith("http"):
    CHANNEL_URL = f"https://t.me/{CHANNEL_URL.lstrip('@')}"
if not CHANNEL_URL and isinstance(CHANNEL_ID, str) and CHANNEL_ID.startswith("@"):
    CHANNEL_URL = f"https://t.me/{CHANNEL_ID[1:]}"

# Render web-service uchun bu avtomatik to'ldiriladi; boshqa hostlarda
# PUBLIC_URL orqali o'zingiz ko'rsatishingiz mumkin.
PUBLIC_URL = (os.getenv("PUBLIC_URL") or os.getenv("RENDER_EXTERNAL_URL", "")).rstrip("/")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET") or secrets.token_urlsafe(24)
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"
WEBAPP_URL = f"{PUBLIC_URL}/webapp/"

REGISTRATION_DEADLINE = datetime(2026, 11, 26, 23, 59, 59)
ALLOWED_GRADES = ("3", "4")
