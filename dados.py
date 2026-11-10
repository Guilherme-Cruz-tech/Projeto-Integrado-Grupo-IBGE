"""Carga dos dados do Censo 2022 (IBGE/SIDRA).

Tabela usada: 9606 - População residente, por cor ou raça, segundo o sexo e a idade
(Resultados do Universo). Retorna um DataFrame "longo" com as colunas:
    sexo | raca | idade (int, 0-100) | pop
A idade 100 representa "100 anos ou mais".

Ordem de tentativa:
1. CSV em cache (data/censo2022_sexo_raca_idade.csv)
2. API do SIDRA (precisa de internet)
3. Dados de DEMONSTRAÇÃO (sintéticos, apenas para testar o layout)
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import requests

PASTA = Path(__file__).parent / "data"
CACHE = PASTA / "censo2022_sexo_raca_idade.csv"

URL_SIDRA = (
    "https://apisidra.ibge.gov.br/values/t/9606/n1/all/v/93/p/2022"
    "/c2/all/c86/all/c287/all"
)

ULTIMO_ERRO = ""  # motivo da última falha ao baixar (mostrado no app)

RACAS = ["Branca", "Preta", "Amarela", "Parda", "Indígena"]
SEXOS = ["Homens", "Mulheres"]

# Faixas quinquenais (rótulo, idade_min, idade_max)
FAIXAS = [(f"{i} a {i + 4}", i, i + 4) for i in range(0, 100, 5)] + [("100+", 100, 100)]
ROTULOS_FAIXAS = [f[0] for f in FAIXAS]


def _achar_coluna(cabecalho: dict, *nomes: str) -> str:
    """Encontra a chave (D4N, D5N...) cujo rótulo no cabeçalho é IGUAL a um dos nomes."""
    alvo = {n.lower() for n in nomes}
    for chave, rotulo in cabecalho.items():
        if chave.endswith("N") and str(rotulo).strip().lower() in alvo:
            return chave
    raise KeyError(f"Coluna não encontrada para {nomes}")


def _idade_para_int(txt: str):
    txt = str(txt).strip()
    if txt.lower() == "menos de 1 ano":
        return 0  # as linhas em meses ("1 mês", "2 meses"...) já estão dentro desta
    m = re.fullmatch(r"(\d+) anos?", txt)
    if m:
        return int(m.group(1))
    m = re.fullmatch(r"(\d+) anos? ou mais", txt)
    if m:
        return int(m.group(1))
    return None  # linhas de total/grupos/“idade ignorada”


def baixar_sidra(timeout: int = 90) -> pd.DataFrame:
    resp = requests.get(URL_SIDRA, timeout=timeout)
    resp.raise_for_status()
    dados = resp.json()
    cab, linhas = dados[0], dados[1:]
    c_sexo = _achar_coluna(cab, "sexo")
    c_raca = _achar_coluna(cab, "cor ou raça", "cor ou raca")
    c_idade = _achar_coluna(cab, "idade")

    df = pd.DataFrame(linhas)
    df = df.rename(columns={c_sexo: "sexo", c_raca: "raca", c_idade: "idade_txt", "V": "pop"})
    df["idade"] = df["idade_txt"].map(_idade_para_int)
    df["pop"] = pd.to_numeric(df["pop"], errors="coerce")
    df = df[df["idade"].notna() & df["pop"].notna()]
    antes = df.copy()
    df = df[df["sexo"].isin(SEXOS) & df["raca"].isin(RACAS)]
    if df.empty:
        raise ValueError(
            "Nenhuma linha reconhecida. Rótulos recebidos -> "
            f"sexo: {sorted(antes['sexo'].unique())[:8]} | "
            f"raça: {sorted(antes['raca'].unique())[:8]} | "
            f"idade: {sorted(antes['idade_txt'].unique())[:8]}"
        )
    df["idade"] = df["idade"].astype(int)
    return df.groupby(["sexo", "raca", "idade"], as_index=False)["pop"].sum()


def gerar_demo(seed: int = 42) -> pd.DataFrame:
    """Dados SINTÉTICOS (não são do IBGE) só para testar o layout offline."""
    rng = np.random.default_rng(seed)
    idades = np.arange(0, 101)
    base = np.interp(idades, [0, 10, 25, 40, 60, 80, 100], [1.0, 1.05, 1.15, 1.2, 0.8, 0.3, 0.02])
    share_raca = {"Branca": 0.435, "Preta": 0.102, "Amarela": 0.004, "Parda": 0.452, "Indígena": 0.007}
    deslocamento = {"Branca": 3, "Preta": 0, "Amarela": 6, "Parda": -3, "Indígena": -8}
    linhas = []
    for sexo, f_sexo in [("Homens", 0.4925), ("Mulheres", 0.5075)]:
        for raca, f in share_raca.items():
            curva = np.clip(np.interp(idades - deslocamento[raca], idades, base), 0.001, None)
            curva = curva / curva.sum()
            if sexo == "Mulheres":
                curva = curva * (1 + 0.004 * np.clip(idades - 45, 0, None))
                curva = curva / curva.sum()
            pop = 203_000_000 * f_sexo * f * curva * rng.normal(1, 0.01, len(idades))
            linhas += [(sexo, raca, int(i), float(p)) for i, p in zip(idades, pop)]
    return pd.DataFrame(linhas, columns=["sexo", "raca", "idade", "pop"])


def carregar(forcar_download: bool = False, permitir_demo: bool = True):
    """Retorna (DataFrame, origem) onde origem ∈ {'cache','sidra','demo'}."""
    if CACHE.exists() and not forcar_download:
        em_cache = pd.read_csv(CACHE)
        if not em_cache.empty:
            return em_cache, "cache"
        CACHE.unlink()  # cache vazio/corrompido: descarta e baixa de novo
    try:
        df = baixar_sidra()
        PASTA.mkdir(exist_ok=True)
        df.to_csv(CACHE, index=False)
        return df, "sidra"
    except Exception as exc:  # sem internet, API fora do ar, mudança de layout...
        global ULTIMO_ERRO
        ULTIMO_ERRO = f"{type(exc).__name__}: {exc}"
        if not permitir_demo:
            raise
        print(f"[aviso] Não foi possível obter dados do SIDRA: {exc}")
        return gerar_demo(), "demo"


def faixa_de(idade: int) -> str:
    return ROTULOS_FAIXAS[min(idade // 5, 20)]


def adicionar_faixa(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["faixa"] = pd.Categorical(
        df["idade"].map(faixa_de), categories=ROTULOS_FAIXAS, ordered=True
    )
    return df
