from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent


def read_csv(relative_path: str, *, sep=",", required=None) -> pd.DataFrame:
    path = ROOT / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Não encontrei o arquivo de dados: {path}")
    df = pd.read_csv(path, sep=sep, encoding="utf-8-sig")
    if required:
        missing = [column for column in required if column not in df.columns]
        if missing:
            raise ValueError(f"O arquivo {path.name} não tem as colunas esperadas: {', '.join(missing)}")
    return df


def format_int(value) -> str:
    try:
        return f"{int(round(float(value))):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "—"


def format_brl(value) -> str:
    try:
        return ("R$ " + f"{float(value):,.2f}").replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return "—"


def style_dark_figure(fig):
    """Aplica a paleta escura/verde usada no Projeto 3 às outras análises."""
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#0b0f19",
        paper_bgcolor="#0b0f19",
        font_color="#f3f4f6",
        colorway=["#34d399", "#60a5fa", "#f43f5e", "#fbbf24", "#a78bfa"],
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.12)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.12)")
    return fig
