#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard: Capacidade de Atendimento dos Corpos de Bombeiros no Brasil
Pergunta central: O Brasil tem Bombeiros suficientes para proteger sua população?

Fontes:
  - SENASP/MJSP — Perfil dos Corpos de Bombeiros Militar (ano base 2024)
  - IBGE — Censo Demográfico 2022
  - IBGE — Projeção Populacional 2024
  - NFPA — Fire Department Profile 2020 (referência: 1,54 bombeiros/1.000 hab.)

Autor: [Autor(a)] — Mestrado IDP
Data: Agosto 2026
"""

import warnings
warnings.filterwarnings("ignore")

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.gridspec import GridSpec
import geobr

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO GERAL
# ══════════════════════════════════════════════════════════════════════════════

BASE = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(BASE, "output")
os.makedirs(SAIDA, exist_ok=True)

# Paleta Okabe-Ito (acessível para daltônicos)
CORES = {
    "laranja":   "#E69F00",
    "azul_cl":   "#56B4E9",
    "verde":     "#009E73",
    "amarelo":   "#F0E442",
    "azul":      "#0072B2",
    "vermelho":  "#D55E00",
    "rosa":      "#CC79A7",
    "preto":     "#000000",
    "cinza":     "#999999",
    "cinza_cl":  "#DDDDDD",
    "branco":    "#FFFFFF",
    "fundo":     "#FAFAFA",
}

# Referência NFPA
META = 1.54  # bombeiros por 1.000 habitantes
LABEL_META = "Referência NFPA Research 2022 (1,54 / 1.000 hab.)"

# Região por UF
REGIOES = {
    "Norte":        ["AC", "AM", "AP", "PA", "RO", "RR", "TO"],
    "Nordeste":     ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "Centro-Oeste": ["DF", "GO", "MS", "MT"],
    "Sudeste":      ["ES", "MG", "RJ", "SP"],
    "Sul":          ["PR", "RS", "SC"],
}
UF_REGIAO = {}
for reg, ufs in REGIOES.items():
    for uf in ufs:
        UF_REGIAO[uf] = reg

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "figure.facecolor": CORES["fundo"],
    "axes.facecolor": CORES["branco"],
    "axes.edgecolor": CORES["cinza"],
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})


# ══════════════════════════════════════════════════════════════════════════════
# 1. CARREGAMENTO DOS DADOS
# ══════════════════════════════════════════════════════════════════════════════

print("Carregando dados...")

# --- SENASP 2024 (CSV local) ---
df_senasp = pd.read_csv(
    os.path.join(BASE, "base-dados", "bd_senas.mjsp_perfil_cbm_ano_base_2024.csv"),
    sep=None, engine="python", encoding="utf-8-sig"
)
df_senasp.columns = df_senasp.columns.str.strip()

# --- IBGE Censo 2022 (CSV local) ---
df_ibge = pd.read_csv(
    os.path.join(BASE, "base-dados", "bd_ibge_censo_2022_municipio.csv"),
    sep=None, engine="python", encoding="utf-8"
)
df_ibge.columns = df_ibge.columns.str.strip()

# --- Dados multianuais CBM (Excel) ---
anos = [2020, 2021, 2022, 2023, 2024]
df_multi = []
for ano in anos:
    path = os.path.join(
        BASE, "base-dados", "Anos_Base_2020_2024",
        f"Ano_base_{ano}", f"Banco de dados CBM ano base {ano}.xlsx"
    )
    tmp = pd.read_excel(path, sheet_name=f"Base_CBM_{ano}")
    tmp.columns = tmp.columns.str.strip()

    uf_col = tmp.columns[0]
    efetivo_col = [c for c in tmp.columns if "Quantidade total do efetivo na ATIVA" in c][0]
    op_m_col = [c for c in tmp.columns if "Efetivo do CBM na Ativa com atividade Operacional Masculino" in c][0]
    op_f_col = [c for c in tmp.columns if "Efetivo do CBM na Ativa com atividade Operacional Feminino" in c][0]

    for _, row in tmp.iterrows():
        uf = str(row[uf_col]).strip()
        if len(uf) == 2 and uf.isalpha():
            uf = uf.upper()
        else:
            continue
        efetivo = pd.to_numeric(row[efetivo_col], errors="coerce") or 0
        op_m = pd.to_numeric(row[op_m_col], errors="coerce") or 0
        op_f = pd.to_numeric(row[op_f_col], errors="coerce") or 0
        df_multi.append({
            "ano": ano, "uf": uf,
            "efetivo_ativa": efetivo,
            "efetivo_operacional": op_m + op_f,
        })

df_multi = pd.DataFrame(df_multi)


# ══════════════════════════════════════════════════════════════════════════════
# 2. TRATAMENTO E CÁLCULOS
# ══════════════════════════════════════════════════════════════════════════════

print("Tratando dados...")

# --- Efetivo por UF (SENASP 2024) ---
cols_num = ["e1", "e1.1.1.1", "e1.1.1.2", "e1.1.1.3", "e2.1.1", "e2.1.2"]
for col in cols_num:
    df_senasp[col] = pd.to_numeric(df_senasp[col], errors="coerce")

df_senasp["efetivo_ativa"] = df_senasp["e1"]
df_senasp["efetivo_combatente"] = df_senasp[["e1.1.1.1", "e1.1.1.2", "e1.1.1.3"]].sum(axis=1)
df_senasp["efetivo_operacional"] = df_senasp[["e2.1.1", "e2.1.2"]].sum(axis=1, min_count=1)

# --- População por UF (IBGE Censo 2022) ---
pop_por_uf = df_ibge.groupby("sigla_uf")["populacao"].sum().reset_index()
pop_por_uf.columns = ["uf", "populacao"]
pop_total = pop_por_uf["populacao"].sum()

# --- Merge principal 2024 ---
df_2024 = pd.merge(
    df_senasp[["uf", "efetivo_ativa", "efetivo_combatente", "efetivo_operacional"]],
    pop_por_uf, on="uf"
)
df_2024["prop_ativa"] = (df_2024["efetivo_ativa"] / df_2024["populacao"]) * 1000
df_2024["prop_combatente"] = (df_2024["efetivo_combatente"] / df_2024["populacao"]) * 1000
df_2024["prop_operacional"] = (df_2024["efetivo_operacional"] / df_2024["populacao"]) * 1000
df_2024["regiao"] = df_2024["uf"].map(UF_REGIAO)
df_2024 = df_2024.dropna(subset=["prop_ativa"])

# --- Déficit nacional ---
efetivo_total = df_2024["efetivo_ativa"].sum()
meta_nacional = round((META / 1000) * pop_total)
deficit = meta_nacional - efetivo_total
prop_nacional = (efetivo_total / pop_total) * 1000

# --- Evolução temporal nacional ---
evolucao = df_multi.groupby("ano").agg(
    efetivo_ativa=("efetivo_ativa", "sum"),
    efetivo_operacional=("efetivo_operacional", "sum"),
).reset_index()
evolucao["populacao_ref"] = pop_total
evolucao["prop_ativa"] = (evolucao["efetivo_ativa"] / evolucao["populacao_ref"]) * 1000
evolucao["prop_operacional"] = (evolucao["efetivo_operacional"] / evolucao["populacao_ref"]) * 1000

# --- UFs acima e abaixo da meta ---
acima_meta = df_2024[df_2024["prop_ativa"] >= META].sort_values("prop_ativa", ascending=False)
abaixo_meta = df_2024[df_2024["prop_ativa"] < META].sort_values("prop_ativa")

print(f"  População Brasil: {pop_total:,.0f}")
print(f"  Efetivo total ativa 2024: {efetivo_total:,.0f}")
print(f"  Meta NFPA: {meta_nacional:,.0f}")
print(f"  Déficit: {deficit:,.0f}")
print(f"  Proporção nacional: {prop_nacional:.2f}/1.000 hab.")
print(f"  UFs acima da meta: {list(acima_meta['uf'])}")
print(f"  Pior UF: {abaixo_meta.iloc[0]['uf']} ({abaixo_meta.iloc[0]['prop_ativa']:.2f})")


# ══════════════════════════════════════════════════════════════════════════════
# 3. FUNÇÕES AUXILIARES
# ══════════════════════════════════════════════════════════════════════════════

def fmt(n, dec=0):
    """Formata número no padrão brasileiro."""
    if dec == 0:
        return f"{int(n):,}".replace(",", ".")
    return f"{n:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def caixa_insight(ax, texto, x=0.98, y=0.95, fontsize=9, cor_fundo=CORES["amarelo"]):
    """Caixa de insight narrativo no canto superior direito do eixo."""
    ax.text(
        x, y, texto, transform=ax.transAxes,
        fontsize=fontsize, fontweight="bold", color=CORES["preto"],
        ha="right", va="top",
        bbox=dict(boxstyle="round,pad=0.5", facecolor=cor_fundo, alpha=0.85, edgecolor="none"),
    )


def nota_rodape(fig, texto, y=-0.01):
    """Adiciona nota de rodapé na figura."""
    fig.text(0.5, y, texto, ha="center", fontsize=8, color=CORES["cinza"], style="italic")


# ══════════════════════════════════════════════════════════════════════════════
# 4. VISUALIZAÇÃO 1 — Abertura: Déficit Numérico
# ══════════════════════════════════════════════════════════════════════════════

print("\nGerando Visualização 1: Déficit numérico...")

fig1, ax1 = plt.subplots(figsize=(12, 6))

categorias = ["Efetivo\nAtual (2024)", "Meta NFPA\n(necessário)"]
valores = [efetivo_total, meta_nacional]
cores_bar = [CORES["vermelho"], CORES["azul"]]

barras = ax1.bar(categorias, valores, color=cores_bar, width=0.45, edgecolor="white", linewidth=2)

for barra, valor in zip(barras, valores):
    ax1.text(
        barra.get_x() + barra.get_width() / 2, barra.get_height() + 4000,
        f"{fmt(valor)}", ha="center", va="bottom",
        fontsize=18, fontweight="bold", color=CORES["preto"],
    )

# Anotação narrativa: déficit
ax1.annotate(
    f"Só temos {fmt(efetivo_total)} Bombeiros.\nFaltam {fmt(deficit)} para proteger a população.",
    xy=(0.5, 0.55), xycoords="axes fraction",
    fontsize=13, fontweight="bold", color=CORES["vermelho"], ha="center",
    bbox=dict(boxstyle="round,pad=0.5", facecolor=CORES["amarelo"], alpha=0.85, edgecolor="none"),
)

# Proporção
ax1.text(
    0.5, 0.38,
    f"Isso equivale a apenas {prop_nacional:.2f} Bombeiros\npara cada 1.000 habitantes.",
    transform=ax1.transAxes, fontsize=11, ha="center", color=CORES["cinza"],
    style="italic",
)

ax1.set_title(
    "O Brasil tem déficit de 242 mil Bombeiros em relação ao padrão internacional",
    fontsize=14, fontweight="bold", pad=20, loc="left",
)
ax1.set_ylabel("Quantidade de Bombeiros Militares", fontsize=11)
ax1.set_ylim(0, meta_nacional * 1.3)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
ax1.grid(axis="x", visible=False)
ax1.grid(axis="y", alpha=0.2)

handles1 = [
    mpatches.Patch(color=CORES["vermelho"], label=f"Efetivo atual: {fmt(efetivo_total)}"),
    mpatches.Patch(color=CORES["azul"], label=f"Meta NFPA: {fmt(meta_nacional)}"),
]
ax1.legend(handles=handles1, loc="upper left", fontsize=9, framealpha=0.9)

nota_rodape(fig1, "Fonte: SENASP/MJSP 2024 · IBGE Censo 2022 · NFPA Fire Department Profile 2020.", y=-0.04)

plt.tight_layout()
fig1.savefig(os.path.join(SAIDA, "v1_deficit.png"), dpi=150, bbox_inches="tight", facecolor=fig1.get_facecolor())
plt.close(fig1)
print("  -> output/v1_deficit.png")


# ══════════════════════════════════════════════════════════════════════════════
# 5. VISUALIZAÇÃO 2 — Mapa Coroplético
# ══════════════════════════════════════════════════════════════════════════════

print("Gerando Visualização 2: Mapa coroplético...")

gdf = geobr.read_state(year=2022)
gdf = gdf.rename(columns={"abbrev_state": "uf"})
gdf_mapa = pd.merge(gdf, df_2024[["uf", "prop_ativa"]], on="uf", how="left")

fig2, ax2 = plt.subplots(figsize=(12, 10))

vmin, vmax = 0, gdf_mapa["prop_ativa"].max()
gdf_mapa.plot(
    column="prop_ativa", ax=ax2, legend=False,
    cmap="YlOrRd", edgecolor="white", linewidth=0.5,
    vmin=vmin, vmax=vmax,
)

sm = plt.cm.ScalarMappable(cmap="YlOrRd", norm=plt.Normalize(vmin=vmin, vmax=vmax))
sm._A = []
cbar = fig2.colorbar(sm, ax=ax2, fraction=0.03, pad=0.04, shrink=0.6)
cbar.set_label("Bombeiros por 1.000 Habitantes", fontsize=10)
cbar.ax.axhline(y=META, color=CORES["preto"], linewidth=2)
cbar.ax.text(1.5, META, f"NFPA ({META})", transform=cbar.ax.get_yaxis_transform(),
             fontsize=8, va="center", fontweight="bold")

for _, row in gdf_mapa.iterrows():
    c = row.geometry.centroid
    x, y = c.x, c.y
    if row["uf"] == "DF":
        x += 1.5; y -= 0.3
    elif row["uf"] == "RR":
        y += 0.3
    pv = row["prop_ativa"]
    if pd.notna(pv):
        ct = CORES["verde"] if pv >= META else CORES["preto"]
        ax2.text(x, y, f"{row['uf']}\n{pv:.2f}", ha="center", va="center",
                fontsize=6, fontweight="bold", color=ct,
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white", alpha=0.7, edgecolor="none"))

# Insight narrativo
caixa_insight(ax2,
    "Apenas 2 estados (DF e AP)\n ultrapassam a referência.\nTodos os demais estão abaixo.",
    x=0.98, y=0.97, fontsize=10,
)

ax2.set_title(
    "A maioria dos estados está muito abaixo da referência internacional",
    fontsize=14, fontweight="bold", pad=15, loc="left",
)
ax2.set_axis_off()
nota_rodape(fig2, "Fonte: SENASP/MJSP 2024 · IBGE Censo 2022. Bombeiros Militares da Ativa por 1.000 habitantes.", y=0.01)

plt.tight_layout()
fig2.savefig(os.path.join(SAIDA, "v2_mapa.png"), dpi=150, bbox_inches="tight", facecolor=fig2.get_facecolor())
plt.close(fig2)
print("  -> output/v2_mapa.png")


# ══════════════════════════════════════════════════════════════════════════════
# 6. VISUALIZAÇÃO 3 — Lollipop Chart
# ══════════════════════════════════════════════════════════════════════════════

print("Gerando Visualização 3: Lollipop por UF...")

df_lolli = df_2024.sort_values("prop_ativa", ascending=True).copy()

fig3, ax3 = plt.subplots(figsize=(12, 10))

y_pos = range(len(df_lolli))
cores_lolli = [CORES["verde"] if v >= META else CORES["vermelho"] for v in df_lolli["prop_ativa"]]

ax3.hlines(y=y_pos, xmin=0, xmax=df_lolli["prop_ativa"], color=cores_lolli, linewidth=1.5, alpha=0.7)
ax3.scatter(df_lolli["prop_ativa"], y_pos, color=cores_lolli, s=50, zorder=5, edgecolors="white", linewidth=0.5)
ax3.axvline(x=META, color=CORES["azul"], linestyle="--", linewidth=1.8, zorder=4, alpha=0.8)

for i, (_, row) in enumerate(df_lolli.iterrows()):
    ax3.text(
        row["prop_ativa"] + 0.02, i, f'{row["prop_ativa"]:.2f}',
        va="center", ha="left", fontsize=8, fontweight="bold",
        color=CORES["verde"] if row["prop_ativa"] >= META else CORES["preto"],
    )

ax3.set_yticks(y_pos)
ax3.set_yticklabels(df_lolli["uf"], fontsize=9)
ax3.set_xlabel("Bombeiros por 1.000 Habitantes", fontsize=11)
ax3.set_title(
    "Quase nenhum estado atende à referência internacional de Bombeiros",
    fontsize=14, fontweight="bold", pad=15, loc="left",
)
ax3.set_xlim(0, df_lolli["prop_ativa"].max() * 1.3)
ax3.grid(axis="y", visible=False)
ax3.grid(axis="x", alpha=0.2)

# Destaque DF e AP
for _, row in acima_meta.iterrows():
    idx = list(df_lolli["uf"]).index(row["uf"])
    ax3.annotate(
        "★", xy=(row["prop_ativa"], idx), fontsize=16,
        color=CORES["laranja"], ha="center", va="center", fontweight="bold",
    )

# Insight
n_abaixo = len(abaixo_meta)
caixa_insight(ax3,
    f"{n_abaixo} dos 27 estados\nestão abaixo da meta.\nApenas DF e AP ★ ultrapassam.",
    x=0.98, y=0.97, fontsize=10,
)

handles3 = [
    mlines.Line2D([], [], color=CORES["azul"], linestyle="--", linewidth=1.8, label=LABEL_META),
    mpatches.Patch(color=CORES["verde"], label="Acima da referência (★)"),
    mpatches.Patch(color=CORES["vermelho"], label="Abaixo da referência"),
]
ax3.legend(handles=handles3, loc="lower right", fontsize=9, framealpha=0.9)

nota_rodape(fig3, "Fonte: SENASP/MJSP 2024 · IBGE Censo 2022 · NFPA Fire Department Profile 2020.", y=-0.01)

plt.tight_layout()
fig3.savefig(os.path.join(SAIDA, "v3_lollipop.png"), dpi=150, bbox_inches="tight", facecolor=fig3.get_facecolor())
plt.close(fig3)
print("  -> output/v3_lollipop.png")


# ══════════════════════════════════════════════════════════════════════════════
# 7. VISUALIZAÇÃO 4 — Evolução Temporal 2020–2024
# ══════════════════════════════════════════════════════════════════════════════

print("Gerando Visualização 4: Evolução temporal...")

fig4, (ax4a, ax4b) = plt.subplots(1, 2, figsize=(14, 5.5))

# --- Esquerda: Efetivo total ---
ax4a.fill_between(evolucao["ano"], evolucao["efetivo_ativa"], alpha=0.12, color=CORES["azul"])
ax4a.plot(evolucao["ano"], evolucao["efetivo_ativa"], marker="o", color=CORES["azul"],
          linewidth=2.5, markersize=8, label="Efetivo Ativa (total)", zorder=5)

ax4a.fill_between(evolucao["ano"], evolucao["efetivo_operacional"], alpha=0.12, color=CORES["laranja"])
ax4a.plot(evolucao["ano"], evolucao["efetivo_operacional"], marker="s", color=CORES["laranja"],
          linewidth=2.5, markersize=8, label="Efetivo Operacional", zorder=5)

ax4a.axhline(y=meta_nacional, color=CORES["vermelho"], linestyle="--", linewidth=1.5, alpha=0.7)
ax4a.text(2024.15, meta_nacional, f"Meta NFPA\n{fmt(meta_nacional)}", fontsize=8,
          color=CORES["vermelho"], va="center", fontweight="bold")

for _, row in evolucao.iterrows():
    ax4a.annotate(
        fmt(row["efetivo_ativa"]),
        xy=(row["ano"], row["efetivo_ativa"]),
        xytext=(0, 10), textcoords="offset points",
        ha="center", fontsize=8, fontweight="bold", color=CORES["azul"],
    )

# Insight
caixa_insight(ax4a,
    "Em 5 anos, o efetivo cresceu\napenas 4% — a defasagem\ncom a meta internacional\ncontinua enorme.",
    x=0.98, y=0.55, fontsize=9,
)

ax4a.set_title("Efetivo total cresceu apenas 4% em 5 anos", fontsize=12, fontweight="bold", loc="left")
ax4a.set_ylabel("Quantidade de Bombeiros", fontsize=10)
ax4a.set_xticks(evolucao["ano"])
ax4a.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
ax4a.legend(fontsize=9, loc="upper left")
ax4a.set_ylim(0, meta_nacional * 1.1)
ax4a.grid(axis="x", visible=False)

# --- Direita: Proporção ---
ax4b.plot(evolucao["ano"], evolucao["prop_ativa"], marker="o", color=CORES["azul"],
          linewidth=2.5, markersize=8, label="Ativa / 1.000 hab.", zorder=5)
ax4b.plot(evolucao["ano"], evolucao["prop_operacional"], marker="s", color=CORES["laranja"],
          linewidth=2.5, markersize=8, label="Operacional / 1.000 hab.", zorder=5)
ax4b.axhline(y=META, color=CORES["vermelho"], linestyle="--", linewidth=1.5, alpha=0.7, label=LABEL_META)

for _, row in evolucao.iterrows():
    ax4b.annotate(
        f'{row["prop_ativa"]:.2f}',
        xy=(row["ano"], row["prop_ativa"]),
        xytext=(0, 10), textcoords="offset points",
        ha="center", fontsize=8, fontweight="bold", color=CORES["azul"],
    )

# Insight
caixa_insight(ax4b,
    "A proporção se mantém\npraticamente estável.\nNão há tendência de melhora.",
    x=0.98, y=0.55, fontsize=9,
)

ax4b.set_title("Proporção estagnada muito abaixo da meta", fontsize=12, fontweight="bold", loc="left")
ax4b.set_ylabel("Bombeiros por 1.000 Habitantes", fontsize=10)
ax4b.set_xticks(evolucao["ano"])
ax4b.legend(fontsize=8, loc="upper left")
ax4b.set_ylim(0, META * 0.5)
ax4b.grid(axis="x", visible=False)

nota_rodape(fig4,
    "Fonte: SENASP/MJSP (anos base 2020–2024) · IBGE Censo 2022. População de referência: 202.083.020 hab.",
    y=-0.06,
)

plt.tight_layout()
fig4.savefig(os.path.join(SAIDA, "v4_evolucao.png"), dpi=150, bbox_inches="tight", facecolor=fig4.get_facecolor())
plt.close(fig4)
print("  -> output/v4_evolucao.png")


# ══════════════════════════════════════════════════════════════════════════════
# 8. VISUALIZAÇÃO 5 — Box Plot por Região
# ══════════════════════════════════════════════════════════════════════════════

print("Gerando Visualização 5: Box plot por região...")

df_regiao = df_2024[df_2024["regiao"].notna()].copy()
ordem_regioes = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]
cores_regiao = [CORES["verde"], CORES["laranja"], CORES["azul"], CORES["rosa"], CORES["azul_cl"]]

fig5, ax5 = plt.subplots(figsize=(12, 6))

dados_box = [df_regiao[df_regiao["regiao"] == r]["prop_ativa"].values for r in ordem_regioes]

bp = ax5.boxplot(
    dados_box, tick_labels=ordem_regioes, patch_artist=True,
    widths=0.5, showmeans=True,
    meanprops=dict(marker="D", markerfacecolor=CORES["preto"], markersize=7),
    medianprops=dict(color=CORES["preto"], linewidth=2),
    flierprops=dict(marker="o", markerfacecolor=CORES["vermelho"], markersize=6),
    whiskerprops=dict(linewidth=1.2),
    capprops=dict(linewidth=1.2),
)

for patch, color in zip(bp["boxes"], cores_regiao):
    patch.set_facecolor(color)
    patch.set_alpha(0.6)
    patch.set_edgecolor(CORES["preto"])

ax5.axhline(y=META, color=CORES["vermelho"], linestyle="--", linewidth=1.8, alpha=0.8, zorder=4)

for i, reg in enumerate(ordem_regioes):
    media_reg = df_regiao[df_regiao["regiao"] == reg]["prop_ativa"].mean()
    ax5.text(
        i + 1, media_reg + 0.02, f"μ={media_reg:.2f}",
        ha="center", fontsize=8, fontweight="bold", color=CORES["preto"],
    )

# Insight narrativo
caixa_insight(ax5,
    "Nenhuma região brasileira atinge\na referência internacional sequer\nem sua melhor UF (em média).\nA desigualdade regional persiste.",
    x=0.98, y=0.97, fontsize=9,
)

ax5.set_title(
    "Nenhuma região brasileira atinge a referência internacional em média",
    fontsize=14, fontweight="bold", pad=15, loc="left",
)
ax5.set_ylabel("Bombeiros por 1.000 Habitantes", fontsize=11)
ax5.set_xlabel("Região", fontsize=11)
ax5.set_ylim(0, df_2024["prop_ativa"].max() * 1.15)

handles5 = [
    mlines.Line2D([], [], color=CORES["vermelho"], linestyle="--", linewidth=1.8, label=LABEL_META),
    mlines.Line2D([], [], marker="D", color=CORES["preto"], markersize=7, linestyle="None", label="Média da região"),
]
ax5.legend(handles=handles5, loc="upper right", fontsize=9, framealpha=0.9)

nota_rodape(fig5, "Fonte: SENASP/MJSP 2024 · IBGE Censo 2022 · Regiões conforme IBGE.", y=-0.03)

plt.tight_layout()
fig5.savefig(os.path.join(SAIDA, "v5_boxplot.png"), dpi=150, bbox_inches="tight", facecolor=fig5.get_facecolor())
plt.close(fig5)
print("  -> output/v5_boxplot.png")


# ══════════════════════════════════════════════════════════════════════════════
# 9. VISUALIZAÇÃO 6 — Conclusão: Antes vs. Depois (Top 10 UFs)
# ══════════════════════════════════════════════════════════════════════════════

print("Gerando Visualização 6: Comparativo antes/depois...")

top10 = df_2024.nlargest(10, "efetivo_ativa").copy()
top10["necessario"] = (META / 1000) * top10["populacao"]
top10["deficit_uf"] = top10["necessario"] - top10["efetivo_ativa"]
top10 = top10.sort_values("efetivo_ativa", ascending=True)

fig6, ax6 = plt.subplots(figsize=(14, 7))

y_pos6 = range(len(top10))

ax6.barh(
    [y - 0.18 for y in y_pos6], top10["efetivo_ativa"],
    height=0.35, color=CORES["vermelho"], label="Efetivo Atual (2024)",
    edgecolor="white", linewidth=0.5, alpha=0.85,
)
ax6.barh(
    [y + 0.18 for y in y_pos6], top10["necessario"],
    height=0.35, color=CORES["azul"], label="Necessário (meta NFPA)",
    edgecolor="white", linewidth=0.5, alpha=0.6,
)

for i, (_, row) in enumerate(top10.iterrows()):
    ax6.text(
        row["efetivo_ativa"] + 200, i - 0.18,
        fmt(row["efetivo_ativa"]),
        va="center", ha="left", fontsize=8, fontweight="bold", color=CORES["vermelho"],
    )
    ax6.text(
        row["necessario"] + 200, i + 0.18,
        f'{fmt(row["necessario"])}  (faltam {fmt(row["deficit_uf"])})',
        va="center", ha="left", fontsize=8, color=CORES["azul"],
    )

ax6.set_yticks(y_pos6)
ax6.set_yticklabels(top10["uf"], fontsize=10, fontweight="bold")
ax6.set_xlabel("Quantidade de Bombeiros Militares", fontsize=11)
ax6.set_title(
    "Mesmo os maiores Corpos de Bombeiros do país ficam aquém da meta",
    fontsize=14, fontweight="bold", pad=15, loc="left",
)
ax6.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
ax6.legend(loc="lower right", fontsize=10, framealpha=0.9)
ax6.grid(axis="y", visible=False)
ax6.grid(axis="x", alpha=0.2)

# Insight narrativo
caixa_insight(ax6,
    "O Rio de Janeiro, mesmo com o\nmaior efetivo do país (11.668),\nprecisaria de 25.983 — faltam\n14.315 Bombeiros só no RJ.",
    x=0.98, y=0.55, fontsize=9,
)

nota_rodape(fig6, "Fonte: SENASP/MJSP 2024 · IBGE Censo 2022 · Top 10 UFs por efetivo total na ativa.", y=-0.03)

plt.tight_layout()
fig6.savefig(os.path.join(SAIDA, "v6_antes_depois.png"), dpi=150, bbox_inches="tight", facecolor=fig6.get_facecolor())
plt.close(fig6)
print("  -> output/v6_antes_depois.png")


# ══════════════════════════════════════════════════════════════════════════════
# 10. DASHBOARD FINAL — Layout Único
# ══════════════════════════════════════════════════════════════════════════════

print("\nMontando dashboard final...")

fig = plt.figure(figsize=(24, 34))
fig.patch.set_facecolor(CORES["fundo"])

# Título geral
fig.text(0.5, 0.985,
    "Capacidade de Atendimento dos Corpos de Bombeiros no Brasil",
    fontsize=24, fontweight="bold", ha="center", color=CORES["preto"],
)
fig.text(0.5, 0.972,
    "O país possui recursos humanos nos Corpos de Bombeiros suficientes para atender à sua população?",
    fontsize=14, ha="center", color=CORES["cinza"], style="italic",
)

gs = GridSpec(4, 2, figure=fig, hspace=0.38, wspace=0.25,
              top=0.96, bottom=0.035, left=0.06, right=0.96)

# ── V1: Déficit ──
ax_v1 = fig.add_subplot(gs[0, 0])
ax_v1.bar(["Efetivo\nAtual", "Meta NFPA"], [efetivo_total, meta_nacional],
         color=[CORES["vermelho"], CORES["azul"]], width=0.45, edgecolor="white", linewidth=1.5)
for i, v in enumerate([efetivo_total, meta_nacional]):
    ax_v1.text(i, v + 4000, f"{fmt(v)}", ha="center", fontsize=14, fontweight="bold")
ax_v1.annotate(
    f"Só temos {fmt(efetivo_total)}.\nFaltam {fmt(deficit)}.",
    xy=(0.5, 0.5), xycoords="axes fraction",
    fontsize=12, fontweight="bold", color=CORES["vermelho"], ha="center",
    bbox=dict(boxstyle="round,pad=0.4", facecolor=CORES["amarelo"], alpha=0.85, edgecolor="none"),
)
ax_v1.set_title("O Brasil tem déficit de 242 mil Bombeiros", fontsize=13, fontweight="bold", loc="left")
ax_v1.set_ylabel("Bombeiros Militares")
ax_v1.set_ylim(0, meta_nacional * 1.3)
ax_v1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
ax_v1.grid(axis="x", visible=False)

# ── V2: Mapa ──
ax_mapa = fig.add_subplot(gs[0, 1])
gdf_mapa.plot(column="prop_ativa", ax=ax_mapa, cmap="YlOrRd", edgecolor="white",
              linewidth=0.5, vmin=0, vmax=gdf_mapa["prop_ativa"].max())
sm2 = plt.cm.ScalarMappable(cmap="YlOrRd", norm=plt.Normalize(0, gdf_mapa["prop_ativa"].max()))
sm2._A = []
cbar2 = fig.colorbar(sm2, ax=ax_mapa, fraction=0.03, pad=0.02, shrink=0.6)
cbar2.set_label("/1.000 hab.", fontsize=9)
cbar2.ax.axhline(y=META, color=CORES["preto"], linewidth=1.5)
for _, row in gdf_mapa.iterrows():
    c = row.geometry.centroid
    px, py = c.x, c.y
    if row["uf"] == "DF": px += 1.5
    pv = row["prop_ativa"]
    if pd.notna(pv):
        ct = CORES["verde"] if pv >= META else CORES["preto"]
        ax_mapa.text(px, py, f'{row["uf"]}\n{pv:.2f}', ha="center", va="center",
                    fontsize=5, fontweight="bold", color=ct,
                    bbox=dict(boxstyle="round,pad=0.1", facecolor="white", alpha=0.7, edgecolor="none"))
ax_mapa.set_title("A maioria dos estados está muito abaixo da meta", fontsize=13, fontweight="bold", loc="left")
ax_mapa.set_axis_off()

# ── V3: Lollipop ──
ax_lolli = fig.add_subplot(gs[1, 0])
df_lolli2 = df_2024.sort_values("prop_ativa", ascending=True)
y_l = range(len(df_lolli2))
c_l = [CORES["verde"] if v >= META else CORES["vermelho"] for v in df_lolli2["prop_ativa"]]
ax_lolli.hlines(y=y_l, xmin=0, xmax=df_lolli2["prop_ativa"], color=c_l, linewidth=1.2, alpha=0.7)
ax_lolli.scatter(df_lolli2["prop_ativa"], y_l, color=c_l, s=35, zorder=5, edgecolors="white", linewidth=0.5)
ax_lolli.axvline(x=META, color=CORES["azul"], linestyle="--", linewidth=1.5, zorder=4, alpha=0.8)
for i, (_, row) in enumerate(df_lolli2.iterrows()):
    ax_lolli.text(row["prop_ativa"] + 0.015, i, f'{row["prop_ativa"]:.2f}',
                 va="center", fontsize=6.5, fontweight="bold",
                 color=CORES["verde"] if row["prop_ativa"] >= META else CORES["preto"])
ax_lolli.set_yticks(y_l)
ax_lolli.set_yticklabels(df_lolli2["uf"], fontsize=7.5)
ax_lolli.set_xlabel("Bombeiros / 1.000 hab.")
ax_lolli.set_title("Quase nenhum estado atende à referência", fontsize=13, fontweight="bold", loc="left")
ax_lolli.set_xlim(0, df_lolli2["prop_ativa"].max() * 1.3)
ax_lolli.grid(axis="y", visible=False)

# ── V5: Box plot ──
ax_box = fig.add_subplot(gs[1, 1])
bp2 = ax_box.boxplot(
    dados_box, tick_labels=ordem_regioes, patch_artist=True, widths=0.5, showmeans=True,
    meanprops=dict(marker="D", markerfacecolor=CORES["preto"], markersize=6),
    medianprops=dict(color=CORES["preto"], linewidth=1.5),
    flierprops=dict(marker="o", markerfacecolor=CORES["vermelho"], markersize=5),
)
for patch, color in zip(bp2["boxes"], cores_regiao):
    patch.set_facecolor(color); patch.set_alpha(0.6); patch.set_edgecolor(CORES["preto"])
ax_box.axhline(y=META, color=CORES["vermelho"], linestyle="--", linewidth=1.5, alpha=0.8)
ax_box.set_title("Nenhuma região atinge a meta em média", fontsize=13, fontweight="bold", loc="left")
ax_box.set_ylabel("Bombeiros / 1.000 hab.")
ax_box.set_ylim(0, df_2024["prop_ativa"].max() * 1.15)

# ── V4: Evolução (largura total) ──
ax_evo = fig.add_subplot(gs[2, :])
ax_evo.fill_between(evolucao["ano"], evolucao["efetivo_ativa"], alpha=0.12, color=CORES["azul"])
ax_evo.plot(evolucao["ano"], evolucao["efetivo_ativa"], marker="o", color=CORES["azul"],
           linewidth=2.5, markersize=8, label="Efetivo Ativa (total)", zorder=5)
ax_evo.fill_between(evolucao["ano"], evolucao["efetivo_operacional"], alpha=0.12, color=CORES["laranja"])
ax_evo.plot(evolucao["ano"], evolucao["efetivo_operacional"], marker="s", color=CORES["laranja"],
           linewidth=2.5, markersize=8, label="Efetivo Operacional", zorder=5)
ax_evo.axhline(y=meta_nacional, color=CORES["vermelho"], linestyle="--", linewidth=1.5, alpha=0.7)
ax_evo.text(2024.15, meta_nacional, f"Meta NFPA: {fmt(meta_nacional)}", fontsize=9,
           color=CORES["vermelho"], va="center", fontweight="bold")
for _, row in evolucao.iterrows():
    ax_evo.annotate(fmt(row["efetivo_ativa"]),
                   xy=(row["ano"], row["efetivo_ativa"]),
                   xytext=(0, 12), textcoords="offset points",
                   ha="center", fontsize=9, fontweight="bold", color=CORES["azul"])
# Insight narrativo na evolução
ax_evo.text(0.5, 0.85,
    "Em 5 anos, o efetivo cresceu apenas 4% — a defasagem com a meta internacional continua enorme. A proporção de Bombeiros por 1.000 habitantes permanece praticamente estável.",
    transform=ax_evo.transAxes, fontsize=11, ha="center", color=CORES["preto"],
    bbox=dict(boxstyle="round,pad=0.5", facecolor=CORES["amarelo"], alpha=0.85, edgecolor="none"),
)
ax_evo.set_title("Efetivo cresceu apenas 4% em 5 anos — defasagem persiste",
                fontsize=14, fontweight="bold", loc="left")
ax_evo.set_ylabel("Quantidade de Bombeiros")
ax_evo.set_xticks(evolucao["ano"])
ax_evo.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
ax_evo.legend(fontsize=10, loc="upper left")
ax_evo.set_ylim(0, meta_nacional * 1.1)
ax_evo.grid(axis="x", visible=False)

# ── V6: Antes vs Depois (largura total) ──
ax_comp = fig.add_subplot(gs[3, :])
y_c = range(len(top10))
ax_comp.barh([y - 0.18 for y in y_c], top10["efetivo_ativa"], height=0.35,
            color=CORES["vermelho"], label="Efetivo Atual (2024)", edgecolor="white", alpha=0.85)
ax_comp.barh([y + 0.18 for y in y_c], top10["necessario"], height=0.35,
            color=CORES["azul"], label="Necessário (meta NFPA)", edgecolor="white", alpha=0.6)
for i, (_, row) in enumerate(top10.iterrows()):
    ax_comp.text(row["efetivo_ativa"] + 200, i - 0.18, fmt(row["efetivo_ativa"]),
                va="center", fontsize=8, fontweight="bold", color=CORES["vermelho"])
    ax_comp.text(row["necessario"] + 200, i + 0.18,
                f'{fmt(row["necessario"])}  (faltam {fmt(row["deficit_uf"])})',
                va="center", fontsize=8, color=CORES["azul"])
ax_comp.set_yticks(y_c)
ax_comp.set_yticklabels(top10["uf"], fontsize=10, fontweight="bold")
ax_comp.set_xlabel("Quantidade de Bombeiros Militares")
ax_comp.set_title("Mesmo os maiores CBM ficam aquém da meta", fontsize=14, fontweight="bold", loc="left")
ax_comp.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
ax_comp.legend(loc="lower right", fontsize=10)
ax_comp.grid(axis="y", visible=False)

# ── Rodapé geral ──
fig.text(0.5, 0.008,
    "Fontes: SENASP/MJSP (ano base 2024) · IBGE Censo 2022 · NFPA Fire Department Profile 2020 (1,54/1.000 hab.) · Dados multianuais SENASP 2020–2024",
    fontsize=9, ha="center", color=CORES["cinza"], style="italic",
)

fig.savefig(os.path.join(SAIDA, "dashboard_completo.png"), dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close(fig)
print("  -> output/dashboard_completo.png")


# ══════════════════════════════════════════════════════════════════════════════
# 11. RESUMO
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "═" * 70)
print("  RESUMO DO DASHBOARD")
print("═" * 70)
print(f"  População Brasil (Censo 2022):     {fmt(pop_total)}")
print(f"  Efetivo total ativa (2024):         {fmt(efetivo_total)}")
print(f"  Referência NFPA (1,54/1.000):       {fmt(meta_nacional)}")
print(f"  Déficit nacional:                   {fmt(deficit)}")
print(f"  Proporção atual:                    {prop_nacional:.2f} /1.000 hab.")
print(f"  Crescimento 2020–2024:             +{((efetivo_total / 66117) - 1) * 100:.1f}%")
print("─" * 70)
print(f"  UFs acima da meta NFPA:             {list(acima_meta['uf'])}")
print(f"  Estado mais abaixo:                 {abaixo_meta.iloc[0]['uf']} ({abaixo_meta.iloc[0]['prop_ativa']:.2f})")
print(f"  Média nacional:                     {df_2024['prop_ativa'].mean():.2f}")
print(f"  Mediana nacional:                   {df_2024['prop_ativa'].median():.2f}")
print("═" * 70)
print("\nArquivos gerados em output/:")
for f in ["v1_deficit.png", "v2_mapa.png", "v3_lollipop.png", "v4_evolucao.png",
          "v5_boxplot.png", "v6_antes_depois.png", "dashboard_completo.png"]:
    print(f"  {f}")
print("\nConcluído!")
