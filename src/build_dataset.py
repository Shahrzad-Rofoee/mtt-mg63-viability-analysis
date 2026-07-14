import pandas as pd

# ------------------------------------------------------------------
# Data source: MTT assay results from a cell-culture laboratory,
# part of an M.Sc. thesis on surface coating of 316L stainless steel
# with electrospun TiO2 and TiO2/Sr nanofibers (single-nozzle and
# dual-nozzle configurations).
#
# MG-63 osteoblast-like cells were cultured on four surface groups:
#   - control: cells cultured directly on tissue-culture polystyrene
#              (TCP), no metal substrate
#   - TiO2:    316L stainless steel coated with TiO2 nanofibers
#   - SN:      316L coated with TiO2/Sr nanofibers, single-nozzle
#              electrospinning
#   - DN:      316L coated with TiO2/Sr nanofibers, dual-nozzle
#              electrospinning
#
# Raw absorbance values (OD 570 nm) were provided directly by the
# laboratory, with no modification.
# ------------------------------------------------------------------

# Read the entire sheet with no header row, since the raw file does
# not have a clean, standard header structure
raw = pd.read_excel("data/rofoee.xlsx", sheet_name="Sheet1", header=None)

# Column positions of each group in the raw Excel sheet (0-indexed),
# separately for Day 1 and Day 3, based on manual inspection of the
# original file (see comments above for the column letters)
day1_columns = {
    "control": 2,   # Excel column C
    "DN": 3,        # Excel column D
    "SN": 4,        # Excel column E
    "TiO2": 7,      # Excel column H
}

day3_columns = {
    "control": 12,  # Excel column M
    "DN": 13,       # Excel column N
    "SN": 14,       # Excel column O
    "TiO2": 17,     # Excel column R
}

# Raw replicate values are located in Excel rows 3 to 6,
# which correspond to 0-indexed rows 2 to 5
replicate_rows = [2, 3, 4, 5]

# Build a tidy (long-format) table: one row per single measurement
records = []

for day, columns in [(1, day1_columns), (3, day3_columns)]:
    for group, col_index in columns.items():
        for rep_number, row_index in enumerate(replicate_rows, start=1):
            value = raw.iloc[row_index, col_index]
            records.append({
                "day": day,
                "group": group,
                "replicate": rep_number,
                "absorbance": value,
            })

tidy_df = pd.DataFrame(records)

# Display the full tidy dataset to check that all 32 values look correct
print(tidy_df)
print(f"\nTotal number of rows: {len(tidy_df)} (expected: 32)")
# Save the tidy dataset to a CSV file for use in later analysis steps
tidy_df.to_csv("data/mtt_tidy.csv", index=False)
print("\nSaved tidy dataset to data/mtt_tidy.csv")