import streamlit as st
import pandas as pd
import plotly.express as px
import time
import joblib
import numpy as np
import os

st.set_page_config(page_title="Tech Challenge - Fase 5", layout="wide")

# ----------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Tech Challenge - Fase 5", 
    page_icon="📊", 
    layout="wide"
)

# ----------------------------------------------------------------------
# 2. FUNÇÕES DE CARREGAMENTO E TRATAMENTO DE DADOS
# ----------------------------------------------------------------------
@st.cache_data
def carregar_dados():
    # 1. Pega o caminho absoluto de onde este arquivo app.py está
    caminho_script = os.path.abspath(__file__)
    
    # 2. Sobe os níveis necessários até achar a pasta raiz do projeto (Fase 5)
    # Se o app.py estiver dentro de 'models', precisamos subir 1 nível (dirname do dirname)
    # Se estiver na raiz, subiria apenas 1. Vamos garantir que ele ache a 'data'
    raiz_projeto = os.path.dirname(os.path.dirname(caminho_script))
    
    # 3. Tenta montar o caminho na raiz. Se não achar, tenta na pasta atual.
    caminho_arquivo = os.path.join(raiz_projeto, 'data', 'BASE DE DADOS PEDE 2024 - DATATHON.xlsx')
    
    # Backup: se você moveu a pasta data para dentro de models por engano
    if not os.path.exists(caminho_arquivo):
        diretorio_atual = os.path.dirname(caminho_script)
        caminho_arquivo = os.path.join(diretorio_atual, 'data', 'BASE DE DADOS PEDE 2024 - DATATHON.xlsx')

    if not os.path.exists(caminho_arquivo):
        st.error(f"❌ Arquivo NÃO encontrado! Verifique se a pasta 'data' está no local correto.\nTentamos em: {caminho_arquivo}")
        st.stop()
        
    df_22 = pd.read_excel(caminho_arquivo, sheet_name='PEDE2022')
    df_23 = pd.read_excel(caminho_arquivo, sheet_name='PEDE2023')
    df_24 = pd.read_excel(caminho_arquivo, sheet_name='PEDE2024')
    
    return df_22, df_23, df_24

@st.cache_data
def normalizar_e_consolidar(df_22, df_23, df_24):
    df_22_padrao = df_22.rename(columns={'Nome': 'Nome_Anonimizado', 'Ano nasc': 'Data_Nascimento', 'Idade 22': 'Idade', 'INDE 22': 'INDE', 'Pedra 22': 'Pedra'}).copy()
    df_22_padrao['Ano_Referencia'] = 2022

    df_23_padrao = df_23.rename(columns={'Data de Nasc': 'Data_Nascimento', 'INDE 2023': 'INDE', 'Pedra 2023': 'Pedra'}).copy()
    df_23_padrao['Ano_Referencia'] = 2023

    df_24_padrao = df_24.rename(columns={'Data de Nasc': 'Data_Nascimento', 'INDE 2024': 'INDE', 'Pedra 2024': 'Pedra'}).copy()
    df_24_padrao['Ano_Referencia'] = 2024

    colunas_finais = ['Ano_Referencia', 'RA', 'Nome_Anonimizado', 'Fase', 'Turma', 'Data_Nascimento', 'Idade', 'Gênero', 'Instituição de ensino', 'INDE', 'Pedra', 'IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP']

    df_22_final = df_22_padrao[[col for col in colunas_finais if col in df_22_padrao.columns]]
    df_23_final = df_23_padrao[[col for col in colunas_finais if col in df_23_padrao.columns]]
    df_24_final = df_24_padrao[[col for col in colunas_finais if col in df_24_padrao.columns]]

    df_consolidado = pd.concat([df_22_final, df_23_final, df_24_final], ignore_index=True)
    
    df_consolidado['INDE'] = df_consolidado['INDE'].astype(str).str.replace(',', '.')
    df_consolidado['INDE'] = pd.to_numeric(df_consolidado['INDE'], errors='coerce')
    
    for col in ['Fase', 'Gênero', 'Pedra']:
        df_consolidado[col] = df_consolidado[col].astype(str).str.strip()
        df_consolidado[col] = df_consolidado[col].replace({'nan': 'Não Informado', 'None': 'Não Informado', '': 'Não Informado'})
    
    df_consolidado['Pedra'] = df_consolidado['Pedra'].replace({'Agata': 'Ágata', 'INCLUIR': 'Sem Classificação'})
    
    return df_consolidado

# ----------------------------------------------------------------------
# 3. EXECUÇÃO DOS DADOS
# ----------------------------------------------------------------------
try:
    df_2022, df_2023, df_2024 = carregar_dados()
    df_master = normalizar_e_consolidar(df_2022, df_2023, df_2024)
except Exception as e:
    st.error(f"Erro ao processar os dados. Detalhe: {e}")
    st.stop()

