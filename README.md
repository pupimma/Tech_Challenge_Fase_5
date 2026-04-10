# Tech_Challenge_Fase_5# 📊 Datathon - ONG Passos Mágicos
### Tech Challenge - Fase 5 | Pós-Graduação em Data Analytics (FIAP)

Este projeto apresenta um ecossistema completo de análise de dados e Inteligência Artificial para a ONG **Passos Mágicos**. A solução contempla desde a normalização de dados históricos (2022-2024) até a implementação de um modelo preditivo de Machine Learning para identificar alunos em risco de defasagem escolar.

---

## 🚀 Link do Projeto
Acesse a aplicação em tempo real: [https://magicsteps.streamlit.app](https://magicsteps.streamlit.app)

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
* `app.py`: Arquivo principal da aplicação Streamlit.
* `requirements.txt`: Lista de dependências para o deploy.
* `modelo_passos_magicos.pkl`: Modelo Random Forest treinado e serializado.
* `data/`: Pasta contendo a base de dados original (Excel).
* `notebooks/`: Jupyter Notebooks utilizados para o treinamento e EDA (Exploratory Data Analysis).

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
