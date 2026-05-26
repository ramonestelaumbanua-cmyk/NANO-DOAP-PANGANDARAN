import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import MultipleLocator

# ============================================================
# KONFIGURASI PATH
# ============================================================
FILE_PATH        = ""
FILE_PATH_TRANSP = ""
OUTPUT_PATH      = ""
SHEET_NAME       = ""
# ============================================================

# ── Load data utama ─────────────────────────────────────────
df = pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME)
df.columns = df.columns.str.strip()

col_date  = "Date"
col_depth = "Depth (m)"
col_temp  = "Temp (deg C)"
col_sal   = "Salinity (PSU)"
col_chl   = "Chl-a (mg m-3)"
col_do    = "DO (mg L-1)"
col_ph    = "pH (NBS)"

df[col_date]  = pd.to_datetime(df[col_date])
df[col_depth] = pd.to_numeric(df[col_depth], errors="coerce")
for col in [col_temp, col_sal, col_chl, col_do, col_ph]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["YearMonth"] = df[col_date].dt.to_period("M")
df = df.sort_values([col_date, col_depth]).reset_index(drop=True)

# ── Load data transparansi ───────────────────────────────────
df_tr = pd.read_excel(FILE_PATH_TRANSP)
df_tr.columns = df_tr.columns.str.strip()
col_tr_date = next(c for c in df_tr.columns if "date" in c.lower())
col_tr_val  = next(c for c in df_tr.columns if "transparency" in c.lower())
df_tr[col_tr_date] = pd.to_datetime(df_tr[col_tr_date])
df_tr[col_tr_val]  = pd.to_numeric(df_tr[col_tr_val], errors="coerce")
df_tr["YearMonth"] = df_tr[col_tr_date].dt.to_period("M")
df_tr = df_tr.sort_values(col_tr_date).reset_index(drop=True)

# ── Parameter config ─────────────────────────────────────────
params = [
    (col_temp, "Temp (°C)",       "a"),
    (col_sal,  "Sal (PSU)",       "b"),
    (col_ph,   "pH (NBS)",        "c"),
    (col_chl,  "Chl-a (mg m⁻³)", "d"),
    (col_do,   "DO (mg L⁻¹)",    "e"),
]

depths       = [0, 10, 20]
depth_colors = {0: "#2ca02c", 10: "#d62728", 20: "#1f77b4"}
depth_labels = {0: "0", 10: "10", 20: "20"}

# ── Global month index ───────────────────────────────────────
all_periods = pd.period_range(
    start=df["YearMonth"].min(),
    end=df["YearMonth"].max(),
    freq="M"
)
period_to_x = {p: i for i, p in enumerate(all_periods)}
n_months    = len(all_periods)

# ══════════════════════════════════════════════════════════════
# FONT & UKURAN
# ══════════════════════════════════════════════════════════════
FS_TICK   = 20
FS_YEAR   = 20
FS_LABEL  = 20
FS_LEGEND = 20
FS_LEGTIT = 20
FS_PANEL  = 20

plt.rcParams.update({
    "font.size":             FS_TICK,
    "axes.labelsize":        FS_LABEL,
    "xtick.labelsize":       FS_TICK,
    "ytick.labelsize":       FS_TICK,
    "legend.fontsize":       FS_LEGEND,
    "legend.title_fontsize": FS_LEGTIT,
    "axes.linewidth":        1.2,
    "lines.linewidth":       1.5,
})

BOX_W   = 0.22
OFFSETS = {0: -BOX_W, 10: 0, 20: BOX_W}

n_panels = len(params) + 1
fig, axes = plt.subplots(
    nrows=n_panels, ncols=1,
    figsize=(25,5  * n_panels),   # ← lebar 25, tinggi 4 inch per panel
    sharex=True
)

