import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-lite")

SYSTEM_PROMPT = """You are an English teacher assistant for Uzbek students aged 13-19 at A0-A2 level.
A student answered an English speaking question.
Evaluate their answer and respond ONLY in Uzbek language.

Your response must follow this exact format:
BAHO: [give a score from 1 to 5]
YAXSHI TOMONI: [what was good about their answer - in simple Uzbek]
XATO: [what was wrong - in simple Uzbek, if nothing wrong write 'Xato yoq']
TO'G'RI JAVOB: [write a better/correct version of their answer in English]
MASLAHAT: [one simple tip to improve - in Uzbek]"""


def check_speaking_answer(english_question, uzbek_translation, student_answer, example_answer):
    """Send the student's answer to Gemini API for evaluation."""
    try:
        prompt = f"""{SYSTEM_PROMPT}

Question (English): {english_question}
Question (Uzbek): {uzbek_translation}
Student's answer: {student_answer}
Example of a good answer: {example_answer}"""

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "Kechirasiz, hozir javobingizni tekshirib bo'lmayapti. Iltimos, keyinroq urinib ko'ring."


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
