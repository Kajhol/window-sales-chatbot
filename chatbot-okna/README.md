# 🏠 Chatbot do obsługi klienta (Window Sales Bot)
![Status](https://img.shields.io/badge/Status-Tworzę-red)
![Wersja](https://img.shields.io/badge/Version-0.2-blue)

👋 Tutaj wrzucam projekt, nad którym ostatnio pracuję. Jest to chatbot dla branży okiennej, który ma za zadanie wstępnie obsłużyć klienta, zanim ten trafi do handlowca.

### 💡 Skąd ten pomysł?
Chciałbym ułatwić pracę wszystkim handlowcom w branży okienniczej

Napisałem tego bota, żeby:
1.  Klient mógł korzystać z usług **24/7**
2.  Odciążyć pracownika rozmawiającego z klientem
3.  Zautomatyzować umawianie pomiarów

---

### ⚙️ Jak to jest zrobione (Tech Stack)
- **Python 3.12.9**
- **NLTK** - przetwarzanie języka naturalnego
- **scikit-learn** - uczenie maszynowe
- **NumPy** - obliczenia

### 🛠️ Co już działa?
- Konfiguracja środowiska Python 3.12.9
- Struktura projektu (foldery, venv)
- Instalacja bibliotek (NLTK, scikit-learn, NumPy)
- Plik intents.json z 6 kategoriami (powitanie, pożegnanie, ceny okien, ceny drzwi, pomiar, kontakt)
- Wczytywanie danych JSON
- Pętla rozmowy (ciągła konwersacja)
- Obsługa nieznanych pytań
- Ignorowanie wielkości liter
- Losowe odpowiedzi z puli
- Dopasowanie częściowe (rozumie dłuższe zdania)

### 🚧 Co jeszcze chcę dodać? (To-Do)
- **Etap 1** - ~~Podstawy chatbota~~ ✅ UKOŃCZONE
- **Etap 2** - Rozbudowa bazy wiedzy (więcej intencji)
- **Etap 3** - Uczenie maszynowe (klasyfikacja tekstu)
- **Etap 4** - Interfejs webowy
- **Etap 5** - Rozszerzenia

### 🚀 Jak uruchomić?
1. Sklonuj repozytorium
2. Utwórz środowisko wirtualne:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install nltk scikit-learn numpy
   ```
3. Uruchom
   ```bash
   python chatbot.py
   ```

### 📫 Kontakt
Jeśli masz pytania do kodu albo uwagi (każde Code Review mile widziane!), znaleźć mnie można tutaj:

- **LinkedIn**:
- **Autor**: Kajhol (Student Informatyki, Politechnika Śląska, 3 rok)
*Śledź to repozytorium, żeby zobaczyć postępy!*