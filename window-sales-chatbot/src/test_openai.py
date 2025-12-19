import os
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from .env file (one folder up)
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

# Check if key is loaded
api_key = os.getenv("OPENAI_API_KEY")
print("Key loaded:", "YES" if api_key else "NO")

# Create OpenAI client
client = OpenAI(api_key=api_key)

# Send test message
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Powiedz 'Cześć, działam!' po polsku"}
    ]
)

# Print response
print("OpenAI odpowiada:")
print(response.choices[0].message.content)