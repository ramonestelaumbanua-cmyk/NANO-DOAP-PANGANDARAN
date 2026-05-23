import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from scipy.ndimage import gaussian_filter1d

# ============================================================
# FONT SIZE GLOBAL
# ============================================================
YLABEL_FONTSIZE = 19   # ← label parameter (Temp, Sal, dst) — atur bebas

plt.rcParams.update({
    "font.size": 22,
    "axes.titlesize": 19,
    "axes.labelsize": 19,
    "xtick.labelsize": 19,
    "ytick.labelsize": 19,
    "legend.fontsize": 19,
    "legend.title_fontsize": 22,
})

# ============================================================
# KONFIGURASI PATH
# ============================================================
FILE_PATH         = r"F:\KULIAH RAMONES\KARIR\Olah Data TEPAST\Data\TEPAST_NanoDoap_Rapi.xlsx"
FILE_TRANSP       = r"F:\KULIAH RAMONES\KARIR\Olah Data TEPAST\Data\TEPAST_NanoDoap_Transparancy.xlsx"
OUTPUT_PATH       = r"F:\KULIAH RAMONES\KARIR\Olah Data TEPAST\TEPAST_TimeSeries_Plot_v4.png"
SHEET_NAME        = "Semua Stasiun"
SHEET_TRANSP      = 0          # ganti ke nama sheet jika bukan sheet pertama
# ============================================================

# ── Baca data utama ─────────────────────────────────────────
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
df = df.sort_values([col_date, col_depth]).reset_index(drop=True)

# ── Baca data Transparency ───────────────────────────────────
df_tr = pd.read_excel(FILE_TRANSP, sheet_name=SHEET_TRANSP)
df_tr.columns = df_tr.columns.str.strip()

col_tr_date   = "Date"
col_tr_transp = "Transparency (m)"   # sesuaikan jika nama kolom berbeda

df_tr[col_tr_date] = pd.to_datetime(df_tr[col_tr_date])
df_tr[col_tr_transp] = pd.to_numeric(df_tr[col_tr_transp], errors="coerce")
df_tr = df_tr.sort_values(col_tr_date).reset_index(drop=True)

date_min = df[col_date].min()
date_max = df[col_date].max()
print(f"Rentang data utama  : {date_min.date()} → {date_max.date()}")
print(f"Rentang Transparency: {df_tr[col_tr_date].min().date()} → {df_tr[col_tr_date].max().date()}")

# ── Parameter (5 parameter per kedalaman + 1 Transparency) ──
params_depth = [
    (col_temp, "Temp (°C)"),
    (col_sal,  "Salinity (PSU)"),
    (col_chl,  "Chl-a (mg m⁻³)"),
    (col_do,   "DO (mg L⁻¹)"),
    (col_ph,   "pH (NBS)"),
]

depths       = [0, 10, 20]
depth_colors = {0: "#2166ac", 10: "#f4a11d", 20: "#1a9850"}
COLOR_TRANSP = "#7b2d8b"   # ungu — warna khas Transparency
sigma        = 3

# ── Fungsi smooth yang aman (handle NaN & ujung data) ────────
def safe_smooth(dates, vals, sigma=3):
    s = pd.Series(vals, index=dates)
    nan_mask = s.isna()
    if nan_mask.all():
        return None, None
    s_interp = s.interpolate(method="time").ffill().bfill()
    smoothed = gaussian_filter1d(s_interp.values.astype(float), sigma=sigma)
    smoothed[nan_mask.values] = np.nan
    return dates, smoothed

# ============================================================
# PLOT — 5 panel kedalaman + 1 panel Transparency
# ============================================================
n_rows = len(params_depth) + 1          # +1 untuk Transparency

fig, axes = plt.subplots(
    nrows=n_rows, ncols=1,
    figsize=(25, 4 * n_rows),
    sharex=True
)

