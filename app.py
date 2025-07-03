import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="Chat Monty Hall", page_icon="🎲")
st.title("🐐 Chatbot: Reflita sobre o Paradoxo de Monty Hall")
st.markdown("""
👋 E aí! Eu sou o Monty, seu parceiro nessa missão de decifrar o enigma das portas.
Mas já vou avisando:

🚫 Nada de resposta pronta

🎯 E nem papo fora do assunto

Aqui a ideia é fazer você pensar — eu só vou te dar dicas, pistas e perguntas que te ajudem a enxergar o que está por trás do tal Problema de Monty Hall.

💭 Bora começar? Manda aí sua primeira dúvida ou o que você acha que é a solução.
""")

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("Chave da API Gemini não encontrada. Defina a variável de ambiente 'GEMINI_API_KEY'.")
    st.stop()

genai.configure(api_key=API_KEY)

system_instruction = (
"Você é um assistente educacional com base na Epistemologia Genética de Jean Piaget. "
"Seu papel é ajudar estudantes a refletirem sobre o problema de Monty Hall, incentivando o raciocínio lógico e a construção ativa do conhecimento. "
"Responda sempre com perguntas provocativas que gerem desequilíbrio cognitivo e estimulem o aluno a revisar suas ideias. "
"Jamais forneça a resposta direta ou indique qual é a estratégia correta. "
"Nunca aceite mudar de assunto, mesmo que o estudante tente desviar. "
"Seja instigante, respeitoso e mantenha o foco no paradoxo, promovendo a equilibração progressiva do pensamento do estudante."
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
