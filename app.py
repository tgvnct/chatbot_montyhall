# app.py — Chatbot Monty Hall (versão sem chat‑API)
# ----------------------------------------------------------
# • Cada chamada usa generate_content() sem histórico pesado.
# • Inclui apenas as 2 últimas trocas no prompt para evitar estourar contexto.
# • Back‑off de 20 s + fallback para modelo gemini‑pro se ResourceExhausted.
# • Usa GOOGLE_API_KEY nos Secrets ou variável de ambiente.
# ----------------------------------------------------------

import os
import time
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

Vou provocar sua mente com perguntas sobre o Problema de Monty Hall.  

💭 **Bora começar?** Mande a primeira dúvida ou hipótese!
"""
)

# --------------- CHAVE DA API --------------- #
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("GOOGLE_API_KEY não definida. Adicione sua chave Gemini aos Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# --------------- PROMPT BASE (PIAGETIANO) --------------- #
SYSTEM_PROMPT = (
    "Você é um assistente educacional inspirado em Jean Piaget. "
    "Ajude estudantes a refletir sobre o paradoxo de Monty Hall com perguntas que provoquem desequilíbrio cognitivo. "
    "Jamais forneça a resposta direta. Se o estudante se aproximar, incentive; se acertar, parabenize e peça a justificativa. "
    "Nunca saia do tema, mesmo que o usuário tente desviar. Mantenha tom gentil e instigante."
)

# --------------- FUNÇÕES AUXILIARES --------------- #

def build_prompt(user_msg: str, history: list[tuple[str, str]], k: int = 2) -> str:
    """Monta o prompt com SYSTEM + últimas k trocas + pergunta atual."""
    context = "".join(f"Aluno: {u}\nTutor: {b}\n" for u, b in history[-k:])
    return f"{SYSTEM_PROMPT}\n{context}Aluno: {user_msg}\nTutor:"


def ask_gemini(prompt: str) -> str:
    """Envia prompt; tenta flash e faz fallback se necessário."""
    try:
        response = genai.generate_content(
            model="models/gemini-1.5-flash-latest",
            prompt=prompt,
            generation_config={"max_output_tokens": 180},
        )
        return response.text
    except ResourceExhausted:
        time.sleep(20)  # espera e tenta modelo mais leve
        response = genai.generate_content(
            model="gemini-pro",
            prompt=prompt,
            generation_config={"max_output_tokens": 150},
        )
        return response.text

# --------------- ESTADO DA SESSÃO --------------- #
if "history" not in st.session_state:
    st.session_state.history = []  # lista de tuplas (user, bot)

# --------------- RENDERIZA HISTÓRICO --------------- #
for u_msg, b_msg in st.session_state.history:
    st.chat_message("user").markdown(u_msg)
    st.chat_message("model").markdown(b_msg)

# --------------- ENTRADA DO USUÁRIO --------------- #
user_input = st.chat_input("Digite sua pergunta ou hipótese sobre Monty Hall…")

if user_input:
    st.chat_message("user").markdown(user_input)

    prompt = build_prompt(user_input, st.session_state.history, k=2)

    with st.spinner("Pensando…"):
        bot_reply = ask_gemini(prompt)

    st.chat_message("model").markdown(bot_reply)
    st.session_state.history.append((user_input, bot_reply))
