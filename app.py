import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="Painel Analítico - Passos Mágicos", page_icon="📊", layout="wide")

@st.cache_data
def carregar_dados():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_arquivo = os.path.join(diretorio_atual, 'data', 'BASE DE DADOS PEDE 2024 - DATATHON.xlsx')
    if not os.path.exists(caminho_arquivo):
        raiz = os.path.dirname(diretorio_atual)
        caminho_arquivo = os.path.join(raiz, 'data', 'BASE DE DADOS PEDE 2024 - DATATHON.xlsx')
    
    if not os.path.exists(caminho_arquivo):
        st.error("Arquivo de dados não encontrado na pasta /data.")
        st.stop()
        
    return (pd.read_excel(caminho_arquivo, sheet_name='PEDE2022'),
            pd.read_excel(caminho_arquivo, sheet_name='PEDE2023'),
            pd.read_excel(caminho_arquivo, sheet_name='PEDE2024'))

@st.cache_data
def processar_base(df_22, df_23, df_24):
    d22 = df_22.rename(columns={'Nome': 'Nome_Anon', 'INDE 22': 'INDE', 'Pedra 22': 'Pedra'}).copy()
    d22['Ano_Ref'] = 2022
    d23 = df_23.rename(columns={'INDE 2023': 'INDE', 'Pedra 2023': 'Pedra'}).copy()
    d23['Ano_Ref'] = 2023
    d24 = df_24.rename(columns={'INDE 2024': 'INDE', 'Pedra 2024': 'Pedra'}).copy()
    d24['Ano_Ref'] = 2024

    cols = ['Ano_Ref', 'RA', 'Fase', 'Turma', 'Gênero', 'INDE', 'Pedra', 'IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP']
    df = pd.concat([d22[[c for c in cols if c in d22]], 
                    d23[[c for c in cols if c in d23]], 
                    d24[[c for c in cols if c in d24]]], ignore_index=True)
    
    df['INDE'] = pd.to_numeric(df['INDE'].astype(str).str.replace(',', '.'), errors='coerce')
    for c in ['Fase', 'Gênero', 'Pedra']:
        df[c] = df[c].astype(str).str.strip().replace({'nan': 'N/I', 'None': 'N/I', '': 'N/I'})
    return df

try:
    raw22, raw23, raw24 = carregar_dados()
    df_master = processar_base(raw22, raw23, raw24)
except Exception as e:
    st.error(f"Falha na pipeline: {e}")
    st.stop()

# 2. FILTROS LATERAIS (RESTAURADOS CONFORME O PRINT)
with st.sidebar:
    st.header("⚙️ Filtros de Análise")
    
    fases = sorted([str(f) for f in df_master['Fase'].unique() if pd.notna(f)])
    fase_sel = st.multiselect("Fase da ONG:", options=fases)
    df_f = df_master[df_master['Fase'].isin(fase_sel)] if fase_sel else df_master
    
    generos = sorted([str(g) for g in df_f['Gênero'].unique() if pd.notna(g)])
    gen_sel = st.multiselect("Gênero Aluno:", options=generos)
    df_f = df_f[df_f['Gênero'].isin(gen_sel)] if gen_sel else df_f
    
    pedras = sorted([str(p) for p in df_f['Pedra'].unique() if pd.notna(p)])
    pedra_sel = st.multiselect("Classificação (Pedra):", options=pedras)
    df_filtrado = df_f[df_f['Pedra'].isin(pedra_sel)] if pedra_sel else df_f

    st.divider()
    st.caption("🚀 **Datathon Fase 5**")
    st.caption("Desenvolvido por: Mauro Pupim")
    st.info("Nota: Este projeto utilizou ferramentas de IA Generativa para otimização de código e suporte na arquitetura Streamlit.")

# 3. INTERFACE DE ABAS
st.title("📊 Painel Analítico - Passos Mágicos")
st.divider()

aba_orig, aba_eng, aba_cons, aba_dash, aba_ia, aba_ins = st.tabs([
    "📓 Originais", "⚙️ Engenharia", "✅ Consolidado", "📈 Dashboard", "🤖 Predição IA", "💡 Insights"
])

with aba_orig:
    ano = st.radio("Selecione o Ano:", ["2022", "2023", "2024"], horizontal=True)
    mapping = {"2022": raw22, "2023": raw23, "2024": raw24}
    st.dataframe(mapping[ano], use_container_width=True)

with aba_eng:
    st.subheader("Processamento de Dados")
    st.write(f"Total de registros normalizados: {len(df_master)}")
    st.dataframe(df_master.head(100), use_container_width=True)

with aba_cons:
    st.subheader("Visualização da Base Filtrada")
    st.dataframe(df_filtrado, use_container_width=True)

