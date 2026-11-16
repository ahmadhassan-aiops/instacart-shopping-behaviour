"""
Chart styling and builders (Plotly).

Colour rules: one colour per single-series chart, a highlight colour plus a
recessive grey when one part of the chart is the point, a one-hue light-to-dark
ramp for the heatmap, and the second categorical slot only when two series are
compared. No colour ramps on bars, no pies.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

# Palette (validated reference palette, light mode)
BLUE = "#2a78d6"       # series 1 / highlight
ORANGE = "#eb6834"     # series 2
QUIET = "#c9d6e6"      # de-emphasised bars (same family as BLUE, recessive)
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SURFACE = "#fcfcfb"
SEQUENTIAL = [
    [0.0, "#f2f7fd"], [0.15, "#cde2fb"], [0.3, "#9ec5f4"], [0.45, "#6da7ec"],
    [0.6, "#3987e5"], [0.75, "#256abf"], [0.9, "#184f95"], [1.0, "#0d366b"],
]

FONT = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
CONFIG = {"displayModeBar": False, "scrollZoom": False}


def style(fig: go.Figure, *, height: int = 360, title: str | None = None, legend: bool = False) -> go.Figure:
    fig.update_layout(
        height=height,
        title=dict(text=title, x=0, xanchor="left", font=dict(size=15, color=INK)) if title else None,
        font=dict(family=FONT, size=13, color=INK_2),
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        margin=dict(l=8, r=16, t=48 if title else 16, b=8),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, xanchor="left", title=None),
        hoverlabel=dict(bgcolor="white", bordercolor=GRID, font=dict(family=FONT, color=INK, size=13)),
        bargap=0.25,
    )
    fig.update_xaxes(automargin=True, showgrid=False, linecolor=AXIS, ticks="", tickfont=dict(color=MUTED), title_font=dict(color=INK_2))
    fig.update_yaxes(automargin=True, gridcolor=GRID, zeroline=False, linecolor=AXIS, tickfont=dict(color=MUTED), title_font=dict(color=INK_2))
    return fig


def bars(
    x, y, *, highlight=None, horizontal: bool = False, hover: str, customdata=None,
    xtitle: str = "", ytitle: str = "", height: int = 360, title: str | None = None,
    text=None,
) -> go.Figure:
    """Single-series bars. `highlight` is a boolean mask: True bars in BLUE, the rest QUIET."""
    n = len(x)
    colors = BLUE if highlight is None else [BLUE if h else QUIET for h in highlight]
    fig = go.Figure(go.Bar(
        x=y if horizontal else x,
        y=x if horizontal else y,
        orientation="h" if horizontal else "v",
        marker=dict(color=colors, line=dict(width=0), cornerradius=4),
        customdata=customdata,
        hovertemplate=hover + "<extra></extra>",
        text=text,
        textposition="outside" if text is not None else None,
        textfont=dict(color=INK_2, size=12),
        cliponaxis=False,
    ))
    style(fig, height=height, title=title)
    if horizontal:
        fig.update_yaxes(autorange="reversed", showgrid=False, tickfont=dict(color=INK_2), title=ytitle, automargin=True)
        fig.update_xaxes(showgrid=True, gridcolor=GRID, title=xtitle)
        fig.update_layout(height=max(height, 26 * n + 60))
    else:
        fig.update_xaxes(title=xtitle)
        fig.update_yaxes(title=ytitle)
    return fig


def heatmap(df: pd.DataFrame, days: list[str], hour_labels: list[str]) -> go.Figure:
    m = df.pivot(index="dow", columns="hour", values="orders").reindex(index=range(7), columns=range(24)).fillna(0)
    fig = go.Figure(go.Heatmap(
        z=m.values, x=hour_labels, y=days,
        colorscale=SEQUENTIAL, xgap=2, ygap=2,
        colorbar=dict(title=dict(text="Orders", side="top"), thickness=10, outlinewidth=0, tickfont=dict(color=MUTED)),
        hovertemplate="%{y}, %{x}<br><b>%{z:,} orders</b><extra></extra>",
    ))
    style(fig, height=330)
    fig.update_yaxes(autorange="reversed", showgrid=False, tickfont=dict(color=INK_2))
    fig.update_xaxes(tickangle=0, nticks=12)
    return fig


def two_lines(x, y1, y2, names: tuple[str, str], *, hover_fmt: str, ytitle: str, xtitle: str = "") -> go.Figure:
    fig = go.Figure()
    for y, name, color in ((y1, names[0], BLUE), (y2, names[1], ORANGE)):
        fig.add_trace(go.Scatter(
            x=x, y=y, name=name, mode="lines",
            line=dict(color=color, width=2.5, shape="spline", smoothing=0.6),
            hovertemplate=f"{name}: %{{y:{hover_fmt}}}<extra></extra>",
        ))
    style(fig, height=360, legend=True)
    fig.update_layout(hovermode="x unified")
    fig.update_xaxes(title=xtitle, showspikes=True, spikecolor=AXIS, spikethickness=1, spikedash="solid")
    fig.update_yaxes(title=ytitle)
    return fig


def vline(fig: go.Figure, x, label: str, bottom: bool = False) -> go.Figure:
    fig.add_vline(x=x, line=dict(color=INK_2, width=1.5, dash="dot"))
    fig.add_annotation(x=x, y=0 if bottom else 1, yref="paper", text=label, showarrow=False, xanchor="left", xshift=6,
                       yanchor="bottom" if bottom else "top", font=dict(color=INK_2, size=12), bgcolor=SURFACE)
    return fig


def hline(fig: go.Figure, y, label: str) -> go.Figure:
    fig.add_hline(y=y, line=dict(color=INK_2, width=1.5, dash="dot"))
    fig.add_annotation(x=1, xref="paper", y=y, text=label, showarrow=False, xanchor="right",
                       yanchor="bottom", font=dict(color=INK_2, size=12), bgcolor=SURFACE)
    return fig
