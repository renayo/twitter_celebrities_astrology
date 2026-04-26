# Twitter Kendra Replication — Outputs

Python replication of [Oshop & Foss (2015), JSE 29(1)](https://github.com/renayo/twitter_celebrities_astrology/blob/main/pkpadmin%2C%2BJSE%2B291%2BOshop.pdf).

## Top-level deliverables

- **Twitter_Kendra_Replication_Report.docx / .pdf** — the focused replication report
- **tcc_computed.csv** — per-celebrity AK/PK and kendra status, computed from scratch via Swiss Ephemeris and compared to the original spreadsheet
- **mc_set_counts.npy** — kendra count per Monte Carlo set of 84 (1,191 sets = 100,044 synthetic charts)
- **results.json** — every numeric result reported in the document, machine-readable

## scripts/

Run in numeric order. Each script reads/writes files to its working directory.

| Script | Purpose | Output |
|---|---|---|
| `gazetteer.py` | (lat, lon, IANA tz) for the 72 unique birthplaces | imported by others |
| `jyotisha.py` | Sidereal Vedic chart calculation: AK, PK, D-1, D-9, kendra detection | imported by others |
| `step1_tcc.py` | Compute kendras for the 84 TCC charts; sanity-check vs. original spreadsheet flags | `tcc_computed.csv` |
| `step2_mc_chunked.py N` | Run `N` Monte Carlo sets of 84 (chunked, resumable). Run repeatedly until 1,191 sets done. | `mc_checkpoint.npy` |
| `step3_stats.py` | All H1/H2 tests, power, Zipf-Mandelbrot fit | `results.json` |
| `step4_figures.py` | All 13 figures (also recomputes a 10K-chart MC distance distribution for Fig 2) | `fig*.png`, `mc_distances.npy` |
| `step5_report.py` | Build the docx report | `Twitter_Kendra_Replication_Report.docx` |

To produce the PDF from the docx: `soffice --headless --convert-to pdf Twitter_Kendra_Replication_Report.docx`

## figures/

13 PNGs at 150 dpi, embedded inside the report. Standalone copies are kept here for downstream use.

## Dependencies

Python 3.12 with: `pyswisseph`, `pandas`, `numpy`, `scipy`, `statsmodels`, `pytz`, `matplotlib`, `python-docx`. LibreOffice for docx → pdf conversion.

## Replication validity

- **60/84 kendra count** (paper: 60/84) ✓
- **Probit intercept 0.10133** (paper: 0.101327) ✓
- **Probit slope 0.08779** (paper: 0.0877916) ✓
- **Top-500 slope 0.16817** (paper: 0.168171) ✓
- **MC mean 46.97 / set of 84** (paper: 46.54) — within 1% on 18× larger MC
- **Validation against published Bieber chart**: AK = Mercury, PK = Saturn, D-1 dist = 2, D-9 dist = 4 — all match the paper exactly.
