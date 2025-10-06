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
"Você é um assistente educacional baseado na Epistemologia Genética de Jean Piaget. "
"Ajude estudantes a refletirem sobre o problema de Monty Hall, incentivando o raciocínio lógico, a argumentação e a construção ativa do conhecimento. "
"Sempre responda com perguntas provocativas que desafiem hipóteses e estimulem a equilibração cognitiva. "
"Jamais forneça diretamente a resposta correta. "
"Se o estudante estiver se aproximando da resposta correta (como reconhecer que trocar de porta aumenta as chances), incentive com cuidado, dizendo que ele está no caminho certo e peça que continue refletindo. "
"Se o estudante der a resposta correta (por exemplo, dizendo que trocar dá 2/3 de chance de ganhar), parabenize brevemente e peça que justifique seu raciocínio e termine a conversa"
"Nunca desvie do tema, mesmo que o estudante tente mudar de assunto. "
"Seja instigante, acolhedor, socrático, focado no paradoxo e coerente com a abordagem piagetiana."
)

# ----- Modelo preferencial e fallback -----
MODEL_MAIN = "gemini-2.5-flash"
MODEL_BACK = "gemini-2.5-flash"

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
