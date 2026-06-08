import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_API_KEYS = [
    os.environ.get("GEMINI_API_KEY_1", ""),
    os.environ.get("GEMINI_API_KEY_2", ""),
    os.environ.get("GEMINI_API_KEY_3", ""),
    os.environ.get("GEMINI_API_KEY_4", ""),
    os.environ.get("GEMINI_API_KEY_5", ""),
]
# Filter empty keys
GEMINI_API_KEYS = [k for k in GEMINI_API_KEYS if k]

# Groq API keys
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_API_KEYS = [
    os.environ.get("GROQ_API_KEY_1", ""),
    os.environ.get("GROQ_API_KEY_2", ""),
    os.environ.get("GROQ_API_KEY_3", ""),
    os.environ.get("GROQ_API_KEY_4", ""),
    os.environ.get("GROQ_API_KEY_5", ""),
]
# Filter empty keys
GROQ_API_KEYS = [k for k in GROQ_API_KEYS if k]

DATABASE_NAME = "speakbot.db"
ADMIN_TELEGRAM_ID = os.environ.get("ADMIN_TELEGRAM_ID", "")
