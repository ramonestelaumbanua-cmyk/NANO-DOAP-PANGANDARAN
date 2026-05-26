import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap

# ============================================================
# FONT SIZE GLOBAL
# ============================================================
LABEL_FONTSIZE  = 14
TITLE_FONTSIZE  = 14
TICK_FONTSIZE   = 12

plt.rcParams.update({
    "font.size":             14,
    "axes.titlesize":        TITLE_FONTSIZE,
    "axes.labelsize":        LABEL_FONTSIZE,
    "xtick.labelsize":       TICK_FONTSIZE,
    "ytick.labelsize":       TICK_FONTSIZE,
    "legend.fontsize":       12,
    "axes.spines.top":       False,
    "axes.spines.right":     False,
})

# ============================================================
# KONFIGURASI PATH  ← sesuaikan dengan path Anda
# ============================================================
FILE_PATH    = ""
FILE_TRANSP  = ""
OUTPUT_PATH  = ""
SHEET_NAME   = ""
SHEET_TRANSP = 0
# ============================================================

# ── Nama kolom ───────────────────────────────────────────────
col_date  = "Date"
col_depth = "Depth (m)"
col_temp  = "Temp (deg C)"
col_sal   = "Salinity (PSU)"
col_chl   = "Chl-a (mg m-3)"
col_do    = "DO (mg L-1)"
col_ph    = "pH (NBS)"

# ── Baca data utama ─────────────────────────────────────────
df = pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME)
df.columns = df.columns.str.strip()
df[col_date]  = pd.to_datetime(df[col_date])
df[col_depth] = pd.to_numeric(df[col_depth], errors="coerce")
for c in [col_temp, col_sal, col_chl, col_do, col_ph]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# ── Baca data Transparency ───────────────────────────────────
df_tr = pd.read_excel(FILE_TRANSP, sheet_name=SHEET_TRANSP)
df_tr.columns = df_tr.columns.str.strip()
col_tr_date   = "Date"
col_tr_transp = "Transparency (m)"
df_tr[col_tr_date]   = pd.to_datetime(df_tr[col_tr_date])
df_tr[col_tr_transp] = pd.to_numeric(df_tr[col_tr_transp], errors="coerce")

# ============================================================
# PALET WARNA GRADASI PER PARAMETER
# Setiap parameter punya colormap khas seperti visualisasi spasial
# (dari nilai rendah → nilai tinggi)
# ============================================================
PARAM_CMAPS = {
    "temp":  "RdYlBu_r",       # merah (hangat) → biru (dingin) — khas suhu
    "sal":   "YlOrRd",         # kuning → oranye → merah — salinitas
    "chl":   "YlGn",           # kuning → hijau — klorofil
    "do":    "Blues",          # biru muda → biru tua — oksigen
    "ph":    "PuOr",           # ungu → oranye — pH
    "transp":"BuPu",           # biru → ungu — transparansi
}

# ============================================================
# FUNGSI: buat histogram dengan bar berwarna gradasi
# ============================================================
def plot_hist_gradient(ax, data, xlabel, cmap_name, bins=15):
    """
    Histogram distribusi frekuensi dengan gradasi warna pada tiap bar.
    Warna bar mengikuti nilai bin (rendah → tinggi) sesuai colormap parameter.
    """
    data_clean = data.dropna()
    if data_clean.empty:
        ax.set_visible(False)
        return

    counts, bin_edges = np.histogram(data_clean, bins=bins)
    cmap   = plt.get_cmap(cmap_name)

    # Normalisasi posisi bin untuk memetakan warna
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    norm = mcolors.Normalize(vmin=bin_centers.min(), vmax=bin_centers.max())

    bar_width = bin_edges[1] - bin_edges[0]

    for i, (cnt, left) in enumerate(zip(counts, bin_edges[:-1])):
        color = cmap(norm(bin_centers[i]))
        ax.bar(left, cnt,
               width=bar_width * 0.92,   # sedikit gap antar bar
               align="edge",
               color=color,
               edgecolor="white",
               linewidth=0.4,
               zorder=3)

    # Grid horizontal seperti contoh gambar
    ax.yaxis.grid(True, linestyle="-", linewidth=0.4,
                  color="lightgrey", zorder=0)
    ax.set_axisbelow(True)

    ax.set_xlabel(xlabel, fontsize=LABEL_FONTSIZE, labelpad=4)
    ax.set_ylabel("Frequency", fontsize=LABEL_FONTSIZE, labelpad=4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)



# ============================================================
# LAYOUT: 3 baris × 2 kolom  (6 panel)
# ============================================================
params = [
    (df[col_temp].dropna(),                      "Temperature (°C)",    "temp"),
    (df[col_sal].dropna(),                        "Salinity (PSU)",      "sal"),
    (df[col_chl].dropna(),                        "Chl-a (mg/L)",        "chl"),
    (df[col_do].dropna(),                         "DO (mg/L)",           "do"),
    (df[col_ph].dropna(),                         "pH (NBS)",            "ph"),
    (df_tr[col_tr_transp].dropna(),               "Transparency (m)",    "transp"),
]

fig, axes = plt.subplots(
    nrows=3, ncols=2,
    figsize=(13, 11),
    constrained_layout=True
)
axes_flat = axes.flatten()

for ax, (data, xlabel, ckey) in zip(axes_flat, params):
    plot_hist_gradient(ax, data, xlabel, PARAM_CMAPS[ckey], bins=15)

plt.savefig(OUTPUT_PATH, dpi=150, bbox_inches="tight")
print(f"\n✅ Grafik disimpan ke:\n{OUTPUT_PATH}")
plt.show()
