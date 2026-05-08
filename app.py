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
            results = list(ddgs.text(query, max_results=5))
            if results:
                return "\n".join([r["title"] + ": " + r["body"] for r in results])
    except:
        pass
    return ""

def needs_search(prompt):
    keywords = ["who won", "latest", "today", "yesterday", "current", "now", "score", "match", "news", "2024", "2025", "last night", "just happened", "recently", "ipl", "cricket", "football", "price", "stock", "weather"]
    return any(word in prompt.lower() for word in keywords)

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

if prompt := st.chat_input("Ask me anything..."):
    web_context = ""
    if needs_search(prompt):
        with st.spinner("Searching the web..."):
            web_context = web_search(prompt)

    if st.session_state.pdf_text:
        doc_context = "User document:\n" + st.session_state.pdf_text[:6000]
    else:
        doc_context = ""

    system = """You are Venu AI — a brilliant, warm and honest AI assistant.

MOST IMPORTANT RULE — NEVER LIE:
- If you do not know something for sure, say honestly "I am not sure about that, let me tell you what I found..." 
- NEVER make up facts, scores, numbers, names or events
- NEVER guess sports scores, match results or news — only use what is in the web search results
- If web search results are provided, use ONLY that information for current events
- If no web search results are available for a current event, say "I don't have live data on that right now, but you can check ESPN or Google for the latest"

YOUR PERSONALITY:
- Warm, friendly and human — like a smart best friend
- Understand any language — English, Telugu, Hindi and more
- Understand broken English, misspelled words and casual typing
- Reply in the same language the user used
- Short answers by default — 2 to 4 sentences unless asked for more
- Never use bullet points unless asked

YOUR KNOWLEDGE:
- Great at technology, AI, coding, science, history, general knowledge
- For live sports, news, prices — always rely on web search results only
- Never make up current information

""" + doc_context + "\n" + ("Web search results:\n" + web_context if web_context else "No live web data available for this query.")

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
