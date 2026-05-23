from openpyxl import load_workbook
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import to_rgba

# LOAD
file_path = ""

wb = load_workbook(file_path, data_only=True)
ws = wb["Sheet1"]

data = ws.values
columns = next(data)

df = pd.DataFrame(data, columns=columns)
df.columns = [str(c).strip() for c in df.columns]

df["Date"] = pd.to_datetime(df["Date"])
df["Month"] = df["Date"].dt.strftime("%b %Y")

params = ["Temp", "Salinity", "Chl-a", "DO", "pH"]

months = sorted(
    df["Month"].unique(),
    key=lambda x: pd.to_datetime(x, format="%b %Y")
)

# CLASSIFICATION
def classify_note(note):

    if pd.isna(note):
        return "raw"

    note = str(note).lower()

    if "forward-fill ph only" in note:
        return "forward_fill"

    if "do exceeded 8.0" in note:
        return "flag4"

    if (
        "interpolation" in note
        or "adjust" in note
        or "replaced" in note
    ):
        return "interpolated"

    if "late-entry" in note:
        return "late_entry"

    return "raw"

base_colors = {
    "raw": "#d4af37",
    "interpolated": "#2e8b57",
    "forward_fill": "#ff8c00",
    "flag4": "#7b2cbf",
    "late_entry": "#1f78b4"
}

legend_labels = {
    "raw": "Raw good",
    "interpolated": "Interpolated",
    "forward_fill": "Forward-fill",
    "flag4": "Flag 4 corrected",
    "late_entry": "Late-entry"
}

# DOT POSITIONS
y_positions = [0, 0.42, 0.84, 1.26, 1.68]

scatter_rows = []

for y_idx, param in enumerate(params):

    for x_idx, month in enumerate(months):

        sub = df[df["Month"] == month]

        if len(sub) == 0:
            continue

        categories = sub["Note"].apply(classify_note)

        counts = categories.value_counts()

        total = len(sub)

        for cat, count in counts.items():

            intensity = count / total

            scatter_rows.append({
                "x": x_idx,
                "y": y_positions[y_idx],
                "category": cat,
                "intensity": intensity
            })

scatter_df = pd.DataFrame(scatter_rows)

# QC
qc_counts = df["QC Flag"].value_counts().sort_index()

qc_labels = {
    1: "Flag 1",
    5: "Flag 5"
}

labels = [qc_labels.get(i, f"Flag {i}") for i in qc_counts.index]
counts = qc_counts.values

# FIGURE
plt.rcParams["font.family"] = "DejaVu Sans"

fig = plt.figure(figsize=(33, 5.9), facecolor="white")

gs = fig.add_gridspec(
    1, 2,
    width_ratios=[5.8, 1],
    wspace=0.10
)

# FIGURE A
ax1 = fig.add_subplot(gs[0])

ax1.set_facecolor("#f8f8f8")

for cat, color in base_colors.items():

    sub = scatter_df[scatter_df["category"] == cat]

    if len(sub) == 0:
        continue

    colors = []

    for intensity in sub["intensity"]:

        rgba = list(to_rgba(color))
        rgba[3] = 0.35 + (0.65 * intensity)
        colors.append(tuple(rgba))

    ax1.scatter(
        sub["x"],
        sub["y"],
        s=240,
        c=colors,
        edgecolors="black",
        linewidths=0.7
    )

same_font = 17

ax1.set_yticks(y_positions)

ax1.set_yticklabels(
    params,
    fontsize=same_font,
    rotation=90,
    va='center'
)

# =========================
# FIX OVERLAP X LABELS
# =========================
tick_idx = list(np.arange(0, len(months), 4))

if (len(months) - 1) not in tick_idx:
    tick_idx.append(len(months) - 1)

tick_idx = sorted(tick_idx)

tick_labels = []

for i in tick_idx:

    dt = pd.to_datetime(months[i], format="%b %Y")

    month_txt = dt.strftime("%b")
    year_txt = dt.strftime("%Y")

    tick_labels.append(f"{month_txt}\n{year_txt}")

ax1.set_xticks(tick_idx)

ax1.set_xticklabels(
    tick_labels,
    fontsize=same_font,
    rotation=0,
    ha='center'
)

ax1.tick_params(
    axis='x',
    pad=12
)

# ruang kanan
ax1.set_xlim(-0.5, len(months) + 1.0)

ax1.set_ylim(-0.08, 1.80)

ax1.grid(alpha=0.2)

ax1.set_title(
    "(a) Distribution of raw and QA/QC-adjusted data",
    fontsize=27,
    weight="bold"
)

# LEGEND
legend_elements = []

for key in ["raw", "interpolated", "forward_fill", "flag4", "late_entry"]:

    legend_elements.append(
        Line2D(
            [0],
            [0],
            marker='o',
            color='w',
            label=legend_labels[key],
            markerfacecolor=base_colors[key],
            markeredgecolor='black',
            markersize=14
        )
    )

ax1.legend(
    handles=legend_elements,
    loc='upper center',
    bbox_to_anchor=(0.5, -0.14),
    ncol=5,
    frameon=False,
    fontsize=15,
    handletextpad=0.5,
    columnspacing=1.5
)

# FIGURE B
ax2 = fig.add_subplot(gs[1])

bars = ax2.bar(
    range(len(counts)),
    counts,
    color=["#2ca25f", "#fdae6b"]
)

ax2.set_xticks(range(len(labels)))

ax2.set_xticklabels(
    labels,
    fontsize=19
)

ax2.yaxis.tick_right()
ax2.yaxis.set_label_position("right")

ax2.set_ylabel(
    "Number of records",
    fontsize=18
)

ax2.tick_params(axis='y', labelsize=16)

ax2.set_ylim(0, max(counts) * 1.18)

ax2.set_title(
    "(b) QA/QC summary",
    fontsize=27,
    weight="bold"
)

for b in bars:

    h = b.get_height()

    ax2.text(
        b.get_x() + b.get_width()/2,
        h + max(counts)*0.02,
        f"{int(h)}",
        ha="center",
        va="bottom",
        fontsize=20,
        weight="bold"
    )

ax2.grid(axis="y", alpha=0.3)

output_path = ""

plt.savefig(
    output_path,
    dpi=600,
    bbox_inches="tight",
    facecolor="white"
)

print(output_path)
