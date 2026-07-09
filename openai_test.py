from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv(r"C:\Users\User\Desktop\PUTER\.env")

key = os.getenv("OPENAI_API_KEY")
print("OPENAI KEY LOADED:", bool(key))

try:
    client = OpenAI(api_key=key)
    response = client.responses.create(
        model="gpt-5.5",
        input="Say OPENAI_OK only."
    )
    print(response.output_text)
except Exception as e:
    print("OPENAI_TEST_FAILED")
    print(type(e).__name__)
    print(e)
