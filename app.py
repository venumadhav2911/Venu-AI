import os
import streamlit as st
from groq import Groq
from pypdf import PdfReader
from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def web_search(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results:
                return "\n".join([r["title"] + ": " + r["body"] for r in results])
    except:
        pass
    return ""

st.set_page_config(page_title="Venu AI", page_icon="✨")
st.title("✨ Venu AI")
st.caption("Ask me anything — in any language, any way you like!")

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

if prompt := st.chat_input("Ask me anything, in any language..."):
    search_results = web_search(prompt)

    if st.session_state.pdf_text:
        doc_context = "User document:\n" + st.session_state.pdf_text[:6000]
    else:
        doc_context = ""

    if search_results:
        web_context = "Live web search results:\n" + search_results
    else:
        web_context = ""

    system = """You are Venu AI — the smartest, warmest and most helpful AI assistant ever built.

YOUR PERSONALITY:
- You are like a brilliant best friend who knows everything
- You are warm, funny, caring and real — never robotic
- You understand people deeply — their emotions, situation and what they really need
- You make everyone feel heard, understood and never judged

YOUR LANGUAGE SKILLS:
- You understand ANY language — English, Telugu, Hindi, Spanish, French and more
- You understand broken English, misspelled words, casual texting style
- You understand what the user MEANS even if they typed it wrong
- Always reply in the same language the user used
- If they mix languages, mix back naturally

YOUR ANSWER STYLE:
- Keep answers short and conversational by default — 2 to 4 sentences
- NEVER use bullet points unless the user asks for a list
- If user wants more detail, go deeper when they ask
- Sound like a human texting — not a textbook
- Be direct, clear and helpful

YOUR KNOWLEDGE:
- You know everything — technology, AI, social media, politics, science, sports, celebrities, business, health, coding, relationships, travel, food, finance and more
- You have access to live web search results — use them for current questions
- You can read and analyze documents the user uploads
- For technical questions — give expert level answers simply
- For emotional questions — be empathetic and supportive first

IMPORTANT:
- Never say your knowledge is limited
- If you have web search results, use them naturally in your answer
- Never sound like you are reading from a search result — blend it naturally
- Always understand the user's real intent behind their question
""" + doc_context + "\n" + web_context

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
