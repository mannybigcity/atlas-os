from dotenv import load_dotenv
from openai import OpenAI

load_dotenv("C:/Users/User/Desktop/PUTER/.env")

client = OpenAI()

speech = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="onyx",
    input="Good evening Manny. This is Atlas. The Kingdom is operational."
)

speech.write_to_file("C:/Users/User/Desktop/PUTER/atlas_onyx_test.mp3")

print("Done. Created C:/Users/User/Desktop/PUTER/atlas_onyx_test.mp3")
