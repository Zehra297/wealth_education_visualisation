import pandas as pd
import glob
import os
import re
import time
import pycountry
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# ── Config ─────────────────────────────────────────────────────────────────────

INPUT_FOLDER  = "data/THE Rankings 2011-2024"
OUTPUT_FILE   = "data/the_combined.csv"
GEOCODE_CACHE = "data/the_geocode_cache.csv"  # saves progress so you can resume

TOP_N         = 200   # only keep top N per year
GEOCODE_DELAY = 1.5   # seconds between Nominatim requests (be polite)

# ── Country name overrides ─────────────────────────────────────────────────────

COUNTRY_OVERRIDES = {
    "United States":                "USA",
    "United Kingdom":               "GBR",
    "Russia":                       "RUS",
    "South Korea":                  "KOR",
    "Republic of Korea":            "KOR",
    "Iran":                         "IRN",
    "Taiwan":                       "TWN",
    "Hong Kong":                    "HKG",
    "Syria":                        "SYR",
    "Tanzania":                     "TZA",
    "Bolivia":                      "BOL",
    "Venezuela":                    "VEN",
    "Vietnam":                      "VNM",
    "Laos":                         "LAO",
    "Moldova":                      "MDA",
    "Macedonia":                    "MKD",
    "Palestine":                    "PSE",
    "Brunei":                       "BRN",
    "Trinidad and Tobago":          "TTO",
    "Bosnia and Herzegovina":       "BIH",
    "Czech Republic":               "CZE",
    "Slovakia":                     "SVK",
    "Turkey":                       "TUR",
    "Mainland China":               "CHN",
    "Macao":                        "MAC",
}

GEOCODE_OVERRIDES = {
    "Pohang University of Science and Technology (POSTECH)":
        (36.0140, 129.3224),
    "University of Illinois at Urbana-Champaign":
        (40.1020, -88.2272),
    "University of Göttingen":
        (51.5586, 9.9294),
    "Ohio State University (Main campus)":
        (40.0076, -83.0300),
    "University of Virginia (Main campus)":
        (38.0336, -78.5080),
    "Korea Advanced Institute of Science and Technology (KAIST)":
        (36.3741, 127.3600),
    "Royal Holloway, University of London":
        (51.4254, -0.5660),
    "Pierre and Marie Curie University":
        (48.8481, 2.3567),
    "University of Würzburg":
        (49.7816, 9.9726),
    "Free University of Berlin":
        (52.4536, 13.2955),
    "Paris Diderot University – Paris 7":
        (48.8277, 2.3814),
    "Joseph Fourier University":
        (45.1933, 5.7680),
    "University of Erlangen-Nuremberg":
        (49.5975, 11.0045),
    "Technical University of Berlin":
        (52.5122, 13.3267),
    "Paris Sciences et Lettres – PSL Research University Paris":
        (48.8502, 2.3445),
    "Yonsei University (Seoul campus)":
        (37.5665, 126.9388),
    "Sapienza University of Rome":
        (41.9038, 12.5152),
    "Penn State (Main campus)":
        (40.7982, -77.8599),
}

# ── ISO lookup ─────────────────────────────────────────────────────────────────

def get_iso3(name: str) -> str | None:
    if not isinstance(name, str):
        return None
    name = name.strip()
    if name in COUNTRY_OVERRIDES:
        return COUNTRY_OVERRIDES[name]
    try:
        return pycountry.countries.search_fuzzy(name)[0].alpha_3
    except LookupError:
        return None

# ── Rank parsing ───────────────────────────────────────────────────────────────

def parse_rank(val) -> int | None:
    """
    THE ranks can be:
      - plain integers:  "1", "42"
      - range strings:   "201-250", "1001+"
      - reporter:        "Reporter", "n/a"
    Returns the lower bound as an integer, or None if unparseable.
    """
    if pd.isna(val):
        return None
    s = str(val).strip()
    if re.match(r"^\d+$", s):
        return int(s)
    m = re.match(r"^(\d+)", s)   # take first number from ranges like "201-250"
    if m:
        return int(m.group(1))
    return None  # "Reporter", "n/a", etc.

def parse_score(val) -> float | None:
    """Scores can be numeric, empty, or 'n/a' / 'Reporter'."""
    if pd.isna(val):
        return None
    s = str(val).strip().lower()
    if s in ("", "n/a", "reporter", "–", "-"):
        return None
    try:
        return float(s)
    except ValueError:
        return None

