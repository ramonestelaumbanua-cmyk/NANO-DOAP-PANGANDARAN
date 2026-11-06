# -*- coding: utf-8 -*-
"""
================================================================================
 Syntax_QC_Correction_Pipeline.py
 NANO-DOAP TEPAST -- Essential Ocean Variables, Pangandaran Bay
================================================================================

PURPOSE
-------
This script reproduces the QC CORRECTION step (QC Flag 5 -> 5 or 6)
described in the "Interpolation method" section of the Data Descriptor:

  1. For each record already flagged QC Flag = 5 (the result of the
     Flag 1-4 anomaly detection described in the Data Quality Control
     section -- see SCOPE NOTE below), find the two nearest valid
     (QC Flag = 1) measurements at the same station-depth combination,
     one before and one after the flagged date.
  2. If the gap between those two valid measurements is <= 1 month
     (31 days), the value is replaced by LINEAR TIME INTERPOLATION and
     remains QC Flag = 5.
  3. If the gap is > 1 month, the value is replaced by CLIMATOLOGY --
     the mean of all QC=1 records at the same station, depth, and
     CALENDAR MONTH (pooled across years) -- and the QC Flag is
     changed to 6.
  4. For every record replaced by climatology, DO Saturation (mg/L and
     %) is recomputed from that record's temperature/salinity using
     the Weiss (1970) solubility relationship.

SCOPE NOTE
----------
This script reproduces the CORRECTION stage (the interpolation-vs-
climatology decision, the value replacement, and the DO Saturation
recomputation) -- this is the part that Reviewer #1 raised in the
round-2 revision, and the part re-validated in this revision (see the
VALIDATION block at the end of the file: 0 discrepancies against all
75 deposited QC=6 records -- 35 from the Flag 1/Flag 2 group and 40
from the Flag 4 group reclassified in this revision).

This script does NOT reproduce the initial anomaly-detection stage
(assigning Flag 1-4 from the raw instrument readings) -- it assumes
the QC Flag column is already set to 5 for records meeting the
following criteria, exactly as described in the "Data Quality
Control" section of the manuscript:

    Flag 1: DO < 4.0 mg/L together with pH > 7.8
    Flag 2: O2 saturation < 60% (Garcia & Gordon, 1992)
    Flag 3: Very low pH at the start of the campaign (identified
            manually, 2 specific records: 19 Sep 2021, Station 1,
            0 m & 10 m)
    Flag 4: DO > 8.0 mg/L (upper literature bound for Indonesian
            coastal waters)

If a raw (pre-flagging) reading file is available and the QC Flag
column has not yet been populated, the detection stage above needs to
be implemented separately before running this script.

INPUT
-----
An Excel file (or pandas DataFrame) with at least the following
columns, one row per station-depth-date combination:

    No., Date, Station, Depth (m), Temp (deg C), Salinity (PSU),
    DO (mg L-1), pH (NBS), DO Sat (mg L-1), DO Sat (%), QC Flag

Records requiring correction must already be flagged QC Flag = 5.
QC Flag = 1 (valid) records are used as the reference pool for both
interpolation and climatology.

OUTPUT
------
The same table, where every record originally QC Flag = 5 has:
  - QC Flag reclassified to 5 (interpolation, gap <= 1 month) or
    6 (climatology, gap > 1 month)
  - DO (mg L-1) [and/or pH (NBS), see the `columns_to_correct`
    parameter] replaced according to the selected method
  - DO Sat (mg L-1) and DO Sat (%) recomputed for QC=6 records

Authors: NANO-DOAP TEPAST Team, Universitas Padjadjaran
Last updated: November 2026 (Scientific Data round 2 revision)
================================================================================
"""

import numpy as np
import pandas as pd

# -----------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------
MAX_INTERPOLATION_GAP_DAYS = 31     # "one month" as defined in the manuscript
COLUMNS_TO_CORRECT = ["DO (mg L-1)"]  # add "pH (NBS)" if relevant


# -----------------------------------------------------------------------
# 1. Weiss (1970) oxygen solubility relationship
# -----------------------------------------------------------------------
def weiss_1970_o2_saturation(temp_c, salinity_psu):
    """
    DO Saturation (mg/L) as a function of Temperature (deg C) and
    Salinity (PSU), following Weiss, R. F. (1970). "The solubility of
    nitrogen, oxygen and argon in water and seawater."
    Deep-Sea Res. 17, 721-735. https://doi.org/10.1016/0011-7471(70)90037-9

    Validated against the 468 deposited EOV dataset records: maximum
    absolute difference of 0.02 mg/L from the existing "DO Sat (mg L-1)"
    column (see the VALIDATION block at the end of the file).
    """
    theta = (temp_c + 273.15) / 100.0
    ln_c_star = (
        -173.4292
        + 249.6339 / theta
        + 143.3483 * np.log(theta)
        - 21.8492 * theta
        + salinity_psu * (-0.033096 + 0.014259 * theta - 0.001700 * theta**2)
    )
    # 1.4276 mg/mL converts from mL O2/L (Weiss 1970's original unit) to mg/L
    return 1.4276 * np.exp(ln_c_star)


