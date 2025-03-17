import streamlit as st
# Adicionar estilo para fundo com degradê de vermelho para preto
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


# Carregar os dados
arquivo_excel = "C:/Users/Caio/OneDrive/Área de Trabalho/DADOS FJ/dashboard_app/Relatorio_Mensal_py.xlsx"
df = pd.read_excel(arquivo_excel)

df["Valor (R$)"] = df["Valor (R$)"].astype(str).str.replace(r"[^\d.,-]", "", regex=True)
df["Valor (R$)"] = df["Valor (R$)"].str.replace(",", ".").astype(float)
df["Valor (R$)"] = pd.to_numeric(df["Valor (R$)"], errors='coerce')
df["Valor (R$)"].fillna(0, inplace=True)
df.columns = df.columns.str.strip()  # Remove espaços extras nos nomes das colunas

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
st.subheader("Despesas dos Carros")
fig1 = px.bar(df_filtrado[df_filtrado["Categoria"] == "Despesa dos Carros"], 
              x="Tipo", y="Valor (R$)", color="Carros", title="Despesas por Tipo")
st.plotly_chart(fig1)

# Criar gráfico de colunas para Despesas Gerais
st.subheader("Despesas Gerais")
fig2 = px.bar(df_filtrado[df_filtrado["Categoria"] == "Despesas Gerais"], 
              x="Tipo", y="Valor (R$)", title="Despesas Gerais")
st.plotly_chart(fig2)

# Criar gráfico de pizza para Receitas
st.subheader("Receita por Carro")
fig3 = px.pie(df_filtrado[df_filtrado["Categoria"] == "Receitas"], 
              names="Carros", values="Valor (R$)", title="Ganhos por Carro")
st.plotly_chart(fig3)

# Mostrar totais
st.subheader("Totais")
total_despesas = df_filtrado[df_filtrado["Categoria"].isin(["Despesa dos Carros", "Despesas Gerais"])]["Valor (R$)"].sum()
total_receitas = df_filtrado[df_filtrado["Categoria"] == "Receitas"]["Valor (R$)"].sum()
lucro = total_receitas - total_despesas
dizimo = lucro * 0.1

st.write(f"Total de Despesas: R$ {total_despesas:,.2f}")
st.write(f"Total de Receitas: R$ {total_receitas:,.2f}")
st.write(f"Lucro: R$ {lucro:,.2f}")
st.write(f"Dízimo (10% do Lucro): R$ {dizimo:,.2f}")
