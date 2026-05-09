import os
import streamlit as st
from groq import Groq
from pypdf import PdfReader
from dotenv import load_dotenv
import requests
import random
import time

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")
RESEND_KEY = st.secrets.get("RESEND_KEY", "")
FROM_EMAIL = st.secrets.get("FROM_EMAIL", "onboarding@resend.dev")

def send_otp_email(to_email, otp):
    try:
        html = f"""
        <div style="font-family:Inter,sans-serif;max-width:500px;margin:0 auto;padding:2rem;background:#f9fafb;border-radius:16px;">
            <div style="text-align:center;margin-bottom:2rem;">
                <h1 style="background:linear-gradient(135deg,#7c3aed,#2563eb);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:2rem;">✨ Venu AI</h1>
            </div>
            <div style="background:white;border-radius:12px;padding:2rem;box-shadow:0 4px 20px rgba(0,0,0,0.08);">
                <h2 style="color:#111827;margin-bottom:0.5rem;">Your Login Code</h2>
                <p style="color:#6b7280;margin-bottom:1.5rem;">Use this code to sign in to Venu AI. This code expires in 10 minutes.</p>
                <div style="background:linear-gradient(135deg,#7c3aed,#2563eb);border-radius:12px;padding:1.5rem;text-align:center;margin:1.5rem 0;">
                    <span style="color:white;font-size:2.5rem;font-weight:800;letter-spacing:0.5rem;">{otp}</span>
                </div>
                <p style="color:#6b7280;font-size:0.9rem;">If you did not request this code, please ignore this email. Your account is safe.</p>
                <hr style="border:none;border-top:1px solid #e5e7eb;margin:1.5rem 0;">
                <p style="color:#9ca3af;font-size:0.8rem;text-align:center;">This is an automated message from Venu AI. Please do not reply to this email.</p>
                <p style="color:#9ca3af;font-size:0.8rem;text-align:center;">© 2025 Venu AI. All rights reserved.</p>
            </div>
        </div>
        """
        response = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_KEY}", "Content-Type": "application/json"},
            json={"from": f"Venu AI <{FROM_EMAIL}>", "to": [to_email], "subject": "Your Venu AI Login Code", "html": html}
        )
        return response.status_code == 200
    except:
        return False

def save_message(email, role, content):
    try:
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
        requests.post(f"{SUPABASE_URL}/rest/v1/Chat_history", headers=headers, json={"user_email": email, "role": role, "content": content})
    except:
        pass

