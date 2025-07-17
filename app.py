# app.py — Monty Hall “mensagens avulsas”

import os, streamlit as st, google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import time

# ----- Configuração da página -----
st.set_page_config(page_title="Chat Monty Hall", page_icon="🐐")
st.title("🐐 Chatbot: Reflita sobre o Paradoxo de Monty Hall")

st.markdown("""
👋 E aí! Eu sou o Monty, seu parceiro nessa missão de decifrar o enigma das portas.
Mas já vou avisando:

🚫 Nada de resposta pronta

🎯 E nem papo fora do assunto

Aqui a ideia é fazer você pensar — eu só vou te dar dicas, pistas e perguntas que te ajudem a enxergar o que está por trás do tal Problema de Monty Hall.

💭 Bora começar? Manda aí sua primeira dúvida ou o que você acha que é a solução.

""")

# ----- Chave da API -----
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("Defina GOOGLE_API_KEY ou GEMINI_API_KEY nos Secrets.")
    st.stop()
genai.configure(api_key=API_KEY)

# ----- Prompt base -----
SYSTEM = (
    "Você é um assistente educacional inspirado em Piaget. "
    "Ajude estudantes a refletir sobre o paradoxo de Monty Hall com perguntas provocativas. "
    "Nunca forneça a resposta direta. Incentive justificativas. "
    "Mantenha o foco no tema, mesmo que o aluno tente desviar."
)

# ----- Modelo preferencial e fallback -----
MODEL_MAIN = "models/gemini-1.5-flash-latest"
MODEL_BACK = "models/gemini-1.0-pro-latest"

def ask_gemini(user_msg, history, k=2):
    """Envia prompt curto; faz fallback se quota/contexto."""
    short_hist = "".join(f"Aluno: {u}\nTutor: {b}\n" for u, b in history[-k:])
    prompt = f"{SYSTEM}\n{short_hist}Aluno: {user_msg}\nTutor:"
    for model_name in (MODEL_MAIN, MODEL_BACK):
        try:
            model = genai.GenerativeModel(model_name)
            resp = model.generate_content(prompt, generation_config={"max_output_tokens": 160})
            return resp.text
        except ResourceExhausted:
            st.warning("Limite de uso — aguardando 20 s…")
            time.sleep(20)
            # tenta de novo o mesmo modelo após pausa
            try:
                resp = model.generate_content(prompt, generation_config={"max_output_tokens": 160})
                return resp.text
            except ResourceExhausted:
                continue
        except Exception:
            continue
    return "Desculpe, os recursos estão indisponíveis no momento. Tente mais tarde."

# ----- Histórico apenas para exibição -----
if "history" not in st.session_state:
    st.session_state.history = []  # lista de (user, bot)

# Renderiza histórico na interface (não será reenviado)
for u, b in st.session_state.history:
    st.chat_message("user").markdown(u)
    st.chat_message("model").markdown(b)

# Entrada do usuário
user_input = st.chat_input("Digite sua dúvida ou hipótese…")
if user_input:
    st.chat_message("user").markdown(user_input)
    with st.spinner("Pensando…"):
        bot_reply = ask_gemini(user_input, st.session_state.history, k=2)
    st.chat_message("model").markdown(bot_reply)
    st.session_state.history.append((user_input, bot_reply))
