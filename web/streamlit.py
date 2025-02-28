import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os

# Fake data generation function
def generate_fake_data(paciente, data_inicio_periodo, tempo_inicio_periodo, data_fim_periodo, tempo_fim_periodo):
    # Generate fake timestamps between start and end period
    start_datetime = datetime.combine(data_inicio_periodo, tempo_inicio_periodo)
    end_datetime = datetime.combine(data_fim_periodo, tempo_fim_periodo)
    
    num_points = 100  # Number of data points to simulate
    timestamps = [start_datetime + timedelta(seconds=i*(end_datetime - start_datetime).total_seconds()/num_points) for i in range(num_points)]
    
    # Generate fake data for movement and other metrics
    movimento_x = np.random.randn(num_points)
    movimento_y = np.random.randn(num_points)
    movimento_z = np.random.randn(num_points)
    temperatura = np.random.normal(loc=37, scale=0.5, size=num_points)  # Temperature around 37°C
    batimento_cardiaco = np.random.normal(loc=80, scale=10, size=num_points)  # Heart rate around 80 BPM

    # Create DataFrame with the fake data
    df = pd.DataFrame({
        'timestamp': timestamps,
        'movimento_x': movimento_x,
        'movimento_y': movimento_y,
        'movimento_z': movimento_z,
        'temperatura': temperatura,
        'batimento_cardiaco': batimento_cardiaco
    })

    return df

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
    # Gerar dados falsos
    df = generate_fake_data(paciente, data_inicio_periodo, tempo_inicio_periodo, data_fim_periodo, tempo_fim_periodo)

    # Armazenar os dados na sessão
    st.session_state['dados_api'] = df

    # Exibição dos dados
    with placeholder.container():
        display_data()

    # Espera 10 segundos antes de atualizar os dados
    time.sleep(10)

    # Simula o refresh da página, sem `st.experimental_rerun()`
    placeholder.empty()
