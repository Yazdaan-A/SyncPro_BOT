# SyncPro_BOT 🤖

**SyncPro_BOT** is an advanced, multi-language AI chatbot app built with Streamlit and Google Gemini/Gemma APIs. It offers persistent chat history (PostgreSQL), model switching, a modern user interface, dark/light themes, and is ready for deployment on Streamlit Cloud and Docker.

---

## 🚀 Features

- **Conversational AI:** Ask questions in natural language, powered by Google Gemini/Gemma LLMs
- **Switch Models:** Choose between Gemini and Gemma AI models in-app
- **Auto Language Detection:** Chat in any language, auto-detects and translates responses
- **Persistent Chat History:** All chats are saved in PostgreSQL for analytics and retrieval
- **Download Chat:** Export chat session as a text file
- **Modern UI:** Responsive, chat-style interface with avatars and theme toggle (dark/light)
- **Deploy Anywhere:** Works locally, on Streamlit Cloud, or via Docker

---

## 📂 Project Structure
   SyncPro_BOT/
├── main.py # Main Streamlit app
├── requirements.txt # Python dependencies
├── runtime.txt # Python version for Streamlit Cloud (e.g., python-3.10)
├── README.md # This file

---

## 🛠️ Prerequisites

- Python 3.10+
- Gemini or Gemma API key (from [Google AI Studio](https://aistudio.google.com/app/apikey))
- PostgreSQL database (e.g., [Supabase](https://supabase.com/))

---

## 🔑 Setup: API Keys & Database

1. **Local:**  
   Create a `.env` file:
GOOGLE_API_KEY=your-gemini-or-gemma-api-key
DATABASE_URL=postgresql://username:password@host:port/dbname


2. **Streamlit Cloud:**  
Go to **App settings → Secrets** and add:

GOOGLE_API_KEY="your-gemini-or-gemma-api-key"
DATABASE_URL="your-database-url"

---

## ⚡ Installation & Running Locally

```bash
pip install -r requirements.txt
streamlit run main.py

##☁️ Deploying to Streamlit Cloud
Push your code to GitHub

Create app on Streamlit Cloud

Set secrets for GOOGLE_API_KEY and DATABASE_URL

Set main file path to main.py

(Optional) Add runtime.txt with python-3.10 to force Python version