def load_messages(email):
    try:
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
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
.chat-item { border-radius: 8px; padding: 0.6rem 0.8rem; margin: 0.2rem 0; font-size: 0.85rem; color: #374151 !important; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.section-label { font-size: 0.75rem; font-weight: 600; color: #9ca3af !important; text-transform: uppercase; letter-spacing: 0.05em; padding: 0.5rem 0; }
[data-testid="stChatMessageContent"] { background: #ffffff !important; border: 1px solid #e5e7eb !important; border-radius: 12px !important; color: #111827 !important; box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important; }
.stChatInputContainer textarea { background: #f9fafb !important; border: 1px solid #d1d5db !important; border-radius: 12px !important; color: #111827 !important; }
.stMarkdown p { color: #111827 !important; line-height: 1.7; }
.footer-text { text-align: center; color: #9ca3af; font-size: 0.75rem; padding: 1rem; }
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_guest" not in st.session_state:
    st.session_state.is_guest = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "otp_code" not in st.session_state:
    st.session_state.otp_code = ""
if "otp_email" not in st.session_state:
    st.session_state.otp_email = ""
if "otp_time" not in st.session_state:
    st.session_state.otp_time = 0
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []

if not st.session_state.logged_in and not st.session_state.is_guest:
    st.markdown("""
    <div style="text-align:center;padding:3rem 0 2rem 0;">
        <h1 style="font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,#7c3aed,#2563eb);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">✨ Venu AI</h1>
        <p style="color:#6b7280;font-size:1rem;margin-top:0.5rem;">Your personal AI assistant</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""<div style="background:white;border-radius:16px;padding:2rem;box-shadow:0 4px 20px rgba(0,0,0,0.08);border:1px solid #e5e7eb;">""", unsafe_allow_html=True)

        if not st.session_state.otp_sent:
            st.markdown("<h3 style='text-align:center;color:#111827;'>Sign in to Venu AI</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center;color:#6b7280;font-size:0.9rem;margin-bottom:1rem;'>Enter your email to receive a login code</p>", unsafe_allow_html=True)
            email = st.text_input("Email address", placeholder="you@gmail.com", label_visibility="collapsed")

            if st.button("📧 Send Login Code", use_container_width=True):
                if "@" in email and "." in email:
                    otp = str(random.randint(100000, 999999))
                    if send_otp_email(email, otp):
                        st.session_state.otp_code = otp
                        st.session_state.otp_email = email
                        st.session_state.otp_sent = True
                        st.session_state.otp_time = time.time()
                        st.rerun()
                    else:
                        st.error("Could not send email. Please try again.")
                else:
                    st.error("Please enter a valid email!")

            st.markdown("<div style='text-align:center;color:#9ca3af;padding:0.5rem;'>— or —</div>", unsafe_allow_html=True)

            if st.button("👤 Continue as Guest", use_container_width=True):
                st.session_state.is_guest = True
                st.session_state.user_email = "guest"
                st.rerun()

        else:
            time_left = int(600 - (time.time() - st.session_state.otp_time))
            st.markdown(f"<h3 style='text-align:center;color:#111827;'>Check your email! 📧</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;color:#6b7280;font-size:0.9rem;'>We sent a 6-digit code to<br><strong>{st.session_state.otp_email}</strong></p>", unsafe_allow_html=True)

            if time_left > 0:
                st.markdown(f"<p style='text-align:center;color:#7c3aed;font-size:0.85rem;'>Code expires in {time_left} seconds</p>", unsafe_allow_html=True)
            else:
                st.error("Code expired! Please request a new one.")
                if st.button("🔄 Send New Code", use_container_width=True):
                    st.session_state.otp_sent = False
                    st.rerun()

            otp_input = st.text_input("Enter 6-digit code", placeholder="123456", max_chars=6, label_visibility="collapsed")

            if st.button("✅ Verify Code", use_container_width=True):
                if time_left <= 0:
                    st.error("Code expired! Please request a new one.")
                elif otp_input == st.session_state.otp_code:
                    st.session_state.logged_in = True
                    st.session_state.user_email = st.session_state.otp_email
                    st.session_state.messages = load_messages(st.session_state.otp_email)
                    st.session_state.otp_sent = False
                    st.success("✅ Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Wrong code! Please try again.")

            if st.button("← Back", use_container_width=True):
                st.session_state.otp_sent = False
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#9ca3af;font-size:0.8rem;margin-top:1rem;'>🔒 Secure login — no password needed</p>", unsafe_allow_html=True)

else:
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">✨ Venu AI</div>', unsafe_allow_html=True)
        if st.session_state.is_guest:
            st.markdown('<p style="color:#6b7280;font-size:0.85rem;">👤 Guest User</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p style="color:#6b7280;font-size:0.85rem;">👤 {st.session_state.user_email}</p>', unsafe_allow_html=True)

        if st.button("✏️ New Chat", use_container_width=True):
            if st.session_state.messages:
                first_msg = st.session_state.messages[0]["content"][:45] + "..."
                st.session_state.chat_sessions.append(first_msg)
            st.session_state.messages = []
            st.session_state.pdf_text = ""
            st.rerun()

        if st.button("🚪 Sign Out", use_container_width=True):
            for key in ["logged_in", "is_guest", "user_email", "otp_sent", "otp_code", "messages"]:
                if key in st.session_state:
                    del st.session_state[key]
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
        name = "Guest" if st.session_state.get("is_guest") else st.session_state.user_email.split("@")[0].capitalize()
        st.markdown(f"""
        <div style="text-align:center;padding:3rem 0 1rem 0;">
            <h1 style="font-size:2rem;font-weight:700;color:#111827;">Hello, {name}! 👋</h1>
            <p style="color:#6b7280;">Ask me anything — in any language!</p>
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
        if not st.session_state.get("is_guest"):
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
                if not st.session_state.get("is_guest"):
                    save_message(st.session_state.user_email, "assistant", reply)
