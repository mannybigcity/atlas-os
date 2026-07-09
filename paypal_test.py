import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
SECRET = os.getenv("PAYPAL_SECRET")

url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"

response = requests.post(
    url,
    data={"grant_type": "client_credentials"},
    auth=HTTPBasicAuth(CLIENT_ID, SECRET)
)

print(response.status_code)
print(response.text)