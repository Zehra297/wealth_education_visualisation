import pandas as pd
import pycountry
import os

# ── Config ─────────────────────────────────────────────────────────────────────
# Add all your CSVs here with the name of their iso3 column

FILES = [
    {"path": "data/scimago_combined.csv",                        "iso3_col": "iso3"},
    {"path": "data/the_combined.csv",                            "iso3_col": "iso3"},
    {"path": "data/gdp-per-capita-worldbank.csv",                "iso3_col": "Code"},
    {"path": "data/gross-national-income-per-capita-worldbank.csv", "iso3_col": "Code"},
    {"path": "data/world-education-data.csv",                         "iso3_col": "country_code"},
]

# ── Lookup ─────────────────────────────────────────────────────────────────────

def get_numeric(iso3: str) -> str | None:
    if not isinstance(iso3, str) or iso3.strip() == "":
        return None
    try:
        country = pycountry.countries.get(alpha_3=iso3.strip())
        return country.numeric if country else None
    except Exception:
        return None

# ── Process ────────────────────────────────────────────────────────────────────

for file in FILES:
    fpath    = file["path"]
    iso3_col = file["iso3_col"]

    if not os.path.exists(fpath):
        print(f"  ⚠ File not found, skipping: {fpath}")
        continue

    df = pd.read_csv(fpath)

    if iso3_col not in df.columns:
        print(f"  ⚠ Column '{iso3_col}' not found in {fpath}, skipping")
        print(f"     Available columns: {df.columns.tolist()}")
        continue

    if "numeric_code" in df.columns:
        print(f"  ↩ numeric_code already exists in {fpath}, skipping")
        continue

    df["numeric_code"] = df[iso3_col].apply(get_numeric)

    matched   = df["numeric_code"].notna().sum()
    unmatched = df["numeric_code"].isna().sum()

    df.to_csv(fpath, index=False)

    print(f"  ✓ {os.path.basename(fpath)}")
    print(f"    matched: {matched:,}  |  unmatched: {unmatched:,}")
    if unmatched:
        missing = df.loc[df["numeric_code"].isna(), iso3_col].dropna().unique()
        print(f"    unmatched codes: {sorted(missing)}")

print("\n── Done ──────────────────────────────────────────────────────────────────")