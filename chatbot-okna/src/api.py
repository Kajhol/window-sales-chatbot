from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import random
import os

# Tworzymy aplikację FastAPI
app = FastAPI(
    title="Window Sales Chatbot API",
    description="API dla chatbota sprzedającego okna i drzwi",
    version="0.3"
)

# Dodajemy CORS - pozwala stronie HTML łączyć się z API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wczytanie danych z intents.json
katalog_skryptu = os.path.dirname(os.path.abspath(__file__))
sciezka_pliku = os.path.join(katalog_skryptu, '..', 'data', 'intents.json')

with open(sciezka_pliku, "r", encoding="utf-8") as plik:
    dane = json.load(plik)

intencje = dane["intents"]

# Modele danych
class Pytanie(BaseModel):
    tekst: str

class Odpowiedz(BaseModel):
    bot: str
    znaleziono: bool

# Funkcja logiki chatbota
def znajdz_odpowiedz(tekst_uzytkownika: str) -> dict:
    tekst_uzytkownika = tekst_uzytkownika.lower()
    
    for intencja in intencje:
        for wzorzec in intencja["patterns"]:
            if wzorzec.lower() in tekst_uzytkownika:
                odpowiedz = random.choice(intencja["responses"])
                return {
                    "bot": odpowiedz,
                    "znaleziono": True
                }
    
    return {
        "bot": "Przepraszam, nie rozumiem. Spróbuj zapytać o: ceny okien, ceny drzwi, pomiar, kontakt.",
        "znaleziono": False
    }

#Strona główna
@app.get("/")
def strona_glowna():
    return {
        "status": "online",
        "wiadomosc": "Window Sales Chatbot API",
        "wersja": "0.3",
        "dokumentacja": "/docs"
    }

#Rozmowa z botem
@app.post("/chat", response_model=Odpowiedz)
def rozmawiaj(pytanie: Pytanie):
    odpowiedz = znajdz_odpowiedz(pytanie.tekst)
    return odpowiedz

#Informacje
@app.get("/info")
def informacje():
    return {
        "projekt": "Window Sales Chatbot",
        "autor": "Kajetan Hołdan",
        "uczelnia": "Politechnika Śląska",
        "rok": 3,
        "liczba_intencji": len(intencje)
    }

#Lista dostępnych tematów
@app.get("/intencje")
def lista_intencji():
    tematy = []
    for intencja in intencje:
        tematy.append({
            "tag": intencja["tag"],
            "przyklady": intencja["patterns"][:3]
        })
    return {"tematy": tematy}