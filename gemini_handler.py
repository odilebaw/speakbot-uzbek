import google.generativeai as genai
import base64
import random
from config import GEMINI_API_KEYS, GEMINI_API_KEY

async def check_speaking_answer(english_question, uzbek_translation, student_answer, example_answer):
    all_keys = GEMINI_API_KEYS if GEMINI_API_KEYS else [GEMINI_API_KEY]

    prompt = f"""You are a strict English teacher for Uzbek students aged 13-19 at A0-A2 level.
The student was asked: "{english_question}"
Student's answer: "{student_answer}"

Your job:
1. Find EVERY grammar and vocabulary mistake
2. Explain EACH mistake clearly in Uzbek like this example:
   "'I go' emas 'I went' bo'lishi kerak - chunki o'tgan zamon (past tense) ishlatilishi kerak"
   "'she drink' emas 'she drinks' bo'lishi kerak - chunki 3-shaxs birlikda fe'lga -s qo'shiladi"

Respond ONLY in this exact format:

BAHO: [1-5: 5=no mistakes, 4=1 mistake, 3=2-3 mistakes, 2=4+ mistakes, 1=very poor]
YAXSHI: [one positive thing about their answer in Uzbek]
XATO: [explain EACH mistake separately with reason in Uzbek. If no mistakes: 'Xato yo'q']
TOGRI: [write the fully corrected sentence in English]
MASLAHAT: [one specific tip in Uzbek based on their main mistake]"""

    last_error = None
    for key in all_keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-2.5-flash-lite")

            response = model.generate_content(prompt)
            text = response.text.strip()

            result = {
                'score': '3',
                'good': '',
                'mistake': '',
                'correct': '',
                'tip': ''
            }

            for line in text.split(''):
                line = line.strip()
                if ':' in line:
                    k, _, value = line.partition(':')
                    k = k.strip().upper()
                    value = value.strip()
                    if k == 'BAHO':
                        result['score'] = value
                    elif k == 'YAXSHI':
                        result['good'] = value
                    elif k == 'XATO':
                        result['mistake'] = value
                    elif k == 'TOGRI':
                        result['correct'] = value
                    elif k == 'MASLAHAT':
                        result['tip'] = value

            return result

        except Exception as e:
            last_error = str(e)
            continue

    return {
        'score': '0',
        'good': '',
        'mistake': f'Barcha keylar ishlamadi: {last_error}',
        'correct': '',
        'tip': 'Iltimos keyinroq urinib koring'
    }

async def check_voice_answer(english_question, uzbek_translation, voice_file_path, example_answer):
    all_keys = GEMINI_API_KEYS if GEMINI_API_KEYS else [GEMINI_API_KEY]

    with open(voice_file_path, 'rb') as f:
        audio_data = f.read()
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')

    prompt = f"""You are a strict English grammar teacher for Uzbek students (A0-A2 level).
The student was asked: "{english_question}"

Listen to the student's voice and do the following:

TASK 1: Write EXACTLY what the student said word by word.
TASK 2: Check EVERY word for grammar mistakes. Look for:
- Wrong pronoun (I instead of My, He instead of His)
- Wrong verb form (go instead of goes, are instead of is)
- Missing words (missing 'is', 'a', 'the')
- Wrong word choice
- Repeated words
TASK 3: For EACH mistake found, write it like this:
'[wrong]' -> '[correct]' : [why in Uzbek]

Respond ONLY in this format:

TRANSCRIPT: [word for word what student said]
BAHO: [1-5, very strict: 5=perfect, 4=1 mistake, 3=2 mistakes, 2=3-4 mistakes, 1=5+ mistakes]
YAXSHI: [one positive thing in Uzbek]
XATO: [each mistake on new line. If zero mistakes: 'Xato yoq']
TOGRI: [corrected full sentence]
MASLAHAT: [one tip in Uzbek]

RULE: If student made ANY mistake, XATO must NOT be empty."""

    last_error = None
    for key in all_keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-2.5-flash-lite")

            response = model.generate_content([
                prompt,
                {
                    "inline_data": {
                        "mime_type": "audio/ogg",
                        "data": audio_base64
                    }
                }
            ])

            text = response.text.strip()
            result = {
                'transcript': '',
                'score': '3',
                'good': '',
                'mistake': '',
                'correct': '',
                'tip': ''
            }

            current_key = None
            current_value_lines = []

            for line in text.split('
'):
                line = line.strip()
                if not line:
                    continue
                if ':' in line:
                    first_word = line.split(':')[0].strip().upper()
                    if first_word in ['TRANSCRIPT', 'BAHO', 'YAXSHI', 'XATO', 'TOGRI', 'MASLAHAT']:
                        if current_key and current_value_lines:
                            value = ' '.join(current_value_lines).strip()
                            if current_key == 'TRANSCRIPT': result['transcript'] = value
                            elif current_key == 'BAHO': result['score'] = value
                            elif current_key == 'YAXSHI': result['good'] = value
                            elif current_key == 'XATO': result['mistake'] = value
                            elif current_key == 'TOGRI': result['correct'] = value
                            elif current_key == 'MASLAHAT': result['tip'] = value
                        current_key = first_word
                        current_value_lines = [line.partition(':')[2].strip()]
                    else:
                        if current_key:
                            current_value_lines.append(line)
                else:
                    if current_key:
                        current_value_lines.append(line)

            if current_key and current_value_lines:
                value = ' '.join(current_value_lines).strip()
                if current_key == 'TRANSCRIPT': result['transcript'] = value
                elif current_key == 'BAHO': result['score'] = value
                elif current_key == 'YAXSHI': result['good'] = value
                elif current_key == 'XATO': result['mistake'] = value
                elif current_key == 'TOGRI': result['correct'] = value
                elif current_key == 'MASLAHAT': result['tip'] = value

            return result

        except Exception as e:
            last_error = str(e)
            continue

    return {
        'transcript': '',
        'score': '0',
        'good': '',
        'mistake': f'Barcha keylar ishlamadi: {last_error}',
        'correct': '',
        'tip': 'Iltimos keyinroq urinib koring'
    }

def get_daily_question(topic):
    """Generate 1 new speaking question on the given topic."""
    all_keys = GEMINI_API_KEYS if GEMINI_API_KEYS else [GEMINI_API_KEY]

    prompt = f"""Generate 1 simple English speaking question for Uzbek students aged 13-19 at A0-A2 level.
Topic: {topic}

Respond in this exact format (no extra text):
QUESTION: [question in English]
UZBEK: [translation of the question in Uzbek]
EXAMPLE: [a simple example answer in English, 1-2 sentences]"""

    for key in all_keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-2.5-flash-lite")

            response = model.generate_content(prompt)
            text = response.text

            lines = text.strip().split("
")
            english_question = ""
            uzbek_translation = ""
            example_answer = ""

            for line in lines:
                if line.startswith("QUESTION:"):
                    english_question = line.replace("QUESTION:", "").strip()
                elif line.startswith("UZBEK:"):
                    uzbek_translation = line.replace("UZBEK:", "").strip()
                elif line.startswith("EXAMPLE:"):
                    example_answer = line.replace("EXAMPLE:", "").strip()

            return {
                "english_question": english_question,
                "uzbek_translation": uzbek_translation,
                "example_answer": example_answer
            }
        except Exception:
            continue

    return {
        "english_question": "",
        "uzbek_translation": "",
        "example_answer": "",
        "error": "Kechirasiz, savol yaratib bo'lmayapti. Iltimos, keyinroq urinib ko'ring."
    }