# ── Fungsi utama boxplot ─────────────────────────────────────
def draw_boxplot_panel(ax, data_col, df_src, depth_col, ym_col,
                       depths, depth_colors, period_to_x,
                       panel_label, ylabel, is_transparency=False):

    ax.set_facecolor("white")
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_linewidth(1.2)
    ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.45, zorder=0)
    ax.tick_params(axis="y", labelsize=FS_TICK, length=5, width=1.2)

    loop_depths = [None] if is_transparency else depths

    for d in loop_depths:
        if is_transparency:
            df_sub = df_src.copy()
            offset = 0
            color  = "#7b2d8b"
        else:
            df_sub = df_src[df_src[depth_col] == d].copy()
            offset = OFFSETS[d]
            color  = depth_colors[d]

        if df_sub.empty:
            continue

        grouped = df_sub.groupby(ym_col)[data_col].apply(list)

        for period, vals in grouped.items():
            vals = [v for v in vals if not np.isnan(v)]
            if len(vals) == 0 or period not in period_to_x:
                continue

            xc   = period_to_x[period] + offset
            vals = np.array(vals)

            q1, med, q3 = np.percentile(vals, [25, 50, 75])
            iqr      = q3 - q1
            lo_vals  = vals[vals >= q1 - 1.5 * iqr]
            hi_vals  = vals[vals <= q3 + 1.5 * iqr]
            w_lo     = float(lo_vals.min()) if len(lo_vals) > 0 else float(q1)
            w_hi     = float(hi_vals.max()) if len(hi_vals) > 0 else float(q3)
            outliers = vals[(vals < w_lo) | (vals > w_hi)]

            # Box
            rect = mpatches.FancyBboxPatch(
                (xc - BOX_W / 2, q1), BOX_W, q3 - q1,
                boxstyle="square,pad=0",
                linewidth=1.0, edgecolor="black",
                facecolor=color, alpha=0.85, zorder=3
            )
            ax.add_patch(rect)

            # Median
            ax.plot([xc - BOX_W / 2, xc + BOX_W / 2], [med, med],
                    color="black", linewidth=1.8, zorder=4)

            # Whiskers
            ax.plot([xc, xc], [q1, w_lo], color="black", linewidth=1.0, zorder=3)
            ax.plot([xc, xc], [q3, w_hi], color="black", linewidth=1.0, zorder=3)

            # Caps
            cw = BOX_W * 0.35
            ax.plot([xc - cw, xc + cw], [w_lo, w_lo], color="black", linewidth=1.0, zorder=3)
            ax.plot([xc - cw, xc + cw], [w_hi, w_hi], color="black", linewidth=1.0, zorder=3)

            # Outliers
            if len(outliers) > 0:
                ax.scatter([xc] * len(outliers), outliers,
                           marker="+", color="#1f77b4",
                           s=80, linewidths=1.8, zorder=5)

    # Panel label pojok kanan bawah
    ax.text(0.995, 0.04, panel_label,
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=FS_PANEL, fontstyle="italic", fontweight="bold")

    ax.set_ylabel(ylabel, fontsize=FS_LABEL, labelpad=8)


# ── Render semua panel ───────────────────────────────────────
for ax, (col, ylabel, label) in zip(axes[:len(params)], params):
    draw_boxplot_panel(ax, col, df, col_depth, "YearMonth",
                       depths, depth_colors, period_to_x,
                       label, ylabel, is_transparency=False)

draw_boxplot_panel(axes[-1], col_tr_val, df_tr,
                   None, "YearMonth",
                   None, None, period_to_x,
                   "f", "Transparency (m)", is_transparency=True)

# ── Sumbu X: label bulan + tahun ─────────────────────────────
ax_last = axes[-1]
ax_last.set_xticks(range(n_months))
ax_last.set_xticklabels(
    [p.strftime("%b") for p in all_periods],
    fontsize=FS_TICK, rotation=0, ha="center"
)
ax_last.set_xlim(-0.7, n_months - 0.3)
ax_last.tick_params(axis="x", length=5, width=1.2)

# Label tahun di bawah sumbu X
years_drawn = set()
for i, p in enumerate(all_periods):
    yr = p.strftime("%Y")
    if yr not in years_drawn:
        ax_last.annotate(
            yr,
            xy=(i, 0), xycoords=("data", "axes fraction"),
            xytext=(0, -38), textcoords="offset points",
            ha="center", va="top",
            fontsize=FS_YEAR, fontweight="bold",
            annotation_clip=False
        )
        years_drawn.add(yr)

