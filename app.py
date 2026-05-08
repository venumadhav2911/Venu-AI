import os
import streamlit as st
from groq import Groq
from pypdf import PdfReader
from dotenv import load_dotenv
import requests
import time
import random

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def web_search(query):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()
        results = []
        if data.get("AbstractText"):
            results.append(data["AbstractText"])
        for topic in data.get("RelatedTopics", [])[:3]:
            if isinstance(topic, dict) and topic.get("Text"):
                results.append(topic["Text"])
        if results:
            return "\n".join(results)
    except:
        pass
    return ""

def get_summary(messages):
    if len(messages) < 6:
        return ""
    parts = []
    for msg in messages[:-6]:
        role = "User" if msg["role"] == "user" else "Venu AI"
        parts.append(f"{role}: {msg['content'][:150]}")
    return "Earlier conversation:\n" + "\n".join(parts)

st.set_page_config(page_title="Venu AI", page_icon="✨", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 40%, #0a0e1a 70%, #0f0a1a 100%);
    min-height: 100vh;
}

#stars-container {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}

.star {
    position: absolute;
    background: white;
    border-radius: 50%;
    animation: twinkle linear infinite;
}

@keyframes twinkle {
    0% { opacity: 0; transform: scale(0.5); }
    50% { opacity: 1; transform: scale(1.2); }
    100% { opacity: 0; transform: scale(0.5); }
}

@keyframes sparkle {
    0% { opacity: 0; transform: scale(0) rotate(0deg); }
    50% { opacity: 1; transform: scale(1) rotate(180deg); }
    100% { opacity: 0; transform: scale(0) rotate(360deg); }
}

.sparkle {
    position: absolute;
    width: 6px;
    height: 6px;
    background: linear-gradient(45deg, #a78bfa, #60a5fa);
    clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%);
    animation: sparkle linear infinite;
}

.main-header {
    text-align: center;
    padding: 2rem 0 1rem 0;
    position: relative;
    z-index: 10;
}

.main-header h1 {
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #ffffff 0%, #a78bfa 40%, #60a5fa 70%, #34d399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
}

.main-header p {
    color: #6b7280;
    font-size: 0.95rem;
    margin-top: 0.5rem;
}

section[data-testid="stSidebar"] {
    background: rgba(13, 17, 23, 0.95) !important;
    border-right: 1px solid rgba(139, 92, 246, 0.2) !important;
}

section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

.sidebar-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #a78bfa !important;
    padding: 1rem 0 0.5rem 0;
    border-bottom: 1px solid rgba(139, 92, 246, 0.2);
    margin-bottom: 1rem;
}

.chat-item {
    background: rgba(139, 92, 246, 0.1);
    border: 1px solid rgba(139, 92, 246, 0.2);
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    margin: 0.3rem 0;
    cursor: pointer;
    font-size: 0.85rem;
    color: #d1d5db !important;
    transition: all 0.2s;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.chat-item:hover {
    background: rgba(139, 92, 246, 0.2);
    border-color: rgba(139, 92, 246, 0.4);
}

.stChatMessage {
    background: transparent !important;
    border: none !important;
    padding: 0.5rem 0 !important;
}

[data-testid="stChatMessageContent"] {
    background: rgba(17, 24, 39, 0.8) !important;
    border: 1px solid rgba(75, 85, 99, 0.3) !important;
    border-radius: 12px !important;
    padding: 1rem 1.2rem !important;
    color: #f3f4f6 !important;
    backdrop-filter: blur(10px);
}

[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(96, 165, 250, 0.2)) !important;
    border-color: rgba(139, 92, 246, 0.3) !important;
}

.stChatInputContainer {
    background: rgba(13, 17, 23, 0.9) !important;
    border-top: 1px solid rgba(139, 92, 246, 0.2) !important;
    padding: 1rem !important;
    backdrop-filter: blur(20px);
}

.stChatInputContainer textarea {
    background: rgba(31, 41, 55, 0.8) !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    border-radius: 12px !important;
    color: #f3f4f6 !important;
    font-size: 0.95rem !important;
}

.stChatInputContainer textarea:focus {
    border-color: rgba(139, 92, 246, 0.6) !important;
    box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.1) !important;
}

.stFileUploader {
    background: rgba(17, 24, 39, 0.6) !important;
    border: 1px dashed rgba(139, 92, 246, 0.3) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}

.stSuccess {
    background: rgba(16, 185, 129, 0.1) !important;
    border: 1px solid rgba(16, 185, 129, 0.3) !important;
    border-radius: 8px !important;
    color: #34d399 !important;
}

