from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import ADMIN_IDS
from keyboards import registration_kb

router = Router()

WELCOME_TEXT = (
    "🏆 <b>Navoiy–Qorako'l olimpiadasi</b>\n"
    "3- va 4-sinf o'quvchilari uchun ro'yxatdan o'tish.\n\n"
    "Ro'yxatdan o'tish uchun pastdagi tugmani bosing 👇"
)
NUDGE_TEXT = "Ro'yxatdan o'tish uchun /start buyrug'ini yuboring."


@router.message(CommandStart(), ~F.from_user.id.in_(ADMIN_IDS))
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME_TEXT, reply_markup=registration_kb())


@router.message(~F.from_user.id.in_(ADMIN_IDS))
async def fallback(message: Message) -> None:
    await message.answer(NUDGE_TEXT, reply_markup=registration_kb())
