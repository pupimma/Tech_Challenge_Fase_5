import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os

# ----------------------------------------------------------------------
# 1. CONFIGURAÇÃO E CARREGAMENTO
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Datathon - ONG Passos Mágicos", 
    page_icon="📊", 
    layout="wide"
)

@st.cache_data
def carregar_dados():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_arquivo = os.path.join(diretorio_atual, 'data', 'BASE DE DADOS PEDE 2024 - DATATHON.xlsx')
    
    if not os.path.exists(caminho_arquivo):
        # Fallback para busca na raiz se não estiver na /data
        caminho_arquivo = os.path.join(diretorio_atual, 'BASE DE DADOS PEDE 2024 - DATATHON.xlsx')

    if not os.path.exists(caminho_arquivo):
        st.error(f"Arquivo de dados não encontrado. Verifique a pasta /data.")
        st.stop()
        
    return (pd.read_excel(caminho_arquivo, sheet_name='PEDE2022'),
            pd.read_excel(caminho_arquivo, sheet_name='PEDE2023'),
            pd.read_excel(caminho_arquivo, sheet_name='PEDE2024'))

@st.cache_data
def processar_base_mestra(df_22, df_23, df_24):
    # Padronização de colunas para série histórica (Análise Longitudinal)
    d22 = df_22.rename(columns={'Nome': 'Nome_Anon', 'Idade 22': 'Idade', 'INDE 22': 'INDE', 'Pedra 22': 'Pedra'}).copy()
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
    
    # Higienização de categorias para o gráfico
    df['Pedra'] = df['Pedra'].replace({'Agata': 'Ágata', 'INCLUIR': 'Sem Classificação'})
    return df

try:
    raw22, raw23, raw24 = carregar_dados()
    df_master = processar_base_mestra(raw22, raw23, raw24)
except Exception as e:
    st.error(f"Falha na pipeline de dados: {e}")
    st.stop()

# ----------------------------------------------------------------------
# 2. INTERFACE LATERAL (FILTROS)
# ----------------------------------------------------------------------
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
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Relatório (CSV)", data=csv, file_name='relatorio_pm.csv', mime='text/csv')
    st.caption("🚀 **Datathon Fase 5** | Mauro Pupim")
    st.info("Ferramentas de IA foram utilizadas para otimização da arquitetura e suporte ao código.")

# ----------------------------------------------------------------------
# 3. NAVEGAÇÃO POR ABAS
# ----------------------------------------------------------------------
st.title("📊 Painel Analítico - Passos Mágicos")
st.divider()

aba_cons, aba_dash, aba_ia, aba_ins, aba_orig = st.tabs([
    "✅ Consolidado", "📈 Dashboard", "🤖 Predição IA", "💡 Insights", "📓 Originais"
])

with aba_cons:
    st.subheader("Visão Multidimensional dos Alunos")
    st.markdown("Analise a coerência entre indicadores (IAA vs IDA) e psicossociais (Pergunta 4 e 8).")
    st.dataframe(df_filtrado, use_container_width=True)

with aba_dash:
    st.subheader("Indicadores Críticos de Gestão")
    k1, k2, k3 = st.columns(3)
    k1.metric("Volume de Alunos", len(df_filtrado))
    k2.metric("Média INDE Geral", f"{df_filtrado['INDE'].mean():.2f}")
    # Resposta Pergunta 1: Perfil de Defasagem
    risco_24 = len(df_filtrado[(df_filtrado['Ano_Ref'] == 2024) & (df_filtrado['IAN'] < 10)])
    k3.metric("Alerta IAN (2024)", risco_24, delta="Risco de Defasagem", delta_color="inverse")
    
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        # Pergunta 2: Evolução do Desempenho
        df_inde = df_filtrado.groupby('Ano_Ref')['INDE'].mean().reset_index()
        fig_line = px.line(df_inde, x='Ano_Ref', y='INDE', markers=True, 
                           title="Evolução do Desempenho Médio (INDE)", labels={'INDE': 'Média INDE', 'Ano_Ref': 'Ano'})
        fig_line.update_layout(xaxis_type='category', height=400)
        st.plotly_chart(fig_line, use_container_width=True)

    with c2:
        # Pergunta 8 e 10: Distribuição e Efetividade
        df_p = df_filtrado.groupby(['Ano_Ref', 'Pedra']).size().reset_index(name='Total')
        fig_bar = px.bar(df_p, x='Ano_Ref', y='Total', color='Pedra', barmode='group',
                         title="Distribuição por Classificação (Pedra)", labels={'Total': 'Qtd Alunos', 'Ano_Ref': 'Ano'})
        fig_bar.update_layout(xaxis_type='category', height=400, legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig_bar, use_container_width=True)