# Sembunyikan x-tick di panel atas
for ax in axes[:-1]:
    ax.set_xlim(-0.7, n_months - 0.3)
    ax.tick_params(axis="x", which="both", bottom=False, labelbottom=False)

# Garis pemisah per tahun
jan_xs = [period_to_x[p] for p in all_periods if p.month == 1]
for ax in axes:
    for x in jan_xs:
        ax.axvline(x - 0.5, color="grey", linewidth=0.7,
                   linestyle="--", alpha=0.45, zorder=1)

# ── Legend gabungan di bawah figure ──────────────────────────
legend_patches = [
    mpatches.Patch(color=depth_colors[0],  label="0 m"),
    mpatches.Patch(color=depth_colors[10], label="10 m"),
    mpatches.Patch(color=depth_colors[20], label="20 m"),
    mpatches.Patch(color="#7b2d8b",        label="Transparency"),
]

fig.legend(
    handles=legend_patches,
    title="Depth (m)",
    title_fontsize=FS_LEGTIT,
    loc="lower center",
    bbox_to_anchor=(0.5, -0.01),
    ncol=4,
    frameon=True,
    framealpha=0.85,
    fontsize=FS_LEGEND,
)

fig.subplots_adjust(bottom=0.06)   # ruang untuk legend di bawah
plt.tight_layout(h_pad=1.0)
plt.savefig(OUTPUT_PATH, dpi=200, bbox_inches="tight")
print(f"\n✅ Grafik disimpan ke:\n{OUTPUT_PATH}")
plt.show()

#%%%
#%%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

# ============================================================
# KONFIGURASI PATH
# ============================================================
FILE_PATH        = ""
FILE_PATH_TRANSP = ""
OUTPUT_DIR       = ""
SHEET_NAME       = ""
# ============================================================

# ── Load data utama ─────────────────────────────────────────
print("Loading data utama...")
df = pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME)
df.columns = df.columns.str.strip()

col_date  = "Date"
col_depth = "Depth (m)"
col_temp  = "Temp (deg C)"
col_sal   = "Salinity (PSU)"
col_chl   = "Chl-a (mg m-3)"
col_do    = "DO (mg L-1)"
col_ph    = "pH (NBS)"

df[col_date]  = pd.to_datetime(df[col_date])
df[col_depth] = pd.to_numeric(df[col_depth], errors="coerce")
for col in [col_temp, col_sal, col_chl, col_do, col_ph]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["YearMonth"] = df[col_date].dt.to_period("M")
df = df.sort_values([col_date, col_depth]).reset_index(drop=True)

# ── Load data transparansi ───────────────────────────────────
print("Loading data transparansi...")
df_tr = pd.read_excel(FILE_PATH_TRANSP)
df_tr.columns = df_tr.columns.str.strip()
col_tr_date = next(c for c in df_tr.columns if "date" in c.lower())
col_tr_val  = next(c for c in df_tr.columns if "transparency" in c.lower())
df_tr[col_tr_date] = pd.to_datetime(df_tr[col_tr_date])
df_tr[col_tr_val]  = pd.to_numeric(df_tr[col_tr_val], errors="coerce")
df_tr["YearMonth"] = df_tr[col_tr_date].dt.to_period("M")
df_tr = df_tr.sort_values(col_tr_date).reset_index(drop=True)

# ── DEBUG ────────────────────────────────────────────────────
print("=== DEBUG INFO ===")
print(f"  Jumlah baris df utama  : {len(df)}")
print(f"  Jumlah baris df transp : {len(df_tr)}")
print(f"  Periode df utama       : {df['YearMonth'].min()} s/d {df['YearMonth'].max()}")
print(f"  Kolom df utama         : {list(df.columns)}")
print(f"  Kolom df transp        : {list(df_tr.columns)}")
print("==================")

