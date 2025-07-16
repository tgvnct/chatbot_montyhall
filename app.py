# app.py — Chatbot Monty Hall com Gemini API e controle de contexto
# Autor: Tiago + ChatGPT | Última revisão: jul 2025

"""Resumo
---------
• Mantém no máximo `MAX_TURNS` trocas por sessão para evitar estouro de contexto.
• Reinicia o chat automaticamente se atingir quota ou contexto (ResourceExhausted).
• Usa variável de ambiente/secret **GOOGLE_API_KEY** para a chave.
"""

import os
import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# ---------------- CONFIGURAÇÃO DA PÁGINA ---------------- #
st.set_page_config(page_title="Chat Monty Hall", page_icon="🎲")
st.title("🐐 Chatbot: Reflita sobre o Paradoxo de Monty Hall")

st.markdown(
    """
👋 **E aí! Eu sou o Monty, seu parceiro nessa missão de decifrar o enigma das portas.**  

🚫 **Nada de resposta pronta** | 🎯 **E nem papo fora do assunto**  

Só vou lançar perguntas e pistas para provocar sua mente sobre o Problema de Monty Hall.  

💭 **Bora começar?** Mande sua primeira dúvida ou hipótese!
"""
)

# ---------------- CHAVE DA API ---------------- #
API_KEY = os.getenv("GOOGLE_API_KEY")  # defina em secrets.toml ou no painel Secrets
if not API_KEY:
    st.error("Chave da API não encontrada. Defina GOOGLE_API_KEY nos Secrets do Streamlit.")
    st.stop()

genai.configure(api_key=API_KEY)

# ---------------- PROMPT DE SISTEMA (PIAGETIANO) ---------------- #
system_instruction = (
    "Você é um assistente educacional inspirado em Jean Piaget. "
    "Ajude estudantes a refletir sobre o paradoxo de Monty Hall fazendo perguntas que gerem desequilíbrio cognitivo. "
    "Nunca forneça a resposta direta. Se o aluno se aproximar da solução, incentive; se acertar, parabenize e peça justificativa. "
    "Nunca desvie do tema, mesmo que o usuário tente. Mantenha tom gentil e instigante."
)

# ---------------- INICIALIZA MODELO ---------------- #
model = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash-latest",
    system_instruction=system_instruction,
)

# ---------------- CONTROLE DE HISTÓRICO ---------------- #
MAX_TURNS = 12  # nº máximo de trocas antes de reiniciar

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat()
    st.session_state.turns = 0

# ---------------- RENDERIZA HISTÓRICO ---------------- #
for msg in st.session_state.chat.history:
    with st.chat_message(msg.role):
        st.markdown(msg.parts[0].text)

# ---------------- ENTRADA DO USUÁRIO ---------------- #
user_input = st.chat_input("Digite sua pergunta ou ideia sobre Monty Hall…")

if user_input:
    # Mostra mensagem do usuário
    st.chat_message("user").markdown(user_input)

    # Incrementa contador de turnos e verifica limite
    st.session_state.turns += 1
    if st.session_state.turns > MAX_TURNS:
        st.session_state.chat = model.start_chat()
        st.session_state.turns = 1  # conta a interação atual

    # Tenta enviar mensagem, com captura de erro
    try:
        with st.chat_message("model"):
            response = st.session_state.chat.send_message(user_input)
            st.markdown(response.text)
    except ResourceExhausted:
        st.warning("Contexto ou quota excedidos; reiniciando a conversa para continuar.")
        st.session_state.chat = model.start_chat()
        st.session_state.turns = 1
        with st.chat_message("model"):
            response = st.session_state.chat.send_message(user_input)
            st.markdown(response.text)
