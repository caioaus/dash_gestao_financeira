import streamlit as st
st.markdown(
    """
    <style>
        /* Fundo com degradê */
        .stApp {
            background: linear-gradient(135deg, #FF4136, #111);
            color: white;
        }
        
        /* Ajusta a cor do texto */
        h1, h2, h3, h4, h5, h6, p, .stTextInput, .stSelectbox, .stButton {
            color: white !important;
        }

        /* Estiliza os gráficos */
        .stPlotlyChart {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 10px;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
    <style>
        /* Cor da barra lateral */
        section[data-testid="stSidebar"] {
            background-color: black;
            color: red;
        }

        /* Ajuste para os textos dentro da barra lateral */
        section[data-testid="stSidebar"] * {
            color: red !important;
        }

        /* Ajuste específico para os meses no selectbox */
        section[data-testid="stSidebar"] select {
            color: red !important;
        }
    </style>
""", unsafe_allow_html=True)
import pandas as pd
import plotly.express as px

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap');
        /* Estilização do título */
        .titulo-container {
            background-color: #800000;  /* Um tom de vermelho escuro elegante */
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 4px 4px 10px rgba(0, 0, 0, 0.5); /* Efeito de relevo */
        }

        .titulo-texto {
            font-size: 45px;
            font-weight: bold;
            font-family: 'Poppins', sans-serif;
            color: white;
        }
    </style>

    <div class="titulo-container">
        <p class="titulo-texto">Gestão Financeira</p>
    </div>
""", unsafe_allow_html=True)
# Carregar os dados
arquivo_excel = "Relatorio_Mensal_py.xlsx"
df = pd.read_excel(arquivo_excel)

df["Valor (R$)"] = df["Valor (R$)"].astype(str).str.replace(r"[^\d.,-]", "", regex=True)
df["Valor (R$)"] = df["Valor (R$)"].str.replace(",", ".").astype(float)
df["Valor (R$)"] = pd.to_numeric(df["Valor (R$)"], errors='coerce')
df["Valor (R$)"].fillna(0, inplace=True)
df.columns = df.columns.str.strip()  # Remove espaços extras nos nomes das colunas
# Criar uma nova coluna de trimestre
# Criar nova coluna de trimestre
df["Trimestre"] = pd.to_datetime(df["Mês do Pagamento"], format='%m').dt.to_period("Q")

# Criar filtros interativos
st.sidebar.header("Filtros")
trimestre_selecionado = st.sidebar.selectbox("Selecione o Trimestre", df["Trimestre"].unique())
mes_selecionado = st.sidebar.selectbox("Selecione o Mês", df["Mês do Pagamento"].unique())
dia_semana_selecionado = st.sidebar.multiselect("Selecione o(s) Dia(s) da Semana", 
                                                df["Dia do Pagamento"].unique(), 
                                                default=df["Dia do Pagamento"].unique())

# Adiciona o logo na barra lateral
st.sidebar.image("logo_fj.jpg", use_container_width=True)  

df_filtrado = df[
    (df["Mês do Pagamento"] == mes_selecionado) & 
    (df["Dia do Pagamento"].isin(dia_semana_selecionado))
]

# Criar layout em matriz 2x2
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

# Criar gráfico de barras para Despesas dos Carros
with col1:
    st.subheader("Despesas dos Carros")
    fig1 = px.bar(df_filtrado[df_filtrado["Categoria"] == "Despesa dos Carros"], 
                  x="Tipo", y="Valor (R$)", color="Carros", title="Despesas por Tipo")
    st.plotly_chart(fig1)

# Criar gráfico de colunas para Despesas Gerais
with col2:
    st.subheader("Despesas Gerais")
    fig2 = px.bar(df_filtrado[df_filtrado["Categoria"] == "Despesas Gerais"], 
                  x="Tipo", y="Valor (R$)", title="Despesas Gerais")
    st.plotly_chart(fig2)

# Criar gráfico de pizza para Receitas
with col3:
    st.subheader("Receita por Carro")
    fig3 = px.pie(df_filtrado[df_filtrado["Categoria"] == "Receitas"], 
                  names="Carros", values="Valor (R$)", title="Ganhos por Carro")
    st.plotly_chart(fig3)

# Criar gráfico de linha para evolução do faturamento no trimestre
df_trimestre = df[df["Trimestre"] == trimestre_selecionado].groupby(["Mês do Pagamento"])["Valor (R$)"].sum().reset_index()

with col4:
    st.subheader("Evolução do Faturamento")
    fig4 = px.line(df_trimestre, x="Mês do Pagamento", y="Valor (R$)", title=f"Faturamento {trimestre_selecionado}")
    st.plotly_chart(fig4)
# Mostrar totais
st.subheader("Totais")
total_despesas = df_filtrado[df_filtrado["Categoria"].isin(["Despesa dos Carros", "Despesas Gerais"])]["Valor (R$)"].sum()
total_receitas = df_filtrado[df_filtrado["Categoria"] == "Receitas"]["Valor (R$)"].sum()
lucro = total_receitas - total_despesas
dizimo = lucro * 0.1

st.write(df_filtrado)
st.write(f"Total de Despesas: R$ {total_despesas:,.2f}")
st.write(f"Total de Receitas: R$ {total_receitas:,.2f}")
st.write(f"Lucro: R$ {lucro:,.2f}")
st.write(f"Dízimo (10% do Lucro): R$ {dizimo:,.2f}")
