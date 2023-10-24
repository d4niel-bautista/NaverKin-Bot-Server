import openai
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

async def generate_text(query: str, prompt: str, prohibited_words: list = []):
    if not openai.api_key:
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    messages = [{"role": "system", "content": prompt}, {"role": "user", "content": query}]

    try:
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        response_message = response["choices"][0]["message"]["content"]

        if not any(prohib_word in response_message for prohib_word in prohibited_words):
            return response_message
        else:
            await asyncio.sleep(1)
            return await generate_text(query=query, prompt=prompt, prohibited_words=prohibited_words)
    except Exception as e:
        print(e)
        return "ERROR WITH CHATGPT"