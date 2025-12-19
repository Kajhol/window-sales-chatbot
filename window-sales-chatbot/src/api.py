from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import json
import os

# Load API key from .env file
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

# Create OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create FastAPI application
app = FastAPI(
    title="Window Sales Chatbot API",
    description="API for window and door sales chatbot",
    version="0.4"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load intents for context
script_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_directory, '..', 'data', 'intents.json')

with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

intents = data["intents"]

# System prompt - tells AI how to behave
SYSTEM_PROMPT = """Jesteś pomocnym asystentem firmy sprzedającej okna i drzwi.

Twoje zadania:
- Odpowiadaj na pytania o ceny okien i drzwi
- Pomagaj umówić bezpłatny pomiar
- Podawaj informacje kontaktowe
- Bądź uprzejmy i profesjonalny

Informacje o firmie:
- Okna PVC od 400 zł/m²
- Okna aluminiowe od 800 zł/m²
- Drzwi wejściowe od 2000 zł
- Drzwi wewnętrzne od 300 zł
- Telefon: 123-456-789
- Email: biuro@firma.pl
- Godziny pracy: pon-pt 8-18, sob 9-14

Odpowiadaj krótko i konkretnie po polsku."""

# Data models
class Question(BaseModel):
    text: str

class Answer(BaseModel):
    bot: str

# Chat with OpenAI
def ask_openai(user_message: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        max_tokens=200
    )
    return response.choices[0].message.content

# ENDPOINT 1: Home page
@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Window Sales Chatbot API with OpenAI",
        "version": "0.4"
    }

# ENDPOINT 2: Chat with bot (NOW WITH AI!)
@app.post("/chat", response_model=Answer)
def chat(question: Question):
    response = ask_openai(question.text)
    return {"bot": response}

# ENDPOINT 3: Information
@app.get("/info")
def info():
    return {
        "project": "Window Sales Chatbot",
        "author": "Kajetan Holdan",
        "university": "Silesian University of Technology",
        "ai_model": "GPT-4o-mini"
    }