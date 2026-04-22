import pandas as pd

# ── Config ─────────────────────────────────────────────────────────────────────

MAIN_PATH   = "data/world-education-data.csv"
GOV_PATH    = "data/percent-gdp-education-wb.csv"

MAIN_COL    = "gov_exp_pct_gdp"

# ── Load ───────────────────────────────────────────────────────────────────────

main = pd.read_csv(MAIN_PATH, dtype={"numeric_code": str})
gov  = pd.read_csv(GOV_PATH,  dtype={"numeric_code": str})

main["numeric_code"] = main["numeric_code"].str.zfill(3)
gov["numeric_code"]  = gov["numeric_code"].str.zfill(3)

# ── Melt wide -> long ──────────────────────────────────────────────────────────

year_cols = [col for col in gov.columns if col.strip().isdigit()]

gov_long = gov.melt(
    id_vars=["numeric_code"],
    value_vars=year_cols,
    var_name="year",
    value_name="gov_exp_src"
)

gov_long["year"] = gov_long["year"].astype(int)
gov_long = gov_long[gov_long["year"] >= 1996]
gov_long = gov_long[gov_long["gov_exp_src"].notna()]

# ── Add missing years ──────────────────────────────────────────────────────────

countries   = main[["country", "country_code", "numeric_code"]].drop_duplicates()
main_years  = main[["numeric_code", "year"]].drop_duplicates()
gov_years   = gov_long[["numeric_code", "year"]].drop_duplicates()

missing = gov_years.merge(main_years, on=["numeric_code", "year"], how="left", indicator=True)
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

main = main.merge(gov_long, on=["numeric_code", "year"], how="left")

mask = main[MAIN_COL].isna() & main["gov_exp_src"].notna()
filled = mask.sum()

main.loc[mask, MAIN_COL] = main.loc[mask, "gov_exp_src"]
main = main.drop(columns=["gov_exp_src"])

# ── Save ───────────────────────────────────────────────────────────────────────

main.to_csv(MAIN_PATH, index=False)

print(f"✓ Filled {filled:,} nulls in '{MAIN_COL}'")
print(f"  Remaining nulls: {main[MAIN_COL].isna().sum():,}")