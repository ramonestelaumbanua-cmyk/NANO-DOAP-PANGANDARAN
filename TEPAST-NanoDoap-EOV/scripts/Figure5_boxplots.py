# -*- coding: utf-8 -*-
"""
Figure5_boxplots.py
NANO-DOAP TEPAST -- Essential Ocean Variables, Pangandaran Bay

Reproduces Figure 5 (by-depth boxplots for each EOV: 0 m, 10 m, 20 m)
from the corrected EOV dataset.
"""
import pandas as pd
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

BLUE = '#1f77b4'
ORANGE = '#E6A817'
GREEN = '#17A673'
colors = {0: BLUE, 10: ORANGE, 20: GREEN}

# Note: unicode superscript/subscript minus (U+207B) is missing from the
# Liberation Sans glyph table, so Chl-a/DO units use matplotlib mathtext
# ($^{-3}$, $^{-1}$) instead of the unicode "⁻³"/"⁻¹" characters -- the same
# fix already applied in Figure3/Figure4.
panels = [
    ('a', 'Temperature', 'Temp (deg C)', 'Temperature (°C)'),
    ('b', 'Salinity', 'Salinity (PSU)', 'Salinity (PSU)'),
    ('c', 'Chlorophyll-a', 'Chl-a (mg m-3)', 'Chl-a (mg m$^{-3}$)'),
    ('d', 'Dissolved Oxygen', 'DO (mg L-1)', 'DO (mg L$^{-1}$)'),
    ('e', 'pH (NBS)', 'pH (NBS)', 'pH (NBS)'),
]

# n is identical (156) across all five variables and all three depths --
# verified directly against the deposited data file (asserted below) rather
# than assumed, before being written into each panel's annotation.
N_PER_DEPTH = 156
for _, _, col, _ in panels:
    for d in (0, 10, 20):
        n = df[df['Depth (m)'] == d][col].dropna().shape[0]
        assert n == N_PER_DEPTH, f"n mismatch for {col} at {d} m: {n}"

fig, axes = plt.subplots(1, 5, figsize=(24.5, 7.4), dpi=100)
fig.subplots_adjust(left=0.035, right=0.99, top=0.89, bottom=0.21, wspace=0.42)

for ax, (letter, title, col, ylabel) in zip(axes, panels):
    data = [df[df['Depth (m)'] == d][col].dropna().values for d in [0, 10, 20]]
    bp = ax.boxplot(data, positions=[1, 2, 3], widths=0.6, patch_artist=True,
                     showfliers=True,
                     flierprops=dict(marker='D', markersize=4, markerfacecolor='black', markeredgecolor='black'),
                     medianprops=dict(color='black', linewidth=1.6),
                     whiskerprops=dict(color='black', linewidth=1.3),
                     capprops=dict(color='black', linewidth=1.3),
                     boxprops=dict(edgecolor='black', linewidth=1.1))
    for patch, d in zip(bp['boxes'], [0, 10, 20]):
        patch.set_facecolor(colors[d])
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(['0 m', '10 m', '20 m'], fontsize=21)
    ax.set_xlabel('Depth (m)', fontsize=22, labelpad=10)
    ax.set_ylabel(ylabel, fontsize=23)
    ax.set_title(f"({letter}) {title}", loc='left', fontsize=23, fontweight='bold')
    if letter in ('d', 'e'):  # DO, pH: one decimal place for consistency
        ax.yaxis.set_major_locator(plt.MaxNLocator(nbins=5))
        ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.1f'))
    ax.text(0.5, -0.30, f'n = {N_PER_DEPTH} each', transform=ax.transAxes,
            fontsize=17, ha='center')
    ax.tick_params(axis='y', labelsize=19)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_linewidth(1.4)
    ax.spines['left'].set_linewidth(1.4)

plt.savefig('Figure5_boxplots.png', dpi=300, facecolor='white')
plt.savefig('Figure5_boxplots.tiff', dpi=300, facecolor='white', pil_kwargs={'compression': 'tiff_lzw'})
print("done")
