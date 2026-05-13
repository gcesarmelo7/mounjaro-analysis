import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import csv

filtered_df = pd.read_csv ('filtered_df.csv')
df = pd.read_csv ('df.csv')

st.markdown("Bem-vindo ao site!") # df, err, func, keras!
st.markdown("Aqui são os dados provenientes da ANVISA sobre a TIRZEPATIDA (MOUNJARO) em Janeiro de 2026")
st.markdown("Assim que sair mais informações, procuro atualizar esta página com dados recentes. Aproveite!")
st.markdown("Farmacêutico e Cientista de Dados: Giovanni Melo. CRF: 96.140")
# st.dataframe(filtered_df)

# Set page configuration
st.set_page_config(page_title="Análise de Vendas Tirzepatida", layout="wide")

st.title("📊 Análise de Vendas: Mounjaro (Tirzepatida)")
st.markdown("Análise exploratória de dados de vendas em Janeiro 2026.")

# --- DATA LOADING ---
@st.cache_data # This keeps the app fast by caching the data
def load_data():
    filtered_df = pd.read_csv('filtered_df.csv')
    df = pd.read_csv('df.csv')
    return filtered_df, df

filtered_df, df = load_data()

# --- TOP OVERVIEW ---
st.header("Visão Geral dos Dados")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Amostra dos Dados")
    st.dataframe(filtered_df.head(10))

#with col2:
#    st.subheader("Total de Registros")
#    st.metric("Linhas Processadas", f"{len(filtered_df):,}")

###

# --- GEOGRAPHIC ANALYSIS ---
st.header("Análise por Estado (UF)")
uf_state = filtered_df.groupby('SG_UF_VENDA')['QT_VENDIDA'].sum().sort_values(ascending=False)
uf_state_top10 = uf_state.head(10)

fig1, ax1 = plt.subplots(figsize=(10, 6))
plt.style.use('dark_background')
colors = ['red' if i < 3 else 'darkgray' for i in range(len(uf_state_top10))]
ax1.bar(uf_state_top10.index, uf_state_top10.values, color=colors, edgecolor='grey')

half_value = uf_state_top10.max() / 4
ax1.axhline(y=half_value, color='silver', linestyle='--', linewidth=1.5)
ax1.text(x=9, y=half_value, s='25% das vendas ', color='whitesmoke', va='bottom', ha='right', fontweight='bold')

ax1.set_title('Top 10 Estados por Vendas')
ax1.set_ylabel('Vendas')
st.pyplot(fig1)

###

# --- DEMOGRAPHICS (GENDER & AGE) ---
st.header("Demografia dos Consumidores")
col_gender, col_age = st.columns(2)

with col_gender:
    st.subheader("Distribuição por Gênero")
    gender_counts = filtered_df['SG_SEXO'].value_counts()
    fig2, ax2 = plt.subplots()
    ax2.pie(gender_counts, labels=gender_counts.index, autopct='%1.f%%', 
            colors=['indianred','royalblue'], startangle=140)
    ax2.axis('equal')
    st.pyplot(fig2)

with col_age:
    st.subheader("Distribuição por Idade (Top 3 Destaques)")
    # Cleaning
    age_df = filtered_df.copy()
    age_df['NU_IDADE'] = pd.to_numeric(age_df['NU_IDADE'], errors='coerce')
    age_df = age_df[age_df['NU_IDADE'].between(10, 100)]
    
    fig3, ax3 = plt.subplots()
    n, bins, patches = ax3.hist(age_df['NU_IDADE'], bins=18, color='silver', edgecolor='dimgray')
    
    top_3_indices = np.argsort(n)[-3:]
    for i in top_3_indices:
        patches[i].set_facecolor('olive')
    patches[top_3_indices[-1]].set_label('Top 3 Frequências')
    
    ax3.set_xticks(range(10, 101, 10))
    ax3.legend()
    st.pyplot(fig3)

###

# --- DEEP DIVE: SÃO PAULO ---
st.header("Foco: Estado de São Paulo")

# Filtering Logic
city_tirz = (df['SG_UF_VENDA'] == 'SP') & (df['DS_PRINCIPIO_ATIVO'].str.contains('TIRZEPATIDA', case=False))
df_city_mounjaro = df[city_tirz]
city_sales = df_city_mounjaro.groupby('NO_MUNICIPIO_VENDA')['QT_VENDIDA'].sum()

tab1, tab2 = st.tabs(["Com a Capital", "Apenas Interior/Litoral"])

with tab1:
    st.subheader("Impacto da Capital")
    cities_sp_top10 = city_sales.sort_values(ascending=False).head(5)
    fig4, ax4 = plt.subplots()
    colors_h = ['dimgray'] * 4 + ['firebrick']
    ax4.barh(cities_sp_top10.index[::-1], cities_sp_top10.values[::-1], color=colors_h)
    st.pyplot(fig4)
    st.warning("São Paulo capital apresenta um grande outlier de vendas.")

with tab2:
    st.subheader("Top 10 Cidades (Excluindo a Capital)")
    city_sales_no_sp = city_sales.drop('SÃO PAULO', errors='ignore')
    cities_interior_top10 = city_sales_no_sp.sort_values(ascending=False).head(10)
    
    fig5, ax5 = plt.subplots(figsize=(10, 6))
    colors_int = ['lightgray'] * 7 + ['royalblue'] * 3
    ax5.barh(cities_interior_top10.index[::-1], cities_interior_top10.values[::-1], color=colors_int)
    
    v_mean = cities_interior_top10.mean()
    ax5.axvline(v_mean, color='firebrick', linestyle='--')
    
    st.pyplot(fig5)
    st.info(f"Média de vendas no interior: {int(v_mean)} unidades. Campinas, Ribeirão e Santos lideram.")

    ### GEMINI TEST

    import streamlit as st
import pandas as pd

# 1. Load Data
@st.cache_data
def load_data():
    filtered_df = pd.read_csv('filtered_df.csv')
    df = pd.read_csv('df.csv')
    return filtered_df, df

filtered_df, df = load_data()

st.title("Explore os dados você mesmo!")

# 2. Create the Dropdown (Selectbox)
# We define a list of options for the user
option = st.selectbox(
    'Qual tabela você gostaria de visualizar?',
    ('Resumo Geral', 'Vendas por Estado', 'Top Cidades em SP', 'Dados Brutos')
)

st.write(f"Você selecionou: **{option}**")

# 3. Logic to display different tables based on selection
if option == 'Resumo Geral':
    st.subheader("Estatísticas Descritivas")
    st.write(filtered_df.describe())

elif option == 'Vendas por Estado':
    st.subheader("Total de Vendas por UF")
    uf_summary = filtered_df.groupby('SG_UF_VENDA')['QT_VENDIDA'].sum().reset_index()
    st.table(uf_summary.sort_values(by='QT_VENDIDA', ascending=False))

elif option == 'Top Cidades em SP':
    st.subheader("Top 5 Cidades Paulistas")
    city_sales = df[df['SG_UF_VENDA'] == 'SP'].groupby('NO_MUNICIPIO_VENDA')['QT_VENDIDA'].sum()
    top_cities = city_sales.sort_values(ascending=False).head(5)
    st.dataframe(top_cities)

elif option == 'Dados Brutos':
    st.subheader("Visualização dos Microdados")
    # Adding a slider to let the user choose how many rows to see
    rows = st.slider("Quantidade de linhas", 5, 100, 20)
    st.dataframe(filtered_df.head(rows))

