"""Step 3: Full statistical analysis.

Hypothesis 1: incidence of either-D1-or-D9 kendra is higher in TCC (60/84) than
in the Monte Carlo set, by:
  (a) normal approximation
  (b) hypergeometric (Fisher's exact, two-by-two)
  (c) Fisher's exact test
Plus a direct empirical p-value from the bootstrap.

Hypothesis 2: probit regression of kendra ~ followers (in millions).

Power analysis: simulation-based, both for H1 (one-sample proportion vs reference)
and H2 (probit slope detection).

Plus: distribution of AK->PK house relationships, Zipf-Mandelbrot fit,
and various supporting statistics.
"""

import json
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

tcc = pd.read_csv("tcc_computed.csv")
mc_counts = np.load("mc_checkpoint.npy")

N = 84
N_MC = len(mc_counts)
N_MC_CHARTS = N_MC * N

# --- TCC observed ---
tcc_d1_kendras = int(tcc["D1_kendra"].sum())
tcc_d9_kendras = int(tcc["D9_kendra"].sum())
tcc_either_kendras = int(tcc["Either_kendra"].sum())
tcc_proportion = tcc_either_kendras / N

# --- Monte Carlo summary ---
mc_total_kendras = int(mc_counts.sum())
mc_proportion = mc_total_kendras / N_MC_CHARTS
mc_mean = float(mc_counts.mean())
mc_sd = float(mc_counts.std(ddof=1))

results = {
    "n_charts_tcc": N,
    "n_sets_mc": N_MC,
    "n_charts_mc": N_MC_CHARTS,
    "tcc_d1_kendras": tcc_d1_kendras,
    "tcc_d9_kendras": tcc_d9_kendras,
    "tcc_either_kendras": tcc_either_kendras,
    "tcc_proportion": tcc_proportion,
    "mc_mean_per_set_of_84": mc_mean,
    "mc_sd_per_set_of_84": mc_sd,
    "mc_proportion_overall": mc_proportion,
    "mc_total_kendras": mc_total_kendras,
}

# === H1, method (a): Normal approximation ===
z_score = (tcc_either_kendras - mc_mean) / mc_sd
p_normal_one_sided = 1 - stats.norm.cdf(z_score)
results["H1_normal_z"] = float(z_score)
results["H1_normal_p_one_sided"] = float(p_normal_one_sided)

# === H1, method (b): Direct empirical p-value from bootstrap ===
# Probability under H0 that a single set of 84 has >= observed
p_empirical = float((mc_counts >= tcc_either_kendras).sum() / N_MC)
results["H1_empirical_p_one_sided"] = p_empirical

# === H1, method (c): Fisher's exact ===
# 2x2 table:
#   |          | kendra | no kendra
#   | TCC      | 60     | 24
#   | MC pool  | mc_total | N_MC_CHARTS - mc_total
table = np.array([
    [tcc_either_kendras, N - tcc_either_kendras],
    [mc_total_kendras, N_MC_CHARTS - mc_total_kendras],
])
or_, p_fisher = stats.fisher_exact(table, alternative="greater")
results["H1_fisher_odds_ratio"] = float(or_)
results["H1_fisher_p_one_sided"] = float(p_fisher)

# === H1, method (d): Two-proportion z-test (additional sanity) ===
p1 = tcc_either_kendras / N
p2 = mc_proportion
p_pool = (tcc_either_kendras + mc_total_kendras) / (N + N_MC_CHARTS)
se_pool = np.sqrt(p_pool * (1 - p_pool) * (1/N + 1/N_MC_CHARTS))
z_two_prop = (p1 - p2) / se_pool
p_two_prop = 1 - stats.norm.cdf(z_two_prop)
results["H1_two_prop_z"] = float(z_two_prop)
results["H1_two_prop_p_one_sided"] = float(p_two_prop)

# === Power analysis for H1 (simulation-based) ===
# Under H0: each chart is kendra with prob = mc_proportion
# Under H1 (observed): each chart is kendra with prob = tcc_proportion
# Power = P(reject H0 at alpha=0.05 | H1 true) for n=84
ALPHA = 0.05
# Critical k: smallest k such that P(K >= k | H0) <= alpha
# K ~ Binomial(N, mc_proportion)
k_crit = stats.binom.isf(ALPHA, N, mc_proportion) + 1
# Achieved alpha at k_crit
actual_alpha = float(stats.binom.sf(k_crit - 1, N, mc_proportion))
# Power = P(K >= k_crit | p = tcc_proportion)
power_h1 = float(stats.binom.sf(k_crit - 1, N, tcc_proportion))
results["H1_power_alpha_target"] = ALPHA
results["H1_power_k_critical"] = int(k_crit)
results["H1_power_actual_alpha"] = actual_alpha
results["H1_power_against_observed_effect"] = power_h1

# === H2: Probit regression of Either_kendra ~ Followers (in millions) ===
y = tcc["Either_kendra"].astype(int).to_numpy()
x = (tcc["Followers"].astype(float) / 1e6).to_numpy()
X = sm.add_constant(x)

probit_model = sm.Probit(y, X).fit(disp=False)
results["H2_top1000_intercept"] = float(probit_model.params[0])
results["H2_top1000_slope"] = float(probit_model.params[1])
results["H2_top1000_intercept_p"] = float(probit_model.pvalues[0])
results["H2_top1000_slope_p"] = float(probit_model.pvalues[1])
results["H2_top1000_intercept_se"] = float(probit_model.bse[0])
results["H2_top1000_slope_se"] = float(probit_model.bse[1])
results["H2_top1000_aic"] = float(probit_model.aic)
results["H2_top1000_bic"] = float(probit_model.bic)
results["H2_top1000_llf"] = float(probit_model.llf)
results["H2_top1000_llnull"] = float(probit_model.llnull)
results["H2_top1000_pseudo_r2_mcfadden"] = float(probit_model.prsquared)
results["H2_top1000_lr_stat"] = float(2 * (probit_model.llf - probit_model.llnull))

