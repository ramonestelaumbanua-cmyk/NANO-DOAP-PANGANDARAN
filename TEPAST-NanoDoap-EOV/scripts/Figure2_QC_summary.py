# -*- coding: utf-8 -*-
"""
Figure2_QC_summary.py
NANO-DOAP TEPAST -- Essential Ocean Variables, Pangandaran Bay

Reproduces Figure 2 (QA/QC summary): panel (a) shows per-record QC
status over time for each station-depth combination; panel (b) shows
record counts by QC code (QC=1 raw good, QC=5 short-gap corrected,
QC=6 climatology-substituted).
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Journal (Nature portfolio) figure requirements: sans-serif typeface,
# preferably Helvetica/Arial; Liberation Sans is a free, metrically
# Arial-compatible substitute available in this environment.
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Liberation Sans', 'Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['pdf.fonttype'] = 42  # embed as real text, not outlines
plt.rcParams['ps.fonttype'] = 42

df = pd.read_pickle('../data/eov_df_corrected.pkl')
df['Date'] = pd.to_datetime(df['Date'])

GREEN = '#009E73'
ORANGE = '#E69F00'
BLUE = '#0072B2'

combos = []
for st in [1,2,3]:
    for dep in [0,10,20]:
        combos.append((st,dep))
combo_to_row = {c: i for i,c in enumerate(combos)}
n_rows = len(combos)

df['row'] = df.apply(lambda r: combo_to_row[(r['Station'], r['Depth (m)'])], axis=1)
df['yplot'] = n_rows - 1 - df['row']

FIG_W, FIG_H = 13.79, 8.68
fig = plt.figure(figsize=(FIG_W, FIG_H), dpi=100)

LEFT, WIDTH = 0.075, 0.905

A_TOP_IN = 8.07
A_H_IN = 2.04
A_BOTTOM_IN = A_TOP_IN - A_H_IN
ax = fig.add_axes([LEFT, A_BOTTOM_IN/FIG_H, WIDTH, A_H_IN/FIG_H])

qc1 = df[df['QC Flag']==1]
qc5 = df[df['QC Flag']==5]
qc6 = df[df['QC Flag']==6]

ax.scatter(qc1['Date'], qc1['yplot'], c=GREEN, marker='o', s=50, edgecolors='black', linewidths=0.4, zorder=2)
ax.scatter(qc5['Date'], qc5['yplot'], c=ORANGE, marker='o', s=50, edgecolors='black', linewidths=0.4, zorder=3)
ax.scatter(qc6['Date'], qc6['yplot'], c=BLUE, marker='D', s=58, edgecolors='black', linewidths=0.4, zorder=4)

ax.set_ylim(-0.6, n_rows-1+0.6)
ax.set_yticks([])
ax.spines['top'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_position(('data', -0.6))
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.tick_params(axis='x', labelsize=17)

B_TOP_IN = 5.60
B_H_IN = 3.55
B_BOTTOM_IN = B_TOP_IN - B_H_IN
ax2 = fig.add_axes([LEFT, B_BOTTOM_IN/FIG_H, WIDTH-0.015, B_H_IN/FIG_H])

counts = [len(qc1), len(qc5), len(qc6)]
total = len(df)
labels = ['QC=1\n(raw good)', 'QC=5\n(short-gap corrected)', 'QC=6\n(climatology)']
colors = [GREEN, ORANGE, BLUE]
bars = ax2.bar(labels, counts, color=colors, width=0.6)
for b, c in zip(bars, counts):
    pct = c/total*100
    ax2.text(b.get_x()+b.get_width()/2, b.get_height()+8, f"{c}\n({pct:.1f}%)",
              ha='center', va='bottom', fontsize=17, fontweight='bold')
ax2.set_ylabel('Number of records', fontsize=17)
ax2.set_ylim(0, max(counts)*1.25)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.tick_params(axis='both', labelsize=16)

# --- panel labels placed with fig.text at an IDENTICAL absolute x (figure
# fraction) so 'a' and 'b' are left-aligned regardless of each axes' own
# left edge/width ---
LABEL_X = 0.012
fig.text(LABEL_X, (A_TOP_IN+0.28)/FIG_H, 'a', fontsize=26, fontweight='bold', va='top', ha='left')
fig.text(LABEL_X, (B_TOP_IN+0.28)/FIG_H, 'b', fontsize=26, fontweight='bold', va='top', ha='left')

plt.savefig('Figure2_QC_summary.png', dpi=300, facecolor='white')
plt.savefig('Figure2_QC_summary.tiff', dpi=300, facecolor='white', pil_kwargs={'compression': 'tiff_lzw'})
print("counts:", counts, "total:", total)
