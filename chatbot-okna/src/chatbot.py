import json
import random
import os

# Ustalanie poprawnej ścieżki (to musi zostać, żeby widział plik)
katalog_skryptu = os.path.dirname(os.path.abspath(__file__))
sciezka_pliku = os.path.join(katalog_skryptu, '..', 'data', 'intents.json')

# Wczytywanie danych bez sprawdzania błędów
with open(sciezka_pliku, "r", encoding="utf-8") as plik:
    dane = json.load(plik)

intencje = dane["intents"]

print("Bot: Witaj! Napisz 'quit' aby zakończyć.")

# Pętla rozmowy
while True:
    tekst_uzytkownika = input("Ty: ")
    tekst_uzytkownika = tekst_uzytkownika.lower()
    
    if tekst_uzytkownika == "quit":
        print("Bot: Do widzenia!")
        break
    
    znaleziono = False
    
    for intencja in intencje:
        for wzorzec in intencja["patterns"]:
            # Dodano .lower() do wzorca dla pewności
            if wzorzec.lower() in tekst_uzytkownika:
                odpowiedz = random.choice(intencja["responses"])
                print("Bot:", odpowiedz)
                znaleziono = True
                break
        if znaleziono:
            break
    
    if not znaleziono:
        print("Bot: Przepraszam, nie rozumiem. Spróbuj inaczej.")