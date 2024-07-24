import openai
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def qa(query):
    response = client.chat.completions.create(
                model="gpt-4o-mini-2024-07-18",
                messages=[
                    {"role": "system", "content": "Your name is Orion. You are a omniscient AI. You can answer any question."},
                    {"role": "user", "content": query}
                ]
            )

    return response.choices[0].message.content


if __name__ == '__main__':
    print(qa("What is the capital of France?"))