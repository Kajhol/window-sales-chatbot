from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import random
import os

# Create FastAPI application
app = FastAPI(
    title="Window Sales Chatbot API",
    description="API for window and door sales chatbot",
    version="0.3"
)

# Add CORS - allows frontend to connect to API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data from intents.json
script_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_directory, '..', 'data', 'intents.json')

with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

intents = data["intents"]

# Data models
class Question(BaseModel):
    text: str

class Answer(BaseModel):
    bot: str
    found: bool

# Chatbot logic function
def find_response(user_text: str) -> dict:
    user_text = user_text.lower()
    
    for intent in intents:
        for pattern in intent["patterns"]:
            if pattern.lower() in user_text:
                response = random.choice(intent["responses"])
                return {
                    "bot": response,
                    "found": True
                }
    
    return {
        "bot": "Przepraszam, nie rozumiem. Spróbuj zapytać o: ceny okien, ceny drzwi, pomiar, kontakt.",
        "found": False
    }

# ENDPOINT 1: Home page
@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Window Sales Chatbot API",
        "version": "0.3",
        "documentation": "/docs"
    }

# ENDPOINT 2: Chat with bot
@app.post("/chat", response_model=Answer)
def chat(question: Question):
    response = find_response(question.text)
    return response

# ENDPOINT 3: Information
@app.get("/info")
def info():
    return {
        "project": "Window Sales Chatbot",
        "author": "Kajetan Holdan",
        "university": "Silesian University of Technology",
        "year": 3,
        "intents_count": len(intents)
    }

# ENDPOINT 4: List of available topics
@app.get("/intents")
def list_intents():
    topics = []
    for intent in intents:
        topics.append({
            "tag": intent["tag"],
            "examples": intent["patterns"][:3]
        })
    return {"topics": topics}