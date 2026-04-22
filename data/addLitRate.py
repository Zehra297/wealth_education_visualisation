import pandas as pd
import os

# ── Config ─────────────────────────────────────────────────────────────────────

MAIN_PATH    = "data/world-education-data.csv"
LIT_PATH     = "data/literacy-rates-among-adults.csv"

MAIN_COL     = "lit_rate_adult_pct"
LIT_COL      = "Literacy rate among adults"

JOIN_KEYS    = ["numeric_code", "year"]   # main dataset join keys
LIT_KEYS     = ["numeric_code", "Year"]   # literacy dataset join keys (note capital Y)

# ── Load ───────────────────────────────────────────────────────────────────────

main = pd.read_csv(MAIN_PATH, dtype={"numeric_code": str})
lit  = pd.read_csv(LIT_PATH,  dtype={"numeric_code": str})

# Normalise the year column name so both DataFrames share the same key name
lit = lit.rename(columns={"Year": "year"})
lit = lit[lit["year"] >= 1996]

main["numeric_code"] = main["numeric_code"].astype(str).str.zfill(3)
lit["numeric_code"]  = lit["numeric_code"].astype(str).str.zfill(3)

# ── Add missing years ──────────────────────────────────────────────────────────

# Get all country identifiers from main
countries = main[["country", "country_code", "numeric_code"]].drop_duplicates()

# Get the years present in lit that are missing from main (per country)
main_years = main[["numeric_code", "year"]].drop_duplicates()
lit_years  = lit[["numeric_code", "year"]].drop_duplicates()

missing = lit_years.merge(main_years, on=["numeric_code", "year"], how="left", indicator=True)
missing = missing[missing["_merge"] == "left_only"].drop(columns="_merge")

# Build new rows with only the key columns filled, everything else null
new_rows = missing.merge(countries, on="numeric_code", how="left")
new_rows = new_rows.reindex(columns=main.columns)  # match column order, nulls for the rest

main = pd.concat([main, new_rows], ignore_index=True).sort_values(["country_code", "year"])
# ── Merge & fill ──────────────────────────────────────────────────────────────

lit_slim = lit[["numeric_code", "year", LIT_COL]].copy()

main = main.merge(lit_slim, on=["numeric_code", "year"], how="left")

# Only fill where the main value is null
mask = main[MAIN_COL].isna() & main[LIT_COL].notna()
filled = mask.sum()

main.loc[mask, MAIN_COL] = main.loc[mask, LIT_COL]
main = main.drop(columns=[LIT_COL])

# ── Save ───────────────────────────────────────────────────────────────────────

main.to_csv(MAIN_PATH, index=False)

print(f"✓ Filled {filled:,} null values in '{MAIN_COL}' from literacy dataset")

null_remaining = main[MAIN_COL].isna().sum()
print(f"  Remaining nulls in '{MAIN_COL}': {null_remaining:,}")