# === H2 also for Top 500 subset ===
top500 = tcc[tcc["Rank"] <= 500].copy()
y500 = top500["Either_kendra"].astype(int).to_numpy()
x500 = (top500["Followers"].astype(float) / 1e6).to_numpy()
X500 = sm.add_constant(x500)
probit500 = sm.Probit(y500, X500).fit(disp=False)
results["H2_top500_n"] = len(top500)
results["H2_top500_intercept"] = float(probit500.params[0])
results["H2_top500_slope"] = float(probit500.params[1])
results["H2_top500_intercept_p"] = float(probit500.pvalues[0])
results["H2_top500_slope_p"] = float(probit500.pvalues[1])
results["H2_top500_aic"] = float(probit500.aic)
results["H2_top500_bic"] = float(probit500.bic)
results["H2_top500_pseudo_r2_mcfadden"] = float(probit500.prsquared)

# Logit comparison for top1000 (paper says probit was better)
logit_model = sm.Logit(y, X).fit(disp=False)
results["H2_top1000_logit_aic"] = float(logit_model.aic)
results["H2_top1000_logit_bic"] = float(logit_model.bic)
results["H2_top1000_probit_better_aic"] = float(probit_model.aic) < float(logit_model.aic)

# === Power analysis for H2 (simulation-based, top-1000 model) ===
# Resample x distribution with replacement, simulate y from fitted probit, refit, count rejections
rng = np.random.default_rng(2026)
N_POWER_SIM = 2000
beta0_obs = probit_model.params[0]
beta1_obs = probit_model.params[1]
rejections = 0
for _ in range(N_POWER_SIM):
    x_sim = rng.choice(x, size=len(x), replace=True)
    p_sim = stats.norm.cdf(beta0_obs + beta1_obs * x_sim)
    y_sim = (rng.random(len(x_sim)) < p_sim).astype(int)
    if y_sim.sum() in (0, len(y_sim)):
        continue
    try:
        m = sm.Probit(y_sim, sm.add_constant(x_sim)).fit(disp=False, maxiter=50)
        if m.pvalues[1] < ALPHA:
            rejections += 1
    except Exception:
        pass
power_h2 = rejections / N_POWER_SIM
results["H2_power_simulation_n"] = N_POWER_SIM
results["H2_power_against_fitted_effect"] = float(power_h2)

# === Distribution of AK->PK house relationships in TCC (D-1 + D-9 combined) ===
combined_dist = []
for _, r in tcc.iterrows():
    combined_dist.append(int(r["D1_distance"]))
    combined_dist.append(int(r["D9_distance"]))

dist_counts_tcc = np.bincount(combined_dist, minlength=13)[1:13]  # houses 1..12
results["tcc_house_dist_d1_d9_combined"] = dist_counts_tcc.tolist()

# Categorize: kendra (1,4,7,10), panapara (2,5,8,11), apoklima (3,6,9,12)
def classify(h):
    if h in (1, 4, 7, 10): return "kendra"
    if h in (2, 5, 8, 11): return "panapara"
    if h in (3, 6, 9, 12): return "apoklima"

cats_tcc = pd.Series([classify(h) for h in combined_dist]).value_counts()
results["tcc_kendra_count_d1_d9"] = int(cats_tcc.get("kendra", 0))
results["tcc_panapara_count_d1_d9"] = int(cats_tcc.get("panapara", 0))
results["tcc_apoklima_count_d1_d9"] = int(cats_tcc.get("apoklima", 0))

# === Zipf-Mandelbrot remark: rank vs followers ===
# Standard ZM: f(r) = C / (r + b)^s
# We fit log(followers) = a - s*log(rank + b) via grid+optimize
from scipy.optimize import curve_fit
ranks = tcc["Rank"].astype(float).to_numpy()
followers = tcc["Followers"].astype(float).to_numpy()
order = np.argsort(ranks)
ranks_s = ranks[order]
followers_s = followers[order]

def zm(r, C, b, s):
    return C / np.power(r + b, s)

try:
    popt, _ = curve_fit(zm, ranks_s, followers_s, p0=[1e9, 1.0, 1.0], maxfev=5000)
    pred = zm(ranks_s, *popt)
    ss_res = np.sum((followers_s - pred) ** 2)
    ss_tot = np.sum((followers_s - followers_s.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot
    results["zipf_mandelbrot_C"] = float(popt[0])
    results["zipf_mandelbrot_b"] = float(popt[1])
    results["zipf_mandelbrot_s"] = float(popt[2])
    results["zipf_mandelbrot_r2"] = float(r2)
except Exception as e:
    results["zipf_mandelbrot_error"] = str(e)

# === Save ===
with open("results.json", "w") as f:
    json.dump(results, f, indent=2)

print("=== SUMMARY ===")
for k, v in results.items():
    if isinstance(v, float):
        print(f"  {k}: {v:.6g}")
    else:
        print(f"  {k}: {v}")

# Save MC counts as JSON-friendly summary too
mc_count_freq = pd.Series(mc_counts).value_counts().sort_index()
mc_count_freq.to_csv("mc_count_freq.csv")
