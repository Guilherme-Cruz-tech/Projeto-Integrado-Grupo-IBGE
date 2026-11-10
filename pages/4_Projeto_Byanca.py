import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Projeto 4 - Mulheres", layout="wide")

st.markdown(
    """
    <style>
        .stApp { background-color: #0b0f19; color: #f3f4f6; }
        header[data-testid="stHeader"] { background-color: #0b0f19 !important; }
        .main-title { font-size: 2.2rem; color: #f472b6; font-weight: 800; margin-bottom: 0px; }
        .sub-title { font-size: 1.1rem; color: #9ca3af; margin-bottom: 20px; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="main-title">Projeto 4: Mulheres — Indicadores da População Feminina</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-title">Recortes e Comparações Territoriais por UF e Região</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

COR_FUNDO = "#0b0f19"
COR_TEXTO = "#f3f4f6"
PALETA = ["#f472b6", "#60a5fa", "#34d399", "#fbbf24", "#a78bfa"]
FAIXAS = {
    "Mulheres_0_14": "0 a 14 anos",
    "Mulheres_15_29": "15 a 29 anos",
    "Mulheres_30_59": "30 a 59 anos",
    "Mulheres_60_mais": "60 anos ou mais",
}


def fmt(valor, casas=0):
    """Formata número no padrão brasileiro (1.234.567,8)."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def estilo(fig):
    fig.update_layout(
        plot_bgcolor=COR_FUNDO, paper_bgcolor=COR_FUNDO, font_color=COR_TEXTO
    )
    return fig


@st.cache_data
def carregar_dados():
    try:
        return pd.read_csv("dados_mulheres_ibge.csv")
    except Exception:
        return pd.DataFrame(
            {
                "UF": ["SP", "BA", "AM", "RS"],
                "Regiao": ["Sudeste", "Nordeste", "Norte", "Sul"],
                "Populacao_Total": [44411000, 14136000, 3942000, 10882000],
                "Populacao_Feminina": [22960000, 7336000, 1987000, 5626000],
                "Pct_Feminina": [51.7, 51.9, 50.4, 51.7],
                "Razao_Sexo": [93.4, 92.7, 98.4, 93.4],
                "Mulheres_0_14": [4000000, 1500000, 490000, 950000],
                "Mulheres_15_29": [5300000, 1800000, 520000, 1200000],
                "Mulheres_30_59": [9600000, 3000000, 800000, 2400000],
                "Mulheres_60_mais": [4000000, 1000000, 177000, 1076000],
                "Pct_Mulheres_Urbana": [97.0, 77.0, 79.0, 88.0],
                "Pct_Domicilios_Chefia_Feminina": [50.0, 52.0, 50.0, 46.0],
                "Rendimento_Medio_Mulheres": [2800, 1600, 1750, 2750],
                "Rendimento_Medio_Homens": [3600, 1900, 2100, 3600],
                "Taxa_Alfabetizacao_Mulheres": [97.0, 88.5, 92.5, 97.5],
                "Taxa_Alfabetizacao_Homens": [96.5, 86.0, 92.0, 97.0],
            }
        )


df_original = carregar_dados()

with st.sidebar:
    st.markdown("### ⚙️ Painel de Controlo")

    regioes = ["Todas"] + sorted(df_original["Regiao"].unique())
    regiao_sel = st.selectbox("Região:", regioes)

    if regiao_sel != "Todas":
        ufs_disponiveis = ["Todas"] + sorted(
            df_original[df_original["Regiao"] == regiao_sel]["UF"].unique()
        )
    else:
        ufs_disponiveis = ["Todas"] + sorted(df_original["UF"].unique())

    uf_sel = st.selectbox("Unidade Federativa (UF):", ufs_disponiveis)

    pct_min, pct_max = float(df_original["Pct_Feminina"].min()), float(
        df_original["Pct_Feminina"].max()
    )
    faixa_pct = st.slider(
        "% de mulheres na população:",
        min_value=pct_min,
        max_value=pct_max,
        value=(pct_min, pct_max),
        step=0.1,
    )

    st.markdown("---")
    st.markdown("#### 📈 Seleção dos 9 Gráficos Obrigatórios")
    opcao_grafico = st.selectbox(
        "Escolha o Tipo de Gráfico:",
        [
            "1. Gráfico de Barras (População Feminina por Região)",
            "2. Boxplot (Dispersão e Outliers do % de Mulheres)",
            "3. Gráfico de Dispersão (Rendimento vs % Urbana)",
            "4. Gráfico de Distribuição (Histograma do Rendimento)",
            "5. Gráfico de Frequência (UFs por Faixa de % Feminina)",
            "6. Heatmap (Região vs Faixa Etária)",
            "7. Gráfico de Linhas (Estrutura Etária por Região)",
            "8. Gráfico de Pizza (Proporção Urbana vs Rural)",
            "9. Gráfico de Regressão (Alfabetização vs Rendimento)",
        ],
    )

df_filtrado = df_original.copy()
if regiao_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Regiao"] == regiao_sel]
if uf_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["UF"] == uf_sel]
df_filtrado = df_filtrado[
    df_filtrado["Pct_Feminina"].between(faixa_pct[0], faixa_pct[1])
]

