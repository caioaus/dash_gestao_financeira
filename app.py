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

# Adiciona o logo na barra lateral
st.sidebar.image("logo_fj.jpg", use_container_width=True)  

# Criar filtros interativos (segmentações de dados)
st.sidebar.header("Filtros")
mes_selecionado = st.sidebar.selectbox("Selecione o Mês", df["Mês do Pagamento"].unique())
dia_semana_selecionado = st.sidebar.multiselect("Selecione o(s) Dia(s) da Semana", 
                                                df["Dia do Pagamento"].unique(), 
                                                default=df["Dia do Pagamento"].unique())

df_filtrado = df[
    (df["Mês do Pagamento"] == mes_selecionado) & 
    (df["Dia do Pagamento"].isin(dia_semana_selecionado))
]


# Criar gráfico de barras para Despesas dos Carros
col1, col2 = st.columns(2)

with col1:
    st.subheader("Despesas dos Carros")
    fig1 = px.bar(df_filtrado[df_filtrado["Categoria"] == "Despesa dos Carros"], 
                  x="Descrição", y="Valor (R$)", color="Carros", title="Despesas por Tipo")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Despesas Gerais")
    fig2 = px.bar(df_filtrado[df_filtrado["Categoria"] == "Despesas Gerais"], 
                  x="Descrição", y="Valor (R$)", title="Despesas Gerais")
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Receita por Carro")
    fig3 = px.pie(df_filtrado[df_filtrado["Categoria"] == "Receitas"], 
                  names="Carros", values="Valor (R$)", title="Ganhos por Carro")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Totais")
    total_despesas = df_filtrado[df_filtrado["Categoria"].isin(["Despesa dos Carros", "Despesas Gerais"])]["Valor (R$)"].sum()
    total_receitas = df_filtrado[df_filtrado["Categoria"] == "Receitas"]["Valor (R$)"].sum()
    lucro = total_receitas - total_despesas
    dizimo = lucro * 0.1

    st.markdown("""
        <div style="border: 2px solid black; padding: 10px; border-radius: 10px; text-align: center;">
            <h3>Totais</h3>
            <p><strong>Total de Despesas:</strong> R$ {:,.2f}</p>
            <p><strong>Total de Receitas:</strong> R$ {:,.2f}</p>
            <p><strong>Lucro:</strong> R$ {:,.2f}</p>
            <p><strong>Dízimo (10% do Lucro):</strong> R$ {:,.2f}</p>
        </div>
    """.format(total_despesas, total_receitas, lucro, dizimo), unsafe_allow_html=True)

# ==============================
# Rentabilidade dos Carros (última linha em 2 colunas)
# ==============================

st.subheader("Rentabilidade dos Carros")
df_carros_filtrado = df_filtrado[df_filtrado["Categoria"].isin(["Receitas", "Despesa dos Carros"])].copy()
df_carros_filtrado = df_carros_filtrado[df_carros_filtrado["Carros"].notna()]

resumo_carros = df_carros_filtrado.groupby(["Carros", "Categoria"])["Valor (R$)"].sum().unstack(fill_value=0)
resumo_carros["Lucro"] = resumo_carros.get("Receitas", 0) - resumo_carros.get("Despesa dos Carros", 0)
resumo_carros["Rentabilidade (%)"] = (resumo_carros["Lucro"] / resumo_carros.get("Despesa dos Carros", 1)) * 100
resumo_carros = resumo_carros.reset_index()

col5, col6 = st.columns(2)

with col5:
    fig_rent = px.bar(
        resumo_carros,
        x="Carros",
        y="Lucro",
        color="Lucro",
        color_continuous_scale="Blues",
        title="Lucro Líquido por Carro"
    )
    st.plotly_chart(fig_rent, use_container_width=True)

with col6:
    st.markdown("### Tabela de Rentabilidade")
    resumo_exibicao = resumo_carros[["Carros", "Receitas", "Despesa dos Carros", "Lucro", "Rentabilidade (%)"]].copy()
    resumo_exibicao["Rentabilidade (%)"] = resumo_exibicao["Rentabilidade (%)"].round(2)
    st.dataframe(resumo_exibicao.style.format({
        "Receitas": "R$ {:,.2f}",
        "Despesa dos Carros": "R$ {:,.2f}",
        "Lucro": "R$ {:,.2f}",
        "Rentabilidade (%)": "{:.2f} %"
    }))
