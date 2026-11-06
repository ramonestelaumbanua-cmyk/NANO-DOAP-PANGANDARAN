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

df = pd.read_pickle('../data/eov_df_corrected.pkl')

BLUE = '#1f77b4'
ORANGE = '#E6A817'
GREEN = '#17A673'
colors = {0: BLUE, 10: ORANGE, 20: GREEN}

panels = [
    ('a', 'Temp (deg C)', 'Temperature (°C)'),
    ('b', 'Salinity (PSU)', 'Salinity (PSU)'),
    ('c', 'Chl-a (mg m-3)', 'Chl-a (mg m⁻³)'),
    ('d', 'DO (mg L-1)', 'DO (mg L⁻¹)'),
    ('e', 'pH (NBS)', 'pH (NBS)'),
]

fig, axes = plt.subplots(1, 5, figsize=(19.9, 4.9), dpi=100)
for ax, (letter, col, ylabel) in zip(axes, panels):
    data = [df[df['Depth (m)']==d][col].dropna().values for d in [0,10,20]]
    bp = ax.boxplot(data, positions=[1,2,3], widths=0.55, patch_artist=True,
                     showfliers=True,
                     flierprops=dict(marker='o', markersize=4, markerfacecolor='none', markeredgecolor='gray'),
                     medianprops=dict(color='black', linewidth=1.3),
                     whiskerprops=dict(color='black', linewidth=1),
                     capprops=dict(color='black', linewidth=1),
                     boxprops=dict(edgecolor='black', linewidth=1))
    for patch, d in zip(bp['boxes'], [0,10,20]):
        patch.set_facecolor(colors[d])
    ax.set_xticks([1,2,3])
    ax.set_xticklabels(['0 m','10 m','20 m'], fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(f"({letter})", loc='left', fontsize=14, fontweight='bold')
    ax.text(0.5, -0.17, 'n = 156 each', transform=ax.transAxes, fontsize=9, ha='center')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('Figure5_boxplots.png', dpi=300, facecolor='white')
print("done")
