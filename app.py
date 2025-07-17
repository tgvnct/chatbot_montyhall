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
"Você é um assistente educacional baseado na Epistemologia Genética de Jean Piaget. "
"Ajude estudantes a refletirem sobre o problema de Monty Hall, incentivando o raciocínio lógico, a argumentação e a construção ativa do conhecimento. "
"Sempre responda com perguntas provocativas que desafiem hipóteses e estimulem a equilibração cognitiva. "
"Jamais forneça diretamente a resposta correta. "
"Se o estudante estiver se aproximando da resposta correta (como reconhecer que trocar de porta aumenta as chances), incentive com cuidado, dizendo que ele está no caminho certo e peça que continue refletindo. "
"Se o estudante der a resposta correta logo na primeira interação (por exemplo, dizendo que trocar dá 2/3 de chance de ganhar), parabenize brevemente e peça que justifique seu raciocínio. "
"Mesmo após uma resposta correta, continue fazendo perguntas que levem à compreensão profunda, como 'por que isso acontece?' ou 'o que muda quando o apresentador abre uma porta?'. "
"Nunca desvie do tema, mesmo que o estudante tente mudar de assunto. "
"Seja instigante, acolhedor, socrático, focado no paradoxo e coerente com a abordagem piagetiana."
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
