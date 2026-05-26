import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import make_interp_spline

# ============================================================
# FONT SIZE GLOBAL
# ============================================================
YLABEL_FONTSIZE = 19
TICK_FONTSIZE   = 19

plt.rcParams.update({
    "font.family":          "DejaVu Sans",
    "font.size":            22,
    "axes.titlesize":       19,
    "axes.labelsize":       19,
    "xtick.labelsize":      TICK_FONTSIZE,
    "ytick.labelsize":      TICK_FONTSIZE,
    "legend.fontsize":      19,
    "legend.title_fontsize":22,
    "axes.spines.top":      False,
    "axes.spines.right":    False,
})

# ============================================================
# KONFIGURASI PATH
# ============================================================
FILE_PATH    = ""
FILE_TRANSP  = ""
OUTPUT_PATH  = ""
SHEET_NAME   = ""
SHEET_TRANSP = 0
# ============================================================

col_date  = "Date"
col_depth = "Depth (m)"
col_temp  = "Temp (deg C)"
col_sal   = "Salinity (PSU)"
col_chl   = "Chl-a (mg m-3)"
col_do    = "DO (mg L-1)"
col_ph    = "pH (NBS)"

col_tr_date   = "Date"
col_tr_transp = "Transparency (m)"

# ── Baca data ────────────────────────────────────────────────
df = pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME)
df.columns = df.columns.str.strip()
df[col_date]  = pd.to_datetime(df[col_date])
df[col_depth] = pd.to_numeric(df[col_depth], errors="coerce")

df_tr = pd.read_excel(FILE_TRANSP, sheet_name=SHEET_TRANSP)
df_tr.columns = df_tr.columns.str.strip()
df_tr[col_tr_date]   = pd.to_datetime(df_tr[col_tr_date])
df_tr[col_tr_transp] = pd.to_numeric(df_tr[col_tr_transp], errors="coerce")

df["Month"]    = df[col_date].dt.month
df_tr["Month"] = df_tr[col_tr_date].dt.month

MONTHS     = np.arange(1, 13)
MON_LABELS = ["Jan","Feb","Mar","Apr","May","Jun",
               "Jul","Aug","Sep","Oct","Nov","Dec"]

params_depth = [
    (col_temp, "Temp (°C)"),
    (col_sal,  "Salinity (PSU)"),
    (col_chl,  "Chl-a (mg m⁻³)"),
    (col_do,   "DO (mg L⁻¹)"),
    (col_ph,   "pH (NBS)"),
]

depths = [0, 10, 20]

depth_colors = {
    0:  "#1c3a5e",
    10: "#4a7fb5",
    20: "#8ec6e6",
}

COLOR_MEAN   = "#c0392b"
COLOR_TRANSP = "#7b2d8b"
SHADE_COLOR  = "#b0b8c1"

# ── Smooth spline ─────────────────────────────────────────────
def spline_smooth(months, vals, n_out=300):
    filled = np.copy(vals.astype(float))
    nan_mask = np.isnan(filled)
    if nan_mask.all():
        return None, None
    idx = np.arange(len(filled))
    filled[nan_mask] = np.interp(idx[nan_mask], idx[~nan_mask], filled[~nan_mask])
    x_ext = np.concatenate([months[-2:] - 12, months, months[:2] + 12])
    y_ext = np.concatenate([filled[-2:], filled, filled[:2]])
    spl     = make_interp_spline(x_ext, y_ext, k=3)
    x_dense = np.linspace(1, 12, n_out)
    y_dense = spl(x_dense)
    return x_dense, y_dense

# ── Agregasi klimatologi ─────────────────────────────────────
def clim_stats(data, col):
    g = data.groupby("Month")[col].agg(["mean","min","max"]).reindex(MONTHS)
    return g["mean"].values, g["min"].values, g["max"].values

# ── Smooth shaded band ───────────────────────────────────────
def smooth_band(months, lo, hi, n_out=300):
    x1, y1 = spline_smooth(months, lo, n_out)
    x2, y2 = spline_smooth(months, hi, n_out)
    return x1, y1, y2

# ============================================================
# PLOT
# ============================================================
n_rows = len(params_depth) + 1
fig, axes = plt.subplots(
    nrows=n_rows, ncols=1,
    figsize=(25, 4 * n_rows),
    sharex=True
)
fig.subplots_adjust(hspace=0.08)

