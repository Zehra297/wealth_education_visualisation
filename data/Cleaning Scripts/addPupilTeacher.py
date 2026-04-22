import pandas as pd

# ── Config ─────────────────────────────────────────────────────────────────────

MAIN_PATH  = "data/world-education-data.csv"
PTR_PATH   = "data/pupil-teacher-ratio-for-primary-education-by-country.csv"

MAIN_COL   = "pupil_teacher_primary"
PTR_COL    = "Pupil-qualified teacher ratio in primary education"

# ── Load ───────────────────────────────────────────────────────────────────────

main = pd.read_csv(MAIN_PATH, dtype={"numeric_code": str})
ptr  = pd.read_csv(PTR_PATH,  dtype={"numeric_code": str})

main["numeric_code"] = main["numeric_code"].str.zfill(3)
ptr["numeric_code"]  = ptr["numeric_code"].str.zfill(3)

ptr = ptr.rename(columns={"Year": "year"})
ptr = ptr[ptr["year"] >= 1996]

# ── Add missing years ──────────────────────────────────────────────────────────

countries  = main[["country", "country_code", "numeric_code"]].drop_duplicates()
main_years = main[["numeric_code", "year"]].drop_duplicates()
ptr_years  = ptr[["numeric_code", "year"]].drop_duplicates()

missing = ptr_years.merge(main_years, on=["numeric_code", "year"], how="left", indicator=True)
missing = missing[missing["_merge"] == "left_only"].drop(columns="_merge")

new_rows = missing.merge(countries, on="numeric_code", how="left")
new_rows = new_rows.reindex(columns=main.columns)

main = pd.concat([main, new_rows], ignore_index=True).sort_values(["country_code", "year"])

# ── Guard: drop rows with no country identifier ────────────────────────────────
before = len(main)
main = main[main["country_code"].notna() & (main["country_code"].str.strip() != "")]
main = main[main["numeric_code"].notna() & (main["numeric_code"].str.strip() != "")]
after = len(main)
if before - after:
    print(f"  ⚠ Dropped {before - after:,} rows with missing country identifiers")

# ── Merge & fill ──────────────────────────────────────────────────────────────

ptr_slim = ptr[["numeric_code", "year", PTR_COL]].copy()

main = main.merge(ptr_slim, on=["numeric_code", "year"], how="left")

mask = main[MAIN_COL].isna() & main[PTR_COL].notna()
filled = mask.sum()

main.loc[mask, MAIN_COL] = main.loc[mask, PTR_COL]
main = main.drop(columns=[PTR_COL])

# ── Save ───────────────────────────────────────────────────────────────────────

main.to_csv(MAIN_PATH, index=False)

print(f"✓ Filled {filled:,} nulls in '{MAIN_COL}'")
print(f"  Remaining nulls: {main[MAIN_COL].isna().sum():,}")