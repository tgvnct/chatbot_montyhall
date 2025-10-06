import streamlit as st
import requests
import json

# --- Configuração da Página ---
st.set_page_config(
    page_title="Verificador de Modelos Gemini",
    page_icon="🔍",
    layout="centered",
)

st.title("🔍 Verificador de Modelos da API Gemini")
st.write("Este aplicativo testa sua chave de API para listar os modelos que ela tem permissão para usar.")

# --- Configuração da API do Gemini ---
# Tenta obter a chave de API dos segredos do Streamlit.
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    st.success("Chave de API encontrada com sucesso!")
except (FileNotFoundError, KeyError):
    st.error("Chave de API do Gemini não encontrada. Configure-a em 'Settings > Secrets'.")
    st.stop()

# --- Função para Listar Modelos ---
def list_available_models():
    """
    Faz uma chamada para a API do Google para obter a lista de modelos disponíveis.
    """
    # URL do endpoint para listar modelos.
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        st.write("Fazendo a chamada para a API...")
        response = requests.get(url, timeout=30)
        response.raise_for_status() # Lança um erro para respostas HTTP ruins (4xx ou 5xx).
        
        st.write("Resposta recebida com sucesso! Processando os dados...")
        data = response.json()
        
        st.subheader("Modelos Disponíveis para sua Chave de API:")
        
        if "models" in data and data["models"]:
            # Exibe os dados brutos para depuração completa
            st.json(data)
            
            st.subheader("Nomes dos Modelos Prontos para Usar:")
            # Extrai e exibe apenas os nomes dos modelos de forma clara
            for model in data["models"]:
                model_name = model.get("name")
                if model_name:
                    # O formato do nome é "models/gemini-pro", então extraímos a parte final
                    simple_name = model_name.split('/')[-1]
                    st.code(simple_name, language="text")
        else:
            st.warning("A API não retornou nenhum modelo disponível.")
            st.json(data)

    except requests.exceptions.RequestException as e:
        st.error(f"Ocorreu um erro de rede ou na API:")
        st.code(f"{e}\n\nResposta recebida:\n{response.text if 'response' in locals() else 'N/A'}", language="text")
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        st.error(f"Erro ao processar a resposta da API:")
        st.code(f"{e}\n\nJSON recebido:\n{data}", language="text")

# --- Botão para Executar a Verificação ---
if st.button("Listar Modelos Disponíveis"):
    with st.spinner("Buscando modelos..."):
        list_available_models()

