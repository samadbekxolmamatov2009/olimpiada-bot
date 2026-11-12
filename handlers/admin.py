import io
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from config import ADMIN_IDS
from db import count_registrations, get_all_registrations
from keyboards import admin_menu_kb

router = Router()

ADMIN_WELCOME = "👋 Admin panel.\nNavoiy–Qorako'l olimpiadasi ro'yxatini boshqarish."


@router.message(CommandStart(), F.from_user.id.in_(ADMIN_IDS))
async def admin_start(message: Message) -> None:
    await message.answer(ADMIN_WELCOME, reply_markup=admin_menu_kb())


@router.message(Command("admin"), F.from_user.id.in_(ADMIN_IDS))
async def admin_panel(message: Message) -> None:
    await message.answer(ADMIN_WELCOME, reply_markup=admin_menu_kb())


@router.callback_query(F.data == "admin_export", F.from_user.id.in_(ADMIN_IDS))
async def admin_export(callback: CallbackQuery) -> None:
    rows = await get_all_registrations()
    if not rows:
        await callback.message.answer("Hali hech kim ro'yxatdan o'tmagan.")
        await callback.answer()
        return

    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Ro'yxat"
    ws.append(
        ["№", "Ism Familya", "Tumani", "Maktabi", "Sinfi", "Ota-ona tel raqami", "Admin kiritgan", "Sana"]
    )
    for idx, (full_name, district, school, grade, parent_phone, by_admin, created_at) in enumerate(
        rows, start=1
    ):
        ws.append(
            [idx, full_name, district, school, grade, parent_phone, "Ha" if by_admin else "Yo'q", created_at]
        )

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    filename = f"navoiy_qorakul_olimpiada_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    await callback.message.answer_document(
        BufferedInputFile(buf.read(), filename=filename),
        caption=f"Jami: {await count_registrations()} ta ro'yxatdan o'tgan.",
    )
    await callback.answer()
