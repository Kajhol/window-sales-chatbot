# 🏠 Window Sales Chatbot
![Status](https://img.shields.io/badge/Status-In%20Progress-red)
![Version](https://img.shields.io/badge/Version-1.3-blue)

👋 A chatbot for window/door sales industry. It handles initial customer contact before they reach a salesperson.

### 💡 Why this project?
I want to help salespeople in window industry by:
1. **24/7** availability for customers
2. Reducing workload of sales staff
3. Automating measurement appointments

---

### ⚙️ Tech Stack
- **Python 3.12.9**
- **NLTK** - natural language processing
- **scikit-learn** - machine learning
- **NumPy** - calculations
- **HTML/CSS/JS** - frontend interface 

### 🛠️ What works?
### Stage 1 - Basic Chatbot (COMPLETED)
- Python environment setup
- intents.json with 6 categories
- Console version (chatbot.py)

### Stage 2 - REST API (COMPLETED)
- FastAPI integration
- JSON request/response format
- CORS enabled for frontend

### Stage 3 - Frontend (COMPLETED)
- HTML chat interface
- JavaScript API integration
- Real-time bot responses

### 🚧 To-Do
- **Stage 4** - OpenAI API integration
- **Stage 5** - RAG (knowledge base)
- **Stage 5** - Extensions (company data, deployment to cloud)

### 🚀 How to run?
1. Clone repository
   ```bash
   git clone https://github.com/Kajhol/chatbot-okna.git
   cd chatbot-okna
   ```
3. Create and activate virtual environment:
   ```bash
   python -m venv venv
   ```
   For windows:
   ```bash
   venv\Scripts\activate.bat
   ```
4. Install dependencies
   ```bash
   pip install fastapi uvicorn python-multipart nltk scikit-learn numpy
   ```
5. Run API server
   ```bash
   cd chatbot-okna/src
   uvicorn api:app --reload
   ```
6. Open in browser index.html:  
   chatbot-okna/chatbot-okna/frontend/index.html

### 📫 Contact
Questions or code review? Find me here:

- LinkedIn: https://www.linkedin.com/in/kajetan-hołdan-9b4a503a0/
- Author: Kajhol (Computer Science Student, Silesian University of Technology, 3rd year)
  
---

  *Star this repo to follow progress!*
