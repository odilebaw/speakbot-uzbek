# SpeakBot Uzbek 🤖

## Loyiha haqida

**O'zbek tilida:** SpeakBot - bu 13-19 yoshdagi o'zbek o'quvchilari uchun ingliz tilida speaking mashq qilish Telegram boti. Bot sun'iy intellekt (Google Gemini) yordamida o'quvchilarning javoblarini tekshiradi va baho beradi.

**In English:** SpeakBot is a Telegram bot designed for Uzbek students aged 13-19 to practice English speaking skills. The bot uses AI (Google Gemini) to evaluate student responses and provide feedback at A0-A2 level.

## Imkoniyatlar (Features)

- 📝 **Speaking savollar** - 20 ta tayyor savol 5 ta mavzuda (family, school, hobbies, food, daily life)
- 🤖 **AI tekshiruv** - Google Gemini orqali javoblarni real-time tekshirish
- 📊 **Statistika** - Har bir o'quvchi uchun shaxsiy natijalar va o'rtacha ball
- 🔥 **Kunlik vazifa (Daily Challenge)** - Har kuni yangi savol, streak tizimi
- 📚 **Mavzu tanlash** - O'quvchi o'zi xohlagan mavzuni tanlash imkoniyati
- 🏆 **Reyting** - Top o'quvchilar ro'yxati
- 👨‍🏫 **Admin panel** - O'qituvchi uchun to'liq boshqaruv paneli
- 📢 **Broadcast** - Barcha o'quvchilarga xabar yuborish
- ⏰ **Kunlik eslatma** - Har kuni soat 18:00 da avtomatik eslatma

## O'rnatish (Installation)

### 1. Loyihani yuklab olish

```bash
git clone https://github.com/YOUR_USERNAME/speakbot.git
cd speakbot
```

### 2. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 3. Konfiguratsiya

`config.py` faylida quyidagi qiymatlarni o'zgartiring:

```python
TELEGRAM_BOT_TOKEN = "your_real_token"      # @BotFather dan oling
GEMINI_API_KEY = "your_real_key"            # Google AI Studio dan oling
ADMIN_TELEGRAM_ID = "your_telegram_id"      # @userinfobot dan oling
```

Yoki `.env.example` faylini `.env` ga nusxalab, o'zgaruvchilarni to'ldiring.

### 4. Botni ishga tushirish

```bash
python bot.py
```

## Ishlatish (Usage)

### O'quvchilar uchun (For Students)

| Buyruq | Tavsif |
|--------|--------|
| `/start` | Botni ishga tushirish va ro'yxatdan o'tish |
| `/help` | Barcha buyruqlar ro'yxati |
| `/stats` | Shaxsiy statistika ko'rish |
| `/topic` | Mavzu tanlash |
| `/daily` | Kunlik vazifa olish |

**Qanday ishlaydi:**
1. `/start` buyrug'ini yuboring
2. "Savol olish" tugmasini bosing
3. Ingliz tilida javob yozing
4. AI javobingizni tekshiradi va baho beradi (1-5 ball)
5. Xatolaringizni ko'ring va o'rganing!

### O'qituvchi/Admin uchun (For Teacher/Admin)

| Buyruq | Tavsif |
|--------|--------|
| `/admin` | Admin panelni ochish |
| `/allstats` | Barcha o'quvchilar statistikasi |
| `/broadcast [xabar]` | Barcha o'quvchilarga xabar yuborish |
| `/setchallenge [savol] \| [tarjima] \| [namuna]` | Ertangi kunlik vazifani belgilash |

**Admin panel imkoniyatlari:**
- Barcha o'quvchilar ro'yxati va ularning natijalari
- Umumiy statistika (jami o'quvchilar, javoblar, o'rtacha ball)
- Top 5 o'quvchilar reytingi
- Kunlik vazifa holati
- Broadcast xabar yuborish

## Texnologiyalar (Tech Stack)

- **Python 3.10+** - Asosiy dasturlash tili
- **python-telegram-bot v20.7** - Telegram Bot API kutubxonasi
- **Google Gemini API** - Sun'iy intellekt (AI) javoblarni tekshirish uchun
- **SQLite** - Ma'lumotlar bazasi (o'quvchilar, javoblar, streak)
- **PythonAnywhere** - Hosting platformasi
- **pytz** - Vaqt zonalari bilan ishlash (Asia/Tashkent)

## Loyiha tuzilmasi (Project Structure)

```
speakbot/
├── bot.py                  # Asosiy bot fayli (commands, handlers, main loop)
├── config.py               # Konfiguratsiya (API kalitlari, token)
├── database.py             # SQLite database moduli (CRUD operatsiyalari)
├── gemini_handler.py       # Google Gemini API integratsiyasi
├── questions.py            # 20 ta tayyor savollar banki
├── requirements.txt        # Python kutubxonalar ro'yxati
├── test_bot.py             # Test skripti (database operatsiyalarini tekshirish)
├── .env.example            # Environment variables namunasi
├── .gitignore              # Git ignore fayli
├── pythonanywhere_setup.md # PythonAnywhere deployment qo'llanmasi
└── README.md               # Loyiha hujjati (shu fayl)
```

## Deployment

PythonAnywhere ga deploy qilish uchun `pythonanywhere_setup.md` faylini ko'ring.

## License

This project is for educational purposes.
