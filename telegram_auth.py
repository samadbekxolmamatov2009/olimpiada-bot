import hashlib
import hmac
import json
import time
import urllib.parse
from typing import Optional

from config import BOT_TOKEN

INIT_DATA_MAX_AGE = 24 * 60 * 60  # 24 soat


def validate_init_data(init_data: str) -> Optional[dict]:
    """Telegram Mini App initData imzosini tekshiradi va foydalanuvchi obyektini qaytaradi.

    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    if not init_data:
        return None

    try:
        parsed = dict(urllib.parse.parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        return None

    received_hash = parsed.pop("hash", None)
    if not received_hash:
        return None

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_hash, received_hash):
        return None

    auth_date = parsed.get("auth_date")
    if auth_date and time.time() - int(auth_date) > INIT_DATA_MAX_AGE:
        return None

    user_raw = parsed.get("user")
    if not user_raw:
        return None

    try:
        return json.loads(user_raw)
    except ValueError:
        return None