# ----------------------------------------------------------------------
# 4. MENU LATERAL E FILTROS DINÂMICOS (VERSÃO FINAL BLINDADA)
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Filtros Interativos")
    
    # Criamos listas padrão para evitar erros de "não definido"
    fases_selecionadas = []
    generos_selecionados = []
    pedras_selecionadas = []

    # 1. Filtro de Fase
    fases_lista = df_master['Fase'].dropna().unique().tolist()
    fases_disponiveis = sorted([str(f) for f in fases_lista])
    fases_selecionadas = st.multiselect("Fase da ONG:", options=fases_disponiveis, default=[], placeholder="Escolha as fases...")
    
    df_temp1 = df_master[df_master['Fase'].isin(fases_selecionadas)] if fases_selecionadas else df_master
    
    # 2. Filtro de Gênero
    generos_lista = df_temp1['Gênero'].dropna().unique().tolist()
    generos_disponiveis = sorted([str(g) for g in generos_lista])
    generos_selecionados = st.multiselect("Gênero do Aluno:", options=generos_disponiveis, default=[], placeholder="Escolha o gênero...")
    
    df_temp2 = df_temp1[df_temp1['Gênero'].isin(generos_selecionados)] if generos_selecionados else df_temp1
    
    # 3. Filtro de Pedra
    pedras_lista = df_temp2['Pedra'].dropna().unique().tolist()
    pedras_disponiveis = sorted([str(p) for p in pedras_lista])
    pedras_selecionadas = st.multiselect("Classificação (Pedra):", options=pedras_disponiveis, default=[], placeholder="Escolha as pedras...")
    
    st.divider()
    st.info("Painel Analítico - Datathon Fase 5")

# --- LÓGICA DE FILTRAGEM GLOBAL (PRECISA ESTAR FORA DO SIDEBAR) ---
# Aqui criamos a variável df_filtrado que a Aba 5 e 6 tanto pedem
df_filtrado = df_master.copy()

if fases_selecionadas:
    df_filtrado = df_filtrado[df_filtrado['Fase'].isin(fases_selecionadas)]

if generos_selecionados:
    df_filtrado = df_filtrado[df_filtrado['Gênero'].isin(generos_selecionados)]

if pedras_selecionadas:
    df_filtrado = df_filtrado[df_filtrado['Pedra'].isin(pedras_selecionadas)]

# ----------------------------------------------------------------------
# 5. CONSTRUÇÃO DAS ABAS
# ----------------------------------------------------------------------
st.title("📊 Análise Datathon - ONG Passos Mágicos")
st.markdown("Plataforma de visualização e predição de risco educacional.")
st.divider()

# Criamos as 6 gavetas. Agora o Python sabe que aba5 e aba6 existem!
aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
    "📝 Bases Originais", 
    "⚙️ Engenharia", 
    "✅ Base Consolidada", 
    "📈 Dashboard",
    "🤖 Inteligência Artificial",
    "💡 Insights e Conclusões"
])

with aba1:
    st.markdown("### Visualização dos dados brutos")
    ano_selecionado = st.radio("Selecione o ano para visualizar:", ["2022", "2023", "2024"], horizontal=True)
    if ano_selecionado == "2022":
        st.dataframe(df_2022, use_container_width=True)
    elif ano_selecionado == "2023":
        st.dataframe(df_2023, use_container_width=True)
    else:
        st.dataframe(df_2024, use_container_width=True)

with aba2:
    st.markdown("### Processo de Normalização")
    st.write(f"**Total de registros:** {len(df_master)} linhas.")
    st.dataframe(df_master.head(50), use_container_width=True)

with aba3:
    st.markdown("### ✅ Base Consolidada")
    st.write(f"**Registros encontrados com os filtros atuais:** {len(df_filtrado)} linhas.")
    st.dataframe(df_filtrado, use_container_width=True)

with aba4:
    st.markdown("### 📈 Indicadores de Desempenho")
    col_graf1, col_graf2 = st.columns(2)
    with col_graf1:
        st.subheader("Evolução do INDE Médio")
        df_inde_medio = df_filtrado.groupby('Ano_Referencia')['INDE'].mean().reset_index()
        fig_inde = px.line(df_inde_medio, x='Ano_Referencia', y='INDE', markers=True)
        fig_inde.update_xaxes(type='category', title="Ano de Referência")
        st.plotly_chart(fig_inde, use_container_width=True)
    with col_graf2:
        st.subheader("Distribuição por Pedra")
        df_pedras = df_filtrado.groupby(['Ano_Referencia', 'Pedra']).size().reset_index(name='Quantidade')
        fig_pedras = px.bar(df_pedras, x='Ano_Referencia', y='Quantidade', color='Pedra', barmode='group')
        fig_pedras.update_xaxes(type='category', title="Ano de Referência")
        st.plotly_chart(fig_pedras, use_container_width=True)