# ── Parameter config ─────────────────────────────────────────
# (kolom_data, ylabel, label_panel, nama_file, is_transparency)
params = [
    (col_temp,  "Temp (°C)",        "a", "Temperature",  False),
    (col_sal,   "Sal (PSU)",        "b", "Salinity",      False),
    (col_ph,    "pH (NBS)",         "c", "pH",            False),
    (col_chl,   "Chl-a (mg m⁻³)",  "d", "Chlorophyll-a", False),
    (col_do,    "DO (mg L⁻¹)",     "e", "DO",            False),
    (col_tr_val,"Transparency (m)", "f", "Transparency",  True),
]

depths       = [0, 10, 20]
depth_colors = {0: "#2ca02c", 10: "#d62728", 20: "#1f77b4"}
depth_labels = {0: "0", 10: "10", 20: "20"}

# ── Global period index (semua bulan dari awal sampai akhir) ──
all_periods = pd.period_range(
    start=df["YearMonth"].min(),
    end=df["YearMonth"].max(),
    freq="M"
)
period_to_x = {p: i for i, p in enumerate(all_periods)}
n_months    = len(all_periods)

print(f"  Total bulan di all_periods: {n_months}")
print(f"  Contoh period_to_x (5 pertama): {dict(list(period_to_x.items())[:5])}")

# ══════════════════════════════════════════════════════════════
# FONT & UKURAN
# ══════════════════════════════════════════════════════════════
FS_TICK   = 20
FS_LABEL  = 20
FS_LEGEND = 20
FS_LEGTIT = 20
FS_PANEL  = 20
FS_TITLE  = 25
FS_YEAR   = 20

plt.rcParams.update({
    "font.size":             FS_TICK,
    "axes.labelsize":        FS_LABEL,
    "xtick.labelsize":       FS_TICK,
    "ytick.labelsize":       FS_TICK,
    "legend.fontsize":       FS_LEGEND,
    "legend.title_fontsize": FS_LEGTIT,
    "axes.linewidth":        1.2,
    "lines.linewidth":       1.5,
})

BOX_W   = 0.22
OFFSETS = {0: -BOX_W, 10: 0, 20: BOX_W}


# ══════════════════════════════════════════════════════════════
# FUNGSI PEMBANTU
# ══════════════════════════════════════════════════════════════
def add_year_separators(ax, all_periods, period_to_x, FS_YEAR):
    years_seen = {}
    for p in all_periods:
        yr = p.year
        x  = period_to_x[p]
        if yr not in years_seen:
            years_seen[yr] = x
            if x > 0:
                ax.axvline(x - 0.5, color="gray", linewidth=0.9,
                           linestyle="--", alpha=0.6, zorder=1)

    for yr, x_start in years_seen.items():
        months_this_year = [p for p in all_periods if p.year == yr]
        x_mid = period_to_x[months_this_year[0]] + (len(months_this_year) - 1) / 2
        ax.text(x_mid, 1.012, str(yr),
                transform=ax.get_xaxis_transform(),
                ha="center", va="bottom",
                fontsize=FS_YEAR, fontweight="bold", color="dimgray")


