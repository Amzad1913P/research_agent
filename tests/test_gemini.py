# test_gemini.py

from src.config import config
from google import genai

print("Provider:", config.model_provider)
print("Model:", config.model_name)
print("Key loaded:", bool(config.google_api_key))
print("Key length:", len(config.google_api_key or ""))

client = genai.Client(
    api_key=config.google_api_key.strip()
)

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Reply with exactly: Gemini connection successful"
)

print(response.text)