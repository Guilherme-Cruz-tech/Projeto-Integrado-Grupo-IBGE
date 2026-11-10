import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Projeto 1 - Perfil Etário", layout="wide")

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
    '<p class="main-title">Projeto 1: Perfil Etário — Distribuição por Sexo e Raça/Cor</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-title">Análise Demográfica do Censo 2022</p>',
    unsafe_allow_html=True,
)
st.markdown("---")


@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("censo2022_sexo_raca_idade.csv")
        return df
    except Exception:
        # Dados de fallback caso o ficheiro CSV ainda não esteja presente na raiz
        return pd.DataFrame({
            "Faixa_Etaria": ["0-4 anos", "5-9 anos", "10-14 anos", "15-19 anos", "20-24 anos", "25-29 anos", "30-39 anos", "40-49 anos", "50-59 anos", "60+ anos"],
            "Regiao": ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul", "Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"],
            "Raca_Cor": ["Branca", "Preta", "Parda", "Amarela", "Indígena", "Branca", "Parda", "Preta", "Branca", "Parda"],
            "Homens": [5200000, 5400000, 5600000, 5800000, 6000000, 6200000, 11000000, 9000000, 7000000, 6500000],
            "Mulheres": [5000000, 5200000, 5400000, 5600000, 5900000, 6100000, 10800000, 8900000, 7200000, 6800000],
        })


df_original = carregar_dados()

with st.sidebar:
    st.markdown("### ⚙️ Painel de Controlo")
    
    regioes = ["Todas"] + sorted(df_original["Regiao"].unique()) if "Regiao" in df_original.columns else ["Todas"]
    regiao_sel = st.selectbox("Região:", regioes)

    racas = ["Todas"] + sorted(df_original["Raca_Cor"].unique()) if "Raca_Cor" in df_original.columns else ["Todas"]
    raca_sel = st.selectbox("Raça/Cor:", racas)

    st.markdown("---")
    st.markdown("#### 📈 Visualizações do Perfil Etário")
    opcao_grafico = st.selectbox(
        "Escolha a Análise:",
        [
            "1. Comparação por Sexo e Faixa Etária",
            "2. Distribuição Populacional por Raça/Cor",
            "3. Gráfico de Dispersão por Idade e Sexo",
            "4. Resumo Estatístico por Região",
        ],
    )

df_filtrado = df_original.copy()
if regiao_sel != "Todas" and "Regiao" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["Regiao"] == regiao_sel]
if raca_sel != "Todas" and "Raca_Cor" in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado["Raca_Cor"] == raca_sel]

st.markdown("### 📌 Indicadores Estatísticos")
c1, c2, c3, c4 = st.columns(4)
total_h = df_filtrado["Homens"].sum() if "Homens" in df_filtrado.columns else 0
total_m = df_filtrado["Mulheres"].sum() if "Mulheres" in df_filtrado.columns else 0
c1.metric("Total Homens", f"{total_h:,.0f}".replace(",", "."))
c2.metric("Total Mulheres", f"{total_m:,.0f}".replace(",", "."))
c3.metric("População Total", f"{(total_h + total_m):,.0f}".replace(",", "."))
c4.metric("Grupos Etários", len(df_filtrado))

st.markdown("---")

if df_filtrado.empty:
    st.warning("⚠️ Nenhum registo encontrado com a combinação de filtros selecionada.")
else:
    st.subheader(f"📊 {opcao_grafico}")

    if opcao_grafico.startswith("1."):
        if "Faixa_Etaria" in df_filtrado.columns and "Homens" in df_filtrado.columns and "Mulheres" in df_filtrado.columns:
            df_melt = df_filtrado.melt(id_vars=["Faixa_Etaria"], value_vars=["Homens", "Mulheres"], var_name="Sexo", value_name="Populacao")
            fig = px.bar(
                df_melt,
                x="Faixa_Etaria",
                y="Populacao",
                color="Sexo",
                barmode="group",
                template="plotly_dark",
                title="População por Faixa Etária e Sexo",
                color_discrete_sequence=["#60a5fa", "#f472b6"],
            )
            fig.update_layout(plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19", font_color="#f3f4f6")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.dataframe(df_filtrado, use_container_width=True)

    elif opcao_grafico.startswith("2."):
        if "Raca_Cor" in df_filtrado.columns:
            df_raca = df_filtrado.groupby("Raca_Cor")[["Homens", "Mulheres"]].sum().reset_index()
            fig = px.bar(
                df_raca,
                x="Raca_Cor",
                y=["Homens", "Mulheres"],
                barmode="stack",
                template="plotly_dark",
                title="Distribuição Populacional por Raça/Cor e Sexo",
                color_discrete_sequence=["#34d399", "#a78bfa"],
            )
            fig.update_layout(plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19", font_color="#f3f4f6")
            st.plotly_chart(fig, use_container_width=True)

    elif opcao_grafico.startswith("3."):
        fig = px.scatter(
            df_filtrado,
            x="Homens",
            y="Mulheres",
            color="Faixa_Etaria" if "Faixa_Etaria" in df_filtrado.columns else None,
            size="Homens",
            template="plotly_dark",
            title="Correlação entre População Masculina e Feminina por Faixa Etária",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig.update_layout(plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19", font_color="#f3f4f6")
        st.plotly_chart(fig, use_container_width=True)

    elif opcao_grafico.startswith("4."):
        if "Regiao" in df_filtrado.columns:
            df_reg = df_filtrado.groupby("Regiao")[["Homens", "Mulheres"]].sum().reset_index()
            fig = px.pie(
                df_reg,
                names="Regiao",
                values="Homens",
                hole=0.4,
                template="plotly_dark",
                title="Proporção da População Masculina por Região",
                color_discrete_sequence=["#34d399", "#60a5fa", "#f43f5e", "#fbbf24", "#a78bfa"],
            )
            fig.update_layout(plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19", font_color="#f3f4f6")
            st.plotly_chart(fig, use_container_width=True)

    with st.expander("📄 Ver tabela completa de dados filtrados"):
        st.dataframe(df_filtrado, use_container_width=True)