def draw_single_parameter(ax, data_col, df_src, depth_col, ym_col,
                           depths, depth_colors, period_to_x,
                           panel_label, ylabel, is_transparency=False):
    ax.set_facecolor("white")
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_linewidth(1.2)
    ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.45, zorder=0)
    ax.tick_params(axis="y", labelsize=FS_TICK, length=5, width=1.2)

    loop_depths = [None] if is_transparency else depths

    for d in loop_depths:
        if is_transparency:
            df_sub = df_src.copy()
            offset = 0
            color  = "#7b2d8b"
        else:
            df_sub = df_src[df_src[depth_col] == d].copy()
            offset = OFFSETS[d]
            color  = depth_colors[d]

        if df_sub.empty:
            continue

        grouped = df_sub.groupby(ym_col)[data_col].apply(list)

        for period, vals in grouped.items():
            vals = [v for v in vals if not np.isnan(v)]
            if len(vals) == 0 or period not in period_to_x:
                continue

            xc   = period_to_x[period] + offset
            vals = np.array(vals)

            q1, med, q3 = np.percentile(vals, [25, 50, 75])
            iqr      = q3 - q1
            lo_vals  = vals[vals >= q1 - 1.5 * iqr]
            hi_vals  = vals[vals <= q3 + 1.5 * iqr]
            w_lo     = float(lo_vals.min()) if len(lo_vals) > 0 else float(q1)
            w_hi     = float(hi_vals.max()) if len(hi_vals) > 0 else float(q3)
            outliers = vals[(vals < w_lo) | (vals > w_hi)]

            # Box
            rect = mpatches.FancyBboxPatch(
                (xc - BOX_W / 2, q1), BOX_W, q3 - q1,
                boxstyle="square,pad=0",
                linewidth=1.0, edgecolor="black",
                facecolor=color, alpha=0.85, zorder=3
            )
            ax.add_patch(rect)

            # Median line
            ax.plot([xc - BOX_W / 2, xc + BOX_W / 2], [med, med],
                    color="black", linewidth=1.8, zorder=4)

            # Whiskers
            ax.plot([xc, xc], [q1, w_lo], color="black", linewidth=1.0, zorder=3)
            ax.plot([xc, xc], [q3, w_hi], color="black", linewidth=1.0, zorder=3)

            # Caps
            cw = BOX_W * 0.35
            ax.plot([xc - cw, xc + cw], [w_lo, w_lo], color="black", linewidth=1.0, zorder=3)
            ax.plot([xc - cw, xc + cw], [w_hi, w_hi], color="black", linewidth=1.0, zorder=3)

            # Outliers
            if len(outliers) > 0:
                ax.scatter([xc] * len(outliers), outliers,
                           marker="+", color="#555555",
                           s=80, linewidths=1.8, zorder=5)

    # Panel label pojok kanan bawah
    ax.text(0.995, 0.04, panel_label,
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=FS_PANEL, fontstyle="italic", fontweight="bold")

    ax.set_ylabel(ylabel, fontsize=FS_LABEL, labelpad=8)

    # Legend
    if not is_transparency:
        patches = [mpatches.Patch(color=depth_colors[d], label=depth_labels[d])
                   for d in depths]
        ax.legend(handles=patches,
                  title="Depth (m)", title_fontsize=FS_LEGTIT,
                  loc="upper left", fontsize=FS_LEGEND,
                  frameon=True, framealpha=0.85,
                  borderpad=0.6, handlelength=1.4,
                  handletextpad=0.5)
    else:
        ax.legend(handles=[mpatches.Patch(color="#7b2d8b", label="Transparency")],
                  loc="upper left", fontsize=FS_LEGEND,
                  frameon=True, framealpha=0.85)


# ══════════════════════════════════════════════════════════════
# RENDER PER PARAMETER
# ══════════════════════════════════════════════════════════════
FIG_W = max(20, n_months * 0.85)
FIG_H = 7

os.makedirs(OUTPUT_DIR, exist_ok=True)

for col, ylabel, label, param_name, is_transp in params:
    print(f"▶ Memproses: {param_name} ...")

    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))

    df_src = df_tr if is_transp else df

    draw_single_parameter(
        ax           = ax,
        data_col     = col,
        df_src       = df_src,
        depth_col    = col_depth if not is_transp else None,
        ym_col       = "YearMonth",
        depths       = depths,
        depth_colors = depth_colors,
        period_to_x  = period_to_x,
        panel_label  = label,
        ylabel       = ylabel,
        is_transparency = is_transp,
    )

    # Sumbu X: label bulan
    ax.set_xticks(range(n_months))
    ax.set_xticklabels(
        [p.strftime("%b") for p in all_periods],
        fontsize=FS_TICK, rotation=0, ha="right"
    )
    ax.set_xlim(-0.7, n_months - 0.3)
    ax.tick_params(axis="x", length=5, width=1.2)

    # Separator & label tahun
    add_year_separators(ax, all_periods, period_to_x, FS_YEAR)


    plt.tight_layout()

    out_path = os.path.join(OUTPUT_DIR, f"TEPAST_Boxplot_{param_name}.png")
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✅ Disimpan: {out_path}")

