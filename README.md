# Tech_Challenge_Fase_5# 📊 Datathon - ONG Passos Mágicos
### Tech Challenge - Fase 5 | Pós-Graduação em Data Analytics (FIAP)

Este repositório apresenta um ecossistema de inteligência de dados desenvolvido para a ONG Passos Mágicos. A solução contempla desde a higienização de bases históricas (2022-2024) até a implementação de um modelo preditivo para identificação precoce de risco de defasagem escolar.

---

## 🚀 Link do Projeto
Acesse a aplicação em tempo real: [https://magicsteps.streamlit.app](https://magicsteps.streamlit.app)

---

## 🏗️ Arquitetura da Solução

O projeto foi estruturado para garantir portabilidade e escalabilidade, dividindo-se em três camadas:

1. Data Storage: Armazenamento de bases históricas (.xlsx) na estrutura de pastas local, utilizando caminhos relativos para compatibilidade com ambientes Git e Cloud.

2. ML Engine: Pipeline de ETL e treinamento desenvolvido em Python. Utiliza Random Forest Classifier para predição de risco educacional. O modelo é serializado via joblib para consumo em tempo real.

3. Analytics Frontend: Dashboard interativo em Streamlit que integra a visualização de KPIs históricos e o simulador de predição de IA.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.10+
* **Interface Web:** Streamlit
* **Processamento de Dados:** Pandas / Numpy
* **Visualização:** Plotly Express
* **Machine Learning:** Scikit-Learn (Random Forest)
* **Persistência de Modelo:** Joblib

---

## 🧠 O Modelo Preditivo (Machine Learning)
Desenvolvemos um classificador baseado no algoritmo **Random Forest** (Florestas Aleatórias) para prever a probabilidade de um aluno entrar em "Risco de Defasagem" (definido como INDE < 6.0).

* **Variáveis de Entrada (Features):**
    * **IAN:** Adequação de Nível
    * **IDA:** Desempenho Acadêmico
    * **IEG:** Engajamento nas Atividades
    * **IAA:** Autoavaliação do Aluno
    * **IPS:** Aspecto Psicossocial
    * **IPP:** Aspecto Psicopedagógico
* **Objetivo:** Permitir intervenções preventivas baseadas na queda de indicadores comportamentais antes que ocorra a queda no desempenho final.

---

## 📁 Estrutura do Repositório

    * app.py: Interface principal do Dashboard Streamlit.
    * requirements.txt: Dependências do projeto para deploy.
    * data/: Base de dados original em formato Excel.
    * models/: Binários do modelo treinado (.pkl).
    * notebooks/: Scripts de desenvolvimento, análise exploratória (EDA) e treinamento do modelo.

---

💻 Como rodar localmente
1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o app:
```bash
streamlit run app.py
```
