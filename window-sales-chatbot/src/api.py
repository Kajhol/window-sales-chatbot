from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from datetime import datetime
import os
import re
import json

# Wczytaj klucz API
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

# Klient OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Wczytaj bazę wektorową
script_dir = os.path.dirname(os.path.abspath(__file__))
chroma_dir = os.path.join(script_dir, '..', 'knowledge_base')
leads_file = os.path.join(script_dir, '..', 'data', 'leads.json')

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
    version="2.7"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# System prompt
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
- Opinie Google: [Zobacz opinie](https://maps.google.com/?q=WAFAM+Świętochłowice)

POMIAR: Umawiamy bezpłatny pomiar. Potrzebujemy: miejscowość, kontakt, kiedy pasuje termin.

GDY KLIENT PODA TELEFON LUB EMAIL: Podziękuj i potwierdź że handlowiec oddzwoni/odpisze w ciągu 24h."""

# Pamięć rozmów
conversations = {}

# Pamięć tematów
conversation_topics = {}

# Pamięć zebranych danych do wyceny
collected_data = {}

# LEADY

def load_leads():
    """Wczytaj leady z pliku JSON"""
    if os.path.exists(leads_file):
        with open(leads_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_leads(leads_list):
    """Zapisz leady do pliku JSON"""
    with open(leads_file, 'w', encoding='utf-8') as f:
        json.dump(leads_list, f, ensure_ascii=False, indent=2)

def add_lead(phone: str = None, email: str = None, product: str = None, session_id: str = None):
    """Dodaj nowy lead"""
    leads_list = load_leads()
    
    # Sprawdź czy lead już istnieje
    for lead in leads_list:
        if phone and lead.get("phone") == phone:
            return False
        if email and lead.get("email") == email:
            return False
    
    # Dodaj nowy lead
    new_lead = {
        "id": len(leads_list) + 1,
        "phone": phone,
        "email": email,
        "product": product or "nieznany",
        "session_id": session_id,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "nowy"
    }
    
    leads_list.append(new_lead)
    save_leads(leads_list)
    print(f"Nowy lead #{new_lead['id']}: {phone or email} - {product}")
    return True

def detect_contact_info(message: str):
    """Wykryj telefon lub email w wiadomości"""
    result = {"phone": None, "email": None}
    
    # Wykryj telefon (9 cyfr, różne formaty)
    phone_patterns = [
        r'\b\d{3}[\s-]?\d{3}[\s-]?\d{3}\b',
        r'\b\d{9}\b',
        r'\+48[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{3}\b'
    ]
    
    for pattern in phone_patterns:
        phone_match = re.search(pattern, message)
        if phone_match:
            phone = re.sub(r'[\s\-\+]', '', phone_match.group())
            if phone.startswith('48'):
                phone = phone[2:]
            result["phone"] = phone
            break
    
    # Wykryj email
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', message)
    if email_match:
        result["email"] = email_match.group().lower()
    
    return result


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
    if "telefon" in data:
        context_parts.append(f"Telefon: {data['telefon']}")
    if "email" in data:
        context_parts.append(f"Email: {data['email']}")
    
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
    
    # Wykryj kontakt (telefon/email)
    contact_info = detect_contact_info(message)
    
    if contact_info["phone"]:
        collected_data[session_id]["telefon"] = contact_info["phone"]
        add_lead(
            phone=contact_info["phone"],
            product=collected_data[session_id].get("produkt"),
            session_id=session_id
        )
    
    if contact_info["email"]:
        collected_data[session_id]["email"] = contact_info["email"]
        add_lead(
            email=contact_info["email"],
            product=collected_data[session_id].get("produkt"),
            session_id=session_id
        )

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
    
    # Aktualizuj zebrane dane (w tym leady)
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

    # Dodaj do historii
    history.append({"role": "user", "content": user_message})
    
    # Zbuduj wiadomości dla API
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    recent_history = history[-4:] if len(history) > 4 else history
    for msg in recent_history[:-1]:
        messages.append({"role": msg["role"], "content": msg["content"][:150]})
    
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
        "version": "2.7"
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

# ENDPOINT: Lista leadów
@app.get("/leads")
def get_leads(status: str = None):
    leads_list = load_leads()
    
    if status:
        leads_list = [l for l in leads_list if l.get("status") == status]
    
    return {
        "total": len(leads_list),
        "leads": leads_list
    }

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
    leads_list = load_leads()
    return {
        "project": "WAFAM Sales Chatbot",
        "author": "Kajetan Holdan",
        "version": "2.7",
        "features": ["RAG", "Intent Detection", "Context Memory", "Lead Collection"],
        "total_leads": len(leads_list)
    }