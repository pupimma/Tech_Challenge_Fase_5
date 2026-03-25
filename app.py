import streamlit as st
import pandas as pd

# ----------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA (Sempre o primeiro comando)
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
    # Caminho absoluto para o seu arquivo Excel
    caminho_arquivo = r'C:\Users\mauro.pupim\OneDrive - CantuStore\Documentos\Cursos\FIAP\Tech Challenge - Fase 5\data\BASE DE DADOS PEDE 2024 - DATATHON.xlsx'
    
    # Lendo as três abas da planilha
    df_22 = pd.read_excel(caminho_arquivo, sheet_name='PEDE2022')
    df_23 = pd.read_excel(caminho_arquivo, sheet_name='PEDE2023')
    df_24 = pd.read_excel(caminho_arquivo, sheet_name='PEDE2024')
    
    return df_22, df_23, df_24

@st.cache_data
def normalizar_e_consolidar(df_22, df_23, df_24):
    # Padronizando 2022
    df_22_padrao = df_22.rename(columns={
        'Nome': 'Nome_Anonimizado',
        'Ano nasc': 'Data_Nascimento',
        'Idade 22': 'Idade',
        'INDE 22': 'INDE',
        'Pedra 22': 'Pedra'
    }).copy()
    df_22_padrao['Ano_Referencia'] = 2022

    # Padronizando 2023
    df_23_padrao = df_23.rename(columns={
        'Data de Nasc': 'Data_Nascimento',
        'INDE 2023': 'INDE',
        'Pedra 2023': 'Pedra'
    }).copy()
    df_23_padrao['Ano_Referencia'] = 2023

    # Padronizando 2024
    df_24_padrao = df_24.rename(columns={
        'Data de Nasc': 'Data_Nascimento',
        'INDE 2024': 'INDE',
        'Pedra 2024': 'Pedra'
    }).copy()
    df_24_padrao['Ano_Referencia'] = 2024

    # Lista das colunas que queremos manter na base final
    colunas_finais = [
        'Ano_Referencia', 'RA', 'Nome_Anonimizado', 'Fase', 'Turma', 
        'Data_Nascimento', 'Idade', 'Gênero', 'Instituição de ensino', 
        'INDE', 'Pedra'
    ]

    # Filtrando para garantir que só as colunas desejadas fiquem no dataframe
    df_22_final = df_22_padrao[[col for col in colunas_finais if col in df_22_padrao.columns]]
    df_23_final = df_23_padrao[[col for col in colunas_finais if col in df_23_padrao.columns]]
    df_24_final = df_24_padrao[[col for col in colunas_finais if col in df_24_padrao.columns]]

    # Empilhando tudo
    df_consolidado = pd.concat([df_22_final, df_23_final, df_24_final], ignore_index=True)
    return df_consolidado


# ----------------------------------------------------------------------
# 3. EXECUÇÃO DOS DADOS (Criando as variáveis que alimentarão a tela)
# ----------------------------------------------------------------------
try:
    # Primeiro carrega os dados originais
    df_2022, df_2023, df_2024 = carregar_dados()
    # Depois cria a base consolidada usando os dados carregados acima
    df_master = normalizar_e_consolidar(df_2022, df_2023, df_2024)
except Exception as e:
    st.error(f"Erro ao processar os dados. Detalhe: {e}")
    st.stop()


# ----------------------------------------------------------------------
# 4. CONSTRUÇÃO DO VISUAL DA PÁGINA (Layout, Sidebar e Abas)
# ----------------------------------------------------------------------

# Menu Lateral
with st.sidebar:
    st.header("⚙️ Configurações")
    st.info("Painel de análise de dados do Datathon ONG Passos Mágicos.")

# Cabeçalho
st.title("📊 Análise Datathon - ONG Passos Mágicos")
st.markdown("Visualização, normalização e consolidação das bases de dados anuais.")
st.divider()

# Métricas de Resumo
st.subheader("Volume de Registros por Ano Originais")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Base 2022", value=f"{len(df_2022)}", delta="Linhas")
with col2:
    st.metric(label="Base 2023", value=f"{len(df_2023)}", delta="Linhas")
with col3:
    st.metric(label="Base 2024", value=f"{len(df_2024)}", delta="Linhas")

st.divider()

# Abas de Navegação
aba1, aba2, aba3 = st.tabs(["📝 Bases Originais", "⚙️ Engenharia e Padronização", "✅ Base Consolidada"])

with aba1:
    st.markdown("### Visualização dos dados brutos")
    
    # Botão para alternar a visualização das bases originais
    ano_selecionado = st.radio(
        "Selecione o ano para visualizar:",
        ["2022", "2023", "2024"],
        horizontal=True
    )
    
    if ano_selecionado == "2022":
        st.dataframe(df_2022, use_container_width=True)
    elif ano_selecionado == "2023":
        st.dataframe(df_2023, use_container_width=True)
    else:
        st.dataframe(df_2024, use_container_width=True)

with aba2:
    st.markdown("### Processo de Normalização")
    st.write("Para analisar a ONG como um negócio, as colunas dos três anos foram padronizadas e empilhadas, criando uma visão temporal unificada.")
    
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
    st.markdown("### Resultado Consolidado (Super DataFrame)")
    st.success("Tabela final unificada e pronta para uso.")
    
    st.dataframe(df_master, use_container_width=True)
    
    # Botão de Exportação
    csv = df_master.to_csv(index=False, sep=';', decimal=',').encode('utf-8')
    st.download_button(
        label="📥 Baixar Base Consolidada (CSV)",
        data=csv,
        file_name='passos_magicos_consolidado.csv',
        mime='text/csv',
    )