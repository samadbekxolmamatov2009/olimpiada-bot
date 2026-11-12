# olimpiada-bot

Navoiy–Qorako'l olimpiadasi (3- va 4-sinflar) uchun ro'yxatdan o'tish Telegram boti.
Ro'yxatdan o'tish **Telegram Mini App** (Web App) ichida, zamonaviy forma ko'rinishida amalga oshadi.

## Qanday ishlaydi

1. Foydalanuvchi botga `/start` yuboradi.
2. Agar `CHANNEL_ID` sozlangan bo'lsa — bot avval shu kanalga obuna ekanini tekshiradi.
   Obuna bo'lmasa, "📢 Kanalga o'tish" va "✅ Men obuna bo'ldim" tugmalari ko'rsatiladi;
   obuna bo'lib, tugmani bosgandan keyingina davom etadi.
3. Bot "📝 Ro'yxatdan o'tish" tugmasini yuboradi — bosilganda Telegram ichida Mini App ochiladi.
4. Mini App formasida: **Ism familya → Tug'ilgan sana → Tumani → Maktabi → Sinfi (3/4) → Ota-ona tel raqami**
   to'ldiriladi va "Ro'yxatdan o'tish" bosiladi. Telefon maydoniga `+998 ` avtomatik yozilgan
   holda ochiladi — foydalanuvchi faqat qolgan raqamlarni kiritadi.
5. Mini App Telegramning `initData`sini backendga yuboradi, backend uni (bot token bilan HMAC
   orqali) tasdiqlab, haqiqiy Telegram foydalanuvchisi ekanini tekshiradi — soxta so'rovlar
   qabul qilinmaydi.
6. Sinfi 3 yoki 4 bo'lmasa — forma umuman shu ikki variantdan boshqasini taklif qilmaydi, shunga
   qaramay backend ham qayta tekshiradi.
7. Bir marta ro'yxatdan o'tgan foydalanuvchi qayta botga kirsa, forma o'rniga
   "✅ Siz allaqachon ro'yxatdan o'tgansiz" oynasi ko'rsatiladi.
8. Ro'yxatdan o'tish bot ishga tushgan kundan **2026-yil 20-noyabrgacha** ochiq; muddat
   tugagach forma yopiq ekani ko'rsatiladi.
9. Admin (`ADMIN_IDS`dagi foydalanuvchilar) uchun `/start` boshqacha menyu ochadi (obuna
   tekshiruvisiz):
   - 📥 **Ro'yxatni yuklab olish** — barcha ro'yxatdan o'tganlar **Excel (.xlsx)** qilib yuboriladi.
   - ✍️ **Ota-ona o'rniga ro'yxatdan o'tkazish** — xuddi shu Mini App ochiladi, lekin admin
     rejimida: cheklovsiz, ketma-ket bir nechta o'quvchini qo'lda kiritish mumkin.

Ma'lumotlar **Turso (libSQL)** bazasida saqlanadi.

## Loyiha tuzilishi

- `app.py` — FastAPI serveri: Telegram webhook, Mini App statik fayllari va `/api/*` endpointlari.
- `handlers/registration.py`, `handlers/admin.py` — aiogram bot handlerlari.
- `webapp/` — Mini App (HTML/CSS/JS).
- `db.py` — Turso bilan ishlovchi async DB qatlami.
- `telegram_auth.py` — Mini App `initData` imzosini tekshirish.
- `config.py` — barcha sozlamalar (`.env` orqali).

## Kerakli environment o'zgaruvchilar

| O'zgaruvchi | Tavsif |
|---|---|
| `BOT_TOKEN` | @BotFather dan olingan bot token |
| `ADMIN_IDS` | Admin(lar)ning Telegram ID raqamlari, vergul bilan (masalan `123456789,987654321`). ID ni bilish uchun @userinfobot ga yozing |
| `TURSO_DATABASE_URL` | Turso bazangiz manzili, masalan `libsql://olimpiada-bot-<org>.turso.io` |
| `TURSO_AUTH_TOKEN` | Turso auth token |
| `PUBLIC_URL` | Ixtiyoriy. Render'da avtomatik (`RENDER_EXTERNAL_URL`) olinadi, boshqa hostda qo'lda yoziladi |
| `WEBHOOK_SECRET` | Ixtiyoriy. O'zingiz tanlagan maxfiy so'z — webhook manzilini taxmin qilib bo'lmasligi uchun |
| `CHANNEL_ID` | Ixtiyoriy. Majburiy obuna kanali (`-100...` ID yoki `@username`). Bo'sh bo'lsa, obuna tekshiruvi o'chirilgan bo'ladi |
| `CHANNEL_URL` | Ixtiyoriy. "Kanalga o'tish" tugmasi havolasi (yopiq/raqamli kanal uchun kerak) |

**Muhim:** `CHANNEL_ID` ishlashi uchun botni shu kanalga **admin** qilib qo'shing — aks holda
bot obuna holatini tekshira olmaydi.

Turso bazasini yaratish:

```bash
turso db create olimpiada-bot
turso db show --url olimpiada-bot
turso db tokens create olimpiada-bot
```

Bu — frontend/boshqa backend ishlatayotgan Turso bazasidan **alohida**, faqat shu bot uchun baza.

## Render'ga joylash

**Build Command:**

```bash
pip install -r requirements.txt
```

**Start Command:**

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

Qadamlar:

1. Render'da **Web Service** yarating, ushbu repo (`olimpiada-bot`) ga ulang.
2. Build/Start Command'larni yuqoridagidek kiriting.
3. **Environment** bo'limida `BOT_TOKEN`, `ADMIN_IDS`, `TURSO_DATABASE_URL`, `TURSO_AUTH_TOKEN`
   ni qo'ying (`WEBHOOK_SECRET`ni ham qo'yish tavsiya etiladi; qo'ymasangiz ham ishlayveradi,
   lekin har qayta deploy/restartda yangi tasodifiy qiymat olinadi).
4. Deploy qiling. Ilova ishga tushganda o'zi avtomatik ravishda Telegram webhookni
   `https://<servis-nomi>.onrender.com/webhook/<WEBHOOK_SECRET>` manziliga o'rnatadi
   (`RENDER_EXTERNAL_URL` orqali) — qo'shimcha hech narsa qilish shart emas.

## Mahalliy ishga tushirish

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # va to'ldiring
```

Mahalliy sinov uchun `PUBLIC_URL`ga ochiq https manzil (masalan ngrok) kerak bo'ladi, aks holda
webhook o'rnatilmaydi:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```