print("\n🎉 Semua parameter selesai dirender.")

#%%

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator

# =========================
# LOAD DATA
# =========================
main_file = ""
trans_file = ""

df = pd.read_excel(main_file)
trans_df = pd.read_excel(trans_file)

df.columns = [c.strip() for c in df.columns]
trans_df.columns = [c.strip() for c in trans_df.columns]

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["MonthYear"] = df["Date"].dt.strftime("%b-%Y")

date_col = [c for c in trans_df.columns if "date" in c.lower()][0]
trans_df[date_col] = pd.to_datetime(trans_df[date_col], errors="coerce")
trans_df["MonthYear"] = trans_df[date_col].dt.strftime("%b-%Y")

# Transparency column
trans_col = [c for c in trans_df.columns if "trans" in c.lower()][0]

# Parameters
params = [
    ("Temp (deg C)", "Temperature"),
    ("Salinity (PSU)", "Salinity"),
    ("pH (NBS)", "pH"),
    ("Chl-a (mg m-3)", "Chlorophyll-a"),
    ("DO (mg L-1)", "Dissolved Oxygen"),
]

depth_col = "Depth (m)"

colors = {
    0: "limegreen",
    10: "tomato",
    20: "dodgerblue"
}

months = list(dict.fromkeys(df["MonthYear"].dropna()))

# =========================
# FIGURE
# =========================
fig, axes = plt.subplots(
    6,
    1,
    figsize=(24, 15),
    sharex=True
)

# =========================
# MAIN PANELS
# =========================
for idx, (col, title) in enumerate(params):

    ax = axes[idx]
    width = 0.22

    for j, depth in enumerate(sorted(df[depth_col].dropna().unique())):

        box_data = []
        positions = []

        for i, month in enumerate(months):

            vals = df[
                (df["MonthYear"] == month) &
                (df[depth_col] == depth)
            ][col].dropna().values

            if len(vals) > 0:
                box_data.append(vals)
                positions.append(i + (j - 1) * width)

        if len(box_data) > 0:
            bp = ax.boxplot(
                box_data,
                positions=positions,
                widths=width,
                patch_artist=True,
                showfliers=False
            )

            for patch in bp['boxes']:
                patch.set_facecolor(colors.get(depth, "gray"))
                patch.set_alpha(0.85)

            for median in bp['medians']:
                median.set_color("black")

    # Tambahkan 4 tick khusus suhu dan salinitas
    if title in ["Temperature", "Salinity"]:
        ax.yaxis.set_major_locator(MaxNLocator(4))

    legend_elements = [
        Patch(facecolor="limegreen", edgecolor='black', label='0 m'),
        Patch(facecolor="tomato", edgecolor='black', label='10 m'),
        Patch(facecolor="dodgerblue", edgecolor='black', label='20 m')
    ]

    ax.legend(
        handles=legend_elements,
        title="Depth (m)",
        loc="upper left",
        fontsize=10,
        title_fontsize=11,
        frameon=True
    )

    ax.set_title(
        f"({chr(97+idx)}) {title}",
        loc="left",
        fontsize=16,
        fontweight="bold"
    )

    ax.tick_params(axis='y', labelsize=14)

    ax.grid(True, alpha=0.3)

# =========================
# TRANSPARENCY PANEL
# =========================
ax = axes[5]

box_data = []
positions = []

for i, month in enumerate(months):

    vals = trans_df[
        trans_df["MonthYear"] == month
    ][trans_col].dropna().values

    if len(vals) > 0:
        box_data.append(vals)
        positions.append(i)

bp = ax.boxplot(
    box_data,
    positions=positions,
    widths=0.35,
    patch_artist=True,
    showfliers=False
)

for patch in bp['boxes']:
    patch.set_facecolor("mediumorchid")
    patch.set_alpha(0.9)

ax.set_title(
    "(f) Transparency",
    loc="left",
    fontsize=18,
    fontweight="bold"
)

ax.tick_params(axis='y', labelsize=16)

