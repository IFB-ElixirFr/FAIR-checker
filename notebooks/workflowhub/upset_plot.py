"""
Generates an UpSet plot from a FAIR-Checker evaluation CSV.
Each FAIR metric is treated as a boolean: score > 0 means "passed".

Usage:
    python upset_plot.py [--input wfhub-fc_evals-2026.csv] [--output upset_wfhub_2026]
"""

import argparse
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches
from upsetplot import UpSet, from_indicators

parser = argparse.ArgumentParser()
parser.add_argument("--input", default="wfhub-fc_evals-2026.csv")
parser.add_argument("--output", default="upset_wfhub_2026")
args = parser.parse_args()

mpl.rcParams["font.family"] = "sans-serif"
mpl.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans"]
mpl.rcParams["font.size"] = 9

METRIC_COLS = [
    "F1A",
    "F1B",
    "F2A",
    "F2B",
    "A1.1",
    "A1.2",
    "I1",
    "I2",
    "I3",
    "R1.1",
    "R1.2",
    "R1.3",
]

# Okabe-Ito colorblind-safe colors per FAIR dimension
DIM_COLORS = {
    "F": "#0072B2",
    "A": "#009E73",
    "I": "#E69F00",
    "R": "#D55E00",
}


def dim_color(metric):
    return DIM_COLORS.get(metric[0], "#888888")


df = pd.read_csv(args.input, index_col=0)

binary_df = df[METRIC_COLS].gt(0)
upset_data = from_indicators(METRIC_COLS, data=binary_df)

fig = plt.figure(figsize=(16, 6))

upset = UpSet(
    upset_data,
    subset_size="count",
    show_counts=False,  # disabled — upsetplot 0.9 bug with newer mpl
    sort_by="cardinality",
    sort_categories_by=None,  # preserve F→A→I→R order
    totals_plot_elements=3,
    facecolor="black",
)

axes_dict = upset.plot(fig)

# Recolor matrix dots per-dot: active (alpha≈1) → black, inactive (alpha≈0.18) → light grey
import numpy as np

matrix_ax = axes_dict["matrix"]
for coll in matrix_ax.collections:
    fc = coll.get_facecolor()
    if fc is None or len(fc) == 0:
        continue
    fc = np.array(fc)
    new_fc = np.where(
        (fc[:, 3:4] > 0.5),  # active dot mask (alpha > 0.5)
        np.array([[0, 0, 0, 1]]),  # black
        np.array([[0.8, 0.8, 0.8, 1]]),  # light grey
    )
    coll.set_facecolor(new_fc)
    coll.set_edgecolor(new_fc)

# Annotate intersection bars with counts
intersect_ax = axes_dict["intersections"]
ymax = intersect_ax.get_ylim()[1]
for bar in intersect_ax.patches:
    h = bar.get_height()
    if h > 0:
        intersect_ax.text(
            bar.get_x() + bar.get_width() / 2,
            h + ymax * 0.01,
            str(int(h)),
            ha="center",
            va="bottom",
            fontsize=7,
        )

# Color totals (set membership) bars by FAIR dimension.
# upsetplot draws one horizontal bar per category, bottom-to-top.
totals_ax = axes_dict["totals"]
patches = totals_ax.patches
# categories are rendered bottom-to-top in the matrix but the totals
# bars are ordered to match the y-tick positions (top-to-bottom index).
ytick_labels = [t.get_text() for t in totals_ax.get_yticklabels()]
if ytick_labels and len(ytick_labels) == len(patches):
    for bar, label in zip(patches, ytick_labels):
        bar.set_facecolor(dim_color(label))
else:
    # fallback: map by position assuming METRIC_COLS order bottom-to-top
    for i, bar in enumerate(patches):
        bar.set_facecolor(dim_color(METRIC_COLS[i % len(METRIC_COLS)]))

# Legend
handles = [mpatches.Patch(color=c, label=f"{d} metrics") for d, c in DIM_COLORS.items()]
intersect_ax.legend(
    handles=handles,
    loc="upper left",
    frameon=False,
    fontsize=8,
    title="FAIR dimension",
    title_fontsize=8,
    bbox_to_anchor=(1.02, 1),
    borderaxespad=0,
)

intersect_ax.set_title(
    "WorkflowHub FAIR metric pass/fail combinations — 2026",
    fontsize=11,
    fontweight="bold",
    pad=10,
)

plt.savefig(f"{args.output}.pdf", bbox_inches="tight", dpi=300)
plt.savefig(f"{args.output}.png", bbox_inches="tight", dpi=300)
print(f"Saved: {args.output}.pdf and {args.output}.png")
