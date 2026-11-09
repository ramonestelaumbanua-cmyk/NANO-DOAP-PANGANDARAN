# -*- coding: utf-8 -*-
"""
Figure4_seasonal_climatology.py
NANO-DOAP TEPAST -- Essential Ocean Variables, Pangandaran Bay

Reproduces Figure 4 (monthly climatology: min-max range, overall
mean, and per-depth mean for each EOV plus Secchi-depth transparency)
from the corrected EOV dataset.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Journal (Nature portfolio) figure requirements: sans-serif typeface,
# preferably Helvetica/Arial; Liberation Sans is a free, metrically
# Arial-compatible substitute available in this environment.
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Liberation Sans', 'Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

df = pd.read_pickle('../data/eov_df_corrected.pkl')
df['Date'] = pd.to_datetime(df['Date'])
df['Month'] = df['Date'].dt.month

trans = pd.read_excel('../data/Transparency_final.xlsx', sheet_name=0, header=2)
trans['Date'] = pd.to_datetime(trans['Date'])
trans['Month'] = trans['Date'].dt.month

BLUE = '#1f77b4'
ORANGE = '#E6A817'
GREEN = '#17A673'
MEAN_RED = '#C0392B'
MAGENTA = '#C77DC7'
depth_colors = {0: BLUE, 10: ORANGE, 20: GREEN}

months = list(range(1, 13))
month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Note: unicode superscript/subscript minus (U+207B) is missing from the
# Liberation Sans glyph table, so Chl-a/DO units use matplotlib mathtext
# ($^{-3}$, $^{-1}$) instead of the unicode "⁻³"/"⁻¹" characters -- the same
# fix already applied in Figure3_time_series.py.
panels = [
    ('a', 'Temperature (°C)', 'Temp (deg C)', True),
    ('b', 'Salinity (PSU)', 'Salinity (PSU)', True),
    ('c', 'Chl-a (mg m$^{-3}$)', 'Chl-a (mg m-3)', True),
    ('d', 'DO (mg L$^{-1}$)', 'DO (mg L-1)', True),
    ('e', 'pH (NBS)', 'pH (NBS)', True),
    ('f', 'Transparency (m)', 'Transparency (m)', False),
]

# Manual GridSpec with fixed margins -- same values used in
# Figure3_time_series.py -- so this figure's left edge, panel height, and
# overall proportions match Figure 3 for visual consistency across the
# manuscript, and so every panel's left edge stays flush regardless of each
# y-axis's own tick-label width.
fig = plt.figure(figsize=(13.8, 18.5), dpi=100)
gs = fig.add_gridspec(6, 1, left=0.095, right=0.965, top=0.955, bottom=0.035, hspace=0.85)
axes = [fig.add_subplot(gs[i]) for i in range(6)]

for ax, (letter, ylabel, col, by_depth) in zip(axes, panels):
    ax.set_title(f"({letter}) {ylabel.split(' (')[0]}", loc='left', fontsize=22, fontweight='bold')
    if by_depth:
        src = df
        grp_all = src.groupby('Month')[col]
        mn = grp_all.min().reindex(months)
        mx = grp_all.max().reindex(months)
        ax.fill_between(months, mn, mx, color='lightgray', alpha=0.7, label='Min-max range', zorder=1)
        overall_mean = grp_all.mean().reindex(months)
        for d in [0, 10, 20]:
            sub = src[src['Depth (m)'] == d]
            m = sub.groupby('Month')[col].mean().reindex(months)
            ax.plot(months, m, color=depth_colors[d], marker='o', markersize=5, linewidth=2.0,
                    label=f'Depth: {d} m', zorder=3)
        ax.plot(months, overall_mean, color=MEAN_RED, linestyle='--', linewidth=2.0,
                label='Overall mean', zorder=4)
        # Small legend placed just ABOVE the plot box (outside the data area,
        # level with the title row) on every by-depth panel -- same fix
        # applied to the Depth legend in Figure3_time_series.py, so it never
        # covers the min-max band or the mean lines.
        ax.legend(loc='lower right', bbox_to_anchor=(1.0, 1.0), borderaxespad=0.1,
                  ncol=5, fontsize=11.5, frameon=True, facecolor='white', framealpha=1.0,
                  edgecolor='black', borderpad=0.3, labelspacing=0.3, handlelength=1.3,
                  columnspacing=0.8, handletextpad=0.4).set_zorder(10)
    else:
        grp_all = trans.groupby('Month')['Transparency (m)']
        mn = grp_all.min().reindex(months)
        mx = grp_all.max().reindex(months)
        ax.fill_between(months, mn, mx, color='lightgray', alpha=0.7, label='Min-max range', zorder=1)
        m = grp_all.mean().reindex(months)
        ax.plot(months, m, color=MAGENTA, marker='o', markersize=5, linewidth=2.0,
                label='Mean', zorder=3)
        ax.legend(loc='lower right', bbox_to_anchor=(1.0, 1.0), borderaxespad=0.1,
                  ncol=2, fontsize=11.5, frameon=True, facecolor='white', framealpha=1.0,
                  edgecolor='black', borderpad=0.3, labelspacing=0.3, handlelength=1.3,
                  columnspacing=0.8, handletextpad=0.4).set_zorder(10)

    ax.set_xticks(months)
    ax.set_xticklabels(month_labels, fontsize=20)
    ax.set_ylabel(ylabel, fontsize=19)
    if letter in ('d', 'e', 'f'):  # DO, pH, Transparency: one decimal place for consistency
        ax.yaxis.set_major_locator(plt.MaxNLocator(nbins=4))
        ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.1f'))
    ax.tick_params(axis='x', labelrotation=0, labelsize=20)
    ax.tick_params(axis='y', labelsize=19)
    for lbl in ax.get_xticklabels():
        lbl.set_ha('center')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # Thicken the visible spines so the bottom/left axis lines stay solid and
    # clearly visible at any display/preview scale (same fix as Figure 3).
    ax.spines['bottom'].set_linewidth(1.4)
    ax.spines['left'].set_linewidth(1.4)

axes[-1].set_xlabel('Month', fontsize=18)

# Align all y-axis labels to the same horizontal position, regardless of how
# wide each panel's own y-tick numbers are.
fig.align_ylabels(axes)

plt.savefig('Figure4_seasonal_climatology.png', dpi=300, facecolor='white')
plt.savefig('Figure4_seasonal_climatology.tiff', dpi=300, facecolor='white', pil_kwargs={'compression': 'tiff_lzw'})
print("done")
