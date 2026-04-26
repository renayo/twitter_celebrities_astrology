"""
Jyotisha calculations for the Twitter Kendra replication.

Following Oshop & Foss (2015):
- Sidereal zodiac, Lahiri ayanamsa
- Mean lunar nodes
- Grahas: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu (North Node).
  South node (Ketu) is omitted per Jaimini's Upadesa Sutras.
- AK (AtmaKaraka) = graha with highest degree within its sidereal sign,
  but Rahu's degree is computed as (30 - rahu_deg_in_sign) due to mean retrograde motion.
- PK (PutraKaraka) = graha with the 6th highest degree by the same ranking.
- D-1 = rashi: sign occupied by each graha based on geocentric sidereal longitude.
- D-9 = navamsha: each 30-degree sign is divided into 9 parts of 3°20'.
  The navamsha sign is computed using the standard rule used in Jyotisha software
  (continuous counting from the start of the sign for movable signs, etc.) — but
  Shri Jyoti Star uses the standard formula:
      navamsha_sign = (rashi_sign_index * 9 + part_index) mod 12
  where rashi_sign_index is 0..11 starting from Aries, and part_index is 0..8.
  This produces the same result as the traditional movable/fixed/dual rules.
- Kendra: two signs are in kendra if their inclusive distance is 1, 4, 7, or 10.
  Equivalently |sign_a - sign_b| mod 3 == 0.
"""

import swisseph as swe
from datetime import datetime
import pytz

# Configure once
swe.set_sid_mode(swe.SIDM_LAHIRI)

# Grahas used in the karaka ranking (paper uses these 8; mean nodes for Rahu)
GRAHAS = [
    ("Sun", swe.SUN),
    ("Moon", swe.MOON),
    ("Mars", swe.MARS),
    ("Mercury", swe.MERCURY),
    ("Jupiter", swe.JUPITER),
    ("Venus", swe.VENUS),
    ("Saturn", swe.SATURN),
    ("Rahu", swe.MEAN_NODE),  # mean node, per paper
]

FLAG = swe.FLG_SIDEREAL | swe.FLG_SWIEPH


def to_julian_day(year, month, day, hour, minute, tz_name):
    """Convert local birth time to Julian Day in UT."""
    tz = pytz.timezone(tz_name)
    # Build naive datetime then localize (handles historical DST correctly)
    naive = datetime(year, month, day, hour, minute)
    local = tz.localize(naive, is_dst=None)
    utc = local.astimezone(pytz.UTC)
    # swe.julday expects UT
    ut_hour = utc.hour + utc.minute / 60.0 + utc.second / 3600.0
    jd = swe.julday(utc.year, utc.month, utc.day, ut_hour)
    return jd


def graha_longitudes(jd):
    """Return dict {graha_name: sidereal_longitude_in_degrees}."""
    out = {}
    for name, ipl in GRAHAS:
        pos, _ = swe.calc_ut(jd, ipl, FLAG)
        out[name] = pos[0] % 360.0
    return out


def sign_index(lon):
    """0=Aries, 1=Taurus, ..., 11=Pisces"""
    return int(lon // 30) % 12


def deg_in_sign(lon):
    return lon % 30.0


def navamsha_sign(lon):
    """Standard navamsha: each 30° sign divided into 9 parts of 3°20'.
    For sign s and part p (0-indexed), navamsha sign = (s*9 + p) mod 12 — but only
    if we use the rule that movable signs start navamsha from themselves, fixed signs
    from the 9th, dual from the 5th. The simple formula (s*9 + p) % 12 gives this
    for movable signs (s in 0,3,6,9). The general formula that matches all classes is:
        navamsha_sign = (s_class_start + p) % 12
    where s_class_start = s for movable, s+8 for fixed (which equals s-4 mod 12 ... actually)
    Use the well-known derivation: navamsha_sign = (s * 9 + p) % 12 only works when
    you account for parity. Easier: use the absolute formula:
        navamsha_index_global = floor(lon / (30/9)) = floor(lon * 9 / 30)
        navamsha_sign = navamsha_index_global % 12
    This is the standard formula used by virtually all Jyotisha software including
    Shri Jyoti Star, JHora, and Parashara's Light. It produces the canonical result.
    """
    return int(lon * 9 / 30) % 12


def rank_grahas(longitudes):
    """Return list of (graha, score) sorted from highest to lowest 'degree' for karaka ranking.
    For Rahu, use 30 - deg_in_sign because of mean retrograde motion (per paper).
    """
    scored = []
    for g, lon in longitudes.items():
        d = deg_in_sign(lon)
        if g == "Rahu":
            d = 30.0 - d
        scored.append((g, d))
    scored.sort(key=lambda x: -x[1])
    return scored


def ak_pk(longitudes):
    """Return (AK_graha, PK_graha) per the paper's rule."""
    ranked = rank_grahas(longitudes)
    return ranked[0][0], ranked[5][0]  # 1st and 6th highest


def is_kendra(sign_a, sign_b):
    """Two signs are in kendra if the inclusive house distance is 1, 4, 7, or 10.
    Equivalently, |a - b| mod 3 == 0.
    """
    return (abs(sign_a - sign_b) % 3) == 0


def inclusive_house_distance(sign_a, sign_b):
    """House distance counting AK as house 1 and counting forward to PK."""
    return ((sign_b - sign_a) % 12) + 1


def assess_chart(year, month, day, hour, minute, tz_name):
    """Compute everything needed for the kendra study."""
    jd = to_julian_day(year, month, day, hour, minute, tz_name)
    lons = graha_longitudes(jd)
    ak, pk = ak_pk(lons)

    # D-1 signs
    d1_signs = {g: sign_index(lons[g]) for g in lons}
    # D-9 signs
    d9_signs = {g: navamsha_sign(lons[g]) for g in lons}

    d1_dist = inclusive_house_distance(d1_signs[ak], d1_signs[pk])
    d9_dist = inclusive_house_distance(d9_signs[ak], d9_signs[pk])

    d1_kendra = is_kendra(d1_signs[ak], d1_signs[pk])
    d9_kendra = is_kendra(d9_signs[ak], d9_signs[pk])
    either = d1_kendra or d9_kendra

    return {
        "AK": ak,
        "PK": pk,
        "D1_AK_sign": d1_signs[ak],
        "D1_PK_sign": d1_signs[pk],
        "D9_AK_sign": d9_signs[ak],
        "D9_PK_sign": d9_signs[pk],
        "D1_distance": d1_dist,
        "D9_distance": d9_dist,
        "D1_kendra": int(d1_kendra),
        "D9_kendra": int(d9_kendra),
        "Either_kendra": int(either),
    }
