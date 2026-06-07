import base64

import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)


async def check_speaking_answer(english_question, uzbek_translation, student_answer, example_answer):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        
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

        response = model.generate_content(prompt)
        text = response.text.strip()
        
        lines = text.split('\n')
        result = {
            'score': '3',
            'good': '',
            'mistake': '',
            'correct': '',
            'tip': ''
        }
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, _, value = line.partition(':')
                key = key.strip().upper()
                value = value.strip()
                if key == 'TRANSCRIPT':
                    result['transcript'] = value
                elif key == 'BAHO':
                    result['score'] = value
                elif key == 'YAXSHI':
                    result['good'] = value
                elif key == 'XATO':
                    result['mistake'] = value
                elif key == 'TOGRI':
                    result['correct'] = value
                elif key == 'MASLAHAT':
                    result['tip'] = value
        
        return result
        
    except Exception as e:
        return {
            'score': '0',
            'good': '',
            'mistake': f'Xato yuz berdi: {str(e)}',
            'correct': '',
            'tip': 'Qayta urinib ko\'ring'
        }


async def check_voice_answer(english_question, uzbek_translation, voice_file_path, example_answer):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        
        with open(voice_file_path, 'rb') as f:
            audio_data = f.read()
        
        import base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        prompt = f"""You are a strict English teacher for Uzbek students aged 13-19 at A0-A2 level.
The student was asked: "{english_question}"

Listen to the student's voice answer carefully.

Your job:
1. Write down EXACTLY what the student said, word by word
2. Find EVERY grammar and vocabulary mistake
3. Explain EACH mistake clearly in Uzbek like this example:
   "'I go' emas 'I went' bo'lishi kerak - chunki o'tgan zamon (past tense) ishlatilishi kerak"
   "'she drink' emas 'she drinks' bo'lishi kerak - chunki 3-shaxs birlikda fe'lga -s qo'shiladi"

Respond ONLY in this exact format:

TRANSCRIPT: [write word by word exactly what student said]
BAHO: [1-5: 5=no mistakes, 4=1 mistake, 3=2-3 mistakes, 2=4+ mistakes, 1=very poor]
YAXSHI: [one positive thing about their answer in Uzbek]
XATO: [explain EACH mistake separately with reason in Uzbek. If no mistakes: 'Xato yo'q']
TOGRI: [write the fully corrected sentence in English]
MASLAHAT: [one specific tip in Uzbek based on their main mistake]"""

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
        lines = text.split('\n')
        result = {
            'transcript': '',
            'score': '3',
            'good': '',
            'mistake': '',
            'correct': '',
            'tip': ''
        }
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, _, value = line.partition(':')
                key = key.strip().upper()
                value = value.strip()
                if key == 'TRANSCRIPT':
                    result['transcript'] = value
                elif key == 'BAHO':
                    result['score'] = value
                elif key == 'YAXSHI':
                    result['good'] = value
                elif key == 'XATO':
                    result['mistake'] = value
                elif key == 'TOGRI':
                    result['correct'] = value
                elif key == 'MASLAHAT':
                    result['tip'] = value
        
        return result
        
    except Exception as e:
        return {
            'transcript': '',
            'score': '0',
            'good': '',
            'mistake': f'Ovoz xatosi: {str(e)}',
            'correct': '',
            'tip': 'Qayta urinib koring'
        }


def get_daily_question(topic):
    """Ask Gemini to generate 1 new speaking question on the given topic."""
    try:
        prompt = f"""Generate 1 simple English speaking question for Uzbek students aged 13-19 at A0-A2 level.
Topic: {topic}

Respond in this exact format (no extra text):
QUESTION: [question in English]
UZBEK: [translation of the question in Uzbek]
EXAMPLE: [a simple example answer in English, 1-2 sentences]"""

        response = model.generate_content(prompt)
        text = response.text

        lines = text.strip().split("\n")
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
    except Exception as e:
        return {
            "english_question": "",
            "uzbek_translation": "",
            "example_answer": "",
            "error": "Kechirasiz, savol yaratib bo'lmayapti. Iltimos, keyinroq urinib ko'ring."
        }
