from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from config import WEBAPP_URL


def registration_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Ro'yxatdan o'tish", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
    )


def admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📥 Ro'yxatni yuklab olish", callback_data="admin_export")],
            [
                InlineKeyboardButton(
                    text="✍️ Ota-ona o'rniga ro'yxatdan o'tkazish",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                )
            ],
        ]
    )
