from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os

# Wczytaj klucz API
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

# Klient OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Wczytaj bazę wektorową
script_dir = os.path.dirname(os.path.abspath(__file__))
chroma_dir = os.path.join(script_dir, '..', 'knowledge_base')

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

vectorstore = Chroma(
    persist_directory=chroma_dir,
    embedding_function=embeddings,
    collection_name="wafam_knowledge"
)

print("Baza wektorowa załadowana!")

# FastAPI
app = FastAPI(
    title="WAFAM Chatbot API",
    description="AI Chatbot with Advanced RAG",
    version="2.6"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# System prompt - KRÓTKI ale SKUTECZNY
SYSTEM_PROMPT = """Jesteś asystentem WAFAM (okna, drzwi, rolety, bramy) ze Świętochłowic.

JAK ODPOWIADAĆ:
1. Przeczytaj pytanie klienta
2. Odpowiedz KONKRETNIE na to pytanie (2-3 zdania)
3. Zadaj JEDNO pytanie pomocnicze

WAŻNE:
- NIE ignoruj pytań klienta
- NIE zmieniaj tematu
- NIE powtarzaj się
- Pamiętaj o czym była rozmowa

PRODUKTY:
- Okna: standardowe (DECCO 82, Ideal 7000) i premium (Salamander, DECCO 83)
- Drzwi: pełne (bezpieczne) i przeszklone (estetyczne)
- Rolety: podtynkowe (nowe budynki) i nadstawne (modernizacja)
- Bramy garażowe, żaluzje fasadowe

CENY: Nie podawaj. Wycena indywidualna i bezpłatna.

WYCENA - pytaj o: produkt, ilość, wymiary, miejscowość, montaż, kontakt (telefon/email)

KONTAKT: Marcin 603693023, Aleksandra 693375868 | inwestycje@wafam.pl | ul. Chorzowska 121, Świętochłowice | pn-pt 8-17, sb 8-14

SOCIAL MEDIA:
- Facebook: [WAFAM na Facebooku](https://www.facebook.com/WafamOknaPcv)
- Opinie Google: [Zobacz opinie](https://www.google.com/maps/place/Wafam+Fabryka+Okien/@50.3050299,18.8892615,18z/data=!3m1!5s0x4716d2a8ee3ce311:0x390f303738ceddca!4m8!3m7!1s0x4716d2a8b8f8fb6f:0x81202c6977db6ea7!8m2!3d50.3050289!4d18.8900286!9m1!1b1!16s%2Fg%2F1tgpwykp?entry=ttu&g_ep=EgoyMDI1)

POMIAR: Umawiamy bezpłatny pomiar. Potrzebujemy: miejscowość, kontakt, kiedy pasuje termin."""

# Pamięć rozmów
conversations = {}

# Pamięć tematów
conversation_topics = {}

# Pamięć zebranych danych do wyceny
collected_data = {}

# Modele danych
class Message(BaseModel):
    text: str
    session_id: str = "default"

class Answer(BaseModel):
    bot: str
    sources: list[str] = []

# Funkcja wyszukiwania w bazie
def search_knowledge(query: str, k: int = 2):
    results = vectorstore.similarity_search_with_score(query, k=k)
    
    contexts = []
    sources = []
    
    for doc, score in results:
        # Tylko fragmenty z dobrym dopasowaniem (score < 0.5)
        if score < 0.8:
            content = doc.page_content[:400]
            contexts.append(content)
            title = doc.metadata.get('title', 'Nieznane')
            sources.append(title)
    
    return contexts, sources

# Funkcja rozpoznawania intencji
def detect_intent(message: str) -> str:
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["pomiar", "umówić", "wizyta", "przyjechać"]):
        return "pomiar"
    elif any(word in message_lower for word in ["cena", "koszt", "ile", "kosztuje", "drogo", "tanio"]):
        return "cena"
    elif any(word in message_lower for word in ["kontakt", "telefon", "zadzwonić", "email", "adres", "gdzie jesteście"]):
        return "kontakt"
    elif any(word in message_lower for word in ["jakie macie", "co macie", "oferta", "produkty", "asortyment"]):
        return "produkty"
    elif any(word in message_lower for word in ["polecasz", "polecacie", "doradzisz", "co wybrać", "która", "który"]):
        return "rekomendacja"
    elif any(word in message_lower for word in ["dlaczego", "czemu", "po co"]):
        return "wyjasnienie"
    elif any(word in message_lower for word in ["wycena", "ofertę", "przygotuj"]):
        return "wycena"
    else:
        return "ogolne"

# Funkcja budowania kontekstu rozmowy
def build_conversation_context(session_id: str) -> str:
    if session_id not in collected_data:
        collected_data[session_id] = {}
    
    data = collected_data[session_id]
    
    if not data:
        return ""
    
    context_parts = []
    if "produkt" in data:
        context_parts.append(f"Produkt: {data['produkt']}")
    if "miejscowosc" in data:
        context_parts.append(f"Miejscowość: {data['miejscowosc']}")
    if "wymiary" in data:
        context_parts.append(f"Wymiary: {data['wymiary']}")
    
    if context_parts:
        return "ZEBRANE DANE: " + ", ".join(context_parts)
    return ""

