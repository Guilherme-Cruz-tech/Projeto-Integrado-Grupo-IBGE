from pathlib import Path
import streamlit as st
from ibge_utils import read_csv, format_int

st.set_page_config(page_title="Painel IBGE · Censo 2022", page_icon="📊", layout="wide")
st.title("Painel de análises demográficas")
st.caption("Projetos reunidos com os arquivos de dados presentes nesta pasta.")
st.info("Use a barra lateral para abrir os Projetos 1 a 5. Esta página inicial resume as bases disponíveis; cada análise também oferece filtros e gráficos.")

try:
    idade = read_csv("data/censo2022_sexo_raca_idade.csv", required=["sexo", "raca", "idade", "pop"])
    mulheres = read_csv("dados_mulheres_ibge.csv", required=["UF", "Regiao", "Populacao_Total", "Populacao_Feminina"])
    renda = read_csv("rendimento_responsaveis.csv", required=["UF", "Regiao", "Sexo", "Raca", "Rendimento_Responsavel"])
    read_csv("dados_ibge_projeto.csv", required=["UF", "Regiao", "Etnia", "Populacao_Indigena"])
    alfabet = read_csv("dados/ibge_alfabetizacao_sexo_raca.csv", sep=";", required=["Grupo de Cor ou Raça", "Sexo", "Taxa de Alfabetização (%)"])
    a, b, c, d = st.columns(4)
    a.metric("População no arquivo etário", format_int(idade["pop"].sum()))
    b.metric("Unidades federativas", mulheres["UF"].nunique())
    c.metric("Registros de rendimento", format_int(len(renda)))
    d.metric("Grupos de alfabetização", format_int(len(alfabet)))
    st.subheader("Análises disponíveis")
    st.markdown("""
    - **Projeto 1 — Perfil etário:** distribuição por idade, sexo e raça/cor (Censo 2022).
    - **Projeto 2 — Rendimento dos responsáveis:** comparação por região, sexo e raça/cor.
    - **Projeto 3 — Pessoas indígenas:** população, domicílio, rendimento, alfabetização e deslocamento.
    - **Projeto 4 — Mulheres:** população feminina, faixas etárias, renda e alfabetização por UF.
    - **Projeto 5 — Alfabetização:** taxas de alfabetização/analfabetismo por raça/cor e sexo.
    """)
    st.caption("Nota: os arquivos foram preservados como recebidos. Confira a origem e a metodologia de cada CSV antes de tratar os números como estatísticas oficiais do IBGE; especialmente bases de rendimento e exemplos sintéticos.")
except Exception as exc:
    st.error("Não foi possível carregar uma das bases necessárias para o resumo.")
    st.exception(exc)
    st.caption("Confirme que as pastas data/ e dados/ e os arquivos CSV acompanham app_home.py.")
