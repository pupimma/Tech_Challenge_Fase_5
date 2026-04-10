import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os
import time

# ----------------------------------------------------------------------
# CONFIGURAÇÃO E CARREGAMENTO
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Datathon - ONG Passos Mágicos", 
    page_icon="📊", 
    layout="wide"
)

@st.cache_data
def carregar_dados():
    caminho_script = os.path.abspath(__file__)
    raiz_projeto = os.path.dirname(os.path.dirname(caminho_script))
    caminho_arquivo = os.path.join(raiz_projeto, 'data', 'BASE DE DADOS PEDE 2024 - DATATHON.xlsx')
    
    if not os.path.exists(caminho_arquivo):
        diretorio_atual = os.path.dirname(caminho_script)
        caminho_arquivo = os.path.join(diretorio_atual, 'data', 'BASE DE DADOS PEDE 2024 - DATATHON.xlsx')

    if not os.path.exists(caminho_arquivo):
        st.error(f"Arquivo de dados não encontrado em: {caminho_arquivo}")
        st.stop()
        
    return (pd.read_excel(caminho_arquivo, sheet_name='PEDE2022'),
            pd.read_excel(caminho_arquivo, sheet_name='PEDE2023'),
            pd.read_excel(caminho_arquivo, sheet_name='PEDE2024'))

@st.cache_data
def processar_base_mestra(df_22, df_23, df_24):
    # Padronização de colunas críticas
    df_22_p = df_22.rename(columns={'Nome': 'Nome_Anonimizado', 'Ano nasc': 'Data_Nascimento', 'Idade 22': 'Idade', 'INDE 22': 'INDE', 'Pedra 22': 'Pedra'}).copy()
    df_22_p['Ano_Referencia'] = 2022

    df_23_p = df_23.rename(columns={'Data de Nasc': 'Data_Nascimento', 'INDE 2023': 'INDE', 'Pedra 2023': 'Pedra'}).copy()
    df_23_p['Ano_Referencia'] = 2023

    df_24_p = df_24.rename(columns={'Data de Nasc': 'Data_Nascimento', 'INDE 2024': 'INDE', 'Pedra 2024': 'Pedra'}).copy()
    df_24_p['Ano_Referencia'] = 2024

    cols = ['Ano_Referencia', 'RA', 'Nome_Anonimizado', 'Fase', 'Turma', 'Data_Nascimento', 'Idade', 'Gênero', 'INDE', 'Pedra', 'IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP']
    df = pd.concat([df_22_p[[c for c in cols if c in df_22_p]], 
                    df_23_p[[c for c in cols if c in df_23_p]], 
                    df_24_p[[c for c in cols if c in df_24_p]]], ignore_index=True)
    
    df['INDE'] = pd.to_numeric(df['INDE'].astype(str).str.replace(',', '.'), errors='coerce')
    
    for c in ['Fase', 'Gênero', 'Pedra']:
        df[c] = df[c].astype(str).str.strip().replace({'nan': 'N/I', 'None': 'N/I', '': 'N/I'})
    
    df['Pedra'] = df['Pedra'].replace({'Agata': 'Ágata', 'INCLUIR': 'Sem Classificação'})
    return df

try:
    d22, d23, d24 = carregar_dados()
    df_master = processar_base_mestra(d22, d23, d24)
except Exception as e:
    st.error(f"Falha na pipeline de dados: {e}")
    st.stop()

# ----------------------------------------------------------------------
# INTERFACE LATERAL E FILTRAGEM
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Filtros de Análise")
    
    # Filtro de Fase
    fases_lista = df_master['Fase'].unique().tolist()
    fases_disponiveis = sorted([str(f) for f in fases_lista if pd.notna(f)])
    fases_sel = st.multiselect("Fase da ONG:", options=fases_disponiveis)
    
    df_f = df_master[df_master['Fase'].isin(fases_sel)] if fases_sel else df_master
    
    # Filtro de Gênero
    generos_lista = df_f['Gênero'].unique().tolist()
    generos_disponiveis = sorted([str(g) for g in generos_lista if pd.notna(g)])
    generos_sel = st.multiselect("Gênero Aluno:", options=generos_disponiveis)
    
    df_f = df_f[df_f['Gênero'].isin(generos_sel)] if generos_sel else df_f
    
    # Filtro de Pedra (Onde deu o erro no seu print)
    pedras_lista = df_f['Pedra'].unique().tolist()
    # Forçamos a conversão para string e removemos nulos antes do sorted
    pedras_disponiveis = sorted([str(p) for p in pedras_lista if pd.notna(p)])
    pedras_sel = st.multiselect("Classificação (Pedra):", options=pedras_disponiveis)
    
    df_filtrado = df_f[df_f['Pedra'].isin(pedras_sel)] if pedras_sel else df_f

    st.divider()
    st.caption("🚀 **Datathon Fase 5**")
    st.caption("Desenvolvido por: Mauro Pupim")
    st.info("Nota: Este projeto utilizou ferramentas de IA Generativa para otimização de código e suporte na arquitetura Streamlit.")