# -----------------------------------------------------------------------
# 2. Linear time interpolation (two nearest valid measurements)
# -----------------------------------------------------------------------
def find_flanking_valid(df, station, depth, flagged_date, value_col,
                         date_col="Date", station_col="Station",
                         depth_col="Depth (m)", qc_col="QC Flag"):
    """Find the nearest QC=1 records before & after flagged_date, at the
    same station-depth combination. Returns
    (prev_row, next_row, gap_days) -- either can be None if not found."""
    sub = df[
        (df[station_col] == station)
        & (df[depth_col] == depth)
        & (df[qc_col] == 1)
    ].sort_values(date_col)

    before = sub[sub[date_col] < flagged_date]
    after = sub[sub[date_col] > flagged_date]

    prev_row = before.iloc[-1] if len(before) else None
    next_row = after.iloc[0] if len(after) else None

    gap_days = None
    if prev_row is not None and next_row is not None:
        gap_days = (next_row[date_col] - prev_row[date_col]).days

    return prev_row, next_row, gap_days


def linear_interpolate_value(prev_row, next_row, flagged_date, value_col,
                              date_col="Date"):
    """V(t) = V0 + (V1 - V0) * (t - t0) / (t1 - t0)"""
    t0, t1 = prev_row[date_col], next_row[date_col]
    v0, v1 = prev_row[value_col], next_row[value_col]
    t = flagged_date
    frac = (t - t0).total_seconds() / (t1 - t0).total_seconds()
    return v0 + (v1 - v0) * frac


# -----------------------------------------------------------------------
# 3. Station-depth-calendar-month climatology
# -----------------------------------------------------------------------
def climatology_value(df, station, depth, month, value_col,
                       station_col="Station", depth_col="Depth (m)",
                       month_col="_Month", qc_col="QC Flag"):
    """Mean of QC=1 records at the same station, depth, and calendar
    month, pooled across all years in the study period. Returns
    (mean_value, n_reference_years)."""
    sub = df[
        (df[station_col] == station)
        & (df[depth_col] == depth)
        & (df[month_col] == month)
        & (df[qc_col] == 1)
    ]
    if len(sub) == 0:
        return None, 0
    n_years = sub["_Year"].nunique()
    return sub[value_col].mean(), n_years


# -----------------------------------------------------------------------
# 4. Main pipeline
# -----------------------------------------------------------------------
def run_qc_correction(df, columns_to_correct=COLUMNS_TO_CORRECT,
                       max_gap_days=MAX_INTERPOLATION_GAP_DAYS,
                       date_col="Date", station_col="Station",
                       depth_col="Depth (m)", qc_col="QC Flag",
                       do_col="DO (mg L-1)",
                       do_sat_mgl_col="DO Sat (mg L-1)",
                       do_sat_pct_col="DO Sat (%)",
                       temp_col="Temp (deg C)", sal_col="Salinity (PSU)"):
    """Run the QC=5 -> {5, 6} correction over the whole dataframe. Returns
    (df_corrected, correction_log) -- the log holds one row per corrected
    record, with the method used, old/new value, gap, and (for
    climatology) the number of reference years."""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df["_Month"] = df[date_col].dt.month
    df["_Year"] = df[date_col].dt.year

    log_rows = []
    to_correct = df[df[qc_col] == 5].copy()

    for idx, row in to_correct.iterrows():
        station, depth = row[station_col], row[depth_col]
        flagged_date, month = row[date_col], row["_Month"]

        prev_row, next_row, gap_days = find_flanking_valid(
            df, station, depth, flagged_date, columns_to_correct[0],
            date_col, station_col, depth_col, qc_col,
        )

        use_climatology = (
            gap_days is None or gap_days > max_gap_days
        )

        for col in columns_to_correct:
            old_value = df.at[idx, col]

            if not use_climatology:
                new_value = linear_interpolate_value(
                    prev_row, next_row, flagged_date, col, date_col
                )
                method = "interpolation"
                n_ref_years = None
            else:
                new_value, n_ref_years = climatology_value(
                    df, station, depth, month, col
                )
                method = "climatology"

            df.at[idx, col] = new_value
            log_rows.append({
                "No.": row.get("No."), "Date": flagged_date, "Station": station,
                "Depth (m)": depth, "Column": col, "Method": method,
                "Gap_days": gap_days, "Old_value": old_value,
                "New_value": new_value, "N_reference_years": n_ref_years,
            })

        # QC flag & DO-saturation recompute happen once per record,
        # after all requested columns are corrected
        df.at[idx, qc_col] = 6 if use_climatology else 5

        if use_climatology and do_col in columns_to_correct:
            new_do_sat_mgl = weiss_1970_o2_saturation(
                df.at[idx, temp_col], df.at[idx, sal_col]
            )
            df.at[idx, do_sat_mgl_col] = round(new_do_sat_mgl, 3)
            df.at[idx, do_sat_pct_col] = round(
                df.at[idx, do_col] / new_do_sat_mgl * 100, 1
            )

    df = df.drop(columns=["_Month", "_Year"])
    correction_log = pd.DataFrame(log_rows)
    return df, correction_log


# =========================================================================
# KNOWN LIMITATION
# =========================================================================
# The "QC Flag" column in this export is a SINGLE combined flag for DO
# and pH -- a record is marked QC Flag=5 if EITHER DO or pH was
# flagged, not each independently. As a result, when
# run_qc_correction() searches for the "nearest valid DO measurement"
# using the QC Flag==1 filter, dates where DO was actually valid but
# pH was flagged (or vice versa) are excluded from the reference pool
# -- the gap computed for DO can appear longer than the true DO gap.
#
# Effect: of the 7 records deposited as QC=5 (interpolation, the
# "green italic" group / Flag 1, 1+2, 2 & 3), running this pipeline on
# the combined QC Flag column classifies all 7 as climatology (because
# the DO gap, computed from the combined column, is >1 month or there
# is no "before" record at all at the start of the campaign). The
# QC=5 values actually deposited for these 7 records (No. 1, 2, 183,
# 186, 189, 334, 342) were determined using the per-parameter QC
# status (DO vs pH tracked separately) from the internal working file,
# which is NOT included in this export file -- so they cannot be
# reproduced exactly from this file alone.
#
# The CLIMATOLOGY branch of this pipeline (used for the 75 deposited
# QC=6 records, including the 40 Flag 4 records that are the main
# focus of this revision) is NOT affected by the limitation above --
# Flag 4 records are flagged purely on DO (DO>8.0 mg/L), and the
# validation below confirms 0 discrepancies against all 75 deposited
# QC=6 records.
#
# If a working file with per-parameter QC status becomes available,
# replace the QC Flag==1 filter in find_flanking_valid() and
# climatology_value() with the matching per-column filter so the
# interpolation branch can also be reproduced exactly.
# =========================================================================


# =========================================================================
# VALIDATION -- run against the deposited dataset to verify that this
# pipeline reproduces the same values
# =========================================================================
if __name__ == "__main__":
    INPUT_FILE = "TEPAST_NanoDoap_EOV_Dataset_Finalv4.xlsx"
    SHEET_NAME = 0
    HEADER_ROW = 6   # header row in the v4 file (0-indexed, after the legend)

    print(f"Reading {INPUT_FILE} ...")
    df_final = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME, header=HEADER_ROW)

    # For validation: rather than "rolling back" QC=6 records to QC=5
    # with their old values (not available in the final file), this is
    # a structural check -- it verifies that re-running the climatology
    # calculation on the existing QC=1 data reproduces an identical
    # value to the current "DO (mg L-1)" column for every QC=6 record.
    df_final["Date"] = pd.to_datetime(df_final["Date"])
    df_final["_Month"] = df_final["Date"].dt.month
    df_final["_Year"] = df_final["Date"].dt.year

    qc6 = df_final[df_final["QC Flag"] == 6]
    mismatches = 0
    for idx, row in qc6.iterrows():
        clim_val, n_years = climatology_value(
            df_final, row["Station"], row["Depth (m)"], row["_Month"],
            "DO (mg L-1)",
        )
        if not np.isclose(clim_val, row["DO (mg L-1)"], atol=0.01):
            mismatches += 1
            print(f"  MISMATCH No.{row['No.']}: stored={row['DO (mg L-1)']}, "
                  f"recomputed={clim_val:.4f}")

    print(f"Climatology validation: {mismatches} discrepancies out of "
          f"{len(qc6)} QC=6 records.")

    # Validate the Weiss (1970) relationship against all 468 records
    do_sat_calc = weiss_1970_o2_saturation(
        df_final["Temp (deg C)"], df_final["Salinity (PSU)"]
    )
    diff = (do_sat_calc - df_final["DO Sat (mg L-1)"]).abs()
    print(f"Weiss (1970) DO Sat (mg/L) validation: maximum absolute "
          f"difference = {diff.max():.4f} mg/L (mean {diff.mean():.4f} mg/L) "
          f"against {len(df_final)} records.")

    print("\nDone. To run the full correction on a dataset whose QC=5 "
          "records have not yet been corrected, call run_qc_correction(df) "
          "with a dataframe whose QC Flag column still reads 5 for the "
          "records needing correction.")
