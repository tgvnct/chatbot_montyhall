import os
import time
import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# ---------- Configuração da página ----------
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

# ---------- Chave da API ----------
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("GOOGLE_API_KEY não definida. Adicione sua chave Gemini aos Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# ---------- Prompt base (piagetiano) ----------
SYSTEM = (
    "Você é um assistente educacional inspirado em Jean Piaget. "
    "Ajude estudantes a refletir sobre o paradoxo de Monty Hall com perguntas que provoquem desequilíbrio cognitivo. "
    "Jamais forneça a resposta direta. Se o estudante se aproximar, incentive; se acertar, parabenize e peça a justificativa. "
    "Nunca saia do tema, mesmo que o usuário tente desviar. Mantenha tom gentil e instigante."
)

# ---------- Modelos ----------
model_flash = genai.GenerativeModel("models/gemini-1.5-flash-latest")
model_pro   = genai.GenerativeModel("gemini-pro")  # fallback

# ---------- Função de consulta ----------
def ask_gemini(user_msg: str, history: list[tuple[str, str]], k: int = 2) -> str:
    """Envia prompt ao Gemini com um histórico curto."""
    short_context = "".join(f"Aluno: {u}\nTutor: {b}\n" for u, b in history[-k:])
    prompt = f"{SYSTEM}\n{short_context}Aluno: {user_msg}\nTutor:"
    try:
        resp = model_flash.generate_content(
            prompt, generation_config={"max_output_tokens": 180}
        )
        return resp.text
    except ResourceExhausted:
        st.warning("Limite atingido. Aguardando 20 s e tentando novamente…")
        time.sleep(20)
        resp = model_pro.generate_content(
            prompt, generation_config={"max_output_tokens": 150}
        )
        return resp.text

# ---------- Estado da sessão ----------
if "history" not in st.session_state:
    st.session_state.history = []  # lista de (user, bot)

# ---------- Renderiza histórico ----------
for user_msg, bot_msg in st.session_state.history:
    st.chat_message("user").markdown(user_msg)
    st.chat_message("model").markdown(bot_msg)

# ---------- Entrada do usuário ----------
user_input = st.chat_input("Digite sua pergunta ou hipótese sobre Monty Hall…")

if user_input:
    st.chat_message("user").markdown(user_input)

    with st.spinner("Pensando…"):
        bot_reply = ask_gemini(user_input, st.session_state.history, k=2)

    st.chat_message("model").markdown(bot_reply)
    st.session_state.history.append((user_input, bot_reply))
