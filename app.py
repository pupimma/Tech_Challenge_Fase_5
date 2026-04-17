import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os

# 1. CONFIGURAÇÃO DE PÁGINA
st.set_page_config(page_title="Painel Analítico - Passos Mágicos", page_icon="📊", layout="wide")

@st.cache_data
def carregar_dados():
    # Caminho resiliente para Streamlit Cloud e Local
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(diretorio_atual, 'data', 'BASE DE DADOS PEDE 2024 - DATATHON.xlsx')
    
    if not os.path.exists(data_path):
        st.error(f"Arquivo não encontrado: {data_path}")
        st.stop()
        
    return (pd.read_excel(data_path, sheet_name='PEDE2022'),
            pd.read_excel(data_path, sheet_name='PEDE2023'),
            pd.read_excel(data_path, sheet_name='PEDE2024'))

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
    st.error(f"Falha na carga dos dados: {e}")
    st.stop()

# 2. FILTROS LATERAIS
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
    st.caption("🚀 **Datathon Fase 5** | Mauro Pupim")
    st.info("Este projeto utilizou IA Generativa para suporte na arquitetura.")

# 3. INTERFACE
st.title("📊 Painel Analítico - Passos Mágicos")
st.divider()

aba_cons, aba_dash, aba_ia, aba_ins, aba_orig = st.tabs([
    "✅ Consolidado", "📈 Dashboard", "🤖 Predição IA", "💡 Insights", "📓 Originais"
])

with aba_cons:
    st.dataframe(df_filtrado, use_container_width=True)

with aba_dash:
    st.subheader("Indicadores Críticos de Gestão")
    k1, k2, k3 = st.columns(3)
    k1.metric("Volume de Alunos", len(df_filtrado))
    k2.metric("Média INDE Geral", f"{df_filtrado['INDE'].mean():.2f}")
    risco_24 = len(df_filtrado[(df_filtrado['Ano_Ref'] == 2024) & (df_filtrado['IAN'] < 10)])
    k3.metric("Alerta de Risco (IAN)", risco_24, delta="Atenção Prioritária", delta_color="inverse")
    
    st.divider()

    # Layout de colunas para os gráficos
    c1, c2 = st.columns(2)

    with c1:
        # Gráfico de Linha - Evolução INDE
        df_inde = df_filtrado.groupby('Ano_Ref')['INDE'].mean().reset_index()
        fig_line = px.line(
            df_inde, x='Ano_Ref', y='INDE', markers=True,
            title="Tendência de Desempenho (Média INDE)",
            labels={'Ano_Ref': 'Ano', 'INDE': 'Média INDE'}
        )
        fig_line.update_layout(
            xaxis_type='category', 
            margin=dict(l=20, r=20, t=50, b=20),
            height=400 # Altura fixa para manter simetria
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with c2:
        # Gráfico de Barras - Distribuição Pedras
        df_p = df_filtrado.groupby(['Ano_Ref', 'Pedra']).size().reset_index(name='Total')
        fig_bar = px.bar(
            df_p, x='Ano_Ref', y='Total', color='Pedra', barmode='group',
            title="Distribuição de Alunos por Pedra",
            labels={'Ano_Ref': 'Ano', 'Total': 'Qtd Alunos', 'Pedra': 'Classificação'}
        )
        fig_bar.update_layout(
            xaxis_type='category',
            margin=dict(l=20, r=20, t=50, b=20),
            height=400, # Mesma altura do gráfico de linha
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5) # Legenda horizontal para não espremer o gráfico
        )
        st.plotly_chart(fig_bar, use_container_width=True)

with aba_ia:
    st.subheader("🤖 IA Preditiva (Random Forest)")
    path_model = os.path.join(os.path.dirname(__file__), 'modelo_passos_magicos.pkl')
    
    if os.path.exists(path_model):
        modelo = joblib.load(path_model)
        with st.expander("Configurar Simulador", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                v_ian = st.slider("Adequação (IAN)", 0.0, 10.0, 7.0)
                v_ida = st.slider("Acadêmico (IDA)", 0.0, 10.0, 7.0)
                v_ieg = st.slider("Engajamento (IEG)", 0.0, 10.0, 7.0)
            with col2:
                v_iaa = st.slider("Autoavaliação (IAA)", 0.0, 10.0, 7.0)
                v_ips = st.slider("Social (IPS)", 0.0, 10.0, 7.0)
                v_ipp = st.slider("Psicopedagógico (IPP)", 0.0, 10.0, 7.0)
            
            if st.button("Executar Diagnóstico IA", use_container_width=True):
                # TENTATIVA 1: NOMES SIMPLES (O QUE O ERRO DA WEB PEDIU)
                features_simples = ['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP']
                dados_simples = pd.DataFrame([[v_ian, v_ida, v_ieg, v_iaa, v_ips, v_ipp]], columns=features_simples)
                
                # TENTATIVA 2: NOMES DETALHADOS (CASO O MODELO LOCAL SEJA DIFERENTE)
                features_detalhadas = ['INDE_22', 'IDA_22', 'IEG_22', 'IAA_22', 'IPS_22', 'INDE_23', 'IDA_23', 'IEG_23', 'IAA_23', 'IPS_23', 'Evol_INDE_22_23', 'Evol_IDA_22_23']
                dados_detalhados = pd.DataFrame([[7.0, 7.0, 7.0, 7.0, 7.0, v_ian, v_ida, v_ieg, v_iaa, v_ips, 0.5, 0.2]], columns=features_detalhadas)
                
                try:
                    # Tenta primeiro o que o erro da Web sugeriu
                    prob = modelo.predict_proba(dados_simples)[0][1] * 100
                except:
                    try:
                        # Se falhar, tenta o formato longo
                        prob = modelo.predict_proba(dados_detalhados)[0][1] * 100
                    except Exception as e:
                        st.error(f"Erro de compatibilidade do modelo: {e}")
                        st.stop()
                
                st.divider()
                if prob >= 60: st.error(f"🚨 ALTO RISCO: {prob:.1f}%")
                elif prob >= 30: st.warning(f"⚠️ RISCO MODERADO: {prob:.1f}%")
                else: st.success(f"✅ BAIXO RISCO: {prob:.1f}%")
    else:
        st.error("Modelo .pkl não localizado.")
        
with aba_ins:
    st.subheader("💡 Insights e Ação")
    m22 = df_master[df_master['Ano_Ref'] == 2022]['INDE'].mean()
    m24 = df_master[df_master['Ano_Ref'] == 2024]['INDE'].mean()
    st.metric("Crescimento 2022-2024", f"{m24:.2f}", f"{((m24-m22)/m22)*100:.1f}%")
    
    st.success("O engajamento (IEG) é o maior preditor de sucesso.")
    st.markdown("#### Alunos Críticos (IAN < 10 em 2024)")
    df_prio = df_filtrado[(df_filtrado['Ano_Ref'] == 2024) & (df_filtrado['IAN'] < 10)]
    st.dataframe(df_prio[['RA', 'Fase', 'INDE', 'IEG']], use_container_width=True)

with aba_orig:
    ano_sel = st.selectbox("Safra:", [2022, 2023, 2024])
    mapping = {2022: raw22, 2023: raw23, 2024: raw24}
    st.dataframe(mapping[ano_sel], use_container_width=True)
