import os
import streamlit as st
from groq import Groq
from pypdf import PdfReader
from dotenv import load_dotenv
import requests
import json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

def save_message(email, role, content):
    try:
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        data = {"user_email": email, "role": role, "content": content}
        requests.post(f"{SUPABASE_URL}/rest/v1/Chat_history", headers=headers, json=data)
    except:
        pass

def load_messages(email):
    try:
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        r = requests.get(f"{SUPABASE_URL}/rest/v1/Chat_history?user_email=eq.{email}&order=created_at.asc&limit=50", headers=headers)
        rows = r.json()
        return [{"role": row["role"], "content": row["content"]} for row in rows]
    except:
        return []

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
.stApp { background: #f9fafb; }
section[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e5e7eb !important; }
section[data-testid="stSidebar"] * { color: #111827 !important; }
.sidebar-logo { font-size: 1.3rem; font-weight: 700; color: #7c3aed !important; padding: 1rem 0 1.5rem 0; }
.chat-item { background: transparent; border-radius: 8px; padding: 0.6rem 0.8rem; margin: 0.2rem 0; font-size: 0.85rem; color: #374151 !important; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.chat-item:hover { background: #f3f4f6; }
.section-label { font-size: 0.75rem; font-weight: 600; color: #9ca3af !important; text-transform: uppercase; letter-spacing: 0.05em; padding: 0.5rem 0; }
.main-header { text-align: center; padding: 3rem 0 1rem 0; }
.main-header h1 { font-size: 2rem; font-weight: 700; color: #111827; }
.main-header h1 span { background: linear-gradient(135deg, #7c3aed, #2563eb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.main-header p { color: #6b7280; font-size: 0.95rem; margin-top: 0.5rem; }
[data-testid="stChatMessageContent"] { background: #ffffff !important; border: 1px solid #e5e7eb !important; border-radius: 12px !important; color: #111827 !important; box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important; }
.stChatInputContainer textarea { background: #f9fafb !important; border: 1px solid #d1d5db !important; border-radius: 12px !important; color: #111827 !important; }
.stChatInputContainer textarea:focus { border-color: #7c3aed !important; }
.stMarkdown p { color: #111827 !important; line-height: 1.7; }
.footer-text { text-align: center; color: #9ca3af; font-size: 0.75rem; padding: 1rem; }
.login-box { background: white; border-radius: 16px; padding: 2rem; max-width: 400px; margin: 3rem auto; box-shadow: 0 4px 20px rgba(0,0,0,0.08); border: 1px solid #e5e7eb; text-align: center; }
.login-title { font-size: 1.5rem; font-weight: 700; color: #111827; margin-bottom: 0.5rem; }
.login-sub { color: #6b7280; font-size: 0.9rem; margin-bottom: 1.5rem; }
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []

if not st.session_state.logged_in:
    st.markdown("""
    <div class="main-header">
        <h1>Welcome to <span>Venu AI</span></h1>
        <p>Your personal AI assistant</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("### Sign in to continue")
        email = st.text_input("Enter your email address", placeholder="you@example.com")
        if st.button("Continue with Email", use_container_width=True):
            if "@" in email and "." in email:
                st.session_state.user_email = email
                st.session_state.logged_in = True
                st.session_state.messages = load_messages(email)
                st.rerun()
            else:
                st.error("Please enter a valid email address")
        st.markdown('<p style="text-align:center; color:#9ca3af; font-size:0.8rem; margin-top:1rem;">No password needed — just your email!</p>', unsafe_allow_html=True)
else:
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">✨ Venu AI</div>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#6b7280; font-size:0.85rem;">👤 {st.session_state.user_email}</p>', unsafe_allow_html=True)

        if st.button("✏️ New Chat", use_container_width=True):
            if st.session_state.messages:
                first_msg = st.session_state.messages[0]["content"][:45] + "..."
                st.session_state.chat_sessions.append(first_msg)
            st.session_state.messages = []
            st.session_state.pdf_text = ""
            st.rerun()

        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.messages = []
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
            <h1>Hello! I am <span>Venu AI</span></h1>
            <p>Ask me anything — in any language!</p>
        </div>
        """, unsafe_allow_html=True)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Message Venu AI..."):
        with st.spinner("🔍 Searching..."):
            web_context = web_search(prompt)

        summary = get_summary(st.session_state.messages)
        doc_context = "User document:\n" + st.session_state.pdf_text[:5000] if st.session_state.pdf_text else ""

        system = """You are Venu AI — a brilliant, warm and honest AI assistant.
CRITICAL RULES:
- NEVER ramble or repeat yourself
- Give ONE clear direct answer
- Current year is 2025, Donald Trump is US President since January 2025
- NEVER make up current facts, scores or events
- Use web search results for current data only
- If no web results say honestly you could not find live data

STYLE:
- 2 to 3 sentences MAX by default
- No bullet points unless asked
- Warm human conversational tone
- Understand any language including Telugu and Hindi
- Reply in same language as user

""" + summary + "\n" + doc_context + "\n" + ("Web results:\n" + web_context if web_context else "")

        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_message(st.session_state.user_email, "user", prompt)

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
                save_message(st.session_state.user_email, "assistant", reply)