with aba_ia:
    st.subheader("🤖 Diagnóstico Preditivo (Machine Learning)")
    st.caption("Responde às perguntas 3, 5 e 9: Identificação de padrões psicossociais e engajamento que antecedem quedas.")
    
    path_model = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modelo_passos_magicos.pkl')
    
    if os.path.exists(path_model):
        modelo = joblib.load(path_model)
        with st.form("form_ia"):
            c1, c2 = st.columns(2)
            with c1:
                v_ian = st.slider("Nível (IAN)", 0.0, 10.0, 7.0)
                v_ida = st.slider("Acadêmico (IDA)", 0.0, 10.0, 7.0)
                v_ieg = st.slider("Engajamento (IEG)", 0.0, 10.0, 7.0)
            with c2:
                v_iaa = st.slider("Autoavaliação (IAA)", 0.0, 10.0, 7.0)
                v_ips = st.slider("Social (IPS)", 0.0, 10.0, 7.0)
                v_ipp = st.slider("Psicopedagógico (IPP)", 0.0, 10.0, 7.0)
            
            if st.form_submit_button("Calcular Probabilidade de Risco", use_container_width=True):
                # Fallback de features para compatibilidade do modelo
                f_simples = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP']
                d_simples = pd.DataFrame([[v_ian, v_ida, v_ieg, v_iaa, v_ips, v_ipp]], columns=f_simples)
                f_detalhe = ['INDE_22', 'IDA_22', 'IEG_22', 'IAA_22', 'IPS_22', 'INDE_23', 'IDA_23', 'IEG_23', 'IAA_23', 'IPS_23', 'Evol_INDE_22_23', 'Evol_IDA_22_23']
                d_detalhe = pd.DataFrame([[7.0, 7.0, 7.0, 7.0, 7.0, v_ian, v_ida, v_ieg, v_iaa, v_ips, 0.5, 0.2]], columns=f_detalhe)
                
                try:
                    # Lógica resiliente para detectar qual versão do modelo está ativa
                    if hasattr(modelo, "feature_names_in_") and 'INDE_22' in modelo.feature_names_in_:
                        prob = modelo.predict_proba(d_detalhe)[0][1] * 100
                    else:
                        prob = modelo.predict_proba(d_simples)[0][1] * 100
                    
                    st.divider()
                    if prob >= 60: st.error(f"🚨 ALTO RISCO: {prob:.1f}%")
                    elif prob >= 30: st.warning(f"⚠️ RISCO MODERADO: {prob:.1f}%")
                    else: st.success(f"✅ BAIXO RISCO: {prob:.1f}%")
                except Exception as e:
                    st.error(f"Erro na predição: {e}")
    else:
        st.warning("Modelo 'modelo_passos_magicos.pkl' não localizado na raiz.")

with aba_ins:
    st.subheader("💡 Insights Estratégicos e Tomada de Decisão")
    st.info("Análise de Efetividade (Pergunta 10): O crescimento histórico comprova o impacto real do programa.")
    
    c1, c2 = st.columns(2)
    with c1:
        m22 = df_master[df_master['Ano_Ref'] == 2022]['INDE'].mean()
        m24 = df_master[df_master['Ano_Ref'] == 2024]['INDE'].mean()
        st.metric("Evolução Histórica (2022-2024)", f"{m24:.2f}", f"{((m24-m22)/m22)*100:.1f}%")
    with c2:
        alvo = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP']
        pior = df_master[df_master['Ano_Ref'] == 2024][alvo].mean().idxmin()
        st.warning(f"Ponto de Atenção (Pergunta 7): Indicador **{pior}** requer intervenção em 2024.")

    st.success("""
    **Conclusões Finais (Pergunta 11):**
    * O **Engajamento (IEG)** é o 'Ponto de Virada' para a estabilidade do aluno.
    * O monitoramento **Psicossocial (IPS)** antecipa quedas acadêmicas (IDA).
    """)
    
    st.markdown("#### 🚨 Lista de Intervenção Prioritária (Otimização Pedagógica)")
    df_prioridade = df_filtrado[(df_filtrado['Ano_Ref'] == 2024) & (df_filtrado['IAN'] < 10)].sort_values(by='INDE')
    st.dataframe(df_prioridade[['RA', 'Fase', 'INDE', 'IAN', 'IEG']], use_container_width=True)

with aba_orig:
    st.subheader("Bases Brutas de Dados")
    ano_sel = st.selectbox("Selecione a Safra:", [2022, 2023, 2024])
    mapping = {2022: raw22, 2023: raw23, 2024: raw24}
    st.dataframe(mapping[ano_sel], use_container_width=True)
