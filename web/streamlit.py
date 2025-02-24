import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time

# URL da API Flask para obter dados dos pacientes
API_URL = os.getenv('FLASK_URL')

# Barra lateral para seleção de paciente e período
with st.sidebar:
    st.title('PSM - Post Surgery Monitoring')
    paciente = st.selectbox('Paciente', ['1', '2', '3'])

    coluna_esquerda, coluna_direita = st.columns(2)
    data_inicio_periodo = coluna_esquerda.date_input('Data de Início')
    tempo_inicio_periodo = coluna_direita.time_input('Horário de Início')
    data_fim_periodo = coluna_esquerda.date_input('Data de Fim')
    tempo_fim_periodo = coluna_direita.time_input('Horário de Fim')

# Criar um placeholder para os dados
placeholder = st.empty()

# Função para buscar dados da API
def fetch_data(paciente, data_inicio_periodo, tempo_inicio_periodo, data_fim_periodo, tempo_fim_periodo):
    params = {
        'paciente': paciente,
        'periodo_inicio': datetime.combine(data_inicio_periodo, tempo_inicio_periodo).isoformat(),
        'periodo_fim': datetime.combine(data_fim_periodo, tempo_fim_periodo).isoformat()
    }

    try:
        resposta = requests.get(API_URL, params=params)
        if resposta.status_code == 200:
            return resposta.json()
        else:
            st.error(f"Erro ao buscar dados: {resposta.text}")
    except Exception as e:
        st.error(f"Erro na comunicação com a API: {e}")

    return None

# Função para exibir dados
def display_data():
    if 'dados_api' in st.session_state and not st.session_state['dados_api'].empty:
        df = st.session_state['dados_api']

        st.header('Dados Recebidos')
        st.write(df)

        st.header('Movimento')
        st.line_chart(df[['timestamp', 'movimento_x', 'movimento_y', 'movimento_z']].set_index('timestamp'))

        st.header('Temperatura')
        st.line_chart(df[['timestamp', 'temperatura']].set_index('timestamp'), color="#8A84E2")

        st.header('Batimento Cardíaco')
        st.line_chart(df[['timestamp', 'batimento_cardiaco']].set_index('timestamp'), color="#EE2E31")

# Atualiza os dados a cada 10 segundos
while True:
    # Chama a função para buscar os dados
    dados_api = fetch_data(paciente, data_inicio_periodo, tempo_inicio_periodo, data_fim_periodo, tempo_fim_periodo)

    if dados_api:
        # Criando DataFrame corretamente para cada métrica
        df = pd.DataFrame(dados_api)  # Envolvendo em lista para evitar erro de iteração

        # Tratando dados individuais (float)
        if 'timestamp' in df:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Armazenar os dados na sessão
        st.session_state['dados_api'] = df

        # Exibição dos dados
        with placeholder.container():
            display_data()

    # Espera 10 segundos antes de atualizar os dados
    time.sleep(20)

    # Simula o refresh da página, sem `st.experimental_rerun()`
    placeholder.empty()
