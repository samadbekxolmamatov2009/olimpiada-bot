import io
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from config import ADMIN_IDS, ALLOWED_GRADES
from db import add_registration, count_registrations, get_all_registrations
from keyboards import admin_menu_kb, cancel_kb
from states import AdminRegistration

router = Router()

ADMIN_WELCOME = "👋 Admin panel.\nNavoiy–Qorako'l olimpiadasi ro'yxatini boshqarish."
WRONG_GRADE_TEXT = "⛔️ Bu olimpiada faqat 3- va 4-sinf o'quvchilari uchun. Ro'yxatga kiritilmadi."


@router.message(CommandStart(), F.from_user.id.in_(ADMIN_IDS))
async def admin_start(message: Message) -> None:
    await message.answer(ADMIN_WELCOME, reply_markup=admin_menu_kb())


@router.message(Command("admin"), F.from_user.id.in_(ADMIN_IDS))
async def admin_panel(message: Message) -> None:
    await message.answer(ADMIN_WELCOME, reply_markup=admin_menu_kb())


@router.callback_query(F.data == "admin_export", F.from_user.id.in_(ADMIN_IDS))
async def admin_export(callback: CallbackQuery) -> None:
    rows = get_all_registrations()
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
        caption=f"Jami: {count_registrations()} ta ro'yxatdan o'tgan.",
    )
    await callback.answer()


@router.callback_query(F.data == "admin_register_for_parent", F.from_user.id.in_(ADMIN_IDS))
async def admin_register_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminRegistration.full_name)
    await callback.message.answer(
        "✍️ Ota-ona o'rniga ro'yxatdan o'tkazish.\n\n1️⃣ O'quvchining ism va familyasini kiriting:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "cancel", F.from_user.id.in_(ADMIN_IDS))
async def admin_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer("Bekor qilindi.", reply_markup=admin_menu_kb())
    await callback.answer()


@router.message(AdminRegistration.full_name, F.from_user.id.in_(ADMIN_IDS))
async def areg_full_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < 3:
        await message.answer("Iltimos, ism va familyani to'liq kiriting:")
        return
    await state.update_data(full_name=name)
    await state.set_state(AdminRegistration.district)
    await message.answer("2️⃣ Tumanini kiriting:")


@router.message(AdminRegistration.district, F.from_user.id.in_(ADMIN_IDS))
async def areg_district(message: Message, state: FSMContext) -> None:
    district = (message.text or "").strip()
    if not district:
        await message.answer("Iltimos, tumanini kiriting:")
        return
    await state.update_data(district=district)
    await state.set_state(AdminRegistration.school)
    await message.answer("3️⃣ Maktabini kiriting:")


@router.message(AdminRegistration.school, F.from_user.id.in_(ADMIN_IDS))
async def areg_school(message: Message, state: FSMContext) -> None:
    school = (message.text or "").strip()
    if not school:
        await message.answer("Iltimos, maktabini kiriting:")
        return
    await state.update_data(school=school)
    await state.set_state(AdminRegistration.grade)
    await message.answer("4️⃣ Sinfini kiriting (faqat 3 yoki 4):")


@router.message(AdminRegistration.grade, F.from_user.id.in_(ADMIN_IDS))
async def areg_grade(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    digits = "".join(ch for ch in raw if ch.isdigit())
    if digits not in ALLOWED_GRADES:
        await message.answer(WRONG_GRADE_TEXT, reply_markup=admin_menu_kb())
        await state.clear()
        return
    await state.update_data(grade=int(digits))
    await state.set_state(AdminRegistration.parent_phone)
    await message.answer("5️⃣ Ota-onasining telefon raqamini kiriting:")


@router.message(AdminRegistration.parent_phone, F.from_user.id.in_(ADMIN_IDS))
async def areg_parent_phone(message: Message, state: FSMContext) -> None:
    phone = (message.text or "").strip()
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) < 9:
        await message.answer("Iltimos, telefon raqamini to'g'ri kiriting:")
        return

    data = await state.get_data()
    add_registration(
        telegram_id=None,
        full_name=data["full_name"],
        district=data["district"],
        school=data["school"],
        grade=data["grade"],
        parent_phone=phone,
        registered_by_admin=True,
        admin_id=message.from_user.id,
    )
    await state.clear()
    await message.answer("✅ Ro'yxatga muvaffaqiyatli kiritildi.", reply_markup=admin_menu_kb())
