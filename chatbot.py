import json
import random

# Wczytaj dane
plik = open("data/intents.json", "r", encoding="utf-8")
dane = json.load(plik)
plik.close()

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
            if wzorzec in tekst_uzytkownika:
                odpowiedz = random.choice(intencja["responses"])
                print("Bot:", odpowiedz)
                znaleziono = True
                break
        if znaleziono:
            break
    
    if not znaleziono:
        print("Bot: Przepraszam, nie rozumiem. Spróbuj inaczej.")