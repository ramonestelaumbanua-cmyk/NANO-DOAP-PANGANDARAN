# -*- coding: utf-8 -*-
"""
Figure3_time_series.py
NANO-DOAP TEPAST -- Essential Ocean Variables, Pangandaran Bay

Reproduces Figure 3 (monthly time series, panels a-e by depth as
grouped boxplots, panel f for Secchi-depth transparency) from the
corrected EOV dataset.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta

df = pd.read_pickle('../data/eov_df_corrected.pkl')
df['Date'] = pd.to_datetime(df['Date'])

trans = pd.read_excel('../data/Transparency_final.xlsx', sheet_name=0, header=2)
trans['Date'] = pd.to_datetime(trans['Date'])

BLUE = '#0072B2'   # 0 m
ORANGE = '#E69F00' # 10 m
GREEN = '#009E73'  # 20 m
MAGENTA = '#CC79A7' # transparency

depth_colors = {0: BLUE, 10: ORANGE, 20: GREEN}
depth_order = [0, 10, 20]

panels = [
    ('a', 'Temperature', 'Temp (deg C)', True),
    ('b', 'Salinity', 'Salinity (PSU)', True),
    ('c', 'pH (NBS)', 'pH (NBS)', True),
    ('d', 'Chlorophyll-a', 'Chl-a (mg m-3)', True),
    ('e', 'Dissolved Oxygen', 'DO (mg L-1)', True),
    ('f', 'Transparency', 'Transparency (m)', False),
]

fig, axes = plt.subplots(6, 1, figsize=(13.8, 15.57), dpi=100)

for ax, (letter, title, col, by_depth) in zip(axes, panels):
    ax.set_title(f"({letter}) {title}", loc='left', fontsize=13, fontweight='bold')
    if by_depth:
        dates = sorted(df['Date'].unique())
        n_total = len(df)
        width = 4.5  # days offset between depth sub-boxes
        for i, dep in enumerate(depth_order):
            offset = (i - 1) * width
            box_data = []
            positions = []
            for d in dates:
                vals = df[(df['Date']==d) & (df['Depth (m)']==dep)][col].dropna().values
                if len(vals) == 0:
                    continue
                box_data.append(vals)
                positions.append(mdates.date2num(d) + offset)
            if not box_data:
                continue
            bp = ax.boxplot(box_data, positions=positions, widths=3.2, patch_artist=True,
                             showfliers=True, manage_ticks=False,
                             flierprops=dict(marker='D', markersize=2.5, markerfacecolor='black', markeredgecolor='black'),
                             medianprops=dict(color='black', linewidth=0.9),
                             whiskerprops=dict(color='black', linewidth=0.7),
                             capprops=dict(color='black', linewidth=0.7),
                             boxprops=dict(facecolor=depth_colors[dep], edgecolor='black', linewidth=0.6))
        ax.text(0.01, 0.06, f"N = {n_total}", transform=ax.transAxes, fontsize=9,
                bbox=dict(boxstyle='square', facecolor='white', edgecolor='black', linewidth=0.6))
    else:
        dates = sorted(trans['Date'].unique())
        n_total = len(trans)
        box_data = []
        positions = []
        for d in dates:
            vals = trans[trans['Date']==d]['Transparency (m)'].dropna().values
            if len(vals) == 0:
                continue
            box_data.append(vals)
            positions.append(mdates.date2num(d))
        bp = ax.boxplot(box_data, positions=positions, widths=3.5, patch_artist=True,
                         showfliers=True, manage_ticks=False,
                         flierprops=dict(marker='D', markersize=2.5, markerfacecolor='black', markeredgecolor='black'),
                         medianprops=dict(color='black', linewidth=0.9),
                         whiskerprops=dict(color='black', linewidth=0.7),
                         capprops=dict(color='black', linewidth=0.7),
                         boxprops=dict(facecolor=MAGENTA, edgecolor='black', linewidth=0.6))
        ax.text(0.01, 0.06, f"N = {n_total}", transform=ax.transAxes, fontsize=9,
                bbox=dict(boxstyle='square', facecolor='white', edgecolor='black', linewidth=0.6))

    ax.set_ylabel(title, fontsize=10)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[3,6,9,12]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%Y'))
    ax.set_xlim(pd.Timestamp('2021-07-01'), pd.Timestamp('2026-07-01'))
    ax.tick_params(axis='x', labelrotation=45, labelsize=8)
    ax.tick_params(axis='y', labelsize=9)
    for lbl in ax.get_xticklabels():
        lbl.set_ha('right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# legend on panel a only (depth)
handles = [plt.Rectangle((0,0),1,1, facecolor=depth_colors[d], edgecolor='black', linewidth=0.6) for d in depth_order]
axes[0].legend(handles, ['0 m','10 m','20 m'], title='Depth (m)', loc='upper right', fontsize=8, title_fontsize=9, frameon=True)

axes[-1].set_xlabel('Month-Year', fontsize=11)

plt.tight_layout()
plt.savefig('Figure3_time_series.png', dpi=300, facecolor='white')
print("done")
