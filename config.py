import os
import secrets
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()}

TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL", "")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")

# Render web-service uchun bu avtomatik to'ldiriladi; boshqa hostlarda
# PUBLIC_URL orqali o'zingiz ko'rsatishingiz mumkin.
PUBLIC_URL = (os.getenv("PUBLIC_URL") or os.getenv("RENDER_EXTERNAL_URL", "")).rstrip("/")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET") or secrets.token_urlsafe(24)
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"
WEBAPP_URL = f"{PUBLIC_URL}/webapp/"

REGISTRATION_DEADLINE = datetime(2026, 11, 20, 23, 59, 59)
ALLOWED_GRADES = ("3", "4")
