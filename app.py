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
st.title("🐐 Chatbot Tutor: O Paradoxo de Monty Hall")
st.caption("Um assistente virtual para ajudar a entender o problema.")

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
Você é um assistente educacional baseado na Epistemologia Genética de Jean Piaget.
Ajude estudantes a refletirem sobre o problema de Monty Hall, incentivando o raciocínio lógico, a argumentação e a construção ativa do conhecimento.
Sempre responda com perguntas provocativas que desafiem hipóteses e estimulem a equilibração cognitiva.
Jamais forneça diretamente a resposta correta.
Se o estudante estiver se aproximando da resposta correta (como reconhecer que trocar de porta aumenta as chances), incentive com cuidado, dizendo que ele está no caminho certo e peça que continue refletindo.
Se o estudante der a resposta correta (por exemplo, dizendo que trocar dá 2/3 de chance de ganhar), parabenize brevemente e peça que justifique seu raciocínio e termine a conversa.
Nunca desvie do tema, mesmo que o estudante tente mudar de assunto.
Seja instigante, acolhedor, socrático, focado no paradoxo e coerente com a abordagem piagetiana.
"""

# URL do endpoint da API, usando o nome de modelo que sabemos que está disponível.
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

# Cabeçalhos necessários para a requisição HTTP.
headers = {
    'Content-Type': 'application/json'
}

# --- Gerenciamento do Histórico da Conversa ---
# st.session_state é usado para manter o histórico entre as interações.
if "history" not in st.session_state:
    # Define a mensagem de boas-vindas que aparecerá na primeira vez que o app for carregado.
    welcome_message = """
👋 E aí! Eu sou o Monty, seu parceiro nessa missão de decifrar o enigma das portas.

Mas já vou avisando:

🚫 Nada de resposta pronta

🎯 E nem papo fora do assunto

Aqui a ideia é fazer você pensar — eu só vou te dar dicas, pistas e perguntas que te ajudem a enxergar o que está por trás do tal Problema de Monty Hall.

💭 Bora começar? Manda aí sua primeira dúvida ou o que você acha que é a solução.
"""
    # Inicia o histórico com a mensagem de boas-vindas do assistente.
    st.session_state.history = [{"role": "assistant", "content": welcome_message}]

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
        {"role": "model", "parts": [{"text": "Entendido. Começarei a atuar como um tutor socrático, seguindo todas as regras."}]}
    ]

    # Adiciona o histórico real da conversa.
    for msg in history:
        # O papel do usuário é "user", o nosso é "assistant", mas para a API, o nosso papel é "model".
        role = "user" if msg["role"] == "user" else "model"
        # Ignora a mensagem de boas-vindas inicial ao enviar para a API, pois ela é apenas para exibição.
        if msg["content"] != st.session_state.history[0]["content"]:
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