# ── Panel 1-5 : parameter per kedalaman ─────────────────────
for ax, (col, ylabel) in zip(axes[:len(params_depth)], params_depth):
    df[col] = pd.to_numeric(df[col], errors="coerce")

    df_all = df.groupby(col_date)[col].agg(["min", "max"]).reset_index()
    ax.fill_between(df_all[col_date], df_all["min"], df_all["max"],
                    color="lightgrey", alpha=0.55, zorder=1)

    for d in depths:
        df_d = df[df[col_depth] == d].copy()
        if df_d.empty or df_d[col].isna().all():
            print(f"⚠️  Kedalaman {d}m kosong untuk {col}")
            continue

        df_avg = df_d.groupby(col_date)[col].mean().reset_index().sort_values(col_date)

        ax.scatter(df_avg[col_date], df_avg[col].values,
                   color=depth_colors[d], s=16, alpha=0.65, zorder=4)

        x_smooth, y_smooth = safe_smooth(
            df_avg[col_date].values,
            df_avg[col].values,
            sigma=sigma
        )

        if x_smooth is not None:
            x_s = pd.Series(y_smooth, index=pd.to_datetime(x_smooth))
            not_nan = ~x_s.isna()
            segments = (not_nan != not_nan.shift()).cumsum()[not_nan]
            for _, seg in x_s[not_nan].groupby(segments):
                ax.plot(seg.index, seg.values,
                        color=depth_colors[d], linewidth=2.2, zorder=3)

    ax.set_ylabel(ylabel, fontsize=YLABEL_FONTSIZE)   # ← pakai YLABEL_FONTSIZE
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.spines[["top", "right"]].set_visible(False)

# ── Panel 6 : Transparency ───────────────────────────────────
ax_tr = axes[-1]

tr_range = df_tr.groupby(col_tr_date)[col_tr_transp].agg(["min", "max"]).reset_index()
ax_tr.fill_between(tr_range[col_tr_date], tr_range["min"], tr_range["max"],
                   color="lightgrey", alpha=0.55, zorder=1)

tr_avg = df_tr.groupby(col_tr_date)[col_tr_transp].mean().reset_index().sort_values(col_tr_date)
ax_tr.scatter(tr_avg[col_tr_date], tr_avg[col_tr_transp].values,
              color=COLOR_TRANSP, s=20, alpha=0.70, zorder=4)

x_sm, y_sm = safe_smooth(tr_avg[col_tr_date].values,
                          tr_avg[col_tr_transp].values, sigma=sigma)
if x_sm is not None:
    x_s = pd.Series(y_sm, index=pd.to_datetime(x_sm))
    not_nan = ~x_s.isna()
    segs = (not_nan != not_nan.shift()).cumsum()[not_nan]
    for _, seg in x_s[not_nan].groupby(segs):
        ax_tr.plot(seg.index, seg.values,
                   color=COLOR_TRANSP, linewidth=2.2, zorder=3)

ax_tr.set_ylabel("Transparency (m)", fontsize=YLABEL_FONTSIZE)   # ← pakai YLABEL_FONTSIZE
ax_tr.grid(axis="y", linestyle="--", alpha=0.35)
ax_tr.spines[["top", "right"]].set_visible(False)

# ── Format sumbu X ────────────────────────────────────────────
for a in axes:
    a.set_xlim(date_min - pd.Timedelta(days=15),
               date_max + pd.Timedelta(days=15))

axes[-1].xaxis.set_major_locator(mdates.MonthLocator(interval=4))
axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.setp(axes[-1].xaxis.get_majorticklabels(), rotation=0, ha="center")
axes[-1].set_xlabel("Date", fontsize=YLABEL_FONTSIZE)   # ← pakai YLABEL_FONTSIZE

# ── Legend ────────────────────────────────────────────────────
legend_handles = [
    mpatches.Patch(color="lightgrey",          label="Actual data range, min-max"),
    plt.Line2D([0],[0], color=depth_colors[0],  lw=2, label="0 m smoothed average"),
    plt.Line2D([0],[0], color=depth_colors[10], lw=2, label="10 m smoothed average"),
    plt.Line2D([0],[0], color=depth_colors[20], lw=2, label="20 m smoothed average"),
    plt.Line2D([0],[0], color=COLOR_TRANSP,     lw=2, label="Transparency smoothed average"),
    plt.Line2D([0],[0], marker="o", color="grey", markersize=5,
               linestyle="None", label="Actual average points"),
]

# BARU:
fig.legend(
    handles=legend_handles,
    loc="lower center",
    bbox_to_anchor=(0.5, -0.040),
    ncol=3,
    frameon=False,
)

plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=150, bbox_inches="tight")
print(f"\n✅ Grafik disimpan ke:\n{OUTPUT_PATH}")
plt.show()