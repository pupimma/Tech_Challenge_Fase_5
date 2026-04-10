import streamlit as st
import pandas as pd
import plotly.express as px
import time
import joblib
import numpy as np

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
    caminho_arquivo = r'C:\Users\mauro.pupim\OneDrive - CantuStore\Documentos\Cursos\FIAP\Tech Challenge - Fase 5\data\BASE DE DADOS PEDE 2024 - DATATHON.xlsx'
    
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

    colunas_finais = ['Ano_Referencia', 'RA', 'Nome_Anonimizado', 'Fase', 'Turma', 'Data_Nascimento', 'Idade', 'Gênero', 'Instituição de ensino', 'INDE', 'Pedra']

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
# 4. MENU LATERAL E FILTROS DINÂMICOS
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Filtros Interativos")
    
    fases_disponiveis = sorted(df_master['Fase'].unique().tolist())
    fases_selecionadas = st.multiselect("Fase da ONG:", options=fases_disponiveis, default=[], placeholder="Escolha as fases...")
    
    df_temp1 = df_master[df_master['Fase'].isin(fases_selecionadas)] if fases_selecionadas else df_master
    
    generos_disponiveis = sorted(df_temp1['Gênero'].unique().tolist())
    generos_selecionados = st.multiselect("Gênero do Aluno:", options=generos_disponiveis, default=[], placeholder="Escolha o gênero...")
    
    df_temp2 = df_temp1[df_temp1['Gênero'].isin(generos_selecionados)] if generos_selecionados else df_temp1
    
    pedras_disponiveis = sorted(df_temp2['Pedra'].unique().tolist())
    pedras_selecionadas = st.multiselect("Classificação (Pedra):", options=pedras_disponiveis, default=[], placeholder="Escolha as pedras...")
    
    st.divider()
    st.info("Painel Analítico - Datathon Fase 5")

df_filtrado = df_master.copy()
if fases_selecionadas: df_filtrado = df_filtrado[df_filtrado['Fase'].isin(fases_selecionadas)]
if generos_selecionados: df_filtrado = df_filtrado[df_filtrado['Gênero'].isin(generos_selecionados)]
if pedras_selecionadas: df_filtrado = df_filtrado[df_filtrado['Pedra'].isin(pedras_selecionadas)]

# ----------------------------------------------------------------------
# 5. CONSTRUÇÃO DO VISUAL DA PÁGINA
# ----------------------------------------------------------------------
st.title("📊 Análise Datathon - ONG Passos Mágicos")
st.markdown("Plataforma de visualização e predição de risco educacional.")
st.divider()

aba1, aba2, aba3, aba4, aba5 = st.tabs([
    "📝 Bases Originais", 
    "⚙️ Engenharia", 
    "✅ Base Consolidada", 
    "📈 Dashboard",
    "🤖 Inteligência Artificial"
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
    
    csv = df_filtrado.to_csv(index=False, sep=';', decimal=',').encode('utf-8')
    st.download_button("📥 Baixar Dados Filtrados (CSV)", data=csv, file_name='passos_magicos_filtrado.csv', mime='text/csv')

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

# ----------------------------------------------------------------------
# 6. ABA DE INTELIGÊNCIA ARTIFICIAL (INFERÊNCIA)
# ----------------------------------------------------------------------
with aba5:
    st.markdown("### 🤖 Previsão de Risco de Defasagem (Machine Learning)")
    st.write("Insira os indicadores do aluno para que o modelo preditivo calcule a probabilidade de queda de rendimento.")
    
    def carregar_modelo():
        try:
            return joblib.load('modelo_passos_magicos.pkl')
        except:
            return None
            
    modelo = carregar_modelo()
    
    if modelo is None:
        st.error("⚠️ Arquivo 'modelo_passos_magicos.pkl' não encontrado. Certifique-se de que ele está na mesma pasta que o app.py.")
    else:
        with st.form("form_ml"):
            st.subheader("Indicadores do Aluno")
            col_ml1, col_ml2, col_ml3 = st.columns(3)

            with col_ml1:
                opcoes_fase = fases_selecionadas if fases_selecionadas else ["Fase 1", "Fase 2", "Fase 3", "Fase 4", "Fase 5", "Fase 6", "Fase 7", "Fase 8"]
                fase_input = st.selectbox("Fase do Aluno na ONG", opcoes_fase)
                ida_input = st.slider("Desempenho Acadêmico (IDA)", 0.0, 10.0, 5.0)
                ieg_input = st.slider("Engajamento nas Atividades (IEG)", 0.0, 10.0, 5.0)

            with col_ml2:
                ian_input = st.slider("Adequação de Nível (IAN)", 0.0, 10.0, 5.0)
                ips_input = st.slider("Aspecto Psicossocial (IPS)", 0.0, 10.0, 5.0)
                ipp_input = st.slider("Aspecto Psicopedagógico (IPP)", 0.0, 10.0, 5.0)

            with col_ml3:
                iaa_input = st.slider("Autoavaliação (IAA)", 0.0, 10.0, 5.0)
                inde_input = st.slider("Índice de Desenvolvimento (INDE)", 0.0, 10.0, 5.0)

            submit_button = st.form_submit_button("Gerar Análise Preditiva", use_container_width=True)

if submit_button:
            with st.spinner('Processando dados na Random Forest...'):
                time.sleep(1) 
                
                # CORREÇÃO AQUI: Passamos APENAS as 6 colunas que o modelo conhece (Sem o INDE)
                dados_entrada = pd.DataFrame([[ian_input, ida_input, ieg_input, iaa_input, ips_input, ipp_input]], 
                                             columns=['IAN', 'IDA', 'IEG', 'IAA', 'IPS', 'IPP'])
                
                probabilidade = modelo.predict_proba(dados_entrada)[0][1]
                risco = probabilidade * 100 

                st.markdown("---")
                st.subheader("Resultado do Modelo Random Forest")

                if risco >= 60:
                    st.error(f"🚨 **ALTO RISCO DETECTADO!** Probabilidade de defasagem: **{risco:.1f}%**")
                    st.write("**Ação sugerida:** O perfil validado pelo histórico da ONG indica um forte padrão de queda. O aluno necessita de intervenção imediata.")
                elif risco >= 30:
                    st.warning(f"⚠️ **RISCO MODERADO.** Probabilidade de defasagem: **{risco:.1f}%**")
                    st.write("**Ação sugerida:** Sinais de alerta. Monitorar de perto o Engajamento e o aspecto Psicopedagógico nas próximas semanas.")
                else:
                    st.success(f"✅ **BAIXO RISCO.** Probabilidade de defasagem: **{risco:.1f}%**")
                    st.write("**Ação sugerida:** Aluno com padrão saudável e resiliente. Manter o acompanhamento padrão na fase.")