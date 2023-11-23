import openai
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

async def generate_text(query: str, prompt: str, prohibited_words: list = []):
    if not openai.api_key:
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    messages = [{"role": "system", "content": prompt}, {"role": "user", "content": query}]
    attempts = 0
    try:
        while True:
            if attempts >= 3:
                return "CHATGPT ERROR: KEEPS DETECTING PROHIBITED WORDS IN RESPONSE"
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, stream=True)
            response_message = ''
            for i in response:
                resp = i["choices"][0]["delta"].get("content", "")
                response_message += resp

            detected_prohib_words = any(prohib_word in response_message for prohib_word in prohibited_words)
            if not detected_prohib_words:
                return response_message
            else:
                attempts += 1
    except Exception as e:
        print(e)
        return "ERROR WITH CHATGPT"