with aba_dash:
    st.subheader("Indicadores Críticos de Gestão")
    k1, k2, k3 = st.columns(3)
    k1.metric("Volume de Alunos", len(df_filtrado))
    k2.metric("Média INDE Geral", f"{df_filtrado['INDE'].mean():.2f}")
    risco_24 = len(df_filtrado[(df_filtrado['Ano_Ref'] == 2024) & (df_filtrado['IAN'] < 10)])
    k3.metric("Alerta de Risco (IAN)", risco_24, delta="Atenção Prioritária", delta_color="inverse")
    
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.line(df_filtrado.groupby('Ano_Ref')['INDE'].mean().reset_index(), x='Ano_Ref', y='INDE', title="Evolução INDE", markers=True), use_container_width=True)
    with c2:
        st.plotly_chart(px.bar(df_filtrado.groupby(['Ano_Ref', 'Pedra']).size().reset_index(name='Total'), x='Ano_Ref', y='Total', color='Pedra', title="Distribuição Pedras", barmode='group'), use_container_width=True)

with aba_ia:
    st.subheader("🤖 IA Preditiva (Random Forest)")
    path_model = 'modelo_passos_magicos.pkl'
    if os.path.exists(path_model):
        modelo = joblib.load(path_model)
        with st.expander("Simulador de Risco Educacional", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                i23_inde = st.slider("INDE Atual (2023)", 0.0, 10.0, 7.0)
                i23_ida = st.slider("Desempenho (IDA)", 0.0, 10.0, 7.0)
                i23_ieg = st.slider("Engajamento (IEG)", 0.0, 10.0, 7.0)
                i23_iaa = st.slider("Autoavaliação (IAA)", 0.0, 10.0, 7.0)
                i23_ips = st.slider("Social (IPS)", 0.0, 10.0, 7.0)
            with col2:
                d_inde = st.number_input("Evolução INDE (Ano Anterior)", -5.0, 5.0, 0.5)
                d_ida = st.number_input("Evolução IDA (Ano Anterior)", -5.0, 5.0, 0.2)
            
            if st.button("Calcular Probabilidade de Risco", use_container_width=True):
                # CORREÇÃO TÉCNICA: Enviando as 12 colunas exatas que o modelo exige
                features = ['INDE_22', 'IDA_22', 'IEG_22', 'IAA_22', 'IPS_22', 
                            'INDE_23', 'IDA_23', 'IEG_23', 'IAA_23', 'IPS_23',
                            'Evol_INDE_22_23', 'Evol_IDA_22_23']
                valores = [[7.0, 7.0, 7.0, 7.0, 7.0, i23_inde, i23_ida, i23_ieg, i23_iaa, i23_ips, d_inde, d_ida]]
                entrada = pd.DataFrame(valores, columns=features)
                
                prob = modelo.predict_proba(entrada)[0][1] * 100
                st.divider()
                if prob >= 60: st.error(f"🚨 ALTO RISCO: {prob:.1f}%")
                elif prob >= 30: st.warning(f"⚠️ RISCO MODERADO: {prob:.1f}%")
                else: st.success(f"✅ BAIXO RISCO: {prob:.1f}%")
    else:
        st.error("Modelo .pkl não encontrado.")

with aba_ins:
    st.subheader("💡 Insights Estratégicos")
    
    c_ins1, c_ins2 = st.columns(2)
    with c_ins1:
        m22 = df_master[df_master['Ano_Ref'] == 2022]['INDE'].mean()
        m24 = df_master[df_master['Ano_Ref'] == 2024]['INDE'].mean()
        st.metric("Crescimento INDE (2022-2024)", f"{m24:.2f}", f"{((m24-m22)/m22)*100:.1f}%")
    
    with c_ins2:
        alvo = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP']
        pior = df_master[df_master['Ano_Ref'] == 2024][alvo].mean().idxmin()
        st.warning(f"Foco Pedagógico: Indicador **{pior}** requer atenção imediata em 2024.")

    st.success("""
    **Conclusões Finais:**
    * O engajamento (IEG) foi identificado como a variável de maior impacto na estabilidade do aluno.
    * O modelo permite identificar o risco psicossocial (IPS) antes que ele afete as notas acadêmicas (IDA).
    """)
    
    st.markdown("#### 🚨 Alunos Prioritários para Intervenção (Safra 2024)")
    df_prioridade = df_filtrado[(df_filtrado['Ano_Ref'] == 2024) & (df_filtrado['IAN'] < 10)].sort_values(by='INDE')
    st.dataframe(df_prioridade[['RA', 'Fase', 'INDE', 'IAN', 'IEG']], 
                 column_config={"INDE": st.column_config.ProgressColumn("Aproveitamento INDE", min_value=0, max_value=10, format="%.2f")},
                 use_container_width=True)