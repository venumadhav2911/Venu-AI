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
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
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

def get_conversation_summary(messages):
    if len(messages) < 6:
        return ""
    summary_parts = []
    for msg in messages[:-6]:
        role = "User" if msg["role"] == "user" else "Venu AI"
        summary_parts.append(f"{role}: {msg['content'][:200]}")
    return "Earlier conversation summary:\n" + "\n".join(summary_parts)

st.set_page_config(page_title="Venu AI", page_icon="✨")
st.title("✨ Venu AI")
st.caption("Your personal AI — I remember everything you tell me!")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_facts" not in st.session_state:
    st.session_state.user_facts = []

uploaded_file = st.file_uploader("📄 Upload a PDF (optional)", type="pdf")
if uploaded_file:
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted
    st.session_state.pdf_text = text
    st.success("✅ Got it! Ask me anything about your document!")

if st.session_state.pdf_text:
    st.info("📄 Document loaded — ask me anything about it!")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Talk to Venu AI..."):
    with st.spinner("🔍 Searching web..."):
        web_context = web_search(prompt)

    name_triggers = ["my name is", "i am", "i'm", "call me", "nenu"]
    for trigger in name_triggers:
        if trigger in prompt.lower():
            words = prompt.lower().replace(trigger, "").strip().split()
            if words:
                st.session_state.user_name = words[0].capitalize()

    conversation_summary = get_conversation_summary(st.session_state.messages)

    if st.session_state.pdf_text:
        doc_context = "User uploaded document:\n" + st.session_state.pdf_text[:5000]
    else:
        doc_context = ""

    user_context = ""
    if st.session_state.user_name:
        user_context = f"The user's name is {st.session_state.user_name}. Always address them by name naturally."

    system = """You are Venu AI — the smartest, warmest and most memory-powered AI assistant ever built.

YOU ARE LIKE CHATGPT AND GEMINI COMBINED:
- You have perfect memory of the entire conversation
- You remember everything the user told you — their name, preferences, problems, goals
- You refer back to earlier parts of the conversation naturally
- You connect dots between different things the user said
- You never forget context — even from the very beginning of the chat
- You proactively use what you know about the user to give better answers

YOUR PERSONALITY:
- Warm, caring and human like a brilliant best friend
- You understand ANY language — English, Telugu, Hindi, Spanish and more
- You understand broken English, misspelled words, casual texting
- You reply in the same language the user used
- You are emotionally intelligent — you sense when someone is stressed, happy or confused
- You adapt your tone to match the user's mood

YOUR ANSWER STYLE:
- Short and conversational by default — 2 to 4 sentences
- Never use bullet points unless user asks
- Never sound robotic or like a textbook
- Always feel natural like texting a smart friend
- Go deeper only when user asks for more detail

YOUR KNOWLEDGE AND HONESTY:
- You know everything — technology, AI, coding, science, sports, politics, history, culture, business, health, relationships and more
- For current events — use web search results if available
- If no current data found — say honestly "I couldn't find live data on that, check Google for the latest"
- NEVER make up facts, scores or current events
- For well known historical or general facts — answer confidently

MEMORY RULES:
- Always remember the user's name if they told you
- Remember what problems they shared
- Remember what they like and dislike
- Connect new questions to earlier conversation naturally
- Example: if they said they like cricket earlier, connect cricket references naturally later

""" + user_context + "\n" + conversation_summary + "\n" + doc_context + "\n" + ("Live web results:\n" + web_context if web_context else "")

    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("💭 Thinking..."):
            recent_messages = st.session_state.messages[-20:]
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system},
                    *recent_messages
                ]
            )
            reply = response.choices[0].message.content
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