# ---------------- Indicadores estatísticos ----------------
pop_f = (
    df_filtrado["Populacao_Feminina"]
    if not df_filtrado.empty
    else pd.Series([0])
)
media_pop = pop_f.mean()
mediana_pop = pop_f.median()
q1 = np.percentile(pop_f, 25) if len(pop_f) > 1 else 0
q3 = np.percentile(pop_f, 75) if len(pop_f) > 1 else 0
iqr = q3 - q1
desv_pad = pop_f.std() if len(pop_f) > 1 else 0

st.markdown("### 📌 Indicadores Estatísticos Globais")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Média Populacional", f"{fmt(media_pop)} mulheres")
c2.metric("Mediana (Robusta)", f"{fmt(mediana_pop)} mulheres")
c3.metric("IQR (Q3 - Q1)", f"{fmt(iqr)} mulheres")
c4.metric("Desvio Padrão", f"{fmt(desv_pad, 1)} mulheres")

if not df_filtrado.empty:
    total_f = df_filtrado["Populacao_Feminina"].sum()
    total_pop = df_filtrado["Populacao_Total"].sum()
    renda_m = df_filtrado["Rendimento_Medio_Mulheres"].mean()
    renda_h = df_filtrado["Rendimento_Medio_Homens"].mean()
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Total de Mulheres", fmt(total_f))
    d2.metric("% de Mulheres", f"{fmt(total_f / total_pop * 100, 1)}%")
    d3.metric("Rendimento Médio (Mulheres)", f"R$ {fmt(renda_m)}")
    d4.metric(
        "Mulheres ganham (vs homens)",
        f"{fmt(renda_m / renda_h * 100, 1)}%",
        delta=f"{fmt(renda_m - renda_h)} R$",
    )

st.markdown("---")

if df_filtrado.empty:
    st.warning(
        "⚠️ Nenhum registo encontrado com a combinação de filtros selecionada."
    )
