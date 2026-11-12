from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📥 Ro'yxatni yuklab olish", callback_data="admin_export")],
            [
                InlineKeyboardButton(
                    text="✍️ Ota-ona o'rniga ro'yxatdan o'tkazish",
                    callback_data="admin_register_for_parent",
                )
            ],
        ]
    )


def cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]]
    )
