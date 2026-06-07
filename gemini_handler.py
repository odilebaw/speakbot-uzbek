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

Analyze the student's answer carefully. Then:

1. Find ALL grammar mistakes (subject-verb agreement, tense, articles, prepositions, word order)
2. Find ALL vocabulary mistakes (wrong words, incorrect spelling)
3. Be STRICT - even small mistakes must be reported

Respond ONLY in this exact format, nothing else:

BAHO: [1-5, be strict: 5=perfect, 4=1 small mistake, 3=2-3 mistakes, 2=many mistakes, 1=very poor]
YAXSHI: [what was good about their answer in Uzbek]
XATO: [list ALL grammar and vocabulary mistakes in Uzbek, for example: "'she go' emas 'she goes' bolishi kerak (3rd person singular)", if truly no mistakes write 'Xato yoq']
TOGRI: [write the fully corrected version of exactly what they wrote]
MASLAHAT: [one specific improvement tip in Uzbek based on their mistakes]"""

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


async def check_voice_answer(english_question, uzbek_translation, voice_file_path, example_answer):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        
        with open(voice_file_path, 'rb') as f:
            audio_data = f.read()
        
        import base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        prompt = f"""You are a strict English teacher for Uzbek students aged 13-19 at A0-A2 level.

The student was asked: "{english_question}"

Listen carefully to the student's voice answer. Then:

1. Write down EXACTLY what the student said word by word
2. Find ALL grammar mistakes (subject-verb agreement, tense, articles, prepositions, word order)
3. Find ALL vocabulary mistakes (wrong words, incorrect spelling in speech)
4. Be STRICT - even small mistakes must be reported

Respond ONLY in this exact format, nothing else:

TRANSCRIPT: [write exactly what the student said word by word]
BAHO: [1-5, be strict: 5=perfect, 4=1 small mistake, 3=2-3 mistakes, 2=many mistakes, 1=very poor]
YAXSHI: [what was good about their answer in Uzbek]
XATO: [list ALL grammar and vocabulary mistakes in Uzbek, for example: "'she go' emas 'she goes' bolishi kerak (3rd person singular)", if truly no mistakes write 'Xato yoq']
TOGRI: [write the fully corrected version of exactly what they said]
MASLAHAT: [one specific improvement tip in Uzbek based on their mistakes]"""

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
            if line.startswith('TRANSCRIPT:'):
                result['transcript'] = line.replace('TRANSCRIPT:', '').strip()
            elif line.startswith('BAHO:'):
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
