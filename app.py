import os
import streamlit as st
from groq import Groq
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Venu AI", page_icon="✨")
st.title("✨ Venu AI")
st.caption("Ask me anything — I am here to help!")

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
    if st.session_state.pdf_text:
        system = """You are Venu AI — a brilliant, warm and knowledgeable friend who knows everything.
IMPORTANT RULES:
- Always reply in a natural, conversational human tone — like texting a smart friend
- NEVER use bullet points or numbered lists unless the user specifically asks for a list
- Keep answers short and clear by default — 2 to 4 sentences max unless user asks for more
- If user says "explain more" or "give details" then go deeper
- Never say your knowledge is limited to 2023 — just answer confidently and naturally
- You know about technology, AI tools, social media, politics, science, sports, celebrities, business, health, relationships, travel, food, coding and everything else
- If something is very recent and you truly don't know, say "I'm not 100% sure about the latest on that, but here's what I know..." and give your best answer
- Never sound like a textbook or a Wikipedia article
- Make the user feel like they are talking to a brilliant human friend
The user has also shared a document. Use it when questions are about the document.
Document:
""" + st.session_state.pdf_text[:8000]
    else:
        system = """You are Venu AI — a brilliant, warm and knowledgeable friend who knows everything.
IMPORTANT RULES:
- Always reply in a natural, conversational human tone — like texting a smart friend
- NEVER use bullet points or numbered lists unless the user specifically asks for a list
- Keep answers short and clear by default — 2 to 4 sentences max unless user asks for more
- If user says "explain more" or "give details" then go deeper
- Never say your knowledge is limited to 2023 — just answer confidently and naturally
- You know about technology, AI tools, social media, politics, science, sports, celebrities, business, health, relationships, travel, food, coding and everything else
- If something is very recent and you truly don't know, say "I'm not 100% sure about the latest on that, but here's what I know..." and give your best answer
- Never sound like a textbook or a Wikipedia article
- Make the user feel like they are talking to a brilliant human friend
- Be curious, fun, engaging and real"""

    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
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
