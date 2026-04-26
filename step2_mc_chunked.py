"""Chunked Monte Carlo — runs `chunk_size` sets, saves to disk, exits.
Run repeatedly until `total_sets` is reached. Resumable if interrupted."""

import sys
import os
import numpy as np
import pandas as pd
from gazetteer import lookup
from jyotisha import assess_chart
from datetime import datetime

TOTAL_SETS = 1191
SET_SIZE = 84
CHUNK = int(sys.argv[1]) if len(sys.argv) > 1 else 200
CHECKPOINT = "mc_checkpoint.npy"

# Load data
df = pd.read_excel("tcc.xlsx")
years = df["Birth Year"].astype(int).to_numpy()
months = df["Birth Month"].astype(int).to_numpy()
days = df["Birth Day"].astype(int).to_numpy()
times_places = []
for _, r in df.iterrows():
    _, _, tz = lookup(r["Birth Town"], r["Birth State"], r["Birth Country"])
    times_places.append((int(r["Birth Time Hour"]), int(r["Birth Time Min"]), tz))

# Resume
if os.path.exists(CHECKPOINT):
    counts = np.load(CHECKPOINT).tolist()
else:
    counts = []

start = len(counts)
end = min(start + CHUNK, TOTAL_SETS)
if start >= TOTAL_SETS:
    print(f"Already done: {start}/{TOTAL_SETS} sets")
    sys.exit(0)

# Use stable seed sequence so resumed runs are reproducible (different seed per set)
master_seed = 12345

import time
t0 = time.time()
for s in range(start, end):
    rng = np.random.default_rng([master_seed, s])
    k = 0
    for _ in range(SET_SIZE):
        while True:
            y = int(years[rng.integers(0, len(years))])
            m = int(months[rng.integers(0, len(months))])
            d = int(days[rng.integers(0, len(days))])
            try:
                datetime(y, m, d)
                break
            except ValueError:
                continue
        h, mi, tz = times_places[int(rng.integers(0, len(times_places)))]
        try:
            a = assess_chart(y, m, d, h, mi, tz)
            if a["Either_kendra"]:
                k += 1
        except Exception:
            continue
    counts.append(k)

np.save(CHECKPOINT, np.array(counts, dtype=np.int32))
print(f"chunk done: {start}->{end}/{TOTAL_SETS}  elapsed={time.time()-t0:.1f}s  "
      f"running mean={np.mean(counts):.4f}")
