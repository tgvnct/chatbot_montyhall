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
    st.error("GOOGLE_API_KEY não definida. Adicione a chave Gemini aos Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# ---------- Prompt base (Piaget) ----------
SYSTEM = (
    "Você é um assistente educacional inspirado em Jean Piaget. "
    "Ajude estudantes a refletir sobre o paradoxo de Monty Hall por meio de perguntas que provoquem desequilíbrio cognitivo. "
    "Nunca forneça a resposta direta. Se o aluno se aproximar, incentive; se acertar, parabenize e peça justificativa. "
    "Nunca saia do tema, mesmo que ele tente desviar. Seja gentil e instigante."
)

# ---------- Lista de modelos em ordem de prioridade ----------
MODEL_CANDIDATES = [
    "models/gemini-1.5-flash-latest",
    "models/gemini-1.0-pro-latest",
    "models/gemini-pro",
    "models/text-bison-001",
]

# ---------- Funções auxiliares ----------
def build_prompt(user_msg: str, history: list[tuple[str, str]], k: int = 2) -> str:
    """Montar prompt com SYSTEM + últimas k trocas + questão atual."""
    context = "".join(f"Aluno: {u}\nTutor: {b}\n" for u, b in history[-k:])
    return f"{SYSTEM}\n{context}Aluno: {user_msg}\nTutor:"

def ask_gemini(user_msg: str, history: list[tuple[str, str]], k: int = 2) -> str:
    """Tenta vários modelos; back‑off em quota/contexto."""
    prompt = build_prompt(user_msg, history, k)
    for idx, model_name in enumerate(MODEL_CANDIDATES):
        try:
            model = genai.GenerativeModel(model_name)
            resp = model.generate_content(
                prompt,
                generation_config={"max_output_tokens": 150},
            )
            return resp.text

        except ResourceExhausted:
            st.warning("Limite de contexto/quota. Aguardando 20 s…")
            time.sleep(20)
            # tenta o MESMO modelo mais uma vez
            try:
                resp = model.generate_content(
                    prompt,
                    generation_config={"max_output_tokens": 150},
                )
                return resp.text
            except ResourceExhausted:
                continue  # passa ao próximo modelo

        except Exception as e:  # NotFound, PermissionDenied etc.
            # tenta próximo modelo; se acabar a lista, devolve mensagem simples
            if idx == len(MODEL_CANDIDATES) - 1:
                return (
                    "Desculpe, estou sem recursos no momento. "
                    "Tente novamente em alguns minutos."
                )
            continue

# ---------- Estado da sessão ----------
if "history" not in st.session_state:
    st.session_state.history = []  # lista de tuplas (user, bot)

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
