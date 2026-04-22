import pandas as pd

# ── Config ─────────────────────────────────────────────────────────────────────

MAIN_PATH   = "data/world-education-data.csv"
ENROL_PATH  = "data/primary-secondary-enrollment-completion-rates.csv"

# Mapping from enrolment CSV columns -> main CSV columns
COL_MAP = {
    "Primary enrolment":   "school_enrol_primary_pct",
    "Secondary enrolment": "school_enrol_secondary_pct",
    "Tertiary enrolment":  "school_enrol_tertiary_pct",
    "Primary completion":  "pri_comp_rate_pct",
}

# ── Load ───────────────────────────────────────────────────────────────────────

main  = pd.read_csv(MAIN_PATH,  dtype={"numeric_code": str})
enrol = pd.read_csv(ENROL_PATH, dtype={"numeric_code": str})

main["numeric_code"]  = main["numeric_code"].str.zfill(3)
enrol["numeric_code"] = enrol["numeric_code"].str.zfill(3)

enrol = enrol.rename(columns={"Year": "year"})
enrol = enrol[enrol["year"] >= 1996]

# ── Add missing years ──────────────────────────────────────────────────────────

countries  = main[["country", "country_code", "numeric_code"]].drop_duplicates()
main_years = main[["numeric_code", "year"]].drop_duplicates()
enrol_years = enrol[["numeric_code", "year"]].drop_duplicates()

missing = enrol_years.merge(main_years, on=["numeric_code", "year"], how="left", indicator=True)
missing = missing[missing["_merge"] == "left_only"].drop(columns="_merge")

new_rows = missing.merge(countries, on="numeric_code", how="left")
new_rows = new_rows.reindex(columns=main.columns)

main = pd.concat([main, new_rows], ignore_index=True).sort_values(["country_code", "year"])

# ── Merge & fill ──────────────────────────────────────────────────────────────

enrol_slim = enrol[["numeric_code", "year"] + list(COL_MAP.keys())].copy()

main = main.merge(enrol_slim, on=["numeric_code", "year"], how="left")

total_filled = 0

for enrol_col, main_col in COL_MAP.items():
    mask = main[main_col].isna() & main[enrol_col].notna()
    filled = mask.sum()
    total_filled += filled
    main.loc[mask, main_col] = main.loc[mask, enrol_col]
    print(f"  ✓ {main_col}: filled {filled:,} nulls")

main = main.drop(columns=list(COL_MAP.keys()))

# ── Save ───────────────────────────────────────────────────────────────────────

main.to_csv(MAIN_PATH, index=False)

print(f"\n✓ Total filled: {total_filled:,}")
for main_col in COL_MAP.values():
    remaining = main[main_col].isna().sum()
    print(f"  Remaining nulls in '{main_col}': {remaining:,}")