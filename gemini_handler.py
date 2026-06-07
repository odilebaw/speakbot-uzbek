import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)


async def check_speaking_answer(english_question, uzbek_translation, student_answer, example_answer):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        
        prompt = f"""You are an English teacher for Uzbek students.
A student answered this question: "{english_question}"
Student's answer: "{student_answer}"

Respond ONLY in this exact format, nothing else:
BAHO: 3
YAXSHI: Javob tushunarli va to'g'ri tuzilgan
XATO: Xato yo'q
TOGRI: {example_answer}
MASLAHAT: Ko'proq so'z ishlating"""

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
            if line.startswith('BAHO:'):
                result['score'] = line.replace('BAHO:', '').strip()
            elif line.startswith('YAXSHI:'):
                result['good'] = line.replace('YAXSHI:', '').strip()
            elif line.startswith('XATO:'):
                result['mistake'] = line.replace('XATO:', '').strip()
            elif line.startswith('TOGRI:'):
                result['correct'] = line.replace('TOGRI:', '').strip()
            elif line.startswith('MASLAHAT:'):
                result['tip'] = line.replace('MASLAHAT:', '').strip()
        
        return result
        
    except Exception as e:
        return {
            'score': '0',
            'good': '',
            'mistake': f'Xato yuz berdi: {str(e)}',
            'correct': '',
            'tip': 'Qayta urinib ko\'ring'
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
