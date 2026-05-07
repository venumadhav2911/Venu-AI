import os
import streamlit as st
from groq import Groq
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Venu AI", page_icon="✨")
st.title("✨ Venu AI")
st.caption("Your free AI assistant — chat freely or upload a PDF!")

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
    st.success(f"✅ PDF loaded! Ask me anything about it.")

if st.session_state.pdf_text:
    st.info("📄 PDF loaded — I will answer based on your document.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything..."):
    if st.session_state.pdf_text:
        system = f"You are Venu AI, a helpful assistant. Answer based on this document:\n\n{st.session_state.pdf_text[:8000]}"
    else:
        system = "You are Venu AI, a helpful and friendly AI assistant. Answer any questions clearly."

    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system},
                    *st.session_state.messages
                ]
            )
            reply = response.choices[0].message.content
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})