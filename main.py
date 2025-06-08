import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from googletrans import Translator
import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# --- PAGE CONFIG MUST BE FIRST ---
st.set_page_config(
    page_title="SyncPro_BOT Gemini",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- Theme toggle ---
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "light"
toggle = st.toggle("🌗 Toggle Dark/Light Theme", value=(st.session_state.theme_mode == "dark"))
st.session_state.theme_mode = "dark" if toggle else "light"
if st.session_state.theme_mode == "dark":
    chat_user_bg = "#23272f"
    chat_bot_bg = "#343942"
    text_color = "#eee"
    page_bg = "#181920"
else:
    chat_user_bg = "#DCF8C6"
    chat_bot_bg = "#F1F0F0"
    text_color = "#222"
    page_bg = "#E6F1FF"
st.markdown(f"""
    <style>
    body {{
        background-color: {page_bg} !important;
        color: {text_color} !important;
    }}
    .user-msg {{
        background: {chat_user_bg};
        padding: 12px 16px;
        border-radius: 16px;
        margin-bottom: 6px;
        display: inline-block;
        color: {text_color};
        max-width: 75%;
    }}
    .bot-msg {{
        background: {chat_bot_bg};
        padding: 12px 16px;
        border-radius: 16px;
        margin-bottom: 6px;
        display: inline-block;
        color: {text_color};
        max-width: 75%;
    }}
    .avatar {{
        font-size: 1.7em;
        vertical-align: middle;
        margin-right: 7px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- Load environment variables ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

st.title("🤖 SyncPro_BOT (Gemini & Gemma Multi-Model Chatbot)")

# --- Model Selection Dropdown ---
model_options = {
    "Gemma 12B Instruct": "models/gemma-3-12b-it",
    "Gemini 1.5 Flash": "models/gemini-1.5-flash",
    "Gemini 1.5 Pro": "models/gemini-1.5-pro",
    "Gemini 2.5 Pro Preview": "models/gemini-2.5-pro-preview-06-05",
}
selected_label = st.selectbox(
    "Select Model",
    options=list(model_options.keys()),
    index=0
)
selected_model = model_options[selected_label]

translator = Translator()

# --- SQLAlchemy Setup ---
Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True)
    user = Column(String(64), default="default_user")
    question = Column(Text)
    answer = Column(Text)
    model = Column(String(128))
    lang = Column(String(16))
    timestamp = Column(DateTime, default=datetime.utcnow)

# Connect to DB
@st.cache_resource
def get_engine_and_session():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, Session

engine, Session = get_engine_and_session()
db_session = Session()

# --- Load chat history from DB to session_state ---
if "chat_history" not in st.session_state:
    chats = db_session.query(ChatHistory).order_by(ChatHistory.timestamp).all()
    st.session_state.chat_history = [
        (c.question, c.answer, c.model, c.lang) for c in chats
    ]

user_query = st.text_input("Type your message (any language)...")

# --- Chat Send/Clear/Export Buttons ---
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    send = st.button("Send", use_container_width=True)
with col2:
    clear = st.button("Clear Chat", use_container_width=True)
with col3:
    export = st.button("Export Chat", use_container_width=True)

if send:
    if not GOOGLE_API_KEY:
        st.error("Google API Key not found. Please set GOOGLE_API_KEY in your .env file.")
    elif not user_query:
        st.warning("Please enter your message above.")
    else:
        try:
            try:
                detected = translator.detect(user_query)
                detected_lang = detected.lang if detected.lang else "en"
            except Exception:
                detected_lang = "en"

            if detected_lang != "en":
                try:
                    query_en = translator.translate(user_query, dest='en').text or user_query
                except Exception:
                    query_en = user_query
            else:
                query_en = user_query

            genai.configure(api_key=GOOGLE_API_KEY)
            model = genai.GenerativeModel(selected_model)
            response = model.generate_content(query_en)
            answer_en = response.text if response.text else ""

            if detected_lang != "en":
                try:
                    answer = translator.translate(answer_en, dest=detected_lang).text or answer_en
                except Exception:
                    answer = answer_en
            else:
                answer = answer_en

            question_str = str(user_query)
            answer_str = str(answer)
            modelname_str = str(selected_label)
            lang_str = str(detected_lang)

            # Save to session history and DB
            st.session_state.chat_history.append(
                (question_str, answer_str, modelname_str, lang_str)
            )
            chat_row = ChatHistory(
                user="default_user",
                question=question_str,
                answer=answer_str,
                model=modelname_str,
                lang=lang_str,
            )
            db_session.add(chat_row)
            db_session.commit()

        except Exception as e:
            st.error(f"Error: {e}")

if clear:
    st.session_state.chat_history = []
    db_session.query(ChatHistory).delete()
    db_session.commit()

# --- Export/Download Chat ---
if export:
    if not st.session_state.chat_history:
        st.warning("No chat to export!")
    else:
        chat_lines = []
        for idx, (question, answer, modelname, lang) in enumerate(st.session_state.chat_history, 1):
            chat_lines.append(f"Q{idx} (lang: {lang}): {question}\nA{idx} ({modelname}): {answer}\n")
        chat_text = "\n".join(chat_lines)
        st.download_button(
            label="Download Chat as TXT",
            data=chat_text,
            file_name="chat_history.txt",
            mime="text/plain"
        )

st.markdown("---")
st.subheader(f"Chat (Auto language detection)")
if st.session_state.chat_history:
    for question, answer, modelname, lang in st.session_state.chat_history:
        st.markdown(
            f'<div class="avatar">👤</div><span class="user-msg">{question} <sub style="font-size:0.8em; color:#888;">[{lang}]</sub></span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="avatar">🤖</div><span class="bot-msg"><b>{modelname}:</b><br>{answer}</span>',
            unsafe_allow_html=True,
        )
        st.markdown("")  # space
else:
    st.info("No chat yet. Type your first message above!")
