import streamlit as st
import pandas as pd
import joblib
import os

# Configuração inicial da página
st.set_page_config(
    page_title="Passos Mágicos - Análise de Risco",
    page_icon="🪄",
    layout="wide"
)

# Título e descrição
st.title("🪄 Passos Mágicos: Prevenção de Defasagem Escolar")
st.markdown("""
Esta ferramenta utiliza Inteligência Artificial para analisar o histórico de indicadores do aluno 
e prever a probabilidade de risco de defasagem educacional no ano atual.
""")

# Carregar o modelo treinado (com cache para não recarregar a cada clique)
@st.cache_resource
def carregar_modelo():
    # O caminho assume que o app.py está na raiz e o modelo na pasta models/
    caminho = os.path.join('models', 'modelo_risco_defasagem.pkl')
    return joblib.load(caminho)

try:
    modelo = carregar_modelo()
except FileNotFoundError:
    st.error("Erro: O ficheiro do modelo não foi encontrado. Certifique-se de que exportou o '.pkl' para a pasta 'models/'.")
    st.stop()

st.divider()

st.subheader("Insira os dados históricos do aluno")

# Criando colunas para organizar o formulário
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📅 Indicadores de 2022")
    inde_22 = st.number_input("INDE 2022 (Índice Global)", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
    ida_22 = st.number_input("IDA 2022 (Desempenho Académico)", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
    ieg_22 = st.number_input("IEG 2022 (Engajamento)", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
    iaa_22 = st.number_input("IAA 2022 (Autoavaliação)", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
    ips_22 = st.number_input("IPS 2022 (Psicossocial)", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
    ipv_22 = st.number_input("IPV 2022 (Ponto de Virada)", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
    ian_22 = st.number_input("IAN 2022 (Adequação de Nível)", min_value=0.0, max_value=10.0, value=10.0, step=0.1)

with col2:
    st.markdown("### 📅 Indicadores de 2023")
    inde_23 = st.number_input("INDE 2023 (Índice Global)", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
    ida_23 = st.number_input("IDA 2023 (Desempenho Académico)", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
    ieg_23 = st.number_input("IEG 2023 (Engajamento)", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
    iaa_23 = st.number_input("IAA 2023 (Autoavaliação)", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
    ips_23 = st.number_input("IPS 2023 (Psicossocial)", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
    ipv_23 = st.number_input("IPV 2023 (Ponto de Virada)", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
    ian_23 = st.number_input("IAN 2023 (Adequação de Nível)", min_value=0.0, max_value=10.0, value=10.0, step=0.1)

st.divider()

# Botão de previsão
if st.button("🔍 Analisar Risco de Defasagem", use_container_width=True):
    
    # 1. Calcular as variáveis de evolução em background
    evolucao_inde = inde_23 - inde_22
    evolucao_ida = ida_23 - ida_22
    
    # 2. Montar o DataFrame com a exata mesma ordem das colunas do treino
    features = [
        'INDE_2022', 'IDA_2022', 'IEG_2022', 'IAA_2022', 'IPS_2022', 'IPV_2022', 'IAN_2022',
        'INDE_2023', 'IDA_2023', 'IEG_2023', 'IAA_2023', 'IPS_2023', 'IPV_2023', 'IAN_2023',
        'Evolucao_INDE_22_23', 'Evolucao_IDA_22_23'
    ]
    
    dados_aluno = pd.DataFrame([[
        inde_22, ida_22, ieg_22, iaa_22, ips_22, ipv_22, ian_22,
        inde_23, ida_23, ieg_23, iaa_23, ips_23, ipv_23, ian_23,
        evolucao_inde, evolucao_ida
    ]], columns=features)
    
    # 3. Fazer a previsão
    predicao = modelo.predict(dados_aluno)[0]
    probabilidades = modelo.predict_proba(dados_aluno)[0]
    prob_risco = probabilidades[1] * 100
    
    # 4. Exibir o resultado de forma visual
    st.subheader("Resultado da Análise")
    
    if predicao == 1:
        st.error(f"🚨 **ALERTA DE RISCO:** O modelo indica que este aluno tem **{prob_risco:.1f}%** de probabilidade de entrar em defasagem.")
        st.write("Recomendação: Acionar equipa de acompanhamento psicopedagógico para intervenção preventiva, com foco na análise dos motivos da queda de indicadores passados.")
    else:
        st.success(f"✅ **BOM DESEMPENHO:** O aluno parece estar a seguir uma trajetória positiva (Risco de apenas {prob_risco:.1f}%).")
        st.write("Recomendação: Manter o estímulo e acompanhamento padrão da fase atual.")