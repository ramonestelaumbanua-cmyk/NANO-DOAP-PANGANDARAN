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

# Journal (Nature portfolio) figure requirements: sans-serif typeface,
# preferably Helvetica/Arial; Liberation Sans is a free, metrically
# Arial-compatible substitute available in this environment.
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Liberation Sans', 'Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

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
    ('a', 'Temperature', 'Temperature (°C)', 'Temp (deg C)', True),
    ('b', 'Salinity', 'Salinity (PSU)', 'Salinity (PSU)', True),
    ('c', 'pH (NBS)', 'pH (NBS)', 'pH (NBS)', True),
    ('d', 'Chlorophyll-a', 'Chl-a (mg m$^{-3}$)', 'Chl-a (mg m-3)', True),
    ('e', 'Dissolved Oxygen', 'DO (mg L$^{-1}$)', 'DO (mg L-1)', True),
    ('f', 'Transparency', 'Transparency (m)', 'Transparency (m)', False),
]

# Manual GridSpec (fixed left/right margins) instead of tight/constrained
# layout: this guarantees all 6 panels share an IDENTICAL left edge (plot
# box x0), so the x-axis is flush across panels regardless of how wide
# each panel's own y-tick labels are (e.g. "0.06" vs "8").
fig = plt.figure(figsize=(13.8, 18.5), dpi=100)
gs = fig.add_gridspec(6, 1, left=0.095, right=0.965, top=0.955, bottom=0.035, hspace=0.85)
axes = [fig.add_subplot(gs[i]) for i in range(6)]

legend_handles = [plt.Rectangle((0,0),1,1, facecolor=depth_colors[d], edgecolor='black', linewidth=0.6) for d in depth_order]

for ax, (letter, title, ylabel, col, by_depth) in zip(axes, panels):
    ax.set_title(f"({letter}) {title}", loc='left', fontsize=22, fontweight='bold')
    if by_depth:
        dates = sorted(df['Date'].unique())
        n_total = len(df)
        width = 9  # days offset between depth sub-boxes
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
            bp = ax.boxplot(box_data, positions=positions, widths=8, patch_artist=True,
                             showfliers=True, manage_ticks=False,
                             flierprops=dict(marker='D', markersize=3.5, markerfacecolor='black', markeredgecolor='black'),
                             medianprops=dict(color='black', linewidth=1.4),
                             whiskerprops=dict(color='black', linewidth=1.1),
                             capprops=dict(color='black', linewidth=1.1),
                             boxprops=dict(facecolor=depth_colors[dep], edgecolor='black', linewidth=0.9))
        # y raised (0.06->0.07) and va='bottom' pins the text's own bottom edge
        # (rather than its baseline) at that height, so the white bbox -- which
        # pads a few more points below that -- clears the bottom axis spine
        # instead of sitting on top of / crossing it.
        ax.text(0.012, 0.07, f"N = {n_total}", transform=ax.transAxes, fontsize=16,
                va='bottom', bbox=dict(boxstyle='square,pad=0.3', facecolor='white', edgecolor='black', linewidth=0.6)).set_zorder(10)
        # Placed just ABOVE the plot box (bbox_to_anchor y=1.0), level with the
        # panel title which sits at the same height on the left -- this keeps
        # the legend out of the data area entirely (it no longer overlaps any
        # boxplot) and, by minimizing its internal padding, sits close to the
        # title row rather than floating high above it.
        ax.legend(legend_handles, ['0 m', '10 m', '20 m'], title='Depth (m)',
                  loc='lower right', bbox_to_anchor=(1.0, 1.0), borderaxespad=0.1,
                  ncol=3, fontsize=12, title_fontsize=13, frameon=True,
                  facecolor='white', framealpha=1.0, edgecolor='black',
                  borderpad=0.3, labelspacing=0.3, handlelength=1.3,
                  columnspacing=0.8, handletextpad=0.4).set_zorder(10)
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
        bp = ax.boxplot(box_data, positions=positions, widths=14, patch_artist=True,
                         showfliers=True, manage_ticks=False,
                         flierprops=dict(marker='D', markersize=3.5, markerfacecolor='black', markeredgecolor='black'),
                         medianprops=dict(color='black', linewidth=1.4),
                         whiskerprops=dict(color='black', linewidth=1.1),
                         capprops=dict(color='black', linewidth=1.1),
                         boxprops=dict(facecolor=MAGENTA, edgecolor='black', linewidth=0.9))
        ax.text(0.012, 0.07, f"N = {n_total}", transform=ax.transAxes, fontsize=16,
                va='bottom', bbox=dict(boxstyle='square,pad=0.3', facecolor='white', edgecolor='black', linewidth=0.6)).set_zorder(10)

    ax.set_ylabel(ylabel, fontsize=19)
    if letter in ('c', 'e', 'f'):  # pH, DO, Transparency: one decimal place for consistency
        ax.yaxis.set_major_locator(plt.MaxNLocator(nbins=4))
        ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.1f'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1,7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
    ax.set_xlim(pd.Timestamp('2021-07-01'), pd.Timestamp('2026-07-01'))
    ax.tick_params(axis='x', labelrotation=0, labelsize=20)
    ax.tick_params(axis='y', labelsize=19)
    for lbl in ax.get_xticklabels():
        lbl.set_ha('center')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # Thicken the visible spines so the bottom/left axis lines stay solid and
    # clearly visible at any display/preview scale (a thin 0.8pt default line
    # can visually vanish when a tall multi-panel figure like this one is
    # shrunk for on-screen preview, e.g. in panel c/pH).
    ax.spines['bottom'].set_linewidth(1.4)
    ax.spines['left'].set_linewidth(1.4)

axes[-1].set_xlabel('Month-Year', fontsize=18)

# Align all y-axis labels ("Temperature (°C)", "Salinity (PSU)", ...) to the
# same horizontal position, regardless of how wide each panel's own
# y-tick numbers are.
fig.align_ylabels(axes)

plt.savefig('Figure3_time_series.png', dpi=300, facecolor='white')
plt.savefig('Figure3_time_series.tiff', dpi=300, facecolor='white', pil_kwargs={'compression': 'tiff_lzw'})
print("done")
