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

df = pd.read_pickle('../data/eov_df_corrected.pkl')
trans = pd.read_excel('../data/Transparency_final.xlsx', sheet_name=0, header=2)

BLUE = '#1f77b4'
GOLD = '#E8A800'
TEAL = '#17A673'
DARKORANGE = '#D2560F'
BROWN = '#8B5A3C'
ORCHID = '#C77DC7'

# nbins and ylim per panel: panel 'd' (DO) uses bins=15 with ylim capped at 60
# to match the published Figure 6.
panels = [
    ('a', 'Temp (deg C)',   'Temperature (°C)', BLUE,       df,    12, None),
    ('b', 'Salinity (PSU)', 'Salinity (PSU)',    GOLD,       df,    14, None),
    ('c', 'Chl-a (mg m-3)', 'Chl-a (mg m⁻³)', TEAL, df,   14, None),
    ('d', 'DO (mg L-1)',    'DO (mg/L)',         DARKORANGE, df,    15, (0, 60)),
    ('e', 'pH (NBS)',       'pH (NBS)',          BROWN,      df,    12, None),
    ('f', 'Transparency (m)','Transparency (m)', ORCHID,     trans, 12, None),
]

fig, axes = plt.subplots(3, 2, figsize=(20.0, 17.6), dpi=300)
axes = axes.flatten()

for ax, (letter, col, xlabel, color, src, nbins, ylim) in zip(axes, panels):
    vals = src[col].dropna().values
    n = len(vals)
    mean = vals.mean()
    if ylim is not None:
        ax.hist(vals, bins=nbins, range=(vals.min(), vals.max()),
                 color=color, edgecolor='white', linewidth=0.6)
    else:
        ax.hist(vals, bins=nbins, color=color, edgecolor='white', linewidth=0.6)
    ax.axvline(mean, color='black', linestyle='--', linewidth=1.3, label=f'Mean = {mean:.2f}')
    ax.text(0.02, 0.93, f"N = {n}", transform=ax.transAxes, fontsize=11,
            bbox=dict(boxstyle='square', facecolor='white', edgecolor='black', linewidth=0.7))
    ax.legend(loc='upper right', fontsize=10, frameon=False)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title(f"({letter})", loc='left', fontsize=15, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if ylim is not None:
        ax.set_ylim(*ylim)

plt.tight_layout()
plt.savefig('Figure6_frequency_distributions.png', dpi=300, facecolor='white')
print("saved, panel d N=", len(df['DO (mg L-1)'].dropna()), "mean=", df['DO (mg L-1)'].dropna().mean())
