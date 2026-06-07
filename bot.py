import os
import random
from datetime import date, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from config import TELEGRAM_BOT_TOKEN, ADMIN_TELEGRAM_ID
from database import (
    create_tables, add_student, get_student, save_answer, get_student_stats,
    get_all_students, get_top_students, get_today_answers_count,
    get_total_answers_count, get_average_score_all, get_most_popular_topic,
    get_all_student_telegram_ids, get_student_average_score,
    get_daily_challenge, save_daily_challenge, get_student_daily_answer,
    save_daily_answer, update_student_streak, get_student_streak,
)
from gemini_handler import check_speaking_answer, check_voice_answer, get_daily_question
from questions import QUESTIONS


# --- Keyboards ---

def get_main_menu_keyboard():
    """Return the main menu inline keyboard."""
    keyboard = [
        [InlineKeyboardButton("📝 Savol olish", callback_data="get_question")],
        [InlineKeyboardButton("📊 Mening natijalarim", callback_data="my_stats")],
        [InlineKeyboardButton("📚 Mavzu tanlash", callback_data="choose_topic")],
        [InlineKeyboardButton("ℹ️ Yordam", callback_data="help")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_topic_keyboard():
    """Return the topic selection inline keyboard."""
    keyboard = [
        [InlineKeyboardButton("👨‍👩‍👧 Family", callback_data="topic_family")],
        [InlineKeyboardButton("🏫 School", callback_data="topic_school")],
        [InlineKeyboardButton("🎨 Hobbies", callback_data="topic_hobbies")],
        [InlineKeyboardButton("🍽 Food", callback_data="topic_food")],
        [InlineKeyboardButton("🌅 Daily Life", callback_data="topic_daily life")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_keyboard():
    """Return the admin panel inline keyboard."""
    keyboard = [
        [InlineKeyboardButton("👥 Barcha o'quvchilar", callback_data="admin_all_students")],
        [InlineKeyboardButton("📊 Umumiy statistika", callback_data="admin_overall_stats")],
        [InlineKeyboardButton("📢 Xabar yuborish", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🏆 Eng yaxshi o'quvchilar", callback_data="admin_top_students")],
        [InlineKeyboardButton("📅 Bugungi vazifani ko'rish", callback_data="admin_daily_challenge")],
    ]
    return InlineKeyboardMarkup(keyboard)


def is_admin(telegram_id):
    """Check if the user is the admin."""
    return str(telegram_id) == str(ADMIN_TELEGRAM_ID)


# --- Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - welcome message, register student, show main menu."""
    user = update.effective_user
    telegram_id = user.id
    name = user.full_name
    username = user.username or ""

    # Register student in database
    add_student(telegram_id, name, username)

    welcome_text = (
        f"Assalomu alaykum, {name}! 👋\n\n"
        "🤖 Men SpeakBot - ingliz tilida speaking mashq qilish uchun yordamchingizman.\n\n"
        "📌 Men sizga savollar beraman, siz ingliz tilida javob yozasiz, "
        "va men sun'iy intellekt yordamida javobingizni tekshiraman.\n\n"
        "Quyidagi tugmalardan birini tanlang:"
    )

    await update.message.reply_text(welcome_text, reply_markup=get_main_menu_keyboard())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command - show all available commands in Uzbek."""
    help_text = (
        "📚 Barcha buyruqlar:\n\n"
        "/start - Botni qayta ishga tushirish\n"
        "/help - Yordam va buyruqlar ro'yxati\n"
        "/stats - Shaxsiy statistikangiz\n"
        "/topic - Mavzu tanlash\n\n"
        "📝 Qanday ishlaydi:\n"
        "1. Savol oling\n"
        "2. Ingliz tilida javob yozing\n"
        "3. AI tekshiradi va baho beradi\n"
        "4. Xatolaringizni ko'ring va o'rganing!"
    )

    await update.message.reply_text(help_text, reply_markup=get_main_menu_keyboard())


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command - show student's personal statistics."""
    telegram_id = update.effective_user.id
    student = get_student(telegram_id)

    if not student:
        await update.message.reply_text(
            "Siz hali ro'yxatdan o'tmagansiz. /start buyrug'ini bosing."
        )
        return

    stats = get_student_stats(student["id"])
    await update.message.reply_text(format_stats_message(stats))


async def topic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /topic command - show topic selection menu."""
    await update.message.reply_text(
        "📚 Mavzu tanlang:", reply_markup=get_topic_keyboard()
    )


# --- Admin Command Handlers ---

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command - show admin panel."""
    telegram_id = update.effective_user.id

    if not is_admin(telegram_id):
        await update.message.reply_text("Bu buyruq faqat admin uchun.")
        return

    await update.message.reply_text(
        "🔐 Admin panel:", reply_markup=get_admin_keyboard()
    )


async def allstats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /allstats command - show all students statistics."""
    telegram_id = update.effective_user.id

    if not is_admin(telegram_id):
        await update.message.reply_text("Bu buyruq faqat admin uchun.")
        return

    students = get_all_students()

    if not students:
        await update.message.reply_text("Hozircha hech qanday o'quvchi yo'q.")
        return

    text = "📊 BARCHA O'QUVCHILAR STATISTIKASI\n\n"
    for student in students:
        avg_score = get_student_average_score(student["id"])
        text += (
            f"👤 {student['name']} (@{student['username']})\n"
            f"   📝 Javoblar: {student['total_answers']}\n"
            f"   ⭐ O'rtacha ball: {avg_score}/5\n"
            f"   📅 Qo'shilgan: {student['joined_date'][:10]}\n\n"
        )

    await update.message.reply_text(text)


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /broadcast command - send message to all students."""
    telegram_id = update.effective_user.id

    if not is_admin(telegram_id):
        await update.message.reply_text("Bu buyruq faqat admin uchun.")
        return

    # Get the message text after /broadcast
    message_text = update.message.text.replace("/broadcast", "", 1).strip()

    if not message_text:
        await update.message.reply_text(
            "Iltimos, xabar matnini kiriting.\n"
            "Misol: /broadcast Ertaga imtihon bor!"
        )
        return

    student_ids = get_all_student_telegram_ids()
    sent_count = 0

    for student_telegram_id in student_ids:
        try:
            await context.bot.send_message(
                chat_id=student_telegram_id,
                text=f"📢 O'qituvchidan xabar:\n\n{message_text}"
            )
            sent_count += 1
        except Exception:
            pass

    await update.message.reply_text(
        f"✅ Xabar {sent_count}/{len(student_ids)} o'quvchiga yuborildi."
    )


# --- Daily Challenge Command Handlers ---

async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /daily command - get today's daily speaking challenge."""
    telegram_id = update.effective_user.id
    student = get_student(telegram_id)

    if not student:
        add_student(telegram_id, update.effective_user.full_name, update.effective_user.username or "")
        student = get_student(telegram_id)

    today = date.today().isoformat()

    # Check if student already answered today
    existing_answer = get_student_daily_answer(student["id"], today)
    if existing_answer:
        feedback_text = (
            f"✅ Bugungi natijangiz:\n\n"
            f"{existing_answer['ai_feedback']}\n\n"
            f"Bugun allaqachon javob berdingiz! Ertaga yangi savol keladi \U0001f31f"
        )
        await update.message.reply_text(feedback_text, reply_markup=get_main_menu_keyboard())
        return

    # Get or generate today's challenge
    challenge = get_daily_challenge(today)
    if not challenge:
        # Generate a new daily challenge
        topics = ["family", "school", "hobbies", "food", "daily life"]
        topic = random.choice(topics)
        result = get_daily_question(topic)

        if result.get("error") or not result.get("english_question"):
            await update.message.reply_text(
                "Kechirasiz, bugungi vazifani yaratib bo'lmayapti. Keyinroq urinib ko'ring."
            )
            return

        save_daily_challenge(
            today,
            result["english_question"],
            result["uzbek_translation"],
            result["example_answer"],
            topic
        )
        challenge = get_daily_challenge(today)

    # Store daily challenge state in user_data
    context.user_data["daily_challenge"] = {
        "date": today,
        "english_question": challenge["english_question"],
        "uzbek_translation": challenge["uzbek_translation"],
        "example_answer": challenge["example_answer"],
    }

    challenge_text = (
        "\U0001f525 KUNLIK VAZIFA\n"
        f"\U0001f4c5 {today}\n"
        "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        f"\U0001f4cc Savol: {challenge['english_question']}\n"
        f"\U0001f1fa\U0001f1ff Tarjima: {challenge['uzbek_translation']}\n"
        "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
        "\u270d\ufe0f Javobingizni yozing:\n"
        "(Bugun faqat 1 ta imkoniyat!)"
    )

    await update.message.reply_text(challenge_text)


async def setchallenge_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setchallenge command - admin sets tomorrow's daily challenge."""
    telegram_id = update.effective_user.id

    if not is_admin(telegram_id):
        await update.message.reply_text("Bu buyruq faqat admin uchun.")
        return

    # Parse the message: /setchallenge [english] | [uzbek] | [example]
    message_text = update.message.text.replace("/setchallenge", "", 1).strip()

    if not message_text:
        await update.message.reply_text(
            "Iltimos, quyidagi formatda yozing:\n\n"
            "/setchallenge [english question] | [uzbek translation] | [example answer]\n\n"
            "Misol: /setchallenge What is your favorite hobby? | Sevimli mashg'ulotingiz nima? | My favorite hobby is reading books."
        )
        return

    parts = message_text.split("|")
    if len(parts) != 3:
        await update.message.reply_text(
            "Noto'g'ri format. 3 ta qism kerak, '|' bilan ajratilgan.\n\n"
            "Misol: /setchallenge What is your favorite hobby? | Sevimli mashg'ulotingiz nima? | My favorite hobby is reading books."
        )
        return

    english_question = parts[0].strip()
    uzbek_translation = parts[1].strip()
    example_answer = parts[2].strip()

    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    save_daily_challenge(tomorrow, english_question, uzbek_translation, example_answer, None)

    await update.message.reply_text(
        f"✅ Ertangi kunlik vazifa saqlandi!\n\n"
        f"📅 Sana: {tomorrow}\n"
        f"📌 Savol: {english_question}\n"
        f"🇺🇿 Tarjima: {uzbek_translation}\n"
        f"💡 Namuna: {example_answer}"
    )


# --- Callback Query Handlers ---

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "get_question":
        await send_random_question(query, context)
    elif data == "my_stats":
        await send_stats(query, context)
    elif data == "choose_topic":
        await query.edit_message_text(
            "📚 Mavzu tanlang:", reply_markup=get_topic_keyboard()
        )
    elif data == "help":
        help_text = (
            "📚 Barcha buyruqlar:\n\n"
            "/start - Botni qayta ishga tushirish\n"
            "/help - Yordam va buyruqlar ro'yxati\n"
            "/stats - Shaxsiy statistikangiz\n"
            "/topic - Mavzu tanlash\n\n"
            "📝 Qanday ishlaydi:\n"
            "1. Savol oling\n"
            "2. Ingliz tilida javob yozing\n"
            "3. AI tekshiradi va baho beradi\n"
            "4. Xatolaringizni ko'ring va o'rganing!"
        )
        await query.edit_message_text(help_text, reply_markup=get_main_menu_keyboard())
    elif data.startswith("topic_"):
        topic = data.replace("topic_", "")
        await send_topic_question(query, context, topic)
    elif data.startswith("admin_"):
        await handle_admin_callback(query, context, data)


async def send_random_question(query, context: ContextTypes.DEFAULT_TYPE):
    """Send a random question to the student."""
    question = random.choice(QUESTIONS)

    # Store the current question in user data for later evaluation
    context.user_data["current_question"] = question

    question_text = (
        f"📌 Savol: {question['english_question']}\n"
        f"🇺🇿 Tarjima: {question['uzbek_translation']}\n"
        f"✍️ Javob yozing yoki 🎤 ovozli xabar yuboring:"
    )

    await query.edit_message_text(question_text)


async def send_topic_question(query, context: ContextTypes.DEFAULT_TYPE, topic: str):
    """Send a question from the selected topic."""
    topic_questions = [q for q in QUESTIONS if q["topic"] == topic]

    if topic_questions:
        question = random.choice(topic_questions)
    else:
        question = random.choice(QUESTIONS)

    # Store the current question in user data for later evaluation
    context.user_data["current_question"] = question

    question_text = (
        f"📌 Savol: {question['english_question']}\n"
        f"🇺🇿 Tarjima: {question['uzbek_translation']}\n"
        f"✍️ Javob yozing yoki 🎤 ovozli xabar yuboring:"
    )

    await query.edit_message_text(question_text)


async def send_stats(query, context: ContextTypes.DEFAULT_TYPE):
    """Send statistics to the student via callback query."""
    telegram_id = query.from_user.id
    student = get_student(telegram_id)

    if not student:
        await query.edit_message_text(
            "Siz hali ro'yxatdan o'tmagansiz. /start buyrug'ini bosing."
        )
        return

    stats = get_student_stats(student["id"])
    stats_text = format_stats_message(stats)
    await query.edit_message_text(stats_text, reply_markup=get_main_menu_keyboard())


async def handle_admin_callback(query, context: ContextTypes.DEFAULT_TYPE, data: str):
    """Handle admin panel inline keyboard callbacks."""
    telegram_id = query.from_user.id

    if not is_admin(telegram_id):
        await query.edit_message_text("Bu funksiya faqat admin uchun.")
        return

    if data == "admin_all_students":
        students = get_all_students()

        if not students:
            await query.edit_message_text(
                "Hozircha hech qanday o'quvchi yo'q.",
                reply_markup=get_admin_keyboard()
            )
            return

        text = "👥 BARCHA O'QUVCHILAR\n\n"
        for student in students:
            avg_score = get_student_average_score(student["id"])
            text += (
                f"👤 {student['name']} (@{student['username']})\n"
                f"   📝 Javoblar: {student['total_answers']}\n"
                f"   ⭐ O'rtacha ball: {avg_score}/5\n"
                f"   📅 Qo'shilgan: {student['joined_date'][:10]}\n\n"
            )

        await query.edit_message_text(text, reply_markup=get_admin_keyboard())

    elif data == "admin_overall_stats":
        all_students = get_all_students()
        total_students = len(all_students)
        today_answers = get_today_answers_count()
        total_answers = get_total_answers_count()
        avg_score = get_average_score_all()

        # Get most popular topic
        popular_topic_result = get_most_popular_topic()
        if popular_topic_result:
            question_id = popular_topic_result["question_id"]
            topic_question = next(
                (q for q in QUESTIONS if q["id"] == question_id), None
            )
            popular_topic = topic_question["topic"] if topic_question else "Noma'lum"
        else:
            popular_topic = "Hali javoblar yo'q"

        text = (
            "📊 UMUMIY STATISTIKA\n\n"
            f"👥 Jami o'quvchilar: {total_students}\n"
            f"📝 Bugungi javoblar: {today_answers}\n"
            f"📝 Jami javoblar: {total_answers}\n"
            f"⭐ O'rtacha ball: {avg_score}/5\n"
            f"📚 Eng mashhur mavzu: {popular_topic}\n"
        )

        await query.edit_message_text(text, reply_markup=get_admin_keyboard())

    elif data == "admin_broadcast":
        await query.edit_message_text(
            "📢 Xabar yuborish uchun quyidagi formatda yozing:\n\n"
            "/broadcast [xabar matni]\n\n"
            "Misol: /broadcast Ertaga imtihon bor!",
            reply_markup=get_admin_keyboard()
        )

    elif data == "admin_top_students":
        top_students = get_top_students(5)

        if not top_students:
            await query.edit_message_text(
                "Hozircha natijalar yo'q.",
                reply_markup=get_admin_keyboard()
            )
            return

        medals = ["🥇", "🥈", "🥉"]
        text = "🏆 TOP 5 O'QUVCHILAR\n\n"

        for i, student in enumerate(top_students):
            if i < 3:
                prefix = f"{i + 1}. {medals[i]}"
            else:
                prefix = f"{i + 1}."
            text += f"{prefix} {student['name']} — {student['avg_score']}/5\n"

        await query.edit_message_text(text, reply_markup=get_admin_keyboard())

    elif data == "admin_daily_challenge":
        today = date.today().isoformat()
        challenge = get_daily_challenge(today)

        if not challenge:
            await query.edit_message_text(
                f"📅 Bugun ({today}) uchun vazifa hali yaratilmagan.\n\n"
                "Vazifa birinchi /daily buyrug'ida avtomatik yaratiladi.",
                reply_markup=get_admin_keyboard()
            )
        else:
            text = (
                f"📅 BUGUNGI KUNLIK VAZIFA\n\n"
                f"📌 Savol: {challenge['english_question']}\n"
                f"🇺🇿 Tarjima: {challenge['uzbek_translation']}\n"
                f"💡 Namuna javob: {challenge['example_answer']}\n"
                f"📚 Mavzu: {challenge['topic'] or 'Belgilanmagan'}\n"
                f"📅 Sana: {challenge['date']}"
            )
            await query.edit_message_text(text, reply_markup=get_admin_keyboard())


# --- Daily Reminder ---

async def send_daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Send daily reminder to all students at 18:00 Uzbekistan time."""
    student_ids = get_all_student_telegram_ids()

    reminder_text = (
        "🌟 Salom! Bugun ingliz tilida mashq qildingizmi?\n"
        "Bir savol javob bering — faqat 2 daqiqa vaqt oladi!\n"
        "/start bosing va boshlang 💪"
    )

    for student_telegram_id in student_ids:
        try:
            await context.bot.send_message(
                chat_id=student_telegram_id,
                text=reminder_text
            )
        except Exception:
            pass


# --- Message Handlers ---

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages - evaluate student's answer."""
    daily_challenge = context.user_data.get("daily_challenge")
    current_question = context.user_data.get("current_question")

    if daily_challenge:
        await handle_daily_challenge_answer(update, context, daily_challenge)
        return

    if not current_question:
        await update.message.reply_text(
            "Iltimos, avval savol oling! Quyidagi tugmani bosing:",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    student_answer = update.message.text
    telegram_id = update.effective_user.id
    student = get_student(telegram_id)

    if not student:
        add_student(telegram_id, update.effective_user.full_name, update.effective_user.username or "")
        student = get_student(telegram_id)

    # Send typing action while waiting for AI response
    await update.message.chat.send_action("typing")

    # Get AI feedback
    ai_feedback = await check_speaking_answer(
        current_question["english_question"],
        current_question["uzbek_translation"],
        student_answer,
        current_question["example_answer"],
    )

    # Get score from feedback dict
    score = int(ai_feedback['score']) if ai_feedback['score'].isdigit() else 3

    # Save to database
    save_answer(student["id"], current_question["id"], student_answer, str(ai_feedback), score)

    # Format and send feedback
    feedback_text = format_feedback(ai_feedback)
    await update.message.reply_text(feedback_text, reply_markup=get_main_menu_keyboard())

    # Clear the current question
    context.user_data.pop("current_question", None)


async def handle_daily_challenge_answer(update: Update, context: ContextTypes.DEFAULT_TYPE, daily_challenge):
    """Handle a student's answer to the daily challenge."""
    student_answer = update.message.text
    telegram_id = update.effective_user.id
    student = get_student(telegram_id)

    if not student:
        add_student(telegram_id, update.effective_user.full_name, update.effective_user.username or "")
        student = get_student(telegram_id)

    challenge_date = daily_challenge["date"]

    # Double-check they haven't already answered (race condition protection)
    existing = get_student_daily_answer(student["id"], challenge_date)
    if existing:
        await update.message.reply_text(
            "Bugun allaqachon javob berdingiz! Ertaga yangi savol keladi \U0001f31f",
            reply_markup=get_main_menu_keyboard()
        )
        context.user_data.pop("daily_challenge", None)
        return

    # Send typing action while waiting for AI response
    await update.message.chat.send_action("typing")

    # Get AI feedback
    ai_feedback = await check_speaking_answer(
        daily_challenge["english_question"],
        daily_challenge["uzbek_translation"],
        student_answer,
        daily_challenge["example_answer"],
    )

    # Get score from feedback dict
    score = int(ai_feedback['score']) if ai_feedback['score'].isdigit() else 3

    # Save the daily answer
    save_daily_answer(student["id"], challenge_date, student_answer, str(ai_feedback), score)

    # Update streak
    streak_info = get_student_streak(student["id"])
    current_streak = streak_info["streak"] if streak_info and streak_info["streak"] else 0
    last_daily_date = streak_info["last_daily_date"] if streak_info else None

    today = date.today()
    yesterday = (today - timedelta(days=1)).isoformat()

    if last_daily_date == yesterday:
        new_streak = current_streak + 1
    elif last_daily_date == today.isoformat():
        new_streak = current_streak
    else:
        new_streak = 1

    update_student_streak(student["id"], new_streak, today.isoformat())

    # Format and send feedback
    feedback_text = format_feedback(ai_feedback)

    # Add streak info
    streak_text = f"\n\n\U0001f525 Streak: {new_streak} kun ketma-ket!\nKeep going! \U0001f4aa"
    feedback_text += streak_text

    # Check for milestone messages
    milestone_msg = get_streak_milestone(new_streak)
    if milestone_msg:
        feedback_text += f"\n\n{milestone_msg}"

    await update.message.reply_text(feedback_text, reply_markup=get_main_menu_keyboard())

    # Clear the daily challenge from user data
    context.user_data.pop("daily_challenge", None)


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages - transcribe and evaluate student's spoken answer."""
    daily_challenge = context.user_data.get("daily_challenge")
    current_question = context.user_data.get("current_question")

    if not current_question and not daily_challenge:
        await update.message.reply_text(
            "Iltimos, avval savol oling! Quyidagi tugmani bosing:",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    telegram_id = update.effective_user.id
    student = get_student(telegram_id)

    if not student:
        add_student(telegram_id, update.effective_user.full_name, update.effective_user.username or "")
        student = get_student(telegram_id)

    # Download voice file
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    file_path = f"/tmp/voice_{update.effective_user.id}_{voice.file_id}.ogg"
    await file.download_to_drive(file_path)

    # Send acknowledgment
    await update.message.reply_text("🎤 Ovozingiz qabul qilindi! Tahlil qilinmoqda...")

    # Send typing action while waiting for AI response
    await update.message.chat.send_action("typing")

    if daily_challenge:
        # Handle daily challenge voice answer
        challenge_date = daily_challenge["date"]

        # Double-check they haven't already answered
        existing = get_student_daily_answer(student["id"], challenge_date)
        if existing:
            os.remove(file_path)
            await update.message.reply_text(
                "Bugun allaqachon javob berdingiz! Ertaga yangi savol keladi \U0001f31f",
                reply_markup=get_main_menu_keyboard()
            )
            context.user_data.pop("daily_challenge", None)
            return

        # Get AI feedback
        ai_feedback = await check_voice_answer(
            daily_challenge["english_question"],
            daily_challenge["uzbek_translation"],
            file_path,
            daily_challenge["example_answer"],
        )

        # Get score from feedback dict
        score = int(ai_feedback['score']) if ai_feedback['score'].isdigit() else 3

        # Save the daily answer
        save_daily_answer(student["id"], challenge_date, "[voice message]", str(ai_feedback), score)

        # Update streak
        streak_info = get_student_streak(student["id"])
        current_streak = streak_info["streak"] if streak_info and streak_info["streak"] else 0
        last_daily_date = streak_info["last_daily_date"] if streak_info else None

        today = date.today()
        yesterday = (today - timedelta(days=1)).isoformat()

        if last_daily_date == yesterday:
            new_streak = current_streak + 1
        elif last_daily_date == today.isoformat():
            new_streak = current_streak
        else:
            new_streak = 1

        update_student_streak(student["id"], new_streak, today.isoformat())

        # Format and send feedback
        feedback_text = format_feedback(ai_feedback)

        # Add streak info
        streak_text = f"\n\n\U0001f525 Streak: {new_streak} kun ketma-ket!\nKeep going! \U0001f4aa"
        feedback_text += streak_text

        # Check for milestone messages
        milestone_msg = get_streak_milestone(new_streak)
        if milestone_msg:
            feedback_text += f"\n\n{milestone_msg}"

        await update.message.reply_text(feedback_text, reply_markup=get_main_menu_keyboard())

        # Clear the daily challenge from user data
        context.user_data.pop("daily_challenge", None)

    else:
        # Handle regular question voice answer
        # Get AI feedback
        ai_feedback = await check_voice_answer(
            current_question["english_question"],
            current_question["uzbek_translation"],
            file_path,
            current_question["example_answer"],
        )

        # Get score from feedback dict
        score = int(ai_feedback['score']) if ai_feedback['score'].isdigit() else 3

        # Save to database
        save_answer(student["id"], current_question["id"], "[voice message]", str(ai_feedback), score)

        # Format and send feedback
        feedback_text = format_feedback(ai_feedback)
        await update.message.reply_text(feedback_text, reply_markup=get_main_menu_keyboard())

        # Clear the current question
        context.user_data.pop("current_question", None)

    # Delete temp file
    os.remove(file_path)


async def handle_non_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle non-text messages (photo, video, audio, document)."""
    await update.message.reply_text("Iltimos, javobingizni yozma shaklda yuboring ✍️")


# --- Helper Functions ---

def format_feedback(feedback: dict) -> str:
    """Format the AI feedback dict into a user-friendly message."""
    score = feedback.get('score', '3')
    good_part = feedback.get('good', '')
    mistake = feedback.get('mistake', '')
    correct_answer = feedback.get('correct', '')
    tip = feedback.get('tip', '')

    feedback_text = (
        f"✅ Bahongiz: {score}/5\n"
        f"👍 Yaxshi tomoni: {good_part}\n"
        f"❌ Xato: {mistake}\n"
        f"💡 To'g'ri javob: {correct_answer}\n"
        f"📌 Maslahat: {tip}"
    )

    return feedback_text


def format_stats_message(stats) -> str:
    """Format student statistics into a readable message."""
    if not stats or stats["total_answers"] == 0:
        return (
            "📊 Sizning natijalaringiz:\n\n"
            "Siz hali birorta ham savolga javob bermagansiz.\n"
            "Boshlash uchun \"📝 Savol olish\" tugmasini bosing!"
        )

    total_answers = stats["total_answers"]
    correct_answers = stats["correct_answers"]

    # Calculate average score (correct answers are those with score >= 3)
    if total_answers > 0:
        average_score = round((correct_answers / total_answers) * 5, 1)
    else:
        average_score = 0

    # Determine best topic based on correct ratio
    best_topic = get_best_topic_label(correct_answers, total_answers)

    # Encouragement message based on progress
    if average_score >= 4:
        encouragement = "🌟 Ajoyib natija! Siz juda yaxshi o'qiyapsiz!"
    elif average_score >= 3:
        encouragement = "👍 Yaxshi! Shunday davom eting!"
    elif average_score >= 2:
        encouragement = "💪 Harakat qiling! Har kuni mashq qilsangiz, yaxshilanadi!"
    else:
        encouragement = "📚 Ko'proq mashq qiling! Har bir xato - bu o'rganish imkoniyati!"

    stats_text = (
        f"📊 Sizning natijalaringiz:\n\n"
        f"📝 Jami javoblar: {total_answers}\n"
        f"⭐ O'rtacha ball: {average_score}/5\n"
        f"🏆 Eng yaxshi mavzu: {best_topic}\n\n"
        f"{encouragement}"
    )

    return stats_text


def get_best_topic_label(correct_answers: int, total_answers: int) -> str:
    """Get the best topic label based on student performance."""
    # Since we don't track per-topic stats in the simple DB, give general feedback
    if correct_answers > total_answers * 0.7:
        return "Barcha mavzularda yaxshi!"
    elif correct_answers > total_answers * 0.5:
        return "Yaxshi yo'ldasiz!"
    else:
        return "Ko'proq mashq kerak"


def get_streak_milestone(streak: int) -> str:
    """Get a milestone message if the streak hits a milestone number."""
    milestones = {
        3: "\U0001f389 3 kun ketma-ket! Zo'r boshlang'ich!",
        7: "\U0001f3c6 1 hafta ketma-ket! Siz ajoyibsiz!",
        14: "\U0001f31f 2 hafta ketma-ket! Haqiqiy chempion!",
        30: "\U0001f451 1 OY ketma-ket! Siz legendasiz!",
    }
    return milestones.get(streak, "")


# --- Main ---

def main():
    """Start the bot."""
    import datetime
    import pytz

    # Create database tables
    create_tables()

    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("topic", topic_command))
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("allstats", allstats_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("daily", daily_command))
    application.add_handler(CommandHandler("setchallenge", setchallenge_command))

    # Add callback query handler for inline buttons
    application.add_handler(CallbackQueryHandler(button_handler))

    # Add message handlers
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message)
    )
    application.add_handler(
        MessageHandler(filters.VOICE, handle_voice_message)
    )
    application.add_handler(
        MessageHandler(
            filters.PHOTO | filters.VIDEO | filters.AUDIO | filters.Document.ALL,
            handle_non_text_message,
        )
    )

    # Set up daily reminder at 18:00 Uzbekistan time (UTC+5)
    uzbekistan_tz = pytz.timezone("Asia/Tashkent")
    reminder_time = datetime.time(hour=18, minute=0, second=0, tzinfo=uzbekistan_tz)
    application.job_queue.run_daily(send_daily_reminder, time=reminder_time)

    # Run the bot
    print("SpeakBot Uzbek ishga tushdi! 🚀")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