else:
    st.subheader(f"📊 {opcao_grafico}")

    if opcao_grafico.startswith("1."):
        dados = (
            df_filtrado.groupby("Regiao")["Populacao_Feminina"]
            .sum()
            .reset_index()
        )
        fig = px.bar(
            dados,
            x="Regiao",
            y="Populacao_Feminina",
            color="Regiao",
            text_auto=".3s",
            template="plotly_dark",
            title="População Feminina por Região",
            color_discrete_sequence=PALETA,
        )
        st.plotly_chart(estilo(fig), use_container_width=True)

    elif opcao_grafico.startswith("2."):
        fig = px.box(
            df_filtrado,
            x="Regiao",
            y="Pct_Feminina",
            color="Regiao",
            points="all",
            hover_name="UF",
            template="plotly_dark",
            title="Dispersão do Percentual de Mulheres por Região (UFs)",
            color_discrete_sequence=PALETA,
        )
        st.plotly_chart(estilo(fig), use_container_width=True)

    elif opcao_grafico.startswith("3."):
        fig = px.scatter(
            df_filtrado,
            x="Pct_Mulheres_Urbana",
            y="Rendimento_Medio_Mulheres",
            size="Populacao_Feminina",
            color="Regiao",
            hover_name="UF",
            template="plotly_dark",
            title="Rendimento Médio das Mulheres vs % de Mulheres em Área Urbana",
            color_discrete_sequence=PALETA,
        )
        st.plotly_chart(estilo(fig), use_container_width=True)

    elif opcao_grafico.startswith("4."):
        media = df_filtrado["Rendimento_Medio_Mulheres"].mean()
        mediana = df_filtrado["Rendimento_Medio_Mulheres"].median()
        fig = px.histogram(
            df_filtrado,
            x="Rendimento_Medio_Mulheres",
            nbins=10,
            template="plotly_dark",
            title="Distribuição do Rendimento Médio das Mulheres (UFs)",
            color_discrete_sequence=["#f472b6"],
        )
        fig.add_vline(
            x=media,
            line_dash="dash",
            line_color="#fbbf24",
            annotation_text=f"Média: R$ {fmt(media)}",
        )
        fig.add_vline(
            x=mediana,
            line_dash="dot",
            line_color="#34d399",
            annotation_text=f"Mediana: R$ {fmt(mediana)}",
            annotation_position="bottom right",
        )
        st.plotly_chart(estilo(fig), use_container_width=True)

    elif opcao_grafico.startswith("5."):
        fig = px.histogram(
            df_filtrado,
            x="Pct_Feminina",
            nbins=8,
            template="plotly_dark",
            title="Frequência de UFs por Faixa de % de Mulheres",
            color_discrete_sequence=["#a78bfa"],
        )
        fig.update_layout(yaxis_title="Número de UFs")
        st.plotly_chart(estilo(fig), use_container_width=True)

    elif opcao_grafico.startswith("6."):
        longo = df_filtrado.melt(
            id_vars=["UF", "Regiao"],
            value_vars=list(FAIXAS),
            var_name="Faixa",
            value_name="Mulheres",
        )
        longo["Faixa"] = longo["Faixa"].map(FAIXAS)
        fig = px.density_heatmap(
            longo,
            x="Faixa",
            y="Regiao",
            z="Mulheres",
            histfunc="sum",
            template="plotly_dark",
            title="Mapa de Calor: Mulheres por Região e Faixa Etária",
            color_continuous_scale="Viridis",
            category_orders={"Faixa": list(FAIXAS.values())},
        )
        st.plotly_chart(estilo(fig), use_container_width=True)

    elif opcao_grafico.startswith("7."):
        longo = df_filtrado.melt(
            id_vars=["Regiao"],
            value_vars=list(FAIXAS),
            var_name="Faixa",
            value_name="Mulheres",
        )
        longo["Faixa"] = longo["Faixa"].map(FAIXAS)
        agr = longo.groupby(["Regiao", "Faixa"], as_index=False)["Mulheres"].sum()
        agr["Percentual"] = (
            agr["Mulheres"] / agr.groupby("Regiao")["Mulheres"].transform("sum") * 100
        )
        fig = px.line(
            agr,
            x="Faixa",
            y="Percentual",
            color="Regiao",
            markers=True,
            template="plotly_dark",
            title="Estrutura Etária da População Feminina (% por faixa)",
            color_discrete_sequence=PALETA,
            category_orders={"Faixa": list(FAIXAS.values())},
        )
        fig.update_layout(yaxis_title="% das mulheres da região")
        st.plotly_chart(estilo(fig), use_container_width=True)

    elif opcao_grafico.startswith("8."):
        urb = (
            df_filtrado["Populacao_Feminina"] * df_filtrado["Pct_Mulheres_Urbana"] / 100
        ).sum()
        rur = df_filtrado["Populacao_Feminina"].sum() - urb
        fig = px.pie(
            names=["Urbana", "Rural"],
            values=[urb, rur],
            hole=0.4,
            template="plotly_dark",
            title="Proporção de Mulheres por Situação do Domicílio",
            color_discrete_sequence=["#f472b6", "#60a5fa"],
        )
        st.plotly_chart(estilo(fig), use_container_width=True)

    elif opcao_grafico.startswith("9."):
        x = df_filtrado["Rendimento_Medio_Mulheres"]
        y = df_filtrado["Taxa_Alfabetizacao_Mulheres"]
        fig = px.scatter(
            df_filtrado,
            x="Rendimento_Medio_Mulheres",
            y="Taxa_Alfabetizacao_Mulheres",
            color="Regiao",
            hover_name="UF",
            template="plotly_dark",
            title="Relação entre Rendimento e Alfabetização das Mulheres",
            color_discrete_sequence=PALETA,
        )
        if len(df_filtrado) > 1 and x.nunique() > 1:
            coef = np.polyfit(x, y, 1)
            x_trend = np.linspace(x.min(), x.max(), 100)
            fig.add_scatter(
                x=x_trend,
                y=np.poly1d(coef)(x_trend),
                mode="lines",
                name="Linha de Regressão",
                line=dict(color="#fbbf24", dash="dash"),
            )
        st.plotly_chart(estilo(fig), use_container_width=True)

    with st.expander("📄 Ver tabela de dados filtrados"):
        st.dataframe(df_filtrado, use_container_width=True)