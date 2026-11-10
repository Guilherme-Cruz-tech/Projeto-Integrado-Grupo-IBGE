from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Projeto 3 - Pessoas Indígenas", layout="wide")

st.markdown(
    """
    <style>
        .stApp { background-color: #0b0f19; color: #f3f4f6; }
        header[data-testid="stHeader"] { background-color: #0b0f19 !important; }
        .main-title { font-size: 2.2rem; color: #34d399; font-weight: 800; margin-bottom: 0px; }
        .sub-title { font-size: 1.1rem; color: #9ca3af; margin-bottom: 20px; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="main-title">Projeto 3: Pessoas Indígenas — Localização e Situação do Domicílio</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-title">Análise Demográfica, Territorial e Estatística Descritiva</p>',
    unsafe_allow_html=True,
)
st.markdown("---")


@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv(Path(__file__).resolve().parents[1] / "dados_ibge_projeto.csv")
        return df
    except Exception:
        dados_fallback = {
            "UF": ["AM", "RR", "MS", "SP"],
            "Regiao": ["Norte", "Norte", "Centro-Oeste", "Sudeste"],
            "Etnia": ["Tikúna", "Yanomami", "Guarani Kaiowá", "Guarani"],
            "Situacao_Domicilio": ["Rural", "Rural", "Rural", "Urbana"],
            "Populacao_Indigena": [35000, 27000, 45000, 9500],
            "Rendimento_Medio": [1200, 1100, 1500, 2400],
            "Taxa_Alfabetizacao": [78.5, 62.0, 81.0, 96.5],
            "Tempo_Deslocamento": [45, 50, 38, 20],
        }
        return pd.DataFrame(dados_fallback)


df_original = carregar_dados()

with st.sidebar:
    st.markdown("### ⚙️ Painel de Controlo")

    regioes = ["Todas"] + list(df_original["Regiao"].unique())
    regiao_sel = st.selectbox("Região:", regioes)

    if regiao_sel != "Todas":
        ufs_disponiveis = [
            "Todas"
        ] + list(
            df_original[df_original["Regiao"] == regiao_sel]["UF"].unique()
        )
    else:
        ufs_disponiveis = ["Todas"] + list(df_original["UF"].unique())

    uf_sel = st.selectbox("Unidade Federativa (UF):", ufs_disponiveis)

    situacoes = ["Todas"] + list(df_original["Situacao_Domicilio"].unique())
    situacao_sel = st.selectbox("Situação do Domicílio:", situacoes)

    etnias_disp = ["Todas"] + list(df_original["Etnia"].unique())
    etnia_sel = st.selectbox("Etnia Específica:", etnias_disp)

    st.markdown("---")
    st.markdown("#### 📈 Seleção dos 9 Gráficos Obrigatórios")
    opcao_grafico = st.selectbox(
        "Escolha o Tipo de Gráfico:",
        [
            "1. Gráfico de Barras (População Indígena por Região)",
            "2. Boxplot (Dispersão e Outliers da População)",
            "3. Gráfico de Dispersão (Rendimento vs População)",
            "4. Gráfico de Distribuição (Histograma do Rendimento)",
            "5. Gráfico de Frequência (Contagem por Etnia)",
            "6. Heatmap (Densidade: Região vs Domicílio)",
            "7. Gráfico de Linhas (Tempo de Deslocamento por Etnia)",
            "8. Gráfico de Pizza (Proporção Urbana vs Rural)",
            "9. Gráfico de Regressão (Alfabetização vs Rendimento)",
        ],
    )

df_filtrado = df_original.copy()
if regiao_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Regiao"] == regiao_sel]
if uf_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["UF"] == uf_sel]
if situacao_sel != "Todas":
    df_filtrado = df_filtrado[
        df_filtrado["Situacao_Domicilio"] == situacao_sel
    ]
if etnia_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Etnia"] == etnia_sel]

pop_ind = (
    df_filtrado["Populacao_Indigena"]
    if not df_filtrado.empty
    else pd.Series([0])
)
media_pop = pop_ind.mean()
mediana_pop = pop_ind.median()
q1 = np.percentile(pop_ind, 25) if len(pop_ind) > 1 else 0
q3 = np.percentile(pop_ind, 75) if len(pop_ind) > 1 else 0
iqr = q3 - q1
desv_pad = pop_ind.std() if len(pop_ind) > 1 else 0

st.markdown("### 📌 Indicadores Estatísticos Globais")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Média Populacional", f"{media_pop:,.0f} hab".replace(",", "."))
c2.metric("Mediana (Robusta)", f"{mediana_pop:,.0f} hab".replace(",", "."))
c3.metric("IQR (Q3 - Q1)", f"{iqr:,.0f} hab".replace(",", "."))
c4.metric("Desvio Padrão", f"{desv_pad:,.1f} hab".replace(",", "."))

st.markdown("---")

if df_filtrado.empty:
    st.warning(
        "⚠️ Nenhum registo encontrado com a combinação de filtros selecionada."
    )
else:
    st.subheader(f"📊 {opcao_grafico}")

    if opcao_grafico.startswith("1."):
        fig = px.bar(
            df_filtrado.groupby("Regiao")["Populacao_Indigena"]
            .sum()
            .reset_index(),
            x="Regiao",
            y="Populacao_Indigena",
            color="Regiao",
            text_auto=True,
            template="plotly_dark",
            color_discrete_sequence=["#34d399", "#60a5fa", "#f43f5e", "#fbbf24", "#a78bfa"],
        )
        fig.update_layout(
            plot_bgcolor="#0b0f19",
            paper_bgcolor="#0b0f19",
            font_color="#f3f4f6",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif opcao_grafico.startswith("2."):
        fig = px.box(
            df_filtrado,
            x="Regiao",
            y="Populacao_Indigena",
            color="Regiao",
            points="all",
            template="plotly_dark",
            title="Distribuição e Identificação de Outliers por Região",
            color_discrete_sequence=["#34d399", "#60a5fa", "#f43f5e", "#fbbf24", "#a78bfa"],
        )
        
        fig.update_yaxes(
            range=[0, 50000],
            tickmode="linear",
            dtick=5000,
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.1)"
        )
        
        fig.update_layout(
            plot_bgcolor="#0b0f19",
            paper_bgcolor="#0b0f19",
            font_color="#f3f4f6",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif opcao_grafico.startswith("3."):
        fig = px.scatter(
            df_filtrado,
            x="Rendimento_Medio",
            y="Populacao_Indigena",
            color="Etnia",
            size="Populacao_Indigena",
            template="plotly_dark",
            title="Cruzamento de Rendimento Médio e Volume Populacional",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig.update_layout(
            plot_bgcolor="#0b0f19",
            paper_bgcolor="#0b0f19",
            font_color="#f3f4f6",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif opcao_grafico.startswith("4."):
        fig = px.histogram(
            df_filtrado,
            x="Rendimento_Medio",
            nbins=10,
            template="plotly_dark",
            color_discrete_sequence=["#34d399"],
            title="Frequência e Distribuição dos Rendimentos",
        )
        fig.update_layout(
            plot_bgcolor="#0b0f19",
            paper_bgcolor="#0b0f19",
            font_color="#f3f4f6",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif opcao_grafico.startswith("5."):
        freq_df = df_filtrado["Etnia"].value_counts().reset_index()
        freq_df.columns = ["Etnia", "Contagem"]
        fig = px.bar(
            freq_df,
            x="Etnia",
            y="Contagem",
            color="Etnia",
            template="plotly_dark",
            title="Frequência de Ocorrência por Grupo Étnico",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig.update_layout(
            plot_bgcolor="#0b0f19",
            paper_bgcolor="#0b0f19",
            font_color="#f3f4f6",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif opcao_grafico.startswith("6."):
        fig = px.density_heatmap(
            df_filtrado,
            x="Regiao",
            y="Situacao_Domicilio",
            z="Populacao_Indigena",
            histfunc="sum",
            template="plotly_dark",
            title="Mapa de Calor: Concentração Domiciliar e Geográfica",
            color_continuous_scale="Viridis",
        )
        fig.update_layout(
            plot_bgcolor="#0b0f19",
            paper_bgcolor="#0b0f19",
            font_color="#f3f4f6",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif opcao_grafico.startswith("7."):
        fig = px.line(
            df_filtrado.sort_values("Tempo_Deslocamento"),
            x="Etnia",
            y="Tempo_Deslocamento",
            markers=True,
            template="plotly_dark",
            title="Variação do Tempo de Deslocamento por Etnia",
            color_discrete_sequence=["#34d399"],
        )
        fig.update_layout(
            plot_bgcolor="#0b0f19",
            paper_bgcolor="#0b0f19",
            font_color="#f3f4f6",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif opcao_grafico.startswith("8."):
        fig = px.pie(
            df_filtrado,
            names="Situacao_Domicilio",
            values="Populacao_Indigena",
            hole=0.4,
            template="plotly_dark",
            title="Proporção da População por Tipo de Domicílio",
            color_discrete_sequence=["#34d399", "#60a5fa"],
        )
        fig.update_layout(
            plot_bgcolor="#0b0f19",
            paper_bgcolor="#0b0f19",
            font_color="#f3f4f6",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif opcao_grafico.startswith("9."):
        x = df_filtrado["Taxa_Alfabetizacao"]
        y = df_filtrado["Rendimento_Medio"]

        fig = px.scatter(
            df_filtrado,
            x="Taxa_Alfabetizacao",
            y="Rendimento_Medio",
            color="Etnia",
            template="plotly_dark",
            title="Relação entre Alfabetização e Rendimento Médio",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )

        if len(df_filtrado) > 1:
            coef = np.polyfit(x, y, 1)
            poly1d_fn = np.poly1d(coef)
            x_trend = np.linspace(x.min(), x.max(), 100)
            y_trend = poly1d_fn(x_trend)

            fig.add_scatter(
                x=x_trend,
                y=y_trend,
                mode="lines",
                name="Linha de Regressão",
                line=dict(color="#f43f5e", dash="dash"),
            )

        fig.update_layout(
            plot_bgcolor="#0b0f19",
            paper_bgcolor="#0b0f19",
            font_color="#f3f4f6",
        )
        st.plotly_chart(fig, use_container_width=True)