# ── Panel 1-5 ────────────────────────────────────────────────
for ax, (col, ylabel) in zip(axes[:len(params_depth)], params_depth):
    df[col] = pd.to_numeric(df[col], errors="coerce")

    # Shaded range
    _, rng_min, rng_max = clim_stats(df, col)
    xb, ylo, yhi = smooth_band(MONTHS, rng_min, rng_max)
    ax.fill_between(xb, ylo, yhi,
                    color=SHADE_COLOR, alpha=0.35, zorder=1, linewidth=0)

    # Garis per kedalaman
    for d in depths:
        df_d = df[df[col_depth] == d].copy()
        if df_d.empty or df_d[col].isna().all():
            continue
        mean_vals, _, _ = clim_stats(df_d, col)
        xd, yd = spline_smooth(MONTHS, mean_vals)
        if xd is not None:
            ax.plot(xd, yd, color=depth_colors[d], linewidth=2.0, zorder=3)

    # Overall Mean
    overall_mean, _, _ = clim_stats(df, col)
    xm, ym = spline_smooth(MONTHS, overall_mean)
    if xm is not None:
        ax.plot(xm, ym, color=COLOR_MEAN, linewidth=2.0,
                linestyle="--", zorder=5)

    ax.set_ylabel(ylabel, fontsize=YLABEL_FONTSIZE)
    ax.grid(axis="y", linestyle="--", linewidth=0.6, color="#d0d0d0", alpha=0.8)
    ax.grid(axis="x", visible=False)
    ax.spines[["top","right"]].set_visible(False)
    ax.tick_params(axis="y", labelsize=TICK_FONTSIZE)

    # ── 4 tick khusus salinity ────────────────────────────────
    if col == col_sal:
        ax.yaxis.set_major_locator(plt.MaxNLocator(nbins=3))
        ax.set_ylim(10, 36)   # ← tambah ini

    ax.set_xlim(0.5, 12.5)

    handles_panel = [
        plt.Line2D([0],[0], color=depth_colors[0],  lw=2, label="Depth: 0m"),
        plt.Line2D([0],[0], color=depth_colors[10], lw=2, label="Depth: 10m"),
        plt.Line2D([0],[0], color=depth_colors[20], lw=2, label="Depth: 20m"),
        plt.Line2D([0],[0], color=COLOR_MEAN, lw=2, ls="--", label="Overall Mean"),
    ]
    ax.legend(
        handles=handles_panel,
        loc="upper left",
        frameon='true',
        fontsize=15,
        ncol=4,
        handlelength=2,
        columnspacing=1.2,
        borderpad=0.4,
    )

# ── Panel 6 : Transparency ───────────────────────────────────
ax_tr = axes[-1]

tr_mean, tr_min, tr_max = clim_stats(df_tr, col_tr_transp)

xb, ylo, yhi = smooth_band(MONTHS, tr_min, tr_max)
ax_tr.fill_between(xb, ylo, yhi,
                   color=SHADE_COLOR, alpha=0.35, zorder=1, linewidth=0)

xtr, ytr = spline_smooth(MONTHS, tr_mean)
if xtr is not None:
    ax_tr.plot(xtr, ytr, color=COLOR_TRANSP, linewidth=2.0, zorder=3)

ax_tr.set_ylabel("Transparency (m)", fontsize=YLABEL_FONTSIZE)
ax_tr.grid(axis="y", linestyle="--", linewidth=0.6, color="#d0d0d0", alpha=0.8)
ax_tr.grid(axis="x", visible=False)
ax_tr.spines[["top","right"]].set_visible(False)
ax_tr.tick_params(axis="y", labelsize=TICK_FONTSIZE)
ax_tr.set_xlim(0.5, 12.5)

# ── Sumbu X ──────────────────────────────────────────────────
axes[-1].set_xticks(MONTHS)
axes[-1].set_xticklabels(MON_LABELS, fontsize=TICK_FONTSIZE)
axes[-1].set_xlabel("Month", fontsize=YLABEL_FONTSIZE)

for a in axes[:-1]:
    plt.setp(a.get_xticklabels(), visible=False)
    a.tick_params(axis="x", length=0)

# ── Simpan ───────────────────────────────────────────────────
plt.savefig(OUTPUT_PATH, dpi=150, bbox_inches="tight", facecolor="white")
print(f"Grafik disimpan ke:\n{OUTPUT_PATH}")
plt.show()
