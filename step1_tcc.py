"""Step 1: Compute AK/PK kendras for all 84 TCC charts; compare to spreadsheet."""

import pandas as pd
from gazetteer import lookup
from jyotisha import assess_chart

df = pd.read_excel("tcc.xlsx")

results = []
for _, r in df.iterrows():
    lat, lon, tz = lookup(r["Birth Town"], r["Birth State"], r["Birth Country"])
    a = assess_chart(
        int(r["Birth Year"]),
        int(r["Birth Month"]),
        int(r["Birth Day"]),
        int(r["Birth Time Hour"]),
        int(r["Birth Time Min"]),
        tz,
    )
    results.append({
        "Name": r["Name"],
        "Followers": r["Followers"],
        "Rank": r["Rank"],
        "tz": tz,
        **a,
        "paper_D1_dist": int(r["D1 AK > PuK H"]),
        "paper_D9_dist": int(r["D9 AK > PuK H"]),
        "paper_D1_kendra": int(r["D1 Kendra"]),
        "paper_D9_kendra": int(r["D9  Kendra"]),
        "paper_Either": int(r["Either D1 or D9 Kendra"]),
    })

out = pd.DataFrame(results)
out["D1_match"] = out["D1_distance"] == out["paper_D1_dist"]
out["D9_match"] = out["D9_distance"] == out["paper_D9_dist"]
out["Either_match"] = out["Either_kendra"] == out["paper_Either"]

print("=== TCC computation summary ===")
print(f"My D1 kendra count:     {out['D1_kendra'].sum()}  (paper: {out['paper_D1_kendra'].sum()})")
print(f"My D9 kendra count:     {out['D9_kendra'].sum()}  (paper: {out['paper_D9_kendra'].sum()})")
print(f"My Either kendra count: {out['Either_kendra'].sum()}  (paper: {out['paper_Either'].sum()})")
print()
print(f"D1 distance matches paper: {out['D1_match'].sum()}/84")
print(f"D9 distance matches paper: {out['D9_match'].sum()}/84")
print(f"Either-kendra matches paper: {out['Either_match'].sum()}/84")
print()

# Show any discrepancies
disc = out[~out["Either_match"]]
if len(disc):
    print("Either-kendra discrepancies:")
    print(disc[["Name","D1_distance","paper_D1_dist","D9_distance","paper_D9_dist","Either_kendra","paper_Either","tz"]].to_string())

out.to_csv("tcc_computed.csv", index=False)
print("\nSaved tcc_computed.csv")
