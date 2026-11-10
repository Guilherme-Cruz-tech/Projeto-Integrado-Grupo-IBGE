import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Projeto 2 - Rendimento (Matheus C.)", layout="wide")

BG = "#0b0f19"
CORES = ["#34d399", "#60a5fa", "#f43f5e", "#fbbf24", "#a78bfa"]

st.markdown(
    """
    <style>
        .stApp { background-color: #0b0f19; color: #f3f4f6; }
        header[data-testid="stHeader"] { background-color: #0b0f19 !important; }
        .main-title { font-size: 2.2rem; color: #60a5fa; font-weight: 800; margin-bottom: 0px; }
        .sub-title { font-size: 1.1rem; color: #9ca3af; margin-bottom: 20px; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="main-title">Projeto 2: Rendimento dos Responsáveis pelos Domicílios</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-title">Análise Comparativa por Região, Sexo e Raça/Cor</p>',
    unsafe_allow_html=True,
)
st.markdown("---")


@st.cache_data
def carregar_dados():
    try:
        return pd.read_csv("ibge_alfabetizacao_sexo_raca.csv")
    except Exception:
        # Fallback de dados estruturados sintéticos caso o CSV não esteja na raiz
        return pd.DataFrame(
            {
                "UF": ["SP", "RJ", "MG", "BA", "PE", "AM", "PA", "RS", "PR", "GO"],
                "Regiao": ["Sudeste", "Sudeste", "Sudeste", "Nordeste", "Nordeste", "Norte", "Norte", "Sul", "Sul", "Centro-Oeste"],
                "Sexo": ["Homem", "Mulher", "Homem", "Mulher", "Homem", "Mulher", "Homem", "Mulher", "Homem", "Mulher"],
                "Raca": ["Branca", "Preta", "Parda", "Parda", "Preta", "Indígena", "Parda", "Branca", "Branca", "Amarela"],
                "Rendimento": [3200.50, 2800.00, 2450.75, 1650.00, 1580.30, 1420.00, 1750.00, 2900.00, 2850.00, 2300.00],
            }
        )


df_original = carregar_dados()

with st.sidebar:
    st.markdown("### ⚙️ Painel de Controlo")

    regioes = ["Todas"] + sorted(df_original["Regiao"].unique()) if "Regiao" in df_original.columns else ["Todas"]
    regiao_sel = st.selectbox("Região:", regioes)

    sexos = ["Todos"] + sorted(df_original["Sexo"].unique()) if "Sexo" in df_original.columns else ["Todos"]
    sexo_sel = st.selectbox("Sexo:", sexos)

    racas = ["Todas"] + sorted(df_original["Raca"].unique()) if "Raca" in df_original.columns else ["Todas"]
    raca_sel = st.selectbox("Raça/Cor:", racas)

    st.markdown("---")
    st.markdown("#### 📈 Visualizações do Rendimento")
    opcao_grafico = st.selectbox(
        "Escolha a Análise:",
        [
            "1. Mediana de Rendimento por Região",
            "2. Boxplot (Dispersão por Raça/Cor)",
            "3. Gráfico de Barras Comparativo (Sexo)",
            "4. Distribuição do Rendimento por UF",
        ],
    )

df_filtrado = df_original.copy()
if regiao_sel != "Todas" and "Regiao" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["Regiao"] == regiao_sel]
if sexo_sel != "Todos" and "Sexo" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["Sexo"] == sexo_sel]
if raca_sel != "Todas" and "Raca" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["Raca"] == raca_sel]

col_renda = "Rendimento" if "Rendimento" in df_filtrado.columns else df_filtrado.select_dtypes(include=["number"]).columns[0]

renda_media = df_filtrado[col_renda].mean() if not df_filtrado.empty else 0
renda_mediana = df_filtrado[col_renda].median() if not df_filtrado.empty else 0

st.markdown("### 📌 Indicadores Estatísticos")
c1, c2, c3 = st.columns(3)
c1.metric("Rendimento Médio", f"R$ {renda_media:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
c2.metric("Mediana", f"R$ {renda_mediana:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
c3.metric("Registos Filtrados", len(df_filtrado))

st.markdown("---")

def estilo(fig):
    fig.update_layout(plot_bgcolor=BG, paper_bgcolor=BG, font_color="#f3f4f6")
    return fig

if df_filtrado.empty:
    st.warning("⚠️ Nenhum registo encontrado com a combinação de filtros selecionada.")
else:
    st.subheader(f"📊 {opcao_grafico}")

    if opcao_grafico.startswith("1."):
        if "Regiao" in df_filtrado.columns:
            df_grp = df_filtrado.groupby("Regiao")[col_renda].median().reset_index()
            fig = px.bar(
                df_grp,
                x="Regiao",
                y=col_renda,
                color="Regiao",
                template="plotly_dark",
                title="Mediana de Rendimento por Região",
                color_discrete_sequence=CORES,
            )
            st.plotly_chart(estilo(fig), use_container_width=True)

    elif opcao_grafico.startswith("2."):
        if "Raca" in df_filtrado.columns:
            fig = px.box(
                df_filtrado,
                x="Raca",
                y=col_renda,
                color="Raca",
                template="plotly_dark",
                title="Dispersão do Rendimento por Raça/Cor",
                color_discrete_sequence=CORES,
            )
            st.plotly_chart(estilo(fig), use_container_width=True)

    elif opcao_grafico.startswith("3."):
        if "Sexo" in df_filtrado.columns:
            df_grp = df_filtrado.groupby("Sexo")[col_renda].mean().reset_index()
            fig = px.bar(
                df_grp,
                x="Sexo",
                y=col_renda,
                color="Sexo",
                template="plotly_dark",
                title="Rendimento Médio por Sexo",
                color_discrete_sequence=["#60a5fa", "#f472b6"],
            )
            st.plotly_chart(estilo(fig), use_container_width=True)

    elif opcao_grafico.startswith("4."):
        if "UF" in df_filtrado.columns:
            fig = px.bar(
                df_filtrado,
                x="UF",
                y=col_renda,
                color="Regiao" if "Regiao" in df_filtrado.columns else None,
                template="plotly_dark",
                title="Rendimento por UF",
                color_discrete_sequence=CORES,
            )
            st.plotly_chart(estilo(fig), use_container_width=True)

    with st.expander("📄 Ver tabela completa de dados filtrados"):
        st.dataframe(df_filtrado, use_container_width=True)