ax.legend(
    [Patch(facecolor="mediumorchid", edgecolor="black")],
    ["Transparency"],
    loc="upper left",
    fontsize=13,
    frameon=True
)

ax.grid(True, alpha=0.3)

# =========================
# X LABELS
# =========================
tick_positions = np.arange(0, len(months), 3)
tick_labels = [months[i] for i in tick_positions]

axes[-1].set_xticks(tick_positions)
axes[-1].set_xticklabels(
    tick_labels,
    rotation=0,
    ha='center',
    fontsize=14
)

fig.supxlabel(
    "Month-Year",
    fontsize=18,
    fontweight="bold"
)

plt.tight_layout()

output_path = ""
plt.savefig(output_path, dpi=300, bbox_inches="tight")

print("Saved:", output_path)

#%%%

import pandas as pd
import matplotlib.pyplot as plt

# =========================
# LOAD DATA
# =========================
path = ""
df = pd.read_excel(path, sheet_name="Semua Stasiun")

depth_order = [0, 10, 20]
df = df[df["Depth (m)"].isin(depth_order)]

# =========================
# PARAMETER
# =========================
params = [
    ("Temp (deg C)", "Temperature (°C)", "(a)"),
    ("Salinity (PSU)", "Salinity (PSU)", "(b)"),
    ("Chl-a (mg m-3)", "Chl-a (mg L$^{-1}$)", "(c)"),
    ("DO (mg L-1)", "DO (mg L$^{-1}$)", "(d)"),
    ("pH (NBS)", "pH (TBS)", "(e)")
]

# =========================
# FONT
# =========================
plt.rcParams.update({
    'font.size': 16,
    'axes.labelsize': 20,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16
})

# =========================
# FIGURE
# =========================
fig, axes = plt.subplots(1, 5, figsize=(24, 7))
fig.patch.set_facecolor("white")

colors = ["#e67c73", "#6aaed6", "#5aa469"]

# =========================
# LOOP PARAMETER
# =========================
for ax, (col, ylabel, panel) in zip(axes, params):

    data = [df[df["Depth (m)"] == d][col].dropna()
            for d in depth_order]

    bp = ax.boxplot(
        data,
        patch_artist=True,
        widths=0.55,
        showfliers=True
    )

    # STYLE
    for patch, c in zip(bp["boxes"], colors):
        patch.set_facecolor(c)
        patch.set_alpha(0.9)
        patch.set_linewidth(1.5)

    for median in bp["medians"]:
        median.set_color("black")
        median.set_linewidth(2.5)

    for whisker in bp["whiskers"]:
        whisker.set_color("gray")
        whisker.set_linewidth(1.2)

    for cap in bp["caps"]:
        cap.set_color("gray")
        cap.set_linewidth(1.2)

    for flier in bp["fliers"]:
        flier.set(
            marker='o',
            markersize=4,
            markerfacecolor='white',
            markeredgecolor='black',
            alpha=0.7
        )

    # LABEL
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(["0 m", "10 m", "20 m"])

    ax.set_ylabel(ylabel)

    ax.text(
        0.05, 0.97,
        panel,
        transform=ax.transAxes,
        fontsize=20,
        fontweight='bold',
        va='top'
    )

    # n value
    n = len(data[0])

    ax.text(
        0.5,
        -0.10,
        f"n={n}",
        transform=ax.transAxes,
        ha='center',
        fontsize=13
    )

    ax.grid(True, linestyle='-', alpha=0.2)
    ax.set_facecolor("white")

# =========================
# EXTENDED Y RANGE
# =========================
axes[0].set_ylim(22, 36)
axes[1].set_ylim(10, 40)
axes[2].set_ylim(0.00, 0.10)
axes[3].set_ylim(2, 10)
axes[4].set_ylim(5, 10)

# =========================
# LAYOUT
# =========================
plt.tight_layout()

# =========================
# SAVE
# =========================
output_path = ""

plt.savefig(
    output_path,
    dpi=600,
    bbox_inches="tight",
    facecolor="white"
)

plt.close()

print(f"Saved figure to: {output_path}")
