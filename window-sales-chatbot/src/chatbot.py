import json
import random
import os

# Set correct path to intents file
script_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_directory, '..', 'data', 'intents.json')

# Load data
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

intents = data["intents"]

print("Bot: Witaj! Wpisz 'quit' aby zakończyć.")

# Conversation loop
while True:
    user_text = input("Ty: ")
    user_text = user_text.lower()
    
    if user_text == "quit":
        print("Bot: Do widzenia!")
        break
    
    found = False
    
    for intent in intents:
        for pattern in intent["patterns"]:
            if pattern.lower() in user_text:
                response = random.choice(intent["responses"])
                print("Bot:", response)
                found = True
                break
        if found:
            break
    
    if not found:
        print("Bot: Przepraszam, nie rozumiem. Spróbuj inaczej.")