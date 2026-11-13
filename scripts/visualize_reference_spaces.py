"""
Visualize all 6 reference spaces
------------
Reads 5 CSV/TSV data files (columns: Superclass, TSNE1, TSNE2) and produces a
3×2 figure with seaborn scatter panels (one per file) plus a legend panel.
"""
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter

# ── 1. Configure inputs ────────────────────────────────────────────────────────

DATASETS = [
    "ZeroPM",
    "COCONUT",
    "DrugBank",
    "PlastChem",
    "AgroTrak",
    "PFAS",
]

FILE_PATHS = [
    "../data/ZeroPM/output_zeropm_partial.csv",
    "../data/COCONUT/output_coconut_partial.csv",
    "../data/DrugBank/output_drugbank_5.1.13_partial.csv",
    "../data/PlastChem/output_plastchem_db_v1.01_partial.csv",
    "../data/AgroTrak/output_agrotrak_zhang_2025_partial.csv",
    "../data/PFAS/output_pfas_nist_partial.csv",
]

TOP_N = 11  # number of top superclasses to keep
DIVERSE_LABEL = "NaN / Diverse"
OUTPUT_FILE = "../output/figure_reference_spaces.png"

# ── 2. Read data ───────────────────────────────────────────────────────────────

dfs = []
datasize_table = []
for path in FILE_PATHS:
    sep = "\t" if path.endswith((".tsv", ".txt")) else ","
    df = pd.read_csv(path, sep=sep)
    assert {"Superclass", "TSNE1", "TSNE2"}.issubset(df.columns), (
        f"{path} is missing required columns."
    )
    datasize_table.append(len(df))
    dfs.append(df)

# ── 3. Determine global top-N superclasses ─────────────────────────────────────

all_superclasses = pd.concat([df["Superclass"] for df in dfs], ignore_index=True)
all_superclasses.dropna(inplace=True) # do not include
counts = Counter(all_superclasses)
top_n = [sc for sc, _ in counts.most_common(TOP_N)]

# ── 4. Build a consistent, global colour palette ───────────────────────────────

# "Alphabet" palette has 26 colors; we need TOP_N + 1 (for Diverse)
# colors = sns.color_palette('colorblind', n_colors=TOP_N + 1)
colors = ['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99']
palette = {sc: colors[i] for i, sc in enumerate(top_n)}
palette[DIVERSE_LABEL] = "lightgrey"  # last colour for Diverse

# Ordered list for the legend (top classes first, Diverse last)
hue_order = top_n + [DIVERSE_LABEL]


# ── 5. Recode minor superclasses ───────────────────────────────────────────────

def recode(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Superclass_plot"] = df["Superclass"].where(
        df["Superclass"].isin(top_n), other=DIVERSE_LABEL
    )
    df['Superclass_plot'] = df['Superclass_plot'].replace(np.nan, DIVERSE_LABEL)
    return df


dfs = [recode(df) for df in dfs]

# ── 6. Figure layout ───────────────────────────────────────────────────────────

fig, axes = plt.subplots(
    3, 2,
    figsize=(10, 13),
)
fig.subplots_adjust(
    hspace=0.30
)

# ── 7. Draw scatter panels ─────────────────────────────────────────────────────

dot_size = 3
dot_size_table = [
    3,      # "ZeroPM",
    3,      # "COCONUT",
    6,      # "DrugBank",
    6,      # "PlastChem",
    10,     # "AgroTrak",
    10,     # "PFAS",
]
alpha = 0.6
linewidth = 0

# Plot Diverse first so named classes sit on top
plot_order = [DIVERSE_LABEL] + top_n

for ax, df, title, dot_size, datasize in zip(axes.flat, dfs, DATASETS, dot_size_table, datasize_table):
    sns.scatterplot(
        data=df,
        x="TSNE1",
        y="TSNE2",
        hue="Superclass_plot",
        hue_order=plot_order,
        palette=palette,
        s=dot_size,
        alpha=alpha,
        linewidth=linewidth,
        ax=ax,
        legend=False,  # unified legend drawn separately
        rasterized=True,
    )

    ax.set_title(f'{title} (n={datasize})', fontsize=10, fontweight="bold")
    ax.set_xlabel("t-SNE 1", fontsize=8)
    ax.set_ylabel("t-SNE 2", fontsize=8)
    ax.tick_params(labelsize=7)
    sns.despine(ax=ax)

# ── 8. Horizontal legend below the figure ─────────────────────────────────────

handles = [
    mpatches.Patch(color=palette[sc], label=sc)
    for sc in hue_order
]

fig.legend(
    handles=handles,
    title="Superclass",
    title_fontsize=9,
    fontsize=8,
    loc="lower center",
    bbox_to_anchor=(0.5, 0.0),  # centred, just below the subplots area
    frameon=False,
    ncol=4,  # spread across 6 columns; adjust if needed
    # handlelength=1.2,
    # handleheight=1.0,
    # columnspacing=1.0,
    # handletextpad=0.5,
)

# ── 9. Save ────────────────────────────────────────────────────────────────────

fig.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
print(f"Saved → {OUTPUT_FILE}")
