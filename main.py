import pandas as pd
import plotly.express as px
import streamlit as st

# =====================
# Configurações iniciais
# =====================
st.set_page_config(page_title="Eficiência da Recomendação", layout="wide")

# Upload do CSV
st.sidebar.header("Parâmetros")
uploaded_file = st.sidebar.file_uploader("Carregar arquivo CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Conversões de data
    df["DATA_LOG"] = pd.to_datetime(df["DATA_LOG"])
    df["ULTIMA_COMPRA"] = pd.to_datetime(df["ULTIMA_COMPRA"], errors="coerce")

    # Definir parâmetro para considerar "compra antiga"
    dias_antigo = st.sidebar.slider("Dias para considerar compra antiga", 30, 720, 60)

    # Classificação da recomendação
    def classificar_recomendacao(row):
        if pd.isna(row["ULTIMA_COMPRA"]):
            return "Novo Produto"
        dias_diff = (row["DATA_LOG"] - row["ULTIMA_COMPRA"]).days
        if dias_diff > dias_antigo:
            return "Compra Antiga"
        return "Recorrente"

    df["STATUS_RECOMENDACAO"] = df.apply(classificar_recomendacao, axis=1)

    # =====================
    # KPIs principais
    # =====================
    total = len(df)
    novos = (df["STATUS_RECOMENDACAO"] == "Novo Produto").sum()
    antigos = (df["STATUS_RECOMENDACAO"] == "Compra Antiga").sum()
    recorrentes = (df["STATUS_RECOMENDACAO"] == "Recorrente").sum()
    totalPedidos = len(df["ID_PEDIDO"].unique())

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Recomendações Aceitas", total)
    col2.metric("Novos Produtos", novos)
    col3.metric("Compras Antigas", antigos)
    col4.metric("Recorrentes", recorrentes)
    col5.metric("Total Pedidos",totalPedidos)

    # =====================
    # Top vendedores
    # =====================
    top_vendedor = df.groupby(["VENDEDOR"]).size().reset_index(name="count")

    # Ordenar do maior para o menor
    top_vendedor = top_vendedor.sort_values(by="count", ascending=False)

    fig_vendedor = px.bar(
        top_vendedor,
        x="VENDEDOR",
        y="count",
        color="VENDEDOR",
        title="Top Vendedores",
        barmode="stack"
    )

    st.plotly_chart(fig_vendedor, use_container_width=True)


    # =====================
    # Gráfico de distribuição
    # =====================
    fig_dist = px.histogram(df, x="STATUS_RECOMENDACAO", color="STATUS_RECOMENDACAO",
                            title="Distribuição das Recomendações")
    st.plotly_chart(fig_dist, use_container_width=True)


    top_prod = df.groupby(["PRODUTO", "STATUS_RECOMENDACAO"]).size().reset_index(name="count")
    top_prod =top_prod.sort_values(by="count", ascending=False)
    fig_prod = px.bar(top_prod, x="PRODUTO", y="count", color="STATUS_RECOMENDACAO",
                      title="Top Produtos Recomendados", barmode="stack")
    fig_prod.update_xaxes(tickangle=45, tickfont=dict(size=10))
    st.plotly_chart(fig_prod, use_container_width=True)

    # =====================
    # Top clientes aderentes
    # =====================
    top_cli = df.groupby(["CLIENTE", "STATUS_RECOMENDACAO"]).size().reset_index(name="count")
    top_cli = top_cli.sort_values(by="count",ascending=False)
    fig_cli = px.bar(top_cli, x="CLIENTE", y="count", color="STATUS_RECOMENDACAO",
                     title="Top Clientes que Mais Aderiram", barmode="stack")
    st.plotly_chart(fig_cli, use_container_width=True)

else:
    st.info("📂 Faça upload do arquivo CSV para começar.")
