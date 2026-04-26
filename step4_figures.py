"""Step 4: Generate all visualizations.

Figures planned (mirroring paper Figs 7-23 where data permits):
  fig01_tcc_house_dist.png     - TCC AK->PK house distribution (D-1+D-9)
  fig02_mc_house_dist.png      - Monte Carlo AK->PK house distribution (D-1+D-9 combined)
  fig03_mc_set_distribution.png - Distribution of kendra-counts per set of 84 in MC
  fig04_mc_normal_fit.png      - MC distribution + best-fit normal
  fig05_mc_hypergeom_fit.png   - MC distribution + hypergeometric fit
  fig06_followers_hist.png     - Histogram of TCC followers
  fig07_followers_qq.png       - Q-Q plot of followers vs normal
  fig08_probit_top1000.png     - Probit regression curve over data
  fig09_probit_derivative.png  - Derivative of probit f(x)
  fig10_probit_top500.png      - Probit regression curve, top-500 subset
  fig11_rank_vs_followers.png  - Rank vs followers (linear)
  fig12_rank_vs_followers_loglog.png - Same, log-log (Zipf-Mandelbrot)
  fig13_quadrant_summary.png   - Kendra/Panapara/Apoklima cultural prescription test
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy import stats

rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 110,
    "savefig.dpi": 150,
    "savefig.bbox": "tight",
})

PALETTE = {
    "primary": "#2E5984",
    "primary_light": "#A8C5E2",
    "accent": "#C8553D",
    "muted": "#888888",
}

tcc = pd.read_csv("tcc_computed.csv")
mc_counts = np.load("mc_checkpoint.npy")
with open("results.json") as f:
    R = json.load(f)

N = 84

# ==================================================================
# Fig 1: TCC AK->PK house distribution (D-1 + D-9 combined)
# ==================================================================
fig, ax = plt.subplots(figsize=(8, 4.5))
combined_dist = list(tcc["D1_distance"]) + list(tcc["D9_distance"])
counts = np.bincount(combined_dist, minlength=13)[1:13]
houses = np.arange(1, 13)
colors = ["#C8553D" if h in (1, 4, 7, 10) else PALETTE["primary_light"] for h in houses]
ax.bar(houses, counts, color=colors, edgecolor="black", linewidth=0.6)
ax.set_xticks(houses)
ax.set_xlabel("Inclusive house distance from AK to PK")
ax.set_ylabel("Count (D-1 + D-9 combined, n=168)")
ax.set_title("Fig 1. TCC: AK→PK house distribution (kendra houses 1, 4, 7, 10 highlighted)")
plt.savefig("fig01_tcc_house_dist.png")
plt.close()

# ==================================================================
# Fig 2: Monte Carlo AK->PK house distribution (computed on the fly)
# To get the MC house distribution we need to redo the bootstrap but
# record distances. Re-run with checkpoint of distances if not present.
# ==================================================================
import os
if not os.path.exists("mc_distances.npy"):
    print("Computing MC distance distribution (this will take ~3 min)...")
    from gazetteer import lookup
    from jyotisha import assess_chart
    from datetime import datetime

    df_tcc = pd.read_excel("tcc.xlsx")
    years = df_tcc["Birth Year"].astype(int).to_numpy()
    months = df_tcc["Birth Month"].astype(int).to_numpy()
    days = df_tcc["Birth Day"].astype(int).to_numpy()
    times_places = []
    for _, r in df_tcc.iterrows():
        _, _, tz = lookup(r["Birth Town"], r["Birth State"], r["Birth Country"])
        times_places.append((int(r["Birth Time Hour"]), int(r["Birth Time Min"]), tz))

    rng = np.random.default_rng(99)
    distances = []  # store (d1_dist, d9_dist)
    N_DIST = 10000  # smaller subset is sufficient for shape
    for _ in range(N_DIST):
        while True:
            y = int(years[rng.integers(0, len(years))])
            m = int(months[rng.integers(0, len(months))])
            d = int(days[rng.integers(0, len(days))])
            try:
                datetime(y, m, d); break
            except ValueError:
                continue
        h, mi, tz = times_places[int(rng.integers(0, len(times_places)))]
        try:
            a = assess_chart(y, m, d, h, mi, tz)
            distances.append((a["D1_distance"], a["D9_distance"]))
        except Exception:
            continue
    distances = np.array(distances)
    np.save("mc_distances.npy", distances)
else:
    distances = np.load("mc_distances.npy")

mc_d1 = distances[:, 0]
mc_d9 = distances[:, 1]

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
combined_mc = np.concatenate([mc_d1, mc_d9])

for ax_, data, title in zip(
    axes,
    [combined_mc, mc_d1, mc_d9],
    [f"D-1 + D-9 combined (n={len(combined_mc):,})",
     f"D-1 only (n={len(mc_d1):,})",
     f"D-9 only (n={len(mc_d9):,})"],
):
    cnts = np.bincount(data, minlength=13)[1:13]
    cols = ["#C8553D" if h in (1, 4, 7, 10) else PALETTE["primary_light"] for h in houses]
    ax_.bar(houses, cnts, color=cols, edgecolor="black", linewidth=0.4)
    ax_.set_xticks(houses)
    ax_.set_xlabel("House distance")
    ax_.set_title(title)
axes[0].set_ylabel("Count")
fig.suptitle("Fig 2. Monte Carlo: AK→PK house distribution (kendra houses highlighted)")
plt.savefig("fig02_mc_house_dist.png")
plt.close()

# ==================================================================
# Fig 3: MC set-level distribution of kendra counts
# ==================================================================
fig, ax = plt.subplots(figsize=(8, 4.5))
unique, freq = np.unique(mc_counts, return_counts=True)
ax.bar(unique, freq, color=PALETTE["primary_light"], edgecolor="black", linewidth=0.4)
ax.axvline(60, color=PALETTE["accent"], linestyle="--", linewidth=2,
           label=f"TCC observed = 60")
ax.axvline(mc_counts.mean(), color=PALETTE["primary"], linestyle=":", linewidth=2,
           label=f"MC mean = {mc_counts.mean():.2f}")
ax.set_xlabel("Either-D1-or-D9 kendra count per set of 84")
ax.set_ylabel(f"Frequency (across {len(mc_counts):,} sets)")
ax.set_title("Fig 3. Monte Carlo distribution of kendra incidence per set of 84")
ax.legend()
plt.savefig("fig03_mc_set_distribution.png")
plt.close()

# ==================================================================
# Fig 4: MC + best-fit normal
# ==================================================================
fig, ax = plt.subplots(figsize=(8, 4.5))
density, bins, _ = ax.hist(mc_counts, bins=range(int(mc_counts.min()), int(mc_counts.max()) + 2),
                           density=True, color=PALETTE["primary_light"], edgecolor="black", linewidth=0.4)
xx = np.linspace(mc_counts.min() - 1, mc_counts.max() + 1, 400)
ax.plot(xx, stats.norm.pdf(xx, loc=mc_counts.mean(), scale=mc_counts.std(ddof=1)),
        color=PALETTE["primary"], linewidth=2.2, label=f"N(μ={mc_counts.mean():.2f}, σ={mc_counts.std(ddof=1):.2f})")
ax.axvline(60, color=PALETTE["accent"], linestyle="--", linewidth=2,
           label=f"TCC = 60 (z = {R['H1_normal_z']:.3f})")
ax.set_xlabel("Either-kendra count per set of 84")
ax.set_ylabel("Density")
ax.set_title("Fig 4. Monte Carlo with best-fit normal approximation")
ax.legend()
plt.savefig("fig04_mc_normal_fit.png")
plt.close()

# ==================================================================
# Fig 5: MC + hypergeometric reference
# Hypergeometric: sample of 84 from population of N_MC_CHARTS with mc_total successes
# ==================================================================
N_MC_CHARTS = R["n_charts_mc"]
mc_total = R["mc_total_kendras"]
ks = np.arange(int(mc_counts.min()), int(mc_counts.max()) + 2)
hg_pmf = stats.hypergeom.pmf(ks, N_MC_CHARTS, mc_total, 84)

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist(mc_counts, bins=range(int(mc_counts.min()), int(mc_counts.max()) + 2),
        density=True, color=PALETTE["primary_light"], edgecolor="black", linewidth=0.4,
        label="MC empirical")
ax.plot(ks, hg_pmf, "o-", color=PALETTE["primary"], linewidth=2, markersize=5,
        label=f"Hypergeometric(M={N_MC_CHARTS:,}, K={mc_total:,}, n=84)")
ax.axvline(60, color=PALETTE["accent"], linestyle="--", linewidth=2, label="TCC = 60")
ax.set_xlabel("Either-kendra count per set of 84")
ax.set_ylabel("Probability / density")
ax.set_title("Fig 5. MC overlay with hypergeometric reference")
ax.legend()
plt.savefig("fig05_mc_hypergeom_fit.png")
plt.close()

# ==================================================================
# Fig 6: Followers histogram
# ==================================================================
fig, ax = plt.subplots(figsize=(8, 4.5))
followers_M = tcc["Followers"] / 1e6
ax.hist(followers_M, bins=20, color=PALETTE["primary_light"], edgecolor="black", linewidth=0.6)
ax.set_xlabel("Followers (millions)")
ax.set_ylabel("Number of celebrities")
ax.set_title("Fig 6. TCC follower distribution")
plt.savefig("fig06_followers_hist.png")
plt.close()

# ==================================================================
# Fig 7: Q-Q plot of followers
# ==================================================================
fig, ax = plt.subplots(figsize=(7, 6))
stats.probplot(tcc["Followers"], dist="norm", plot=ax)
ax.get_lines()[0].set_color(PALETTE["primary"])
ax.get_lines()[0].set_markersize(5)
ax.get_lines()[1].set_color(PALETTE["accent"])
ax.get_lines()[1].set_linestyle("--")
ax.set_title("Fig 7. Normal Q-Q plot of TCC followers")
plt.savefig("fig07_followers_qq.png")
plt.close()

# ==================================================================
# Fig 8: Probit regression curve over data (top-1000)
# ==================================================================
b0, b1 = R["H2_top1000_intercept"], R["H2_top1000_slope"]
xx = np.linspace(0, followers_M.max() * 1.05, 400)
prob_curve = stats.norm.cdf(b0 + b1 * xx)

fig, ax = plt.subplots(figsize=(9, 5))
y = tcc["Either_kendra"]
ax.scatter(followers_M[y == 1], np.ones((y == 1).sum()) + np.random.normal(0, 0.005, (y == 1).sum()),
           color=PALETTE["primary"], alpha=0.55, s=35, label="Kendra (1)")
ax.scatter(followers_M[y == 0], np.zeros((y == 0).sum()) + np.random.normal(0, 0.005, (y == 0).sum()),
           color=PALETTE["muted"], alpha=0.55, s=35, label="No kendra (0)")
ax.plot(xx, prob_curve, color=PALETTE["accent"], linewidth=2.5,
        label=f"Probit: Φ({b0:.4f} + {b1:.4f}·x)")
ax.set_xlabel("Followers (millions)")
ax.set_ylabel("P(kendra in D-1 or D-9)")
ax.set_title(f"Fig 8. Probit regression for top-1000 (n=84, slope p={R['H2_top1000_slope_p']:.4f})")
ax.legend(loc="center right")
ax.set_ylim(-0.08, 1.08)
plt.savefig("fig08_probit_top1000.png")
plt.close()

# ==================================================================
# Fig 9: Derivative of probit
# ==================================================================
deriv = b1 * stats.norm.pdf(b0 + b1 * xx)
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(xx, deriv, color=PALETTE["primary"], linewidth=2)
ax.fill_between(xx, 0, deriv, color=PALETTE["primary_light"], alpha=0.4)
ax.set_xlabel("Followers (millions)")
ax.set_ylabel("d f(x) / dx")
ax.set_title("Fig 9. Derivative of probit f(x): always positive (slope is monotone)")
plt.savefig("fig09_probit_derivative.png")
plt.close()

# ==================================================================
# Fig 10: Probit regression for top-500 subset
# ==================================================================
top500 = tcc[tcc["Rank"] <= 500].copy()
b0_500 = R["H2_top500_intercept"]
b1_500 = R["H2_top500_slope"]
followers_M_500 = top500["Followers"] / 1e6
y_500 = top500["Either_kendra"]
xx500 = np.linspace(0, followers_M_500.max() * 1.05, 400)
curve_500 = stats.norm.cdf(b0_500 + b1_500 * xx500)

fig, ax = plt.subplots(figsize=(9, 5))
ax.scatter(followers_M_500[y_500 == 1], np.ones((y_500 == 1).sum()) + np.random.normal(0, 0.005, (y_500 == 1).sum()),
           color=PALETTE["primary"], alpha=0.55, s=35, label="Kendra (1)")
ax.scatter(followers_M_500[y_500 == 0], np.zeros((y_500 == 0).sum()) + np.random.normal(0, 0.005, (y_500 == 0).sum()),
           color=PALETTE["muted"], alpha=0.55, s=35, label="No kendra (0)")
ax.plot(xx500, curve_500, color=PALETTE["accent"], linewidth=2.5,
        label=f"Probit: Φ({b0_500:.4f} + {b1_500:.4f}·x)")
ax.set_xlabel("Followers (millions)")
ax.set_ylabel("P(kendra in D-1 or D-9)")
ax.set_title(f"Fig 10. Probit regression for top-500 subset (n={R['H2_top500_n']}, slope p={R['H2_top500_slope_p']:.4f})")
ax.legend(loc="center right")
ax.set_ylim(-0.08, 1.08)
plt.savefig("fig10_probit_top500.png")
plt.close()

# ==================================================================
# Fig 11 & 12: Rank vs followers (linear and log-log)
# ==================================================================
followers_arr = tcc["Followers"].to_numpy()
ranks_arr = tcc["Rank"].to_numpy()
order = np.argsort(ranks_arr)
ranks_s = ranks_arr[order]
followers_s = followers_arr[order]

# Zipf-Mandelbrot fit
zm_C = R["zipf_mandelbrot_C"]
zm_b = R["zipf_mandelbrot_b"]
zm_s = R["zipf_mandelbrot_s"]
rr = np.linspace(1, ranks_s.max(), 500)
zm_pred = zm_C / np.power(rr + zm_b, zm_s)

fig, ax = plt.subplots(figsize=(9, 5))
ax.scatter(followers_arr, ranks_arr, color=PALETTE["primary"], alpha=0.65, s=30)
# Plot ZM as followers(x) rank(y)
ax.plot(zm_pred, rr, color=PALETTE["accent"], linewidth=2,
        label=f"Zipf-Mandelbrot fit (R²={R['zipf_mandelbrot_r2']:.4f})")
ax.set_xlabel("Followers")
ax.set_ylabel("Rank")
ax.set_title("Fig 11. Twitter rank vs followers — TCC sample")
ax.invert_yaxis()
ax.legend()
plt.savefig("fig11_rank_vs_followers.png")
plt.close()

fig, ax = plt.subplots(figsize=(9, 5))
ax.loglog(followers_arr, ranks_arr, "o", color=PALETTE["primary"], alpha=0.65, markersize=5)
ax.loglog(zm_pred, rr, "-", color=PALETTE["accent"], linewidth=2,
          label=f"Zipf-Mandelbrot: y = {zm_C:.2e} / (rank + {zm_b:.2f})^{zm_s:.3f}")
ax.set_xlabel("Followers (log)")
ax.set_ylabel("Rank (log)")
ax.set_title("Fig 12. Log-log: Twitter rank vs followers (Zipf-Mandelbrot)")
ax.legend(loc="lower left", fontsize=9)
plt.savefig("fig12_rank_vs_followers_loglog.png")
plt.close()

# ==================================================================
# Fig 13: Cultural prescription test (kendra/panapara/apoklima)
# ==================================================================
def classify(h):
    if h in (1, 4, 7, 10): return "kendra"
    if h in (2, 5, 8, 11): return "panapara"
    return "apoklima"

# TCC totals (D-1 + D-9 combined)
tcc_dist = list(tcc["D1_distance"]) + list(tcc["D9_distance"])
tcc_cat = pd.Series([classify(h) for h in tcc_dist]).value_counts()
mc_dist = combined_mc.tolist()
mc_cat = pd.Series([classify(h) for h in mc_dist]).value_counts()

# Normalize to proportions
tcc_p = {k: tcc_cat.get(k, 0) / len(tcc_dist) for k in ["kendra", "panapara", "apoklima"]}
mc_p = {k: mc_cat.get(k, 0) / len(mc_dist) for k in ["kendra", "panapara", "apoklima"]}

# Chi-square test on TCC vs MC proportions
observed = np.array([tcc_cat.get(k, 0) for k in ["kendra", "panapara", "apoklima"]])
expected_p = np.array([mc_p[k] for k in ["kendra", "panapara", "apoklima"]])
expected = expected_p * len(tcc_dist)
chi2, p_chi2 = stats.chisquare(observed, expected)

fig, ax = plt.subplots(figsize=(8, 4.5))
labels = ["Kendra (1, 4, 7, 10)", "Panapara (2, 5, 8, 11)", "Apoklima (3, 6, 9, 12)"]
x_pos = np.arange(len(labels))
w = 0.38
ax.bar(x_pos - w/2, [tcc_p[k] for k in ["kendra","panapara","apoklima"]],
       width=w, color=PALETTE["accent"], edgecolor="black", linewidth=0.5, label="TCC")
ax.bar(x_pos + w/2, [mc_p[k] for k in ["kendra","panapara","apoklima"]],
       width=w, color=PALETTE["primary_light"], edgecolor="black", linewidth=0.5, label="Monte Carlo")
ax.set_xticks(x_pos)
ax.set_xticklabels(labels)
ax.set_ylabel("Proportion (D-1 + D-9 combined)")
ax.set_title(f"Fig 13. Cultural prescription: kendra > panapara > apoklima (χ² = {chi2:.3f}, p = {p_chi2:.4f})")
ax.legend()
plt.savefig("fig13_quadrant_summary.png")
plt.close()

# Save the chi2 result for the report
R["cultural_chi2"] = float(chi2)
R["cultural_chi2_p"] = float(p_chi2)
with open("results.json", "w") as f:
    json.dump(R, f, indent=2)

print("All 13 figures generated.")
import glob
for f_ in sorted(glob.glob("fig*.png")):
    print(f"  {f_}")
