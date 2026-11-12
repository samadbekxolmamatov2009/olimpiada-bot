# olimpiada-bot

Navoiy–Qorako'l olimpiadasi (3- va 4-sinflar) uchun ro'yxatdan o'tish Telegram boti.

## Imkoniyatlar

- O'quvchi/ota-ona botga quyidagi ma'lumotlarni ketma-ket kiritib ro'yxatdan o'tadi:
  - Ism familya
  - Tumani
  - O'qiyotgan maktabi
  - Sinfi (faqat **3** yoki **4** qabul qilinadi, aks holda ro'yxatga olinmaydi)
  - Ota-onasining telefon raqami
- Har bir foydalanuvchi faqat **bir marta** ro'yxatdan o'tishi mumkin; qayta urinishda bot
  "allaqachon ro'yxatdan o'tgansiz" deb javob beradi va boshqa xabarlarni ro'yxatga olmaydi.
- Ro'yxatdan o'tish bot ishga tushgan kundan **2026-yil 20-noyabrgacha** ochiq.
- Admin (`ADMIN_IDS` ichida ko'rsatilgan foydalanuvchilar):
  - 📥 Barcha ro'yxatdan o'tganlar ro'yxatini **Excel (.xlsx)** fayl ko'rinishida yuklab oladi.
  - ✍️ Ro'yxatdan o'tishni tushunmagan ota-onalar o'rniga o'zi ma'lumotlarni kiritib,
    ro'yxatga qo'shadi.

## O'rnatish

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

`.env.example` faylidan nusxa olib `.env` yarating va to'ldiring:

```bash
cp .env.example .env
```

- `BOT_TOKEN` — @BotFather dan olingan token.
- `ADMIN_IDS` — admin(lar)ning Telegram foydalanuvchi ID raqamlari, vergul bilan ajratilgan
  (masalan: `123456789,987654321`). O'z ID raqamingizni bilish uchun @userinfobot ga yozing.

## Ishga tushirish

```bash
python bot.py
```

Ma'lumotlar `olimpiada.db` (SQLite) faylida saqlanadi.
