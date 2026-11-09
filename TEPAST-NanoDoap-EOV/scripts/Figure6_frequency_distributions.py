# -*- coding: utf-8 -*-
"""
Figure6_frequency_distributions.py
NANO-DOAP TEPAST -- Essential Ocean Variables, Pangandaran Bay

Reproduces Figure 6 (frequency-distribution histograms for the five
EOVs plus Secchi-depth transparency) from the corrected EOV dataset.

Panel (d), DO (mg/L), uses bins=15 over the data range with the
y-axis capped at 60; this matches the published figure.
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
trans = pd.read_excel('../data/Transparency_final.xlsx', sheet_name=0, header=2)

BLUE = '#1f77b4'
GOLD = '#E8A800'
TEAL = '#17A673'
DARKORANGE = '#D2560F'
BROWN = '#8B5A3C'
ORCHID = '#C77DC7'

# Note: unicode superscript/subscript minus (U+207B) is missing from the
# Liberation Sans glyph table, so Chl-a/DO units use matplotlib mathtext
# ($^{-3}$, $^{-1}$) instead of the unicode "⁻³"/"⁻¹" characters -- the same
# fix already applied in Figures 3-5.
# nbins and ylim per panel: panel 'd' (DO) uses bins=15 with ylim capped at 60
# to match the published Figure 6.
panels = [
    ('a', 'Temperature', 'Temp (deg C)', 'Temperature (°C)', BLUE, df, 12, None),
    ('b', 'Salinity', 'Salinity (PSU)', 'Salinity (PSU)', GOLD, df, 14, None),
    ('c', 'Chlorophyll-a', 'Chl-a (mg m-3)', 'Chl-a (mg m$^{-3}$)', TEAL, df, 14, None),
    ('d', 'Dissolved Oxygen', 'DO (mg L-1)', 'DO (mg L$^{-1}$)', DARKORANGE, df, 15, (0, 60)),
    ('e', 'pH (NBS)', 'pH (NBS)', 'pH (NBS)', BROWN, df, 12, None),
    ('f', 'Transparency', 'Transparency (m)', 'Transparency (m)', ORCHID, trans, 12, None),
]

fig, axes = plt.subplots(3, 2, figsize=(20.0, 21.5), dpi=100)
fig.subplots_adjust(left=0.07, right=0.98, top=0.965, bottom=0.04, hspace=0.46, wspace=0.24)
axes = axes.flatten()

for ax, (letter, title, col, xlabel, color, src, nbins, ylim) in zip(axes, panels):
    vals = src[col].dropna().values
    n = len(vals)
    mean = vals.mean()
    if ylim is not None:
        ax.hist(vals, bins=nbins, range=(vals.min(), vals.max()),
                 color=color, edgecolor='white', linewidth=0.6)
    else:
        ax.hist(vals, bins=nbins, color=color, edgecolor='white', linewidth=0.6)
    ax.axvline(mean, color='black', linestyle='--', linewidth=2.0, label=f'Mean = {mean:.2f}')
    ax.text(0.02, 0.93, f"N = {n}", transform=ax.transAxes, fontsize=20, va='top',
            bbox=dict(boxstyle='square,pad=0.3', facecolor='white', edgecolor='black', linewidth=1.0))
    ax.legend(loc='upper right', fontsize=18, frameon=True, facecolor='white',
              framealpha=1.0, edgecolor='black', borderpad=0.4)
    ax.set_xlabel(xlabel, fontsize=24)
    ax.set_ylabel('Frequency', fontsize=24)
    ax.set_title(f"({letter}) {title}", loc='left', fontsize=27, fontweight='bold')
    # Bigger, thicker tick marks (default length/width are too thin to read
    # clearly) in addition to bigger tick-label text.
    ax.tick_params(axis='both', which='major', labelsize=22, length=9, width=1.6)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_linewidth(1.6)
    ax.spines['left'].set_linewidth(1.6)
    if ylim is not None:
        ax.set_ylim(*ylim)

plt.savefig('Figure6_frequency_distributions.png', dpi=300, facecolor='white')
plt.savefig('Figure6_frequency_distributions.tiff', dpi=300, facecolor='white', pil_kwargs={'compression': 'tiff_lzw'})
print("saved, panel d N=", len(df['DO (mg L-1)'].dropna()), "mean=", df['DO (mg L-1)'].dropna().mean())
