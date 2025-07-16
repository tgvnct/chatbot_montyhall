# app.py — Chatbot Monty Hall com Gemini API (versão segura)
# Autor: Tiago + ChatGPT | Revisão: jul 2025
# -----------------------------------------------------------
# • Mantém no máximo MAX_TURNS trocas para não estourar contexto.
# • Captura ResourceExhausted e reenvia a pergunta sem histórico.
# • Usa GOOGLE_API_KEY em secrets.toml / painel de segredos.
# -----------------------------------------------------------

import os
import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# --------------- CONFIG. DA PÁGINA --------------- #
st.set_page_config(page_title="Chat Monty Hall", page_icon="🐐")
st.title("🐐 Chatbot: Reflita sobre o Paradoxo de Monty Hall")

st.markdown(
    """
👋 **E aí! Eu sou o Monty, seu parceiro no enigma das portas.**  

🚫 **Sem resposta pronta** | 🎯 **Sem papo fora do tema**  

Vou lançar perguntas e pistas para mexer nas suas hipóteses sobre o Problema de Monty Hall.  

💭 **Bora começar?** Mande sua primeira ideia ou dúvida!
"""
)

# --------------- CHAVE DA API --------------- #
API_KEY = os.getenv("GOOGLE_API_KEY")  # defina em secrets.toml ou no painel Secrets
if not API_KEY:
    st.error("GOOGLE_API_KEY não definida. Adicione sua chave Gemini aos Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# --------------- PROMPT DE SISTEMA --------------- #
system_instruction = (
    "Você é um assistente educacional inspirado em Jean Piaget. "
    "Ajude estudantes a refletir sobre o paradoxo de Monty Hall com perguntas que provoquem desequilíbrio cognitivo. "
    "Jamais forneça a resposta direta. Se o estudante se aproximar, incentive; se acertar, parabenize e peça a justificativa. "
    "Nunca saia do tema mesmo que o usuário tente desviar. Mantenha tom gentil e instigante."
)

# --------------- MODELO --------------- #
model = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash-latest",
    system_instruction=system_instruction,
)

# --------------- CONTEXTO / HISTÓRICO --------------- #
MAX_TURNS = 12  # máximo de trocas antes de reiniciar

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat()
    st.session_state.turns = 0

# Exibe histórico existente
for msg in st.session_state.chat.history:
    with st.chat_message(msg.role):
        st.markdown(msg.parts[0].text)

# --------------- ENTRADA DO USUÁRIO --------------- #
user_input = st.chat_input("Digite sua pergunta ou hipótese sobre Monty Hall…")

if user_input:
    # Mostra mensagem do usuário
    st.chat_message("user").markdown(user_input)

    # Incrementa e verifica limite de turnos
    st.session_state.turns += 1
    if st.session_state.turns > MAX_TURNS:
        st.session_state.chat = model.start_chat()
        st.session_state.turns = 1  # conta a interação atual

    # Tenta enviar normalmente
    try:
        with st.chat_message("model"):
            response = st.session_state.chat.send_message(user_input)
            st.markdown(response.text)

    # Se contexto/quota estourar, reinicia e reenvia sem histórico
    except ResourceExhausted:
        st.warning("📉 Limite de contexto ou quota excedido. Reiniciando conversa…")
        st.session_state.chat = model.start_chat()
        st.session_state.turns = 1
        with st.chat_message("model"):
            safe_response = model.generate_content(user_input)
            st.markdown(safe_response.text)
