"""Estatísticas descritivas (média, mediana, dispersão) para a pirâmide etária."""
from __future__ import annotations

import numpy as np
import pandas as pd


def media_ponderada(x, w) -> float:
    return float(np.average(x, weights=w))


def mediana_ponderada(x, w) -> float:
    ordem = np.argsort(x)
    x, w = np.asarray(x)[ordem], np.asarray(w)[ordem]
    acum = np.cumsum(w)
    return float(x[np.searchsorted(acum, acum[-1] / 2)])


def quantil_ponderado(x, w, q: float) -> float:
    ordem = np.argsort(x)
    x, w = np.asarray(x)[ordem], np.asarray(w)[ordem]
    acum = np.cumsum(w)
    return float(x[np.searchsorted(acum, acum[-1] * q)])


def desvio_ponderado(x, w) -> float:
    m = media_ponderada(x, w)
    return float(np.sqrt(np.average((np.asarray(x) - m) ** 2, weights=w)))


def estatisticas_idade(df: pd.DataFrame) -> dict:
    """Estatísticas da IDADE das pessoas (cada idade ponderada pela população)."""
    g = df.groupby("idade", as_index=False)["pop"].sum()
    x, w = g["idade"].to_numpy(), g["pop"].to_numpy()
    q1, q3 = quantil_ponderado(x, w, 0.25), quantil_ponderado(x, w, 0.75)
    m, dp = media_ponderada(x, w), desvio_ponderado(x, w)
    return {
        "Idade média (anos)": m,
        "Idade mediana (anos)": mediana_ponderada(x, w),
        "Desvio-padrão (anos)": dp,
        "Coef. de variação (%)": dp / m * 100 if m else np.nan,
        "Q1 (anos)": q1,
        "Q3 (anos)": q3,
        "Intervalo interquartil (anos)": q3 - q1,
    }


def estatisticas_faixas(df: pd.DataFrame) -> dict:
    """Estatísticas do TAMANHO da população por faixa etária (21 faixas de 5 anos)."""
    s = df.groupby("faixa", observed=True)["pop"].sum()
    media, dp = s.mean(), s.std(ddof=0)
    return {
        "Média por faixa (pessoas)": media,
        "Mediana por faixa (pessoas)": s.median(),
        "Desvio-padrão (pessoas)": dp,
        "Coef. de variação (%)": dp / media * 100 if media else np.nan,
        "Mínimo (pessoas)": s.min(),
        "Máximo (pessoas)": s.max(),
        "Amplitude (pessoas)": s.max() - s.min(),
    }


def razao_de_sexo(df: pd.DataFrame, por: str = "faixa") -> pd.DataFrame:
    """Homens para cada 100 mulheres."""
    t = df.pivot_table(index=por, columns="sexo", values="pop", aggfunc="sum", observed=True)
    t["Razão de sexo"] = t["Homens"] / t["Mulheres"] * 100
    return t.reset_index()


def tabela_resumo_por_grupo(df: pd.DataFrame, grupo: str) -> pd.DataFrame:
    """Idade média, mediana e desvio por sexo ou por raça."""
    linhas = []
    for nome, sub in df.groupby(grupo, observed=True):
        e = estatisticas_idade(sub)
        linhas.append(
            {
                grupo.capitalize(): nome,
                "População": sub["pop"].sum(),
                "Idade média": e["Idade média (anos)"],
                "Idade mediana": e["Idade mediana (anos)"],
                "Desvio-padrão": e["Desvio-padrão (anos)"],
                "CV (%)": e["Coef. de variação (%)"],
                "Intervalo interquartil": e["Intervalo interquartil (anos)"],
            }
        )
    return pd.DataFrame(linhas)