# ── Load and combine ───────────────────────────────────────────────────────────

def load_the_file(filepath: str) -> pd.DataFrame:
    """Load one THE CSV, extract year from filename, normalise columns."""

    # Extract year — handles "THE Rankings 2015.csv", "2015.csv", "the_2015.csv" etc.
    basename = os.path.basename(filepath)
    year_match = re.search(r"(20\d{2})", basename)
    if not year_match:
        print(f"  ⚠ Could not extract year from: {basename}, skipping")
        return pd.DataFrame()
    year = int(year_match.group(1))

    df = pd.read_csv(filepath, encoding="utf-8", on_bad_lines="skip")

    # Normalise column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )

    df["year"] = year
    return df


def combine_all(folder: str) -> pd.DataFrame:
    pattern = os.path.join(folder, "*.csv")
    files   = sorted(glob.glob(pattern))

    if not files:
        raise FileNotFoundError(f"No CSVs found in: {folder}")

    print(f"Found {len(files)} files")

    dfs = []
    for f in files:
        df = load_the_file(f)
        if not df.empty:
            print(f"  Loaded {os.path.basename(f)}: {len(df)} rows, columns: {df.columns.tolist()}")
            dfs.append(df)

    return pd.concat(dfs, ignore_index=True)

# ── Clean ──────────────────────────────────────────────────────────────────────

def clean(df: pd.DataFrame) -> pd.DataFrame:

    # ── Standardise key column names across years ──
    # THE has renamed columns across years — map all variants to one name
    rename_map = {
        "name":                              "name",
        "university_name":                   "name",
        "institution":                       "name",
        "institution_name":                  "name",
        "location":                          "country",
        "country":                           "country",
        "rank":                              "rank",
        "scores_overall":                    "score_overall",
        "overall":                           "score_overall",
        "scores_teaching":                   "score_teaching",
        "teaching":                          "score_teaching",
        "scores_research":                   "score_research",
        "research":                          "score_research",
        "scores_citations":                  "score_citations",
        "citations":                         "score_citations",
        "scores_industry_income":            "score_industry_income",
        "industry_income":                   "score_industry_income",
        "scores_international_outlook":      "score_international_outlook",
        "international_outlook":             "score_international_outlook",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # ── Parse ranks and filter to top N ───────────────────────────────────────
    df["rank_numeric"] = df["rank"].apply(parse_rank)
    df = df[df["rank_numeric"].notna()]
    df["rank_numeric"] = df["rank_numeric"].astype(int)
    df = df[df["rank_numeric"] <= TOP_N]

    # ── Parse scores ──────────────────────────────────────────────────────────
    score_cols = [
        "score_overall", "score_teaching", "score_research",
        "score_citations", "score_industry_income", "score_international_outlook"
    ]
    for col in score_cols:
        if col in df.columns:
            df[col] = df[col].apply(parse_score)

    # ── ISO3 ──────────────────────────────────────────────────────────────────
    print("Adding ISO3 codes...")
    if "country" not in df.columns:
        raise KeyError("No 'country' or 'location' column found — check rename_map above")

    unique_countries = df["country"].dropna().unique()
    iso_map = {name: get_iso3(name) for name in unique_countries}

    unmatched = [k for k, v in iso_map.items() if v is None]
    if unmatched:
        print(f"\n  ⚠ Could not find ISO3 for {len(unmatched)} countries — add to COUNTRY_OVERRIDES:")
        for name in sorted(unmatched):
            print(f'      "{name}": "???",')
        print()

    df["iso3"] = df["country"].map(iso_map)

    # ── Drop unused columns ───────────────────────────────────────────────────
    drop_cols = [
        "rank_order", "rank",           # replaced by rank_numeric
        "scores_overall_rank", "scores_teaching_rank",
        "scores_research_rank", "scores_citations_rank",
        "scores_industry_income_rank", "scores_international_outlook_rank",
        "aliases", "subjects_offered", "closed", "unaccredited",
    ]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])
    df = df.rename(columns={"rank_numeric": "rank"})

    # ── Final column order ────────────────────────────────────────────────────
    base_cols = ["year", "rank", "name", "country", "iso3"]
    score_cols_present = [c for c in score_cols if c in df.columns]
    df = df[base_cols + score_cols_present]

    df = df.sort_values(["year", "rank"]).reset_index(drop=True)
    return df

