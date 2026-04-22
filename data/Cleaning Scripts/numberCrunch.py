import pandas as pd

df = pd.read_csv("data/world-education-data.csv", dtype={"numeric_code": str})

metrics = {
    "gov_exp_pct_gdp":           [2, 4, 6, 8],
    "lit_rate_adult_pct":        [50, 75, 90, 95],
    "pri_comp_rate_pct":         [50, 75, 90, 100],
    "pupil_teacher_primary":     [20, 35, 50, 70],
    "pupil_teacher_secondary":   [15, 25, 35, 50],
    "school_enrol_primary_pct":  [75, 90, 100, 110],
    "school_enrol_secondary_pct":[40, 65, 85, 100],
    "school_enrol_tertiary_pct": [10, 25, 50, 75],
}

for col, bins in metrics.items():
    print(f"\n── {col} ──")
    edges = [float('-inf')] + bins + [float('inf')]
    labels = [
        f"< {bins[0]}",
        *[f"{bins[i]}–{bins[i+1]}" for i in range(len(bins)-1)],
        f"> {bins[-1]}"
    ]
    valid = df[col].dropna()
    for label, lo, hi in zip(labels, edges, edges[1:]):
        count = ((valid > lo) & (valid <= hi)).sum()
        pct = count / len(valid) * 100
        print(f"  {label:15s}: {count:5,}  ({pct:.1f}%)")
    print(f"  {'null':15s}: {df[col].isna().sum():5,}")