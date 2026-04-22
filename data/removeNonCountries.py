import pandas as pd

MAIN_PATH = "data/world-education-data.csv"

main = pd.read_csv(MAIN_PATH, dtype={"numeric_code": str})

before = len(main)

# Keep only rows with a valid numeric_code (i.e. real countries)
main = main[main["numeric_code"].notna()]
main = main[main["numeric_code"].str.strip() != ""]

after = len(main)

main.to_csv(MAIN_PATH, index=False)

print(f"✓ Removed {before - after:,} non-country rows")
print(f"  Rows remaining: {after:,}")