# ── Geocoding ─────────────────────────────────────────────────────────────────

def geocode_universities(df: pd.DataFrame) -> pd.DataFrame:
    """
    Geocode unique universities by name + country.
    Saves a cache CSV so progress is not lost if interrupted.
    Re-running the script will skip already-geocoded universities.
    """
    geolocator = Nominatim(user_agent="cw_visualisation_uni_mapper")

    # Load existing cache if it exists
    if os.path.exists(GEOCODE_CACHE):
        cache_df = pd.read_csv(GEOCODE_CACHE)
        cache = dict(zip(cache_df["name"], zip(cache_df["lat"], cache_df["lon"])))
        print(f"Loaded geocode cache with {len(cache)} entries")
    else:
        cache = {}

    unique_unis = df[["name", "country"]].drop_duplicates(subset="name")
    to_geocode  = unique_unis[~unique_unis["name"].isin(cache)]
    total       = len(to_geocode)

    print(f"Geocoding {total} universities (cached: {len(cache)})...")

    for i, (_, row) in enumerate(to_geocode.iterrows(), 1):
        if row["name"] in GEOCODE_OVERRIDES:
            cache[row["name"]] = GEOCODE_OVERRIDES[row["name"]]
            continue
        query = f"{row['name']}, {row['country']}"
        try:
            location = geolocator.geocode(query, timeout=10)
            if location:
                cache[row["name"]] = (location.latitude, location.longitude)
            else:
                # Try just the university name without country
                location = geolocator.geocode(row["name"], timeout=10)
                cache[row["name"]] = (location.latitude, location.longitude) if location else (None, None)
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"  ⚠ Geocoding failed for {row['name']}: {e}")
            cache[row["name"]] = (None, None)

        # Save cache every 10 entries in case of interruption
        if i % 10 == 0 or i == total:
            cache_df = pd.DataFrame(
                [(k, v[0], v[1]) for k, v in cache.items()],
                columns=["name", "lat", "lon"]
            )
            cache_df.to_csv(GEOCODE_CACHE, index=False)
            print(f"  {i}/{total} geocoded, cache saved")

        time.sleep(GEOCODE_DELAY)

    # Join coordinates back to dataframe
    df["lat"] = df["name"].map(lambda n: cache.get(n, (None, None))[0])
    df["lon"] = df["name"].map(lambda n: cache.get(n, (None, None))[1])

    failed = df["lat"].isna().sum()
    if failed:
        print(f"\n  ⚠ {failed} rows have no coordinates — check the_geocode_cache.csv for nulls")
    else:
        print(f"  ✓ All universities geocoded")

    return df

# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("── Loading THE files ─────────────────────────────────")
    raw = combine_all(INPUT_FOLDER)
    print(f"\nLoaded {len(raw):,} rows across {raw['year'].nunique()} years\n")

    print("── Cleaning ──────────────────────────────────────────")
    cleaned = clean(raw)
    print(f"After filtering to top {TOP_N}: {len(cleaned):,} rows\n")

    print("── Geocoding ─────────────────────────────────────────")
    geocoded = geocode_universities(cleaned)

    print("\n── Summary ───────────────────────────────────────────")
    print(f"  Rows:        {len(geocoded):,}")
    print(f"  Years:       {geocoded['year'].min()} – {geocoded['year'].max()}")
    print(f"  Universities:{geocoded['name'].nunique()}")
    print(f"  Countries:   {geocoded['country'].nunique()}")
    null_iso = geocoded['iso3'].isna().sum()
    null_coords = geocoded['lat'].isna().sum()
    if null_iso:
        print(f"  ⚠ Rows with no ISO3:    {null_iso}")
    else:
        print(f"  ✓ All rows have ISO3")
    if null_coords:
        print(f"  ⚠ Rows with no coords:  {null_coords}")
    else:
        print(f"  ✓ All rows have coordinates")

    print("\n── Sample output ─────────────────────────────────────")
    print(geocoded.head(5).to_string(index=False))

    print(f"\n── Saving to {OUTPUT_FILE} ──────────────────────────")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    geocoded.to_csv(OUTPUT_FILE, index=False)
    print("  ✓ Done")