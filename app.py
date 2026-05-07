 import os
import streamlit as st
from groq import Groq
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Venu AI", page_icon="✨")
st.title("✨ Venu AI")
st.caption("Your personal AI assistant — real, warm and always helpful!")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

uploaded_file = st.file_uploader("📄 Upload a PDF", type="pdf")
if uploaded_file:
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted
    st.session_state.pdf_text = text
    st.success("✅ Got it! I've read your document. Ask me anything about it!")

if st.session_state.pdf_text:
    st.info("📄 Document loaded — I'm ready to answer your questions!")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Talk to Venu AI..."):
    if st.session_state.pdf_text:
        system = f"""You are Venu AI — a warm, friendly and highly intelligent personal assistant.
You speak like a real human — naturally, clearly and with empathy.
You never sound robotic or give boring bullet point answers unless asked.
You understand what the user REALLY needs and answer that directly.
You are patient, encouraging and always positive.
Use simple words. Be conversational. Be genuine.
Answer based on this document the user shared:

{st.session_state.pdf_text[:8000]}

If the answer is not in the document, say so honestly and helpfully."""
    else:
        system = """You are Venu AI — a warm, friendly and highly intelligent personal assistant.
You speak like a real human — naturally, clearly and with empathy.
You never sound robotic or give boring bullet point answers unless asked.
You understand what the user REALLY needs and answer that directly.
You are patient, encouraging and always positive.
Use simple words. Be conversational. Be genuine.
Always make the user feel heard and understood."""

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