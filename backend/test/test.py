import os

from openai import OpenAI

api_key = os.getenv("DEEPSEEK_API_KEY", "")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
# Round 1
messages = [{"role": "system", "content": "You are a helpful assistant."},{"role": "user", "content": "9.11 and 9.8, which is greater?"}]
response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=messages,
    stream=True
)

reasoning_content = ""
content = ""

for chunk in response:
    if chunk.choices[0].delta.reasoning_content:
        reasoning_content += chunk.choices[0].delta.reasoning_content if chunk.choices[0].delta.reasoning_content is not None else ''
        print(reasoning_content)
    else:
        content += chunk.choices[0].delta.content if chunk.choices[0].delta.content is not None else ''
        print(content)