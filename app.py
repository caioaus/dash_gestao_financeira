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

# Garantir que tudo seja string para aplicar replace
df["Valor (R$)"] = df["Valor (R$)"].astype(str)
df["Valor (R$)"] = df["Valor (R$)"].str.replace(r"[^\d,.-]", "", regex=True)  # mantém números, vírgulas e pontos
df["Valor (R$)"] = df["Valor (R$)"].str.replace(",", ".")  # converte vírgula em ponto

# Converte para float, ignorando erros
df["Valor (R$)"] = pd.to_numeric(df["Valor (R$)"], errors="coerce")
df["Valor (R$)"].fillna(0, inplace=True)

df["Valor (R$)"] = pd.to_numeric(df["Valor (R$)"], errors='coerce')
df["Valor (R$)"].fillna(0, inplace=True)
df.columns = df.columns.str.strip()  # Remove espaços extras nos nomes das colunas

# Adiciona o logo na barra lateral
st.sidebar.image("logo_fj.jpg", use_container_width=True)  

st.sidebar.header("Filtros")

# Lista de meses válidos
# Padroniza os nomes dos meses
# Cria um dicionário com a ordem correta dos meses
ordem_meses_dict = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12
}

# Padroniza os nomes dos meses na coluna
df["Mês do Pagamento"] = df["Mês do Pagamento"].astype(str).str.lower().str[:3]  # pega os 3 primeiros caracteres

# Cria uma coluna auxiliar para ordenar os meses
df["Ordem Mês"] = df["Mês do Pagamento"].map(ordem_meses_dict)

# Remove duplicatas e ordena corretamente
meses_disponiveis = (
    df[["Mês do Pagamento", "Ordem Mês"]]
    .dropna()
    .drop_duplicates()
    .sort_values("Ordem Mês")["Mês do Pagamento"]
    .tolist()
)

# Selectbox com os meses ordenados
mes_selecionado = st.sidebar.selectbox("Selecione o Mês", meses_disponiveis, index=0)


# Verificar se a seleção é válida
if mes_selecionado not in meses_disponiveis:
    st.warning("Selecione um mês válido.")
    st.stop()

# Filtro de dia da semana
dias_disponiveis = sorted(df["Dia do Pagamento"].dropna().unique())
dia_semana_selecionado = st.sidebar.multiselect(
    "Selecione o(s) Dia(s) da Semana",
    dias_disponiveis,
    default=dias_disponiveis
)

# Aplicar o filtro
df_filtrado = df[
    (df["Mês do Pagamento"] == mes_selecionado) & 
    (df["Dia do Pagamento"].isin(dia_semana_selecionado))
]


# Criação das abas
aba1, aba2 = st.tabs(["📊 Análises", "📈 Indicadores Financeiros"])

# ============================
# ABA 1 - Análises Visuais
# ============================
with aba1:
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

    st.markdown("""
        <div style="border: 2px solid black; padding: 10px; border-radius: 10px; text-align: center;">
            <h3>Totais</h3>
            <p><strong>Total de Despesas:</strong> R$ {:,.2f}</p>
            <p><strong>Total de Receitas:</strong> R$ {:,.2f}</p>
            <p><strong>Lucro:</strong> R$ {:,.2f}</p>
            <p><strong>Dízimo (10% do Lucro):</strong> R$ {:,.2f}</p>
        </div>
    """.format(total_despesas, total_receitas, lucro, dizimo), unsafe_allow_html=True)

    # ============================
    # Rentabilidade dos Carros
    # ============================
    st.subheader("Rentabilidade dos Carros")

    # Filtrar apenas receitas e despesas dos carros
    df_carros_filtrado = df_filtrado[df_filtrado["Categoria"].isin(["Receitas", "Despesa dos Carros"])].copy()
    df_carros_filtrado = df_carros_filtrado[df_carros_filtrado["Carros"].notna()]

    # Agrupar e calcular
    resumo_carros = df_carros_filtrado.groupby(["Carros", "Categoria"])["Valor (R$)"].sum().unstack(fill_value=0)
    resumo_carros["Lucro"] = resumo_carros.get("Receitas", 0) - resumo_carros.get("Despesa dos Carros", 0)
    resumo_carros["Rentabilidade (%)"] = (resumo_carros["Lucro"] / resumo_carros.get("Despesa dos Carros", 1)) * 100
    resumo_carros = resumo_carros.reset_index()

    # Gráfico do lucro por carro
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

# ============================
# ABA 2 - Indicadores Financeiros
# ============================
with aba2:
    
    st.header("Indicadores Financeiros")
    st.markdown("<em>Indicadores calculados com base nos filtros de mês e dias da semana selecionados.</em>", unsafe_allow_html=True)

    # Cálculo dos indicadores
    total_receitas = df_filtrado[df_filtrado["Categoria"] == "Receitas"]["Valor (R$)"].sum()
    total_despesas = df_filtrado[df_filtrado["Categoria"].isin(["Despesa dos Carros", "Despesas Gerais"])]["Valor (R$)"].sum()
    lucro = total_receitas - total_despesas
    dizimo = lucro * 0.10

    rentabilidade = (lucro / total_receitas) if total_receitas else 0
    comprometimento = (total_despesas / total_receitas) if total_receitas else 0

    saldo_pos_dizimo = lucro - dizimo

    # Exibir os resultados 
    st.subheader("Indicadores:")
    st.markdown(f"- **Rentabilidade:** {rentabilidade:.2f}")
    st.markdown(f"- **Comprometimento com Despesas:** {comprometimento:.2f}")
    st.markdown(f"- **Saldo após Dízimo:** R$ {saldo_pos_dizimo:,.2f}")

    # Função para cor estilo semáforo
    def cor_indicador(valor, tipo):
        if tipo == "rentabilidade":
        # Rentabilidade alta é bom
            if valor >= 0.5:
                return "green"
            elif valor >= 0.3:
                return "yellow"
            else:
                return "red"
    
        elif tipo == "comprometimento":
        # Comprometimento baixo é bom
            if valor <= 0.5:
                return "green"
            elif valor <= 0.7:
                return "yellow"
            else:
                return "red"
    
        elif tipo == "saldo":
        # Qualquer saldo positivo é bom
            if valor >= 0:
                return "green"
            elif valor >= -0.3:
                return "yellow"
            else:
                return "red"

    # Layout com colunas
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"<div style='background-color:{cor_indicador(rentabilidade, 'rentabilidade')};"
            f"padding:20px;border-radius:10px;text-align:center'>"
            f"<h4 style='color:white'>Rentabilidade</h4>"
            f"<p style='color:white;font-size:24px'>{rentabilidade:.2%}"
            f"</div>",
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"<div style='background-color:{cor_indicador(comprometimento, 'comprometimento')};"
            f"padding:20px;border-radius:10px;text-align:center'>"
            f"<h4 style='color:white'>Comprometimento</h4>"
            f"<p style='color:white;font-size:24px'>{comprometimento:.2%}"
            f"</div>",
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"<div style='background-color:{cor_indicador(saldo_pos_dizimo, 'saldo')};"
            f"padding:20px;border-radius:10px;text-align:center'>"
            f"<h4 style='color:white'>Saldo após Dízimo</h4>"
            f"<p style='color:white;font-size:24px'>R$ {saldo_pos_dizimo:,.2f}"
            f"</div>",
            unsafe_allow_html=True
        )