# Funkcja aktualizacji zebranych danych
def update_collected_data(session_id: str, message: str):
    if session_id not in collected_data:
        collected_data[session_id] = {}
    
    message_lower = message.lower()
    
    # Wykryj produkt
    if any(word in message_lower for word in ["okna", "okno"]):
        collected_data[session_id]["produkt"] = "okna"
    elif any(word in message_lower for word in ["drzwi"]):
        collected_data[session_id]["produkt"] = "drzwi"
    elif any(word in message_lower for word in ["rolety", "roleta"]):
        collected_data[session_id]["produkt"] = "rolety"
    elif any(word in message_lower for word in ["brama", "bramy", "garaż"]):
        collected_data[session_id]["produkt"] = "bramy"

# Funkcja rozszerzająca krótkie pytania
def expand_query_with_context(user_message: str, session_id: str) -> str:
    short_responses = ["tak", "nie", "podaj", "link", "chcę", "poproszę", "dawaj", "ok", "okej", "dobrze"]
    message_lower = user_message.lower().strip()
    is_short = len(message_lower.split()) <= 4 and any(word in message_lower for word in short_responses)
    
    if is_short and session_id in conversation_topics:
        topic = conversation_topics[session_id]
        return f"{user_message} (kontekst: {topic})"
    
    product_keywords = ["okna", "okno", "drzwi", "rolety", "roleta", "bramy", "brama", "żaluzje", "taras", "przesuwne"]
    for keyword in product_keywords:
        if keyword in message_lower:
            conversation_topics[session_id] = user_message
            break
    
    return user_message

# Funkcja czatu
def ask_wafam_bot(user_message: str, session_id: str) -> dict:
    if session_id not in conversations:
        conversations[session_id] = []
    
    history = conversations[session_id]
    
    # Aktualizuj zebrane dane
    update_collected_data(session_id, user_message)
    
    # Rozpoznaj intencję
    intent = detect_intent(user_message)
    
    # Rozszerz pytanie o kontekst
    expanded_query = expand_query_with_context(user_message, session_id)
    
    # Wyszukaj w bazie wiedzy
    contexts, sources = search_knowledge(expanded_query)
    
    # Zbuduj kontekst z bazy
    if contexts:
        context_text = "\n".join(contexts)
    else:
        context_text = "Brak szczegółowych danych w bazie."
    
    # Dodaj kontekst zebranych danych
    collected_context = build_conversation_context(session_id)
    
    # Zbuduj prompt
    user_prompt = f"""INTENCJA KLIENTA: {intent}
{collected_context}

DANE Z BAZY:
{context_text}

PYTANIE KLIENTA: {user_message}

Odpowiedz KONKRETNIE na pytanie klienta. Nie zmieniaj tematu."""

    # Dodaj do historii (tylko ostatnie pytanie, nie cały prompt)
    history.append({"role": "user", "content": user_message})
    
    # Zbuduj wiadomości dla API - ostatnie 4 wiadomości
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Dodaj skróconą historię
    recent_history = history[-4:] if len(history) > 4 else history
    for msg in recent_history[:-1]:  # Wszystko oprócz ostatniego
        messages.append({"role": msg["role"], "content": msg["content"][:150]})
    
    # Dodaj aktualne pytanie z pełnym kontekstem
    messages.append({"role": "user", "content": user_prompt})
    
    # Wyślij do OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=250,
        temperature=0.3
    )
    
    bot_response = response.choices[0].message.content
    
    # Dodaj odpowiedź do historii
    history.append({"role": "assistant", "content": bot_response})
    
    # Ogranicz historię
    if len(history) > 8:
        conversations[session_id] = history[-8:]
    else:
        conversations[session_id] = history
    
    unique_sources = list(dict.fromkeys(sources))
    
    return {
        "bot": bot_response,
        "sources": unique_sources[:2]
    }

# ENDPOINT: Strona główna
@app.get("/")
def home():
    return {
        "status": "online",
        "message": "WAFAM Chatbot API",
        "version": "2.6"
    }

# ENDPOINT: Czat
@app.post("/chat", response_model=Answer)
def chat(message: Message):
    response = ask_wafam_bot(message.text, message.session_id)
    return response

# ENDPOINT: Wyczyść rozmowę
@app.post("/clear")
def clear_conversation(session_id: str = "default"):
    if session_id in conversations:
        del conversations[session_id]
    if session_id in conversation_topics:
        del conversation_topics[session_id]
    if session_id in collected_data:
        del collected_data[session_id]
    return {"status": "Rozmowa wyczyszczona", "session_id": session_id}

# ENDPOINT: Szukaj w bazie
@app.get("/search")
def search(query: str, limit: int = 2):
    contexts, sources = search_knowledge(query, k=limit)
    return {
        "query": query,
        "results": [
            {"content": ctx, "source": src}
            for ctx, src in zip(contexts, sources)
        ]
    }

# ENDPOINT: Info
@app.get("/info")
def info():
    return {
        "project": "WAFAM Sales Chatbot",
        "author": "Kajetan Holdan",
        "version": "2.6",
        "features": ["RAG", "Intent Detection", "Context Memory", "Data Collection"]
    }