import numpy as np
import pandas as pd
import streamlit as st

# Barra lateral
with st.sidebar:
    st.title('PSM - Post Surgery Monitoring')
    paciente = st.selectbox('Paciente', [1, 2, 3])

    coluna_esquerda, coluna_direita = st.columns(2)
    data_inicio_periodo = coluna_esquerda.date_input('Data de Início')
    tempo_inicio_periodo = coluna_direita.time_input('Horário de Início')
    data_fim_periodo = coluna_esquerda.date_input('Data de Fim')
    tempo_fim_periodo = coluna_direita.time_input('Horário de Fim')

    st.button('Enviar')

# Coletar dados do Firebase
dados_movimento = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['X', 'Y', 'Z'])

dados_temperatura = pd.DataFrame(
    np.random.randn(20, 1),
    columns=['Temperatura'])

dados_batimento_cardiaco = pd.DataFrame(
    np.random.randn(20, 1),
    columns=['Batimento Cardíaco'])

# Gráficos
st.header('Movimento')
st.line_chart(dados_movimento)

st.header('Temperatura')
st.line_chart(dados_temperatura, color="#8A84E2")

st.header('Batimento Cardíaco')
st.line_chart(dados_batimento_cardiaco, color="#EE2E31")
