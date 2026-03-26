import streamlit as st
import pandas as pd
import plotly.express as px

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
    
    # --- TRATAMENTO NÚMEROS ---
    df_consolidado['INDE'] = df_consolidado['INDE'].astype(str).str.replace(',', '.')
    df_consolidado['INDE'] = pd.to_numeric(df_consolidado['INDE'], errors='coerce')
    
    # --- TRATAMENTO TEXTOS (BLINDAGEM CONTRA ERROS NOS FILTROS) ---
    # Transforma em string, arranca espaços invisíveis e trata os "nan"
    for col in ['Fase', 'Gênero', 'Pedra']:
        df_consolidado[col] = df_consolidado[col].astype(str).str.strip()
        df_consolidado[col] = df_consolidado[col].replace({'nan': 'Não Informado', 'None': 'Não Informado', '': 'Não Informado'})
    
    # --- CORREÇÃO DE DIGITAÇÃO ---
    df_consolidado['Pedra'] = df_consolidado['Pedra'].replace({
        'Agata': 'Ágata',
        'INCLUIR': 'Sem Classificação'
    })
    
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
# 4. MENU LATERAL COM FILTROS DINÂMICOS (CASCATA)
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Filtros Interativos")
    st.write("Use as opções abaixo para refinar os dados.")
    
    # Filtro 1 (Fase)
    fases_disponiveis = sorted(df_master['Fase'].unique().tolist())
    fases_selecionadas = st.multiselect("Fase da ONG:", options=fases_disponiveis, default=[], placeholder="Escolha as fases...")
    
    # Atualiza a base temporária só com as Fases selecionadas
    df_temp1 = df_master[df_master['Fase'].isin(fases_selecionadas)] if fases_selecionadas else df_master
    
    # Filtro 2 (Gênero) - Lê apenas o que sobrou no df_temp1
    generos_disponiveis = sorted(df_temp1['Gênero'].unique().tolist())
    generos_selecionados = st.multiselect("Gênero do Aluno:", options=generos_disponiveis, default=[], placeholder="Escolha o gênero...")
    
    # Atualiza a base temporária com Fase + Gênero
    df_temp2 = df_temp1[df_temp1['Gênero'].isin(generos_selecionados)] if generos_selecionados else df_temp1
    
    # Filtro 3 (Pedra) - Lê apenas o que sobrou no df_temp2
    pedras_disponiveis = sorted(df_temp2['Pedra'].unique().tolist())
    pedras_selecionadas = st.multiselect("Classificação (Pedra):", options=pedras_disponiveis, default=[], placeholder="Escolha as pedras...")
    
    st.divider()
    st.info("Painel de análise do Datathon ONG Passos Mágicos.")

# Criando a base filtrada definitiva para os gráficos da tela principal
df_filtrado = df_master.copy()
if fases_selecionadas: df_filtrado = df_filtrado[df_filtrado['Fase'].isin(fases_selecionadas)]
if generos_selecionados: df_filtrado = df_filtrado[df_filtrado['Gênero'].isin(generos_selecionados)]
if pedras_selecionadas: df_filtrado = df_filtrado[df_filtrado['Pedra'].isin(pedras_selecionadas)]

# ----------------------------------------------------------------------
# 5. CONSTRUÇÃO DO VISUAL DA PÁGINA
# ----------------------------------------------------------------------
st.title("📊 Análise Datathon - ONG Passos Mágicos")
st.markdown("Visualização, normalização e consolidação das bases de dados anuais.")
st.divider()

st.subheader("Volume de Registros por Ano (Base Original)")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Base 2022", value=f"{len(df_2022)}", delta="Linhas")
with col2:
    st.metric(label="Base 2023", value=f"{len(df_2023)}", delta="Linhas")
with col3:
    st.metric(label="Base 2024", value=f"{len(df_2024)}", delta="Linhas")
st.divider()

# Abas de Navegação
aba1, aba2, aba3, aba4 = st.tabs(["📝 Bases Originais", "⚙️ Engenharia", "✅ Base Consolidada", "📈 Dashboard"])

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
    st.write("Para analisar a ONG como um negócio, as colunas dos três anos foram padronizadas e empilhadas.")
    with st.expander("Ver regras de padronização (De -> Para)"):
        st.code("""
        2022: 'Nome' -> 'Nome_Anonimizado', 'Idade 22' -> 'Idade', 'INDE 22' -> 'INDE'
        2023: 'Data de Nasc' -> 'Data_Nascimento', 'INDE 2023' -> 'INDE'
        2024: 'Data de Nasc' -> 'Data_Nascimento', 'INDE 2024' -> 'INDE'
        + Adição da coluna 'Ano_Referencia'
        """, language="text")
    st.write(f"**Total de registros após empilhamento:** {len(df_master)} linhas.")
    st.dataframe(df_master.head(50), use_container_width=True)

with aba3:
    st.markdown("### ✅ Base Consolidada (Super DataFrame)")
    st.write(f"**Registros encontrados com os filtros atuais:** {len(df_filtrado)} linhas.")
    st.dataframe(df_filtrado, use_container_width=True)
    
    csv = df_filtrado.to_csv(index=False, sep=';', decimal=',').encode('utf-8')
    st.download_button(
        label="📥 Baixar Dados Filtrados (CSV)",
        data=csv,
        file_name='passos_magicos_filtrado.csv',
        mime='text/csv',
    )

with aba4:
    st.markdown("### 📈 Indicadores de Desempenho")
    
    filtros_ativos = []
    if fases_selecionadas: filtros_ativos.append("Fase")
    if generos_selecionados: filtros_ativos.append("Gênero")
    if pedras_selecionadas: filtros_ativos.append("Pedra")
    
    if filtros_ativos:
        st.warning(f"⚠️ Exibindo dados filtrados por: {', '.join(filtros_ativos)}")
    else:
        st.write("Visão geral de todos os alunos da ONG.")

    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.subheader("Evolução do INDE Médio")
        df_inde_medio = df_filtrado.groupby('Ano_Referencia')['INDE'].mean().reset_index()
        fig_inde = px.line(df_inde_medio, x='Ano_Referencia', y='INDE', markers=True)
        fig_inde.update_xaxes(type='category', title="Ano de Referência")
        fig_inde.update_yaxes(title="INDE Médio")
        st.plotly_chart(fig_inde, use_container_width=True)

    with col_graf2:
        st.subheader("Distribuição por Pedra")
        df_pedras = df_filtrado.groupby(['Ano_Referencia', 'Pedra']).size().reset_index(name='Quantidade')
        fig_pedras = px.bar(df_pedras, x='Ano_Referencia', y='Quantidade', color='Pedra', barmode='group')
        fig_pedras.update_xaxes(type='category', title="Ano de Referência")
        st.plotly_chart(fig_pedras, use_container_width=True)