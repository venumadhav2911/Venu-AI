import os
import streamlit as st
from groq import Groq
from pypdf import PdfReader
from dotenv import load_dotenv
import requests

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

* { font-family: 'Inter', sans-serif; }

.stApp {
    background: #f9fafb;
}

section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e5e7eb !important;
}

section[data-testid="stSidebar"] * {
    color: #111827 !important;
}

.sidebar-logo {
    font-size: 1.3rem;
    font-weight: 700;
    color: #7c3aed !important;
    padding: 1rem 0 1.5rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.new-chat-btn {
    background: #7c3aed;
    color: white !important;
    border: none;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    width: 100%;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    margin-bottom: 1.5rem;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}

.chat-item {
    background: transparent;
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    margin: 0.2rem 0;
    cursor: pointer;
    font-size: 0.85rem;
    color: #374151 !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: background 0.2s;
}

.chat-item:hover {
    background: #f3f4f6;
}

.section-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: #9ca3af !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 0.5rem 0;
    margin-top: 0.5rem;
}

.main-header {
    text-align: center;
    padding: 3rem 0 1rem 0;
}

.main-header h1 {
    font-size: 2rem;
    font-weight: 700;
    color: #111827;
}

.main-header h1 span {
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.main-header p {
    color: #6b7280;
    font-size: 0.95rem;
    margin-top: 0.5rem;
}

.stChatMessage {
    background: transparent !important;
    border: none !important;
    max-width: 800px;
    margin: 0 auto;
}

[data-testid="stChatMessageContent"] {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
    color: #111827 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
}

.stChatInputContainer {
    background: #ffffff !important;
    border-top: 1px solid #e5e7eb !important;
    max-width: 800px;
    margin: 0 auto;
}

.stChatInputContainer textarea {
    background: #f9fafb !important;
    border: 1px solid #d1d5db !important;
    border-radius: 12px !important;
    color: #111827 !important;
    font-size: 0.95rem !important;
}

.stChatInputContainer textarea:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1) !important;
}

.stFileUploader {
    background: #f9fafb !important;
    border: 1px dashed #d1d5db !important;
    border-radius: 12px !important;
}

.stSuccess {
    background: #f0fdf4 !important;
    border: 1px solid #86efac !important;
    border-radius: 8px !important;
    color: #166534 !important;
}

.stInfo {
    background: #eff6ff !important;
    border: 1px solid #93c5fd !important;
    border-radius: 8px !important;
    color: #1e40af !important;
}

.stMarkdown p { color: #111827 !important; line-height: 1.7; }
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #111827 !important; }
.stMarkdown code { background: #f3f4f6 !important; color: #7c3aed !important; border-radius: 4px; padding: 2px 6px; }
.stMarkdown pre { background: #1f2937 !important; border-radius: 8px !important; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f9fafb; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #9ca3af; }

.footer-text {
    text-align: center;
    color: #9ca3af;
    font-size: 0.75rem;
    padding: 1rem;
}
</style>
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
    st.markdown('<div class="sidebar-logo">✨ Venu AI</div>', unsafe_allow_html=True)

    if st.button("✏️ New Chat", use_container_width=True):
        if st.session_state.messages:
            first_msg = st.session_state.messages[0]["content"][:45] + "..."
            st.session_state.chat_sessions.append(first_msg)
        st.session_state.messages = []
        st.session_state.pdf_text = ""
        st.rerun()

    if st.session_state.chat_sessions:
        st.markdown('<div class="section-label">Recent</div>', unsafe_allow_html=True)
        for session in reversed(st.session_state.chat_sessions[-10:]):
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

    st.markdown('<div class="footer-text">Venu AI v2.0<br>Powered by Llama 3.3</div>', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="main-header">
        <h1>Welcome to <span>Venu AI</span></h1>
        <p>Your personal AI assistant — ask me anything, in any language!</p>
    </div>
    """, unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Message Venu AI..."):
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

CRITICAL RULES:
- NEVER ramble or repeat yourself
- Give ONE clear direct answer — no going back and forth
- If you are not sure — say so in ONE sentence and stop
- Current year is 2025, Donald Trump is US President
- NEVER make up current facts, scores or events
- Use web search results for current data only

ANSWER STYLE:
- 2 to 3 sentences MAX by default
- Only go longer if user asks for detail
- No bullet points unless asked
- Warm, human, conversational tone
- Never repeat the same point twice
- Be confident and direct

MEMORY:
- Remember everything from this conversation
- Use user name naturally if known
- Connect earlier conversation naturally

LANGUAGE:
- Any language including Telugu and Hindi
- Understand broken English and casual typing
- Reply in same language as user

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
