import openai
from dotenv import load_dotenv
import os
import pandas as pd
import requests

load_dotenv()  # take environment variables from .env.

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def qa(messages, response_url, headers, data, message_ts):
    response = client.chat.completions.create(
                model="gpt-4o-mini-2024-07-18",
                messages=[{"role": "system", "content": "Your name is Orion. You are a omniscient AI. You can answer any question."}]+messages[-10:]
            )
    first_thread_message = {'role': 'First responder', 'content': 'test 1'}
    first_timestamp = pd.Timestamp.now()
    thread_response_data = data.copy()
    thread_response_data['text'] = first_thread_message['content']
    thread_response_data['thread_ts'] = message_ts
    _ = requests.post(url=response_url, headers=headers, data=thread_response_data)

    second_thread_message = {'role': 'Second responder', 'content': 'test 2'}
    second_timestamp = pd.Timestamp.now()
    thread_response_data['text'] = second_thread_message['content']
    thread_response_data['thread_ts'] = message_ts
    _ = requests.post(url=response_url, headers=headers, data=thread_response_data)
    
    third_thread_message = {'role': 'Third responder', 'content': 'test 3'}
    third_timestamp = pd.Timestamp.now()
    thread_response_data['text'] = third_thread_message['content']
    thread_response_data['thread_ts'] = message_ts
    _ = requests.post(url=response_url, headers=headers, data=thread_response_data)
    
    agent_messages = [first_thread_message, second_thread_message, third_thread_message]
    timestamps = [first_timestamp, second_timestamp, third_timestamp]
    return agent_messages, timestamps, response.choices[0].message.content


if __name__ == '__main__':
    # print(qa("What is the capital of France?"))
    pass