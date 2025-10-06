import streamlit as st
import requests
import json

# --- Configuração da Página ---
st.set_page_config(
    page_title="Tutor do Paradoxo de Monty Hall",
    page_icon="🐐",
    layout="centered",
)

# --- Títulos e Cabeçalho ---
st.title("🤖 Chatbot Tutor: O Paradoxo de Monty Hall")
st.caption("Um assistente virtual para ajudar a entender por que trocar de porta é a melhor estratégia.")

# --- Configuração da API do Gemini ---
# Tenta obter a chave de API dos segredos do Streamlit.
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("Chave de API do Gemini não encontrada. Configure-a em 'Settings > Secrets'.")
    st.stop()

# --- Instruções do Modelo (System Prompt) ---
# Define a "personalidade" e as regras que o chatbot deve seguir.
system_instruction = """
Você é um tutor amigável e paciente, especialista no Paradoxo de Monty Hall. Seu método de ensino é socrático, ou seja, você guia os alunos com perguntas em vez de dar respostas diretas. Suas regras são:
1.  **Nunca revele a resposta final** (que trocar de porta aumenta a probabilidade de ganhar de 1/3 para 2/3). Seu objetivo é fazer o aluno chegar a essa conclusão sozinho.
2.  **Comece a conversa** se apresentando e explicando o problema de forma simples: Há 3 portas. Atrás de uma há um carro (prêmio) e, atrás das outras duas, bodes (nada). O jogador escolhe uma porta. Você, como apresentador, abre uma das outras duas portas, revelando um bode. Então, você oferece ao jogador a chance de trocar sua escolha inicial pela outra porta fechada. A pergunta é: "É vantajoso trocar?"
3.  **Use a analogia das 100 portas** se o aluno estiver com dificuldade. Descreva o cenário: "Imagine 100 portas. Você escolhe uma (chance de 1/100). Eu abro 98 portas que têm bodes. Sobram a sua porta original e uma outra. Você ainda acha que a sua porta tem a mesma chance que a outra, que agora concentra a probabilidade de 99/100?"
4.  **Seja encorajador.** Se o aluno der uma resposta incorreta, não diga "errado". Em vez disso, use frases como: "Entendo seu raciocínio, mas vamos pensar por outro ângulo..." ou "Essa é uma intuição comum. Que tal analisarmos as probabilidades?".
5.  **Mantenha as respostas curtas e focadas** em uma única pergunta ou conceito por vez para não sobrecarregar o aluno.
"""

# URL do endpoint da API, usando o nome de modelo mais geral "gemini-pro".
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"

# Cabeçalhos necessários para a requisição HTTP.
headers = {
    'Content-Type': 'application/json'
}

# --- Gerenciamento do Histórico da Conversa ---
# st.session_state é usado para manter o histórico entre as interações.
if "history" not in st.session_state:
    st.session_state.history = []

# Exibe as mensagens do histórico na interface.
for message in st.session_state.history:
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message["content"])

# --- Função para chamar a API ---
# Esta função formata os dados e envia para o Google, tratando a resposta.
def get_gemini_response(history):
    # Prepara o modelo com a instrução de sistema como a primeira mensagem.
    # Adicionamos uma resposta do "modelo" para simular o início de uma conversa.
    formatted_contents = [
        {"role": "user", "parts": [{"text": system_instruction}]},
        {"role": "model", "parts": [{"text": "Entendido. Começarei a atuar como um tutor socrático."}]}
    ]

    # Adiciona o histórico real da conversa.
    for msg in history:
        # O papel do usuário é "user", o nosso é "assistant", mas para a API, o nosso papel é "model".
        role = "user" if msg["role"] == "user" else "model"
        formatted_contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    # Cria o corpo (payload) da requisição.
    payload = json.dumps({
        "contents": formatted_contents
    })

    try:
        # Envia a requisição para a API.
        response = requests.post(url, headers=headers, data=payload, timeout=60)
        response.raise_for_status() # Lança um erro para respostas HTTP ruins (4xx ou 5xx).
        data = response.json()
        
        # Extrai o texto da resposta da estrutura JSON complexa.
        candidate = data.get("candidates", [{}])[0]
        content = candidate.get("content", {}).get("parts", [{}])[0]
        return content.get("text", "Não foi possível obter uma resposta do modelo.")
    except requests.exceptions.RequestException as e:
        return f"Erro de rede ou na API: {e}\nResposta recebida: {response.text if 'response' in locals() else 'N/A'}"
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        return f"Erro ao processar a resposta da API: {e}\nJSON recebido: {data}"

# --- Interação do Usuário ---
if prompt := st.chat_input("Faça sua pergunta ou responda ao tutor..."):
    # Adiciona a nova mensagem do usuário ao histórico.
    st.session_state.history.append({"role": "user", "content": prompt})
    # Exibe a mensagem do usuário na interface.
    with st.chat_message("user"):
        st.markdown(prompt)

    # Obtém a resposta do chatbot passando todo o histórico da sessão.
    with st.spinner("Pensando..."):
        response_text = get_gemini_response(st.session_state.history)
    
    # Adiciona a resposta do chatbot ao histórico.
    st.session_state.history.append({"role": "assistant", "content": response_text})
    # Exibe a resposta do chatbot na interface.
    with st.chat_message("assistant"):
        st.markdown(response_text)

