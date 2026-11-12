import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from config import ADMIN_IDS, CHANNEL_ID
from keyboards import registration_kb, subscribe_kb

router = Router()
logger = logging.getLogger(__name__)

WELCOME_TEXT = (
    "🏆 <b>Navoiy–Qorako'l olimpiadasi</b>\n"
    "3- va 4-sinf o'quvchilari uchun ro'yxatdan o'tish.\n\n"
    "Ro'yxatdan o'tish uchun pastdagi tugmani bosing 👇"
)
NUDGE_TEXT = "Ro'yxatdan o'tish uchun /start buyrug'ini yuboring."
SUBSCRIBE_TEXT = (
    "📢 Ro'yxatdan o'tishdan oldin kanalimizga obuna bo'ling.\n\n"
    "Obuna bo'lgach, \"✅ Men obuna bo'ldim\" tugmasini bosing."
)
NOT_SUBSCRIBED_ALERT = "Siz hali kanalga obuna bo'lmagansiz."

_NOT_MEMBER_STATUSES = {"left", "kicked"}


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    if not CHANNEL_ID:
        return True
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
    except TelegramBadRequest as e:
        logger.warning("Kanal obunasini tekshirib bo'lmadi: %s", e)
        return False
    return member.status not in _NOT_MEMBER_STATUSES


@router.message(CommandStart(), ~F.from_user.id.in_(ADMIN_IDS))
async def cmd_start(message: Message, bot: Bot) -> None:
    if not await is_subscribed(bot, message.from_user.id):
        await message.answer(SUBSCRIBE_TEXT, reply_markup=subscribe_kb())
        return
    await message.answer(WELCOME_TEXT, reply_markup=registration_kb())


@router.callback_query(F.data == "check_sub", ~F.from_user.id.in_(ADMIN_IDS))
async def check_subscription(callback: CallbackQuery, bot: Bot) -> None:
    if await is_subscribed(bot, callback.from_user.id):
        await callback.message.edit_text(WELCOME_TEXT, reply_markup=registration_kb())
        await callback.answer()
    else:
        await callback.answer(NOT_SUBSCRIBED_ALERT, show_alert=True)


@router.message(~F.from_user.id.in_(ADMIN_IDS))
async def fallback(message: Message, bot: Bot) -> None:
    if not await is_subscribed(bot, message.from_user.id):
        await message.answer(SUBSCRIBE_TEXT, reply_markup=subscribe_kb())
        return
    await message.answer(NUDGE_TEXT, reply_markup=registration_kb())
