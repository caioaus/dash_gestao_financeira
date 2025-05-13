import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# Estilo do app e título
# ==============================
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg, #FF4136, #111);
            color: white;
        }
        h1, h2, h3, h4, h5, h6, p, .stTextInput, .stSelectbox, .stButton {
            color: white !important;
        }
        .stPlotlyChart {
            background-color: rgba(255, 255, 255, 0.1);
            padding: 10px;
            border-radius: 10px;
        }
        section[data-testid="stSidebar"] {
            background-color: black;
            color: red;
        }
        section[data-testid="stSidebar"] * {
            color: red !important;
        }
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap');
        .titulo-container {
            background-color: #800000;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 4px 4px 10px rgba(0, 0, 0, 0.5);
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
    """,
    unsafe_allow_html=True
)

# ==============================
# Upload de Arquivo
# ==============================
st.sidebar.image("logo_fj.jpg", use_container_width=True)
arquivo = st.sidebar.file_uploader("Carregue o arquivo Excel", type=["xlsx"])

if not arquivo:
    st.warning("Por favor, carregue um arquivo Excel (.xlsx) com a aba 'Relatório Mensal'.")
    st.stop()

# ==============================
# Leitura da aba principal
# ==============================
abas = pd.read_excel(arquivo, sheet_name=None)
relatorio = abas.get("Relatório Mensal")

if relatorio is None:
    st.error("A aba 'Relatório Mensal' não foi encontrada.")
    st.stop()

# ==============================
# Tratamento dos dados
# ==============================
df = relatorio.copy()
df.columns = df.columns.str.strip()
df["Valor (R$)"] = df["Valor (R$)"].astype(str).str.replace(r"[^\d,.-]", "", regex=True).str.replace(",", ".")
df["Valor (R$)"] = pd.to_numeric(df["Valor (R$)"], errors='coerce').fillna(0)

# Filtros
ordem_meses_dict = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12
}
df["Mês do Pagamento"] = df["Mês do Pagamento"].astype(str).str.lower().str[:3]
df["Ordem Mês"] = df["Mês do Pagamento"].map(ordem_meses_dict)
meses_disponiveis = (
    df[["Mês do Pagamento", "Ordem Mês"]]
    .dropna()
    .drop_duplicates()
    .sort_values("Ordem Mês")["Mês do Pagamento"]
    .tolist()
)

mes_selecionado = st.sidebar.selectbox("Selecione o Mês", meses_disponiveis, index=0)
dias_disponiveis = sorted(df["Dia do Pagamento"].dropna().unique())
dia_semana_selecionado = st.sidebar.multiselect("Selecione o(s) Dia(s)", dias_disponiveis, default=dias_disponiveis)

df_filtrado = df[
    (df["Mês do Pagamento"] == mes_selecionado) & 
    (df["Dia do Pagamento"].isin(dia_semana_selecionado))
]

# ==============================
# Abas da Interface
# ==============================
aba1, aba2, aba3 = st.tabs(["📊 Gráficos", "🧮 Totais", "🚗 Rentabilidade"])

# ---------------------
# ABA 1 - Gráficos
# ---------------------
with aba1:
    st.subheader("Despesas dos Carros")
    fig1 = px.bar(df_filtrado[df_filtrado["Categoria"] == "Despesa dos Carros"], 
                  x="Tipo", y="Valor (R$)", color="Carros", title="Despesas por Tipo")
    st.plotly_chart(fig1)

    st.subheader("Despesas Gerais")
    fig2 = px.bar(df_filtrado[df_filtrado["Categoria"] == "Despesas Gerais"], 
                  x="Tipo", y="Valor (R$)", title="Despesas Gerais")
    st.plotly_chart(fig2)

    st.subheader("Receita por Carro")
    fig3 = px.pie(df_filtrado[df_filtrado["Categoria"] == "Receitas"], 
                  names="Carros", values="Valor (R$)", title="Ganhos por Carro")
    st.plotly_chart(fig3)

# ---------------------
# ABA 2 - Totais
# ---------------------
with aba2:
    st.subheader("Totais do Mês Selecionado")
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

# ---------------------
# ABA 3 - Rentabilidade
# ---------------------
with aba3:
    st.subheader("Rentabilidade dos Carros")
    df_carros_filtrado = df_filtrado[df_filtrado["Categoria"].isin(["Receitas", "Despesa dos Carros"])].copy()
    df_carros_filtrado = df_carros_filtrado[df_carros_filtrado["Carros"].notna()]
    resumo_carros = df_carros_filtrado.groupby(["Carros", "Categoria"])["Valor (R$)"].sum().unstack(fill_value=0)
    resumo_carros["Lucro"] = resumo_carros.get("Receitas", 0) - resumo_carros.get("Despesa dos Carros", 0)
    resumo_carros["Rentabilidade (%)"] = (resumo_carros["Lucro"] / resumo_carros.get("Despesa dos Carros", 1)) * 100
    resumo_carros = resumo_carros.reset_index()

    fig_rent = px.bar(
        resumo_carros,
        x="Carros",
        y="Lucro",
        color="Lucro",
        color_continuous_scale="Blues",
        title="Lucro Líquido por Carro no Mês Selecionado"
    )
    st.plotly_chart(fig_rent)

    st.markdown("### Tabela de Rentabilidade")
    resumo_exibicao = resumo_carros[["Carros", "Receitas", "Despesa dos Carros", "Lucro", "Rentabilidade (%)"]].copy()
    resumo_exibicao["Rentabilidade (%)"] = resumo_exibicao["Rentabilidade (%)"].round(2)
    st.dataframe(resumo_exibicao.style.format({
        "Receitas": "R$ {:,.2f}",
        "Despesa dos Carros": "R$ {:,.2f}",
        "Lucro": "R$ {:,.2f}",
        "Rentabilidade (%)": "{:.2f} %"
    }))





