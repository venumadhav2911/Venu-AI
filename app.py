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

st.set_page_config(page_title="Venu AI", page_icon="✨")
st.title("✨ Venu AI")
st.caption("Ask me anything — I search the web for you!")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

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

if prompt := st.chat_input("Ask me anything..."):
    with st.spinner("🔍 Searching web..."):
        web_context = web_search(prompt)

    if st.session_state.pdf_text:
        doc_context = "User document:\n" + st.session_state.pdf_text[:6000]
    else:
        doc_context = ""

    system = """You are Venu AI — a brilliant, honest and warm AI assistant.

CRITICAL RULES — FOLLOW STRICTLY:
- NEVER make up facts, scores, numbers, names or events
- NEVER guess or assume anything current
- If web search gave results — use ONLY those results to answer
- If web search gave no results — say honestly "I searched but could not find current data on that. Please check Google for the latest."
- Do NOT pretend to search if you have no results
- Do NOT make up election results, sports scores or news

ANDHRA PRADESH 2024 ELECTIONS — IMPORTANT FACT:
- The 2024 AP elections were held in May 2024
- TDP alliance (NDA) won — N Chandrababu Naidu became Chief Minister
- YSRCP lost badly after winning in 2019

YOUR STYLE:
- Warm, friendly and human like a best friend
- Understand any language including Telugu and Hindi
- Understand broken English and casual typing
- Reply in same language as user
- Short clear answers — no bullet points unless asked
- Never sound robotic

""" + doc_context + "\n" + ("Web search found:\n" + web_context if web_context else "Web search returned no results for this query.")

    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("💭 Thinking..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system},
                    *st.session_state.messages[-10:]
                ]
            )
            reply = response.choices[0].message.content
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
