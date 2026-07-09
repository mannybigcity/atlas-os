# test_brain.py — PUTER's first words

# 1. Bring in the two tools we installed
from openai import OpenAI
from dotenv import load_dotenv

# 2. Load our secret key from config/.env
load_dotenv("config/.env")

# 3. Create the connection to OpenAI (it finds OPENAI_API_KEY automatically)
client = OpenAI()

# 4. Send a message and get a reply
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Say hello and introduce yourself as PUTER in one sentence."}
    ]
)

# 5. Print just the AI's reply
print(response.choices[0].message.content)