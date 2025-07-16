# app.py — Chatbot Monty Hall com truncamento de histórico

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

🚫 **Nada de resposta pronta**  
🎯 **E nem papo fora do assunto**  

Aqui a ideia é fazer você pensar — só vou te dar dicas, pistas e perguntas que ajudem a enxergar o que está por trás do Problema de Monty Hall.  

💭 **Bora começar?** Manda aí sua primeira dúvida ou o que você acha que é a solução.
"""
)

# ---------------- CHAVE DA API GOOGLE GEMINI ---------------- #
API_KEY = os.getenv("GOOGLE_API_KEY")  # definida em secrets.toml ou no painel Secrets
if not API_KEY:
    st.error("Chave da API Gemini não encontrada. Defina GOOGLE_API_KEY nos Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# ---------------- INSTRUÇÃO SISTÊMICA ---------------- #
system_instruction = (
    "Você é um assistente educacional baseado na Epistemologia Genética de Jean Piaget. "
    "Ajude estudantes a refletirem sobre o problema de Monty Hall, incentivando o raciocínio lógico, a argumentação e a construção ativa do conhecimento. "
    "Sempre responda com perguntas provocativas que desafiem hipóteses e estimulem a equilibração cognitiva. "
    "Jamais forneça diretamente a resposta correta. "
    "Se o estudante se aproximar da resposta, incentive; se acertar, parabenize e peça justificativa."
    "Se o estudante der a resposta certa, parabenize e termine a conversa"
    "Nunca desvie do tema, mesmo que o estudante tente mudar de assunto. "
    "Seja instigante, acolhedor e focado no paradoxo."
)

# ---------------- MODELO ---------------- #
model = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash-latest",
    system_instruction=system_instruction,
)

# ---------------- CONSTANTES ---------------- #
MAX_HISTORY = 10  # mantém apenas as 10 últimas interações (user + model)

# ---------------- INICIALIZA SESSÃO ---------------- #
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat()

# ---------------- EXIBE HISTÓRICO EXISTENTE ---------------- #
for msg in st.session_state.chat.history:
    with st.chat_message(msg.role):
        st.markdown(msg.parts[0].text)

# ---------------- ENTRADA DO USUÁRIO ---------------- #
user_input = st.chat_input("Digite sua pergunta ou ideia sobre Monty Hall...")
if user_input:
    st.chat_message("user").markdown(user_input)

    # ----- TRUNCA HISTÓRICO PARA EVITAR ResourceExhausted ----- #
    if len(st.session_state.chat.history) > 2 * MAX_HISTORY:
        st.session_state.chat.history = st.session_state.chat.history[-2 * MAX_HISTORY :]

    # ----- ENVIA MENSAGEM COM TRATAMENTO DE ERRO ----- #
    try:
        with st.chat_message("model"):
            response = st.session_state.chat.send_message(user_input)
            st.markdown(response.text)
    except ResourceExhausted:
        st.warning(
            "Limite de contexto ou quota atingido. O histórico foi reiniciado para continuar a conversa."
        )
        st.session_state.chat = model.start_chat()  # zera histórico
        with st.chat_message("model"):
            response = st.session_state.chat.send_message(user_input)
            st.markdown(response.text)