.stInfo {
    background: rgba(96, 165, 250, 0.1) !important;
    border: 1px solid rgba(96, 165, 250, 0.3) !important;
    border-radius: 8px !important;
    color: #60a5fa !important;
}

.new-chat-btn {
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    color: white !important;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    width: 100%;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    margin-bottom: 1rem;
    text-align: center;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(139, 92, 246, 0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(139, 92, 246, 0.5); }

.stMarkdown p { color: #e5e7eb !important; line-height: 1.7; }
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #f9fafb !important; }
.stMarkdown code { background: rgba(139, 92, 246, 0.15) !important; color: #a78bfa !important; border-radius: 4px; padding: 2px 6px; }
.stMarkdown pre { background: rgba(17, 24, 39, 0.9) !important; border: 1px solid rgba(139, 92, 246, 0.2) !important; border-radius: 8px !important; }
</style>

<div id="stars-container"></div>
<script>
const container = document.getElementById('stars-container');
if (container) {
    for (let i = 0; i < 150; i++) {
        const star = document.createElement('div');
        const size = Math.random() * 3 + 1;
        star.className = 'star';
        star.style.cssText = 
            width: px; height: px;
            left: %;
            top: %;
            animation-duration: s;
            animation-delay: s;
        ;
        container.appendChild(star);
    }
    for (let i = 0; i < 20; i++) {
        const sparkle = document.createElement('div');
        sparkle.className = 'sparkle';
        sparkle.style.cssText = 
            left: %;
            top: %;
            animation-duration: s;
            animation-delay: s;
        ;
        container.appendChild(sparkle);
    }
}
</script>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []

with st.sidebar:
    st.markdown('<div class="sidebar-title">✨ Venu AI</div>', unsafe_allow_html=True)
    if st.button("+ New Chat", use_container_width=True):
        if st.session_state.messages:
            first_msg = st.session_state.messages[0]["content"][:40] + "..."
            st.session_state.chat_sessions.append(first_msg)
        st.session_state.messages = []
        st.session_state.pdf_text = ""
        st.rerun()
    if st.session_state.chat_sessions:
        st.markdown("**Recent Chats**")
        for i, session in enumerate(reversed(st.session_state.chat_sessions[-10:])):
            st.markdown(f'<div class="chat-item">💬 {session}</div>', unsafe_allow_html=True)
    st.markdown("---")
    uploaded_file = st.file_uploader("📄 Upload PDF", type="pdf")
    if uploaded_file:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted
        st.session_state.pdf_text = text
        st.success("✅ PDF loaded!")
    if st.session_state.pdf_text:
        st.info("📄 Document ready!")
    st.markdown("---")
    st.markdown('<p style="color: #4b5563; font-size: 0.8rem; text-align: center;">Venu AI v2.0<br>Powered by Llama 3.3</p>', unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>✨ Venu AI</h1>
    <p>Your personal AI assistant — ask me anything!</p>
</div>
""", unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything, in any language..."):
    with st.spinner("🔍 Searching..."):
        web_context = web_search(prompt)

    for trigger in ["my name is", "i am", "call me", "nenu"]:
        if trigger in prompt.lower():
            words = prompt.lower().replace(trigger, "").strip().split()
            if words:
                st.session_state.user_name = words[0].capitalize()

    summary = get_summary(st.session_state.messages)
    doc_context = "User document:\n" + st.session_state.pdf_text[:5000] if st.session_state.pdf_text else ""
    user_context = f"User's name is {st.session_state.user_name}." if st.session_state.user_name else ""

    system = """You are Venu AI — a brilliant, warm and honest AI assistant.

CRITICAL FACTS:
- Current year is 2025
- Donald Trump is the US President since January 2025
- Use web search results for ALL current events
- NEVER make up facts or current data
- If no web results — say honestly you could not find live data

MEMORY:
- Remember everything from this conversation
- Remember user name, interests and preferences
- Connect earlier conversation naturally

LANGUAGE:
- Understand ANY language including Telugu and Hindi
- Understand broken English and misspelled words
- Reply in same language as user

STYLE:
- 2 to 3 sentences by default
- No bullet points unless asked
- Warm, human, conversational
- Never robotic or textbook style

""" + user_context + "\n" + summary + "\n" + doc_context + "\n" + ("Web results:\n" + web_context if web_context else "")

    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("💭 Thinking..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system},
                    *st.session_state.messages[-20:]
                ]
            )
            reply = response.choices[0].message.content
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
