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
    st.error("GOOGLE_API_KEY não definida. Adicione a chave Gemini nos Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# --------------- PROMPT BASE (PIAGETIANO) --------------- #
SYSTEM_PROMPT = (
    "Você é um assistente educacional inspirado em Jean Piaget. "
    "Ajude estudantes a refletir sobre o paradoxo de Monty Hall com perguntas que provoquem desequilíbrio cognitivo. "
    "Jamais forneça a resposta direta. Se o estudante se aproximar, incentive; se acertar, parabenize e peça a justificativa. "
    "Nunca saia do tema, mesmo que o usuário tente desviar. Mantenha tom gentil e instigante."
)

# --------------- FUNÇÃO HELPERS --------------- #

def build_prompt(user_msg: str, history: list[tuple[str, str]], k: int = 2) -> str:
    """Retorna string: SYSTEM + últimas k trocas + pergunta atual."""
    context = "".join(
        f"Aluno: {u}\nTutor: {b}\n" for u, b in history[-k:]
    )
    return f"{SYSTEM_PROMPT}\n{context}Aluno: {user_msg}\nTutor:"


def ask_gemini(prompt: str):
    """Envia prompt; tenta flash→pro; trata ResourceExhausted."""
    try:
        resp = genai.generate_content(
            model="models/gemini-1.5-flash-latest",
            prompt=prompt,
            generation_config={"max_output_tokens": 180},
        )
        return resp.text
    except ResourceExhausted:
        # back‑off simples (quota/minute) + fallback p/ modelo menor
        time.sleep(20)
        resp = genai.generate_content(
            model="gemini-pro",  # menos exigente de cota
            prompt=prompt,
            generation_config={"max_output_tokens": 150},
        )
        return resp.text

# --------------- ESTADO DA SESSÃO --------------- #
if "history" not in st.session_state:
    st.session_state.history = []  # lista de (user, bot)

# Renderiza histórico
for u, b in st.session_state.history:
    st.chat_message("user").markdown(u)
    st.chat_message("model").markdown(b)

# Entrada
user_input = st.chat_input("Digite sua pergunta ou hipótese sobre Monty Hall…")

if user_input:
    # Mostra imediatamente
    st.chat_message("user").markdown(user_input)

    # Monta prompt curto
    prompt = build_prompt(user_input, st.session_state.history, k=2)

    # Chama Gemini
    with st.spinner("Pensando…"):
        bot_reply = ask_gemini(prompt)

    st.chat_message("model").markdown(bot_reply)

    # Atualiza histórico
    st.session_state.history.append((user_input, bot_reply))
```
