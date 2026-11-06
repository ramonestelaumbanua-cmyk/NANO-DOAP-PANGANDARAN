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

df = pd.read_pickle('../data/eov_df_corrected.pkl')
df['Date'] = pd.to_datetime(df['Date'])
df['Month'] = df['Date'].dt.month

trans = pd.read_excel('../data/Transparency_final.xlsx', sheet_name=0, header=2)
trans['Date'] = pd.to_datetime(trans['Date'])
trans['Month'] = trans['Date'].dt.month

BLUE = '#1f77b4'
ORANGE = '#E6A817'
GREEN = '#17A673'
RED = '#D2691E'
MAGENTA = '#C77DC7'
depth_colors = {0: BLUE, 10: ORANGE, 20: GREEN}

months = list(range(1,13))
month_labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

panels = [
    ('a', 'Temperature (°C)', 'Temp (deg C)', True),
    ('b', 'Salinity (PSU)', 'Salinity (PSU)', True),
    ('c', 'Chl-a (mg m⁻³)', 'Chl-a (mg m-3)', True),
    ('d', 'DO (mg L⁻¹)', 'DO (mg L-1)', True),
    ('e', 'pH (NBS)', 'pH (NBS)', True),
    ('f', 'Transparency (m)', 'Transparency (m)', False),
]

fig, axes = plt.subplots(6, 1, figsize=(14.6, 20.0), dpi=100)

for ax, (letter, ylabel, col, by_depth) in zip(axes, panels):
    ax.set_title(f"({letter}) {ylabel.split(' (')[0]}", loc='left', fontsize=14, fontweight='bold')
    if by_depth:
        src = df
        grp_all = src.groupby('Month')[col]
        mn = grp_all.min().reindex(months)
        mx = grp_all.max().reindex(months)
        ax.fill_between(months, mn, mx, color='lightgray', alpha=0.7, label='Min-max range', zorder=1)
        overall_mean = grp_all.mean().reindex(months)
        for d in [0,10,20]:
            sub = src[src['Depth (m)']==d]
            m = sub.groupby('Month')[col].mean().reindex(months)
            ax.plot(months, m, color=depth_colors[d], marker='o', markersize=4, linewidth=1.8,
                    label=f'Depth: {d}m', zorder=3)
        ax.plot(months, overall_mean, color='#C0392B', linestyle='--', linewidth=1.6, label='Overall Mean', zorder=4)
    else:
        grp_all = trans.groupby('Month')['Transparency (m)']
        mn = grp_all.min().reindex(months)
        mx = grp_all.max().reindex(months)
        ax.fill_between(months, mn, mx, color='lightgray', alpha=0.7, zorder=1)
        m = grp_all.mean().reindex(months)
        ax.plot(months, m, color=MAGENTA, marker='o', markersize=4, linewidth=1.8, zorder=3)

    ax.set_xticks(months)
    ax.set_xticklabels(month_labels, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='y', labelsize=10)

axes[0].legend(loc='upper left', fontsize=9, ncol=2, frameon=True)
axes[-1].set_xlabel('Month', fontsize=12)

plt.tight_layout()
plt.savefig('Figure4_seasonal_climatology.png', dpi=300, facecolor='white')
print("done")