with aba5:
    st.markdown("### 🤖 Previsão de Risco de Defasagem (Machine Learning)")
    
    def carregar_modelo():
        caminho_modelo = 'modelo_passos_magicos.pkl'
        if not os.path.exists(caminho_modelo):
            diretorio_script = os.path.dirname(os.path.abspath(__file__))
            caminho_modelo = os.path.join(diretorio_script, 'modelo_passos_magicos.pkl')
        try:
            return joblib.load(caminho_modelo)
        except:
            return None

    modelo = carregar_modelo()
    if modelo is None:
        st.error("❌ Arquivo 'modelo_passos_magicos.pkl' não encontrado.")
    else:
        col_ia1, col_ia2, col_ia3 = st.columns(3)
        with col_ia1:
            fase_input = st.selectbox("Fase do Aluno", options=fases_disponiveis if 'fases_disponiveis' in locals() else ["Fase 1"])
            ida_input = st.slider("Desempenho (IDA)", 0.0, 10.0, 5.0)
            ieg_input = st.slider("Engajamento (IEG)", 0.0, 10.0, 5.0)
        with col_ia2:
            ian_input = st.slider("Nível (IAN)", 0.0, 10.0, 5.0)
            ips_input = st.slider("Psicossocial (IPS)", 0.0, 10.0, 5.0)
            ipp_input = st.slider("Psicopedagógico (IPP)", 0.0, 10.0, 5.0)
        with col_ia3:
            iaa_input = st.slider("Autoavaliação (IAA)", 0.0, 10.0, 5.0)

        if st.button("Gerar Análise Preditiva"):
            dados_entrada = pd.DataFrame([[ian_input, ida_input, ieg_input, iaa_input, ips_input, ipp_input]], 
                                         columns=['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP'])
            probabilidade = modelo.predict_proba(dados_entrada)[0][1]
            risco = probabilidade * 100 
            st.divider()
            if risco >= 60: st.error(f"🚨 ALTO RISCO: {risco:.1f}%")
            elif risco >= 30: st.warning(f"⚠️ RISCO MODERADO: {risco:.1f}%")
            else: st.success(f"✅ BAIXO RISCO: {risco:.1f}%")

with aba6:
    st.markdown("### 💡 Insights Estratégicos")
    col_ins1, col_ins2 = st.columns(2)
    with col_ins1:
        st.info("#### 📈 Evolução do INDE")
        df_22 = df_master[df_master['Ano_Referencia'] == 2022]
        df_24 = df_master[df_master['Ano_Referencia'] == 2024]
        if not df_22.empty and not df_24.empty:
            inde_22, inde_24 = df_22['INDE'].mean(), df_24['INDE'].mean()
            delta = ((inde_24 - inde_22) / inde_22) * 100
            st.metric("Crescimento (2022-2024)", f"{inde_24:.2f}", f"{delta:.1f}%")
    with col_ins2:
        st.warning("#### ⚠️ Pontos de Atenção")
        existentes = [c for c in ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP'] if c in df_master.columns]
        if existentes:
            df_2024_medias = df_master[df_master['Ano_Referencia'] == 2024][existentes].mean()
            st.write(f"Menor desempenho em 2024: **{df_2024_medias.idxmin()}**")

# ----------------------------------------------------------------------
# ABA 6: INSIGHTS E CONCLUSÕES (VERSÃO SEGURA)
# ----------------------------------------------------------------------
with aba6:
    st.markdown("### 💡 Insights Estratégicos")
    
    col_ins1, col_ins2 = st.columns(2)
    
    with col_ins1:
        st.info("#### 📈 Evolução do INDE")
        # Calculamos as médias garantindo que temos dados
        df_22 = df_master[df_master['Ano_Referencia'] == 2022]
        df_24 = df_master[df_master['Ano_Referencia'] == 2024]
        
        if not df_22.empty and not df_24.empty:
            inde_2022 = df_22['INDE'].mean()
            inde_2024 = df_24['INDE'].mean()
            delta = ((inde_2024 - inde_2022) / inde_2022) * 100 if inde_2022 != 0 else 0
            
            st.metric("Crescimento do Índice Geral (2022-2024)", 
                      f"{inde_2024:.2f}", 
                      f"{delta:.1f}% em relação a 2022")
        else:
            st.write("Dados insuficientes para calcular a evolução temporal.")

    with col_ins2:
        st.warning("#### ⚠️ Pontos de Atenção")
        indicadores_alvo = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP']
        # Filtramos apenas as colunas que realmente chegaram no df_master
        existentes = [c for c in indicadores_alvo if c in df_master.columns]
        
        if existentes:
            df_2024_medias = df_master[df_master['Ano_Referencia'] == 2024][existentes].mean()
            if not df_2024_medias.empty:
                pior_indicador = df_2024_medias.idxmin()
                valor_pior = df_2024_medias.min()
                st.write(f"O indicador com menor desempenho médio em 2024 é o **{pior_indicador}** (Nota: {valor_pior:.2f}).")
                st.write("📌 **Recomendação:** Focar o plano de ação pedagógico neste pilar.")
        else:
            st.write("Sub-indicadores não encontrados na base consolidada.")

    st.divider()
    st.markdown("#### 🎯 Conclusões Finais")
    st.success("""
    * O modelo **Random Forest** validou que a combinação de baixo engajamento (IEG) e desempenho acadêmico (IDA) são os principais gatilhos de risco.
    * A base de dados consolidada permite identificar alunos em 'zona de silêncio' (onde as notas ainda são boas, mas o psicossocial IPS começou a cair).
    """)