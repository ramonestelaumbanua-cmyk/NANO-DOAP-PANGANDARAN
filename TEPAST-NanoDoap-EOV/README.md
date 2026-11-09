# NANO-DOAP TEPAST: Essential Ocean Variables, Pangandaran Bay

Code accompanying the Data Descriptor for the NANO-DOAP TEPAST Essential Ocean
Variable (EOV) dataset collected in Pangandaran Bay (Station 1-3; 0, 10 and 20 m depth).
It contains (i) the QC correction pipeline and (ii) the scripts that reproduce the
manuscript figures.

> Data Descriptor: *add title / journal / DOI here*
> Dataset: *add repository link / DOI here*

## Repository structure

```
.
├── data/                                # input data (not tracked, see data/README.md)
├── scripts/
│   ├── Syntax_QC_Correction_Pipeline.py # QC Flag 5 -> 5/6 correction
│   ├── Figure2_QC_summary.py            # QA/QC summary
│   ├── Figure3_time_series.py           # monthly time series (boxplots by depth)
│   ├── Figure4_seasonal_climatology.py  # monthly climatology
│   ├── Figure5_boxplots.py              # boxplots by depth
│   ├── Figure6_frequency_distributions.py # histograms (EOVs + transparency)
│   └── run_all.py                       # run Figures 2-6 in one go
├── requirements.txt
├── LICENSE
└── README.md
```

## Installation

Tested with Python 3.10.

```bash
git clone https://github.com/<username>/TEPAST-NanoDoap-EOV.git
cd TEPAST-NanoDoap-EOV
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

The scripts use relative paths (`../data/...`), so **run them from inside `scripts/`**.

```bash
cd scripts

# Figures 2-6 (PNG + LZW-compressed TIFF, 300 dpi, saved in scripts/)
python run_all.py
# or one at a time
python Figure3_time_series.py

# QC correction validation against the deposited dataset
python Syntax_QC_Correction_Pipeline.py
```

For the pipeline script, put `TEPAST_NanoDoap_EOV_Dataset_Finalv4.xlsx` in the working
directory (or edit `INPUT_FILE`). To correct a new dataset, import and call
`run_qc_correction(df)`:

```python
import pandas as pd
from Syntax_QC_Correction_Pipeline import run_qc_correction

df_corrected, log = run_qc_correction(df)   # df: QC Flag = 5 for records to correct
```

## QC correction method (summary)

For each record with QC Flag = 5, the nearest valid (QC Flag = 1) measurements before
and after it at the same station-depth are located:

| Gap between valid records | Method | Resulting QC Flag |
|---|---|---|
| <= 31 days | Linear time interpolation | 5 |
| > 31 days (or no flanking record) | Climatology (station + depth + calendar month mean of QC = 1 records) | 6 |

For climatology-replaced records, DO saturation (mg/L and %) is recomputed with the
Weiss (1970) solubility relationship.

**Known limitation:** the QC Flag column in the export is a single combined DO/pH flag, so
the interpolation branch cannot be reproduced exactly from the export alone (7 records).
The climatology branch (75 QC = 6 records) is reproduced with 0 discrepancies. Details are
in the comments at the end of `Syntax_QC_Correction_Pipeline.py`.

## Figure notes

- Fonts: Liberation Sans (Arial-compatible) with fallback to Arial / Helvetica / DejaVu Sans.
  Text is embedded as real text in vector output (`pdf.fonttype = 42`).
- Figure 6, panel (d) (DO): `bins=15`, y-axis capped at 60 to match the published figure.

## Citation

```
<Authors> (2026). <Title>. <Journal>. <DOI>
```

## License

Code is released under the MIT License (see `LICENSE`). Check the data license separately.

## Contact

NANO-DOAP TEPAST Team, Universitas Padjadjaran. *add contact email here*
