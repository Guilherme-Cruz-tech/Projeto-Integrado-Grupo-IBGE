import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Projeto - Rendimento dos Responsáveis", layout="wide")

BG = "#0b0f19"
CORES = ["#34d399", "#60a5fa", "#f43f5e", "#fbbf24", "#a78bfa"]

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
    '<p class="main-title">Projeto: Rendimento dos Responsáveis pelos Domicílios</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-title">Distribuição de renda: média vs mediana, quartis, IQR e outliers</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

UF_REGIAO = {
    "AC": "Norte", "AM": "Norte", "AP": "Norte", "PA": "Norte", "RO": "Norte", "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste", "PB": "Nordeste",
    "PE": "Nordeste", "PI": "Nordeste", "RN": "Nordeste", "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MS": "Centro-Oeste", "MT": "Centro-Oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul",
}
BASE_REGIAO = {"Norte": 1700, "Nordeste": 1500, "Centro-Oeste": 2500, "Sudeste": 2700, "Sul": 2600}

def gerar_dados_exemplo(n_por_uf=250, seed=42):
    rng = np.random.default_rng(seed)
    linhas = []
    for uf, reg in UF_REGIAO.items():
        base = BASE_REGIAO[reg] * rng.uniform(0.85, 1.2)
        sexo = rng.choice(["Homem", "Mulher"], n_por_uf, p=[0.55, 0.45])
        raca = rng.choice(["Branca", "Preta", "Parda", "Amarela", "Indígena"], n_por_uf,
                          p=[0.40, 0.10, 0.45, 0.03, 0.02])
        fator = np.where(sexo == "Mulher", 0.82, 1.0) * np.select(
            [raca == "Branca", raca == "Amarela", raca == "Preta", raca == "Indígena"],
            [1.2, 1.3, 0.8, 0.75], default=0.85)
        renda = rng.lognormal(mean=np.log(base), sigma=0.75, size=n_por_uf) * fator
        linhas.append(pd.DataFrame({"UF": uf, "Regiao": reg, "Sexo": sexo, "Raca": raca,
                                    "Rendimento_Responsavel": renda.round(2)}))
    return pd.concat(linhas, ignore_index=True)

@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("rendimento_responsaveis.csv")
        return df, False
    except Exception:
        return gerar_dados_exemplo(), True

df_original, usando_exemplo = carregar_dados()

if usando_exemplo:
    st.info("ℹ️ Arquivo `rendimento_responsaveis.csv` não encontrado: exibindo dados sintéticos de exemplo.")

with st.sidebar:
    st.markdown("### ⚙️ Painel de Controle")
    regioes = ["Todas"] + sorted(df_original["Regiao"].unique())
    regiao_sel = st.selectbox("Região:", regioes)

    base_uf = df_original if regiao_sel == "Todas" else df_original[df_original["Regiao"] == regiao_sel]
    uf_sel = st.selectbox("Unidade Federativa (UF):", ["Todas"] + sorted(base_uf["UF"].unique()))
    sexo_sel = st.selectbox("Sexo:", ["Todos"] + sorted(df_original["Sexo"].unique()))
    raca_sel = st.selectbox("Raça/Cor:", ["Todas"] + sorted(df_original["Raca"].unique()))

    st.markdown("---")
    remover_outliers = st.checkbox("Ocultar outliers (cerca de Tukey)", value=False)

df = df_original.copy()
if regiao_sel != "Todas": df = df[df["Regiao"] == regiao_sel]
if uf_sel != "Todas": df = df[df["UF"] == uf_sel]
if sexo_sel != "Todos": df = df[df["Sexo"] == sexo_sel]
if raca_sel != "Todas": df = df[df["Raca"] == raca_sel]

COL = "Rendimento_Responsavel"

def fmt_brl(v): return "R$ " + f"{v:,.0f}".replace(",", ".")
def estilo(fig):
    fig.update_layout(plot_bgcolor=BG, paper_bgcolor=BG, font_color="#f3f4f6")
    return fig

if df.empty:
    st.warning("⚠️ Nenhum registro encontrado com a combinação de filtros selecionada.")
    st.stop()

renda = df[COL]
media, mediana = renda.mean(), renda.median()
q1, q3 = renda.quantile(0.25), renda.quantile(0.75)
iqr = q3 - q1
lim_inf, lim_sup = q1 - 1.5 * iqr, q3 + 1.5 * iqr
mask_out = (renda < lim_inf) | (renda > lim_sup)
n_out = int(mask_out.sum())
desvio = renda.std()
assimetria = media / mediana if mediana else np.nan

st.markdown("### 📌 Indicadores Estatísticos")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Média", fmt_brl(media))
c2.metric("Mediana", fmt_brl(mediana))
c3.metric("Desvio Padrão", fmt_brl(desvio))
c4.metric("Média / Mediana", f"{assimetria:.2f}")

st.markdown("---")
df_plot = df[~mask_out] if remover_outliers else df

abas = st.tabs(["1. Histograma", "2. Boxplot Região", "3. Boxplot Sexo/Raça", "4. Média vs Mediana UF", "5. Quartis e IQR", "6. Outliers"])

with abas[0]:
    fig = px.histogram(df_plot, x=COL, nbins=50, template="plotly_dark", color_discrete_sequence=["#34d399"])
    fig.add_vline(x=media, line_dash="dash", line_color="#f43f5e")
    fig.add_vline(x=mediana, line_dash="dash", line_color="#fbbf24")
    st.plotly_chart(estilo(fig), use_container_width=True)

with abas[1]:
    fig = px.box(df_plot, x="Regiao", y=COL, color="Regiao", template="plotly_dark", color_discrete_sequence=CORES)
    st.plotly_chart(estilo(fig), use_container_width=True)

with abas[2]:
    col_a, col_b = st.columns(2)
    with col_a:
        fig = px.box(df_plot, x="Sexo", y=COL, color="Sexo", template="plotly_dark", color_discrete_sequence=CORES)
        st.plotly_chart(estilo(fig), use_container_width=True)
    with col_b:
        fig = px.box(df_plot, x="Raca", y=COL, color="Raca", template="plotly_dark", color_discrete_sequence=CORES)
        st.plotly_chart(estilo(fig), use_container_width=True)

with abas[3]:
    por_uf = df.groupby("UF")[COL].agg(Média="mean", Mediana="median").reset_index()
    longo = por_uf.melt(id_vars="UF", var_name="Medida", value_name="Valor")
    fig = px.bar(longo, x="UF", y="Valor", color="Medida", barmode="group", template="plotly_dark", color_discrete_sequence=["#f43f5e", "#34d399"])
    st.plotly_chart(estilo(fig), use_container_width=True)

with abas[4]:
    tab = df.groupby("UF")[COL].agg(Q1=lambda s: s.quantile(0.25), Mediana="median", Q3=lambda s: s.quantile(0.75)).reset_index()
    tab["IQR"] = tab["Q3"] - tab["Q1"]
    fig = px.bar(tab, x="UF", y="IQR", template="plotly_dark", color_discrete_sequence=["#60a5fa"])
    st.plotly_chart(estilo(fig), use_container_width=True)

with abas[5]:
    fig = px.scatter(df.assign(Outlier=np.where(mask_out, "Outlier", "Normal")).reset_index(), x="index", y=COL, color="Outlier", template="plotly_dark", color_discrete_map={"Normal": "#34d399", "Outlier": "#f43f5e"})
    st.plotly_chart(estilo(fig), use_container_width=True)