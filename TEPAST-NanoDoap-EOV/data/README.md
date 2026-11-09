# Data folder

Data files are **not** tracked in this repository. Place the following files here
before running the figure scripts:

| File | Used by | Description |
|---|---|---|
| `eov_df_corrected.pkl` | Figures 2-6 | Corrected EOV table (pandas DataFrame, 468 records) after the QC correction step |
| `Transparency_final.xlsx` | Figures 3, 4, 6 | Secchi-depth transparency (header on row 3, `header=2`) |
| `TEPAST_NanoDoap_EOV_Dataset_Finalv4.xlsx` | `Syntax_QC_Correction_Pipeline.py` | Deposited EOV dataset (header on row 7, `header=6`) |

The deposited dataset is available from the repository cited in the Data Descriptor
(add DOI / link here).
