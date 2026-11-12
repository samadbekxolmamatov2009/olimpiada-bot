import logging
from contextlib import asynccontextmanager
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import ADMIN_IDS, ALLOWED_GRADES, BOT_TOKEN, PUBLIC_URL, REGISTRATION_DEADLINE, WEBHOOK_PATH
from db import add_registration, close_db, init_db, is_registered
from handlers import admin, registration
from telegram_auth import validate_init_data

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(admin.router)
dp.include_router(registration.router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    if PUBLIC_URL:
        await bot.set_webhook(PUBLIC_URL + WEBHOOK_PATH, drop_pending_updates=True)
    else:
        logging.warning("PUBLIC_URL berilmagan — Telegram webhook o'rnatilmadi.")
    yield
    await close_db()


app = FastAPI(lifespan=lifespan)
app.mount("/webapp", StaticFiles(directory="webapp", html=True), name="webapp")


@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return RedirectResponse(url="/webapp/")


class RegisterPayload(BaseModel):
    init_data: str
    full_name: str
    district: str
    school: str
    grade: int
    parent_phone: str


@app.get("/api/status")
async def api_status(init_data: str):
    user = validate_init_data(init_data)
    if user is None:
        return JSONResponse({"error": "invalid_init_data"}, status_code=403)

    telegram_id = user["id"]
    if telegram_id in ADMIN_IDS:
        return {"role": "admin"}
    if await is_registered(telegram_id):
        return {"role": "registered"}
    if datetime.now() > REGISTRATION_DEADLINE:
        return {"role": "closed"}
    return {"role": "new"}


@app.post("/api/register")
async def api_register(payload: RegisterPayload):
    user = validate_init_data(payload.init_data)
    if user is None:
        return JSONResponse({"error": "invalid_init_data"}, status_code=403)

    telegram_id = user["id"]
    is_admin = telegram_id in ADMIN_IDS

    full_name = payload.full_name.strip()
    district = payload.district.strip()
    school = payload.school.strip()
    parent_phone = payload.parent_phone.strip()
    phone_digits = "".join(ch for ch in parent_phone if ch.isdigit())

    if len(full_name) < 3 or not district or not school or len(phone_digits) < 9:
        return JSONResponse({"error": "invalid_fields"}, status_code=400)
    if str(payload.grade) not in ALLOWED_GRADES:
        return JSONResponse({"error": "invalid_grade"}, status_code=400)

    if not is_admin:
        if datetime.now() > REGISTRATION_DEADLINE:
            return JSONResponse({"error": "closed"}, status_code=403)
        if await is_registered(telegram_id):
            return JSONResponse({"error": "already_registered"}, status_code=409)

    await add_registration(
        full_name=full_name,
        district=district,
        school=school,
        grade=payload.grade,
        parent_phone=parent_phone,
        telegram_id=None if is_admin else telegram_id,
        registered_by_admin=is_admin,
        admin_id=telegram_id if is_admin else None,
    )
    return {"ok": True}


@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}


@app.get("/healthz")
async def healthz():
    return {"ok": True}
