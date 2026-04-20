import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os

# 1. CONFIGURAÇÃO E CARREGAMENTO
st.set_page_config(page_title="Datathon - Passos Mágicos", page_icon="📊", layout="wide")

@st.cache_data
def carregar_dados():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_arquivo = os.path.join(diretorio_atual, 'data', 'BASE DE DADOS PEDE 2024 - DATATHON.xlsx')
    if not os.path.exists(caminho_arquivo):
        caminho_arquivo = os.path.join(diretorio_atual, 'BASE DE DADOS PEDE 2024 - DATATHON.xlsx')
    
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
    df['Pedra'] = df['Pedra'].astype(str).str.strip().replace({'Agata': 'Ágata', 'INCLUIR': 'Sem Classificação', 'nan': 'N/I'})
    return df

try:
    raw22, raw23, raw24 = carregar_dados()
    df_master = processar_base(raw22, raw23, raw24)
except Exception as e:
    st.error(f"Erro na carga: {e}")
    st.stop()

# 2. FILTROS LATERAIS
with st.sidebar:
    st.header("⚙️ Filtros de Análise")
    
    # Forçamos a coluna 'Fase' para string para evitar erro no sorted()
    opcoes_fase = sorted(list(set(str(f) for f in df_master['Fase'].unique() if pd.notna(f))))
    fase_sel = st.multiselect("Fase da ONG:", options=opcoes_fase)
    df_f = df_master[df_master['Fase'].astype(str).isin(fase_sel)] if fase_sel else df_master
    
    # Mesma lógica para Gênero e Pedra para garantir segurança
    opcoes_gen = sorted(list(set(str(g) for g in df_f['Gênero'].unique() if pd.notna(g))))
    gen_sel = st.multiselect("Gênero Aluno:", options=opcoes_gen)
    df_f = df_f[df_f['Gênero'].astype(str).isin(gen_sel)] if gen_sel else df_f
    
    opcoes_pedra = sorted(list(set(str(p) for p in df_f['Pedra'].unique() if pd.notna(p))))
    pedra_sel = st.multiselect("Classificação (Pedra):", options=opcoes_pedra)
    df_filtrado = df_f[df_f['Pedra'].astype(str).isin(pedra_sel)] if pedra_sel else df_f

st.divider()
    st.caption("🚀 **Datathon Fase 5** | Mauro Pupim")
    st.info("💡 **Nota técnica:** Ferramentas de IA foram utilizadas para otimização da arquitetura e suporte ao código.")

# 3. INTERFACE PRINCIPAL
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
    k2.metric("Média INDE", f"{df_filtrado['INDE'].mean():.2f}")
    risco_24 = len(df_filtrado[(df_filtrado['Ano_Ref'] == 2024) & (df_filtrado['IAN'] < 10)])
    k3.metric("Alerta IAN (2024)", risco_24, delta_color="inverse")
    
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        fig_l = px.line(df_filtrado.groupby('Ano_Ref')['INDE'].mean().reset_index(), x='Ano_Ref', y='INDE', markers=True, title="Tendência INDE")
        fig_l.update_layout(xaxis_type='category', height=400)
        st.plotly_chart(fig_l, use_container_width=True)
    with c2:
        df_p = df_filtrado.groupby(['Ano_Ref', 'Pedra']).size().reset_index(name='Total')
        fig_b = px.bar(df_p, x='Ano_Ref', y='Total', color='Pedra', barmode='group', title="Distribuição Pedras")
        fig_b.update_layout(xaxis_type='category', height=400, legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig_b, use_container_width=True)

with aba_ia:
    st.subheader("🤖 Diagnóstico Preditivo (Machine Learning)")
    st.caption("Identificação de padrões que antecedem quedas (Perguntas 3, 5 e 9).")
    
    dir_ia = os.path.dirname(os.path.abspath(__file__))
    path_model = os.path.join(dir_ia, 'models', 'modelo_passos_magicos.pkl')
    if not os.path.exists(path_model):
        path_model = os.path.join(dir_ia, 'modelo_passos_magicos.pkl')

    if os.path.exists(path_model):
        modelo = joblib.load(path_model)
        with st.form("form_ia"):
            col1, col2 = st.columns(2)
            with col1:
                v_ian = st.slider("Nível (IAN)", 0.0, 10.0, 7.0)
                v_ida = st.slider("Acadêmico (IDA)", 0.0, 10.0, 7.0)
                v_ieg = st.slider("Engajamento (IEG)", 0.0, 10.0, 7.0)
            with col2:
                v_iaa = st.slider("Autoavaliação (IAA)", 0.0, 10.0, 7.0)
                v_ips = st.slider("Social (IPS)", 0.0, 10.0, 7.0)
                v_ipp = st.slider("Psicopedagógico (IPP)", 0.0, 10.0, 7.0)
            
            if st.form_submit_button("Calcular Probabilidade de Risco", use_container_width=True):
                # Ocultar o INDE do slider mas manter fixo para o modelo se necessário
                dados_ent = pd.DataFrame([[v_ian, v_ida, v_ieg, v_iaa, v_ips, v_ipp]], columns=['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP'])
                
                try:
                    # Ajuste dinâmico de colunas
                    if hasattr(modelo, "feature_names_in_") and len(modelo.feature_names_in_) > 6:
                        dados_ent['INDE'] = 7.0
                    
                    prob = modelo.predict_proba(dados_ent)[0][1] * 100
                    st.divider()
                    if prob >= 60: st.error(f"🚨 ALTO RISCO: {prob:.1f}%")
                    elif prob >= 30: st.warning(f"⚠️ RISCO MODERADO: {prob:.1f}%")
                    else: st.success(f"✅ BAIXO RISCO: {prob:.1f}%")
                except Exception as e:
                    st.error(f"Erro na predição: {e}")
    else:
        st.warning("Modelo .pkl não localizado nas pastas /models ou raiz.")

with aba_ins:
    st.subheader("💡 Insights e Efetividade")
    st.info("O monitoramento longitudinal confirma o impacto real do programa (Pergunta 10).")
    c_i1, c_i2 = st.columns(2)
    with c_i1:
        m22 = df_master[df_master['Ano_Ref'] == 2022]['INDE'].mean()
        m24 = df_master[df_master['Ano_Ref'] == 2024]['INDE'].mean()
        st.metric("Crescimento Histórico", f"{m24:.2f}", f"{((m24-m22)/m22)*100:.1f}%")
    with c_i2:
        st.warning("Ponto de Virada: O engajamento (IEG) antecipa a evolução pedagógica.")

    st.markdown("#### 🚨 Alunos Prioritários (Ação Pedagógica)")
    df_prio = df_filtrado[(df_filtrado['Ano_Ref'] == 2024) & (df_filtrado['IAN'] < 10)].sort_values(by='INDE')
    st.dataframe(df_prio[['RA', 'Fase', 'INDE', 'IAN', 'IEG']], use_container_width=True)

with aba_orig:
    ano_s = st.selectbox("Safra:", [2022, 2023, 2024])
    m_orig = {2022: raw22, 2023: raw23, 2024: raw24}
    st.dataframe(m_orig[ano_s], use_container_width=True)
