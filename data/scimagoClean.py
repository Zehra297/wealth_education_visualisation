import pandas as pd
import glob
import os
import pycountry

# ── Config ────────────────────────────────────────────────────────────────────

INPUT_FOLDER  = "data/Scimago"
OUTPUT_FILE   = "data/scimago_combined.csv"

# Manual overrides for country names pycountry can't fuzzy-match
COUNTRY_OVERRIDES = {
    "United States":              "USA",
    "United Kingdom":             "GBR",
    "Russia":                     "RUS",
    "South Korea":                "KOR",
    "Republic of Korea":          "KOR",
    "Iran":                       "IRN",
    "Taiwan":                     "TWN",
    "Hong Kong":                  "HKG",
    "Syria":                      "SYR",
    "Tanzania":                   "TZA",
    "Bolivia":                    "BOL",
    "Venezuela":                  "VEN",
    "Vietnam":                    "VNM",
    "Laos":                       "LAO",
    "Moldova":                    "MDA",
    "Macedonia":                  "MKD",
    "Palestine":                  "PSE",
    "Brunei":                     "BRN",
    "Trinidad and Tobago":        "TTO",
    "Bosnia and Herzegovina":     "BIH",
    "Czech Republic":             "CZE",
    "Slovakia":                   "SVK",
    "Cape Verde":              "CPV",
    "Côte d'Ivoire":           "CIV",
    "Democratic Republic Congo": "COD",
    "Netherlands Antilles":    "ANT",
    "Saint Martin (Dutch)":    "SXM",
    "Saint Martin (French)":   "MAF",
    "Turkey":                  "TUR",
    "Virgin Islands (British)":"VGB",
    "Virgin Islands (U.S.)":   "VIR",
}

# ── ISO lookup ─────────────────────────────────────────────────────────────────

def get_iso3(name: str) -> str | None:
    """Return ISO 3166-1 alpha-3 code for a country name string."""
    if name in COUNTRY_OVERRIDES:
        return COUNTRY_OVERRIDES[name]
    try:
        return pycountry.countries.search_fuzzy(name)[0].alpha_3
    except LookupError:
        return None

# ── Load and combine ───────────────────────────────────────────────────────────

def load_scimago_file(filepath: str) -> pd.DataFrame:
    """Load a single SCImago CSV, extract year from filename, normalise columns."""

    # Extract year from filename e.g. "all subject areas - 2012.csv"
    basename = os.path.basename(filepath)
    year = int(basename.replace("all subject areas - ", "").replace(".csv", "").strip())

    # SCImago uses semicolons as delimiters
    df = pd.read_csv(filepath, sep=",")

    # Normalise column names: lowercase, replace spaces with underscores
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )

    # Rename to consistent internal names
    df = df.rename(columns={
        "rank":                   "rank",
        "country":                "country",
        "region":                 "region",
        "documents":              "documents",
        "citable_documents":      "citable_documents",
        "citations":              "citations",
        "self-citations":         "self_citations",
        "citations_per_document": "citations_per_document",
        "h_index":                "h_index",
    })

    df["year"] = year
    return df


def combine_all(folder: str) -> pd.DataFrame:
    pattern = os.path.join(folder, "all subject areas - *.csv")
    files   = sorted(glob.glob(pattern))

    if not files:
        raise FileNotFoundError(f"No SCImago CSVs found in: {folder}")


    print(f"Found {len(files)} files ({os.path.basename(files[0])} → {os.path.basename(files[-1])})")

    dfs = [load_scimago_file(f) for f in files]
    return pd.concat(dfs, ignore_index=True)

# ── Clean ──────────────────────────────────────────────────────────────────────

def clean(df: pd.DataFrame) -> pd.DataFrame:

    # Cast numeric columns — coerce errors to NaN
    numeric_cols = [
        "rank", "documents", "citable_documents",
        "citations", "self_citations", "citations_per_document", "h_index"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Add ISO3 codes
    print("Adding ISO3 codes...")
    unique_countries = df["country"].dropna().unique()
    iso_map = {name: get_iso3(name) for name in unique_countries}

    # Report anything we couldn't match
    unmatched = [k for k, v in iso_map.items() if v is None]
    if unmatched:
        print(f"\n  ⚠ Could not find ISO3 for {len(unmatched)} countries — add to COUNTRY_OVERRIDES:")
        for name in sorted(unmatched):
            print(f"      \"{name}\": \"???\",")
        print()

    df["iso3"] = df["country"].map(iso_map)

    # Drop region — already in GDP/OWID data
    df = df.drop(columns=["region"], errors="ignore")

    # Drop self_citations and citable_documents (not needed for visualisation)
    df = df.drop(columns=["self_citations", "citable_documents"], errors="ignore")

    # Reorder columns cleanly
    col_order = [
        "year", "rank", "country", "iso3",
        "documents", "citations", "citations_per_document", "h_index"
    ]
    df = df[[c for c in col_order if c in df.columns]]

    # Sort
    df = df.sort_values(["year", "rank"]).reset_index(drop=True)

    return df

# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("── Loading SCImago files ─────────────────────────────")
    raw = combine_all(INPUT_FOLDER)
    print(f"Loaded {len(raw):,} rows across {raw['year'].nunique()} years\n")

    print("── Cleaning ──────────────────────────────────────────")
    cleaned = clean(raw)

    print("\n── Summary ───────────────────────────────────────────")
    print(f"  Rows:      {len(cleaned):,}")
    print(f"  Years:     {cleaned['year'].min()} – {cleaned['year'].max()}")
    print(f"  Countries: {cleaned['country'].nunique()}")
    null_iso = cleaned['iso3'].isna().sum()
    if null_iso:
        print(f"  ⚠ Rows with no ISO3: {null_iso} (these will not plot on the map)")
    else:
        print(f"  ✓ All countries matched to ISO3")

    print("\n── Sample output ─────────────────────────────────────")
    print(cleaned.head(10).to_string(index=False))

    print(f"\n── Saving to {OUTPUT_FILE} ───────────────────────────")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    cleaned.to_csv(OUTPUT_FILE, index=False)
    print("  ✓ Done")