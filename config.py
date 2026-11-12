import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()}

REGISTRATION_DEADLINE = datetime(2026, 11, 20, 23, 59, 59)
ALLOWED_GRADES = ("3", "4")