# ----------------------------------------------------------------------
# ESTRUTURA DE NAVEGAÇÃO
# ----------------------------------------------------------------------
st.title("📊 Painel Analítico - Passos Mágicos")
st.divider()

aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
    "📝 Originais", "⚙️ Engenharia", "✅ Consolidado", "📈 Dashboard", "🤖 Predição IA", "💡 Insights"
])

with aba1:
    ano = st.radio("Ano:", ["2022", "2023", "2024"], horizontal=True)
    mapping = {"2022": d22, "2023": d23, "2024": d24}
    st.dataframe(mapping[ano], use_container_width=True)

with aba2:
    st.write(f"Pipeline de normalização concluída: {len(df_master)} registros processados.")
    st.dataframe(df_master.head(50), use_container_width=True)

with aba3:
    st.write(f"Registros filtrados: {len(df_filtrado)}")
    st.dataframe(df_filtrado, use_container_width=True)

with aba4:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Evolução do INDE")
        df_inde = df_filtrado.groupby('Ano_Referencia')['INDE'].mean().reset_index()
        st.plotly_chart(px.line(df_inde, x='Ano_Referencia', y='INDE', markers=True), use_container_width=True)
    with c2:
        st.subheader("Distribuição por Pedra")
        df_p = df_filtrado.groupby(['Ano_Referencia', 'Pedra']).size().reset_index(name='Total')
        st.plotly_chart(px.bar(df_p, x='Ano_Referencia', y='Total', color='Pedra', barmode='group'), use_container_width=True)

with aba5:
    st.subheader("🤖 Algoritmo Preditivo (Random Forest)")
    
    def get_model():
        path = 'modelo_passos_magicos.pkl'
        if not os.path.exists(path):
            path = os.path.join(os.path.dirname(__file__), path)
        try: return joblib.load(path)
        except: return None

    modelo = get_model()
    if modelo is None:
        st.error("Modelo preditivo (.pkl) não localizado na raiz do projeto.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            ida = st.slider("Desempenho (IDA)", 0.0, 10.0, 5.0)
            ieg = st.slider("Engajamento (IEG)", 0.0, 10.0, 5.0)
        with col2:
            ian = st.slider("Nível (IAN)", 0.0, 10.0, 5.0)
            ips = st.slider("Psicossocial (IPS)", 0.0, 10.0, 5.0)
        with col3:
            ipp = st.slider("Psicopedagógico (IPP)", 0.0, 10.0, 5.0)
            iaa = st.slider("Autoavaliação (IAA)", 0.0, 10.0, 5.0)

        if st.button("Executar Predição"):
            entrada = pd.DataFrame([[ian, ida, ieg, iaa, ips, ipp]], columns=['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP'])
            prob = modelo.predict_proba(entrada)[0][1] * 100
            st.divider()
            if prob >= 60: st.error(f"🚨 ALTO RISCO: {prob:.1f}%")
            elif prob >= 30: st.warning(f"⚠️ RISCO MODERADO: {prob:.1f}%")
            else: st.success(f"✅ BAIXO RISCO: {prob:.1f}%")

with aba6:
    st.subheader("💡 Insights Estratégicos")
    c_ins1, c_ins2 = st.columns(2)
    
    with c_ins1:
        d22_m = df_master[df_master['Ano_Referencia'] == 2022]['INDE'].mean()
        d24_m = df_master[df_master['Ano_Referencia'] == 2024]['INDE'].mean()
        if d22_m and d24_m:
            delta = ((d24_m - d22_m) / d22_m) * 100
            st.metric("Crescimento INDE (2022-2024)", f"{d24_m:.2f}", f"{delta:.1f}%")

    with c_ins2:
        alvo = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP']
        exist = [c for c in alvo if c in df_master.columns]
        if exist:
            pior = df_master[df_master['Ano_Referencia'] == 2024][exist].mean().idxmin()
            st.warning(f"Foco Pedagógico: Indicador **{pior}** requer atenção imediata em 2024.")

    st.success("""
    **Conclusões Finais:**
    * O engajamento (IEG) foi identificado como a variável de maior impacto na estabilidade do aluno.
    * O modelo permite identificar o risco psicossocial (IPS) antes que ele afete as notas acadêmicas (IDA).
    """)