import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="Chat Monty Hall", page_icon="🎲")
st.title("🎲 Chatbot: Reflita sobre o Paradoxo de Monty Hall")
st.markdown("""
Este assistente pedagógico foi criado para ajudar estudantes a refletirem sobre o problema de Monty Hall.
Ele **nunca fornecerá a resposta direta** e **jamais sairá do tema**. Em vez disso, responderá sempre com perguntas e pistas que te levem a pensar por conta própria.
""")

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("Chave da API Gemini não encontrada. Defina a variável de ambiente 'GEMINI_API_KEY'.")
    st.stop()

genai.configure(api_key=API_KEY)

system_instruction = (
    "Você é um assistente educacional que ajuda estudantes a refletirem sobre o problema de Monty Hall. "
    "Sempre responda com perguntas que levem o estudante a pensar, sem nunca dar a resposta. "
    "Nunca desvie do tema, mesmo que o usuário tente mudar de assunto. "
    "Seja gentil, instigante e mantenha o foco no paradoxo."
)

model = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash-latest",
    system_instruction=system_instruction
)

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

for msg in st.session_state.chat.history:
    with st.chat_message(msg.role):
        st.markdown(msg.parts[0].text)

user_input = st.chat_input("Digite sua pergunta ou ideia sobre Monty Hall...")
if user_input:
    st.chat_message("user").markdown(user_input)
    with st.chat_message("model"):
        response = st.session_state.chat.send_message(user_input)
        st.markdown(response.text)
