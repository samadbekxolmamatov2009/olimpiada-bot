from datetime import datetime

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import ADMIN_IDS, ALLOWED_GRADES, REGISTRATION_DEADLINE
from db import add_registration, is_registered
from keyboards import cancel_kb
from states import Registration

router = Router()

ALREADY_REGISTERED_TEXT = (
    "✅ Siz allaqachon ro'yxatdan o'tgansiz.\n"
    "Navoiy–Qorako'l olimpiadasi bo'yicha ma'lumotlaringiz qabul qilingan."
)
CLOSED_TEXT = "⛔️ Ro'yxatdan o'tish muddati tugagan (20-noyabr, 2026-yil)."
WELCOME_TEXT = (
    "🏆 <b>Navoiy–Qorako'l olimpiadasi</b>\n"
    "Faqat 3- va 4-sinf o'quvchilari uchun ro'yxatdan o'tish.\n\n"
    "1️⃣ Ism va familyangizni yuboring:"
)
WRONG_GRADE_TEXT = (
    "⛔️ Afsuski, bu olimpiada faqat 3- va 4-sinf o'quvchilari uchun.\n"
    "Siz ro'yxatdan o'ta olmaysiz."
)


@router.message(CommandStart(), ~F.from_user.id.in_(ADMIN_IDS))
async def cmd_start(message: Message, state: FSMContext) -> None:
    if await is_registered(message.from_user.id):
        await message.answer(ALREADY_REGISTERED_TEXT)
        return
    if datetime.now() > REGISTRATION_DEADLINE:
        await message.answer(CLOSED_TEXT)
        return
    await state.set_state(Registration.full_name)
    await message.answer(WELCOME_TEXT, reply_markup=cancel_kb())


@router.callback_query(F.data == "cancel", ~F.from_user.id.in_(ADMIN_IDS))
async def cancel_registration(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer("Ro'yxatdan o'tish bekor qilindi. Qayta boshlash uchun /start bosing.")
    await callback.answer()


@router.message(Registration.full_name)
async def reg_full_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < 3:
        await message.answer("Iltimos, ism va familyangizni to'liq kiriting:")
        return
    await state.update_data(full_name=name)
    await state.set_state(Registration.district)
    await message.answer("2️⃣ Tumaningizni kiriting:")


@router.message(Registration.district)
async def reg_district(message: Message, state: FSMContext) -> None:
    district = (message.text or "").strip()
    if not district:
        await message.answer("Iltimos, tumaningizni kiriting:")
        return
    await state.update_data(district=district)
    await state.set_state(Registration.school)
    await message.answer("3️⃣ O'qiyotgan maktabingizni kiriting:")


@router.message(Registration.school)
async def reg_school(message: Message, state: FSMContext) -> None:
    school = (message.text or "").strip()
    if not school:
        await message.answer("Iltimos, maktabingizni kiriting:")
        return
    await state.update_data(school=school)
    await state.set_state(Registration.grade)
    await message.answer("4️⃣ Sinfingizni kiriting (faqat 3 yoki 4):")


@router.message(Registration.grade)
async def reg_grade(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    digits = "".join(ch for ch in raw if ch.isdigit())
    if digits not in ALLOWED_GRADES:
        await message.answer(WRONG_GRADE_TEXT)
        await state.clear()
        return
    await state.update_data(grade=int(digits))
    await state.set_state(Registration.parent_phone)
    await message.answer("5️⃣ Ota-onangizning telefon raqamini kiriting (masalan: +998901234567):")


@router.message(Registration.parent_phone)
async def reg_parent_phone(message: Message, state: FSMContext) -> None:
    phone = (message.text or "").strip()
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) < 9:
        await message.answer("Iltimos, telefon raqamini to'g'ri kiriting (masalan: +998901234567):")
        return

    if await is_registered(message.from_user.id):
        await state.clear()
        await message.answer(ALREADY_REGISTERED_TEXT)
        return

    data = await state.get_data()
    await add_registration(
        telegram_id=message.from_user.id,
        full_name=data["full_name"],
        district=data["district"],
        school=data["school"],
        grade=data["grade"],
        parent_phone=phone,
    )
    await state.clear()
    await message.answer(
        "✅ Siz muvaffaqiyatli ro'yxatdan o'tdingiz!\n"
        "Navoiy–Qorako'l olimpiadasi bo'yicha ma'lumotlaringiz qabul qilindi."
    )


@router.message(~F.from_user.id.in_(ADMIN_IDS))
async def catch_all(message: Message, state: FSMContext) -> None:
    if await is_registered(message.from_user.id):
        await message.answer(ALREADY_REGISTERED_TEXT)
        return
    if await state.get_state() is None:
        await message.answer("Ro'yxatdan o'tish uchun /start buyrug'ini yuboring.")
