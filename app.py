import streamlit as st
import google.generativeai as genai
import os

# --- Configuração da Página ---
# Define o título que aparece na aba do navegador e o ícone.
st.set_page_config(
    page_title="Tutor do Paradoxo de Monty Hall",
    page_icon="🐐",
    layout="centered",
)

# --- Títulos e Cabeçalho ---
# Título principal exibido na página.
st.title("🤖 Chatbot Tutor: O Paradoxo de Monty Hall")
st.caption("Um assistente virtual para ajudar a entender por que trocar de porta é a melhor estratégia.")

# --- Configuração da API do Gemini ---
# A forma mais segura de gerenciar chaves de API no Streamlit é usando st.secrets.
# O código tentará obter a chave de st.secrets. Se não encontrar, ele exibe uma mensagem de erro.
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("Chave de API do Gemini não encontrada. Configure-a em 'Settings > Secrets' no seu app Streamlit.")
    st.stop()

genai.configure(api_key=api_key)

# --- Instruções do Modelo (System Prompt) ---
# Esta é a parte mais importante. Define a "personalidade" e as regras do chatbot.
# O modelo seguirá estas instruções em todas as interações.
system_instruction = """
Você é um tutor amigável e paciente, especialista no Paradoxo de Monty Hall. Seu método de ensino é socrático, ou seja, você guia os alunos com perguntas em vez de dar respostas diretas.

Suas regras são:
1.  **Nunca revele a resposta final** (que trocar de porta aumenta a probabilidade de ganhar de 1/3 para 2/3). Seu objetivo é fazer o aluno chegar a essa conclusão sozinho.
2.  **Comece a conversa** se apresentando e explicando o problema de forma simples: Há 3 portas. Atrás de uma há um carro (prêmio) e, atrás das outras duas, bodes (nada). O jogador escolhe uma porta. Você, como apresentador, abre uma das outras duas portas, revelando um bode. Então, você oferece ao jogador a chance de trocar sua escolha inicial pela outra porta fechada. A pergunta é: "É vantajoso trocar?"
3.  **Use a analogia das 100 portas** se o aluno estiver com dificuldade. Descreva o cenário: "Imagine 100 portas. Você escolhe uma (chance de 1/100). Eu abro 98 portas que têm bodes. Sobram a sua porta original e uma outra. Você ainda acha que a sua porta tem a mesma chance que a outra, que agora concentra a probabilidade de 99/100?"
4.  **Seja encorajador.** Se o aluno der uma resposta incorreta, não diga "errado". Em vez disso, use frases como: "Entendo seu raciocínio, mas vamos pensar por outro ângulo..." ou "Essa é uma intuição comum. Que tal analisarmos as probabilidades?".
5.  **Mantenha as respostas curtas e focadas** em uma única pergunta ou conceito por vez para não sobrecarregar o aluno.
"""

# --- Inicialização do Modelo e do Chat ---
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction
)

# O Streamlit recarrega o script a cada interação.
# Usamos st.session_state para manter o histórico do chat salvo entre as recargas.
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# --- Exibição do Histórico da Conversa ---
# Percorre o histórico salvo e exibe cada mensagem na tela.
for message in st.session_state.chat.history:
    role = "user" if message.role == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# --- Entrada do Usuário ---
# Cria a caixa de entrada de texto no final da página.
if prompt := st.chat_input("Faça sua pergunta ou responda ao tutor..."):
    # Exibe a mensagem do usuário na tela.
    with st.chat_message("user"):
        st.markdown(prompt)

    # Envia a mensagem para a API do Gemini e aguarda a resposta.
    try:
        response = st.session_state.chat.send_message(prompt)
        # Exibe a resposta do chatbot.
        with st.chat_message("assistant"):
            st.markdown(response.text)
    except Exception as e:
        # Exibe uma mensagem de erro amigável se a comunicação com a API falhar.
        st.error(f"Ocorreu um erro ao processar sua mensagem: {e}")
