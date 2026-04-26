"""
Gazetteer of birth-place coordinates and IANA timezones for the 84 TCC charts.
Coordinates from standard atlases (Astrodienst / Wikipedia city pages); timezones
are the modern IANA zones that pytz uses correctly with historical DST rules.

Lookup key is (birth_town_normalized, birth_state_normalized, birth_country_normalized).
"""

# (lat_deg, lon_deg, iana_tz)
GAZETTEER = {
    # Argentina
    ("buenosaires", "buenosaires", "argentina"): (-34.6037, -58.3816, "America/Argentina/Buenos_Aires"),
    # Australia
    ("melbourne", "victoria", "australia"): (-37.8136, 144.9631, "Australia/Melbourne"),
    # Austria
    ("graz", "styria", "austria"): (47.0707, 15.4395, "Europe/Vienna"),
    # Brazil
    ("riodejaneiro", "riodejaneiro", "brazil"): (-22.9068, -43.1729, "America/Sao_Paulo"),
    ("saopaulo", "saopaulo", "brazil"): (-23.5505, -46.6333, "America/Sao_Paulo"),
    # Canada
    ("london", "ontario", "canada"): (42.9849, -81.2453, "America/Toronto"),
    # China — Xining is in Qinghai province; spreadsheet says "Xinghai" (a county). Use Xining city coords.
    ("xining", "xinghai", "china"): (36.6171, 101.7782, "Asia/Shanghai"),
    # France
    ("brest", "bretagne", "france"): (48.3904, -4.4861, "Europe/Paris"),
    ("paris", "iledefrance", "france"): (48.8566, 2.3522, "Europe/Paris"),
    # Italy
    ("urbino", "marche", "italy"): (43.7263, 12.6365, "Europe/Rome"),
    # Japan
    ("tokyo", "tokyo", "japan"): (35.6762, 139.6503, "Asia/Tokyo"),
    # Panama
    ("colon", "colon", "panama"): (9.3547, -79.9001, "America/Panama"),
    # Portugal — Madeira
    ("funchal", "madiera", "portugal"): (32.6669, -16.9241, "Atlantic/Madeira"),
    # Puerto Rico
    ("sanjuan", "sanjuan", "puertorico"): (18.4655, -66.1057, "America/Puerto_Rico"),
    # Spain — Manacor, Balearic Islands
    ("manacor", "balears", "spain"): (39.5697, 3.2089, "Europe/Madrid"),
    # United Kingdom
    # Note: spreadsheet has "Oldham, BuenosAires, UnitedKingdom" — Oldham is in Greater Manchester, England.
    ("oldham", "buenosaires", "unitedkingdom"): (53.5409, -2.1114, "Europe/London"),
    ("chester", "cheshire", "unitedkingdom"): (53.1934, -2.8931, "Europe/London"),
    ("frodsham", "cheshire", "unitedkingdom"): (53.2932, -2.7270, "Europe/London"),
    ("winchester", "hampshire", "unitedkingdom"): (51.0632, -1.3080, "Europe/London"),
    ("sevensisters", "neathporttalbot", "unitedkingdom"): (51.7700, -3.7300, "Europe/London"),
    ("westonsupermare", "northsomerset", "unitedkingdom"): (51.3461, -2.9772, "Europe/London"),
    ("blackheath", "westmidlands", "unitedkingdom"): (52.4839, -2.0235, "Europe/London"),
    # United States — California
    ("concord", "california", "unitedstates"): (37.9780, -122.0311, "America/Los_Angeles"),
    ("elcentro", "california", "unitedstates"): (32.7920, -115.5631, "America/Los_Angeles"),
    ("hayward(alameda)", "california", "unitedstates"): (37.6688, -122.0808, "America/Los_Angeles"),
    ("hollywood", "california", "unitedstates"): (34.0928, -118.3287, "America/Los_Angeles"),
    ("inglewood", "california", "unitedstates"): (33.9617, -118.3531, "America/Los_Angeles"),
    ("longbeach", "california", "unitedstates"): (33.7701, -118.1937, "America/Los_Angeles"),
    ("losangeles", "california", "unitedstates"): (34.0522, -118.2437, "America/Los_Angeles"),
    ("newportbeach", "california", "unitedstates"): (33.6189, -117.9298, "America/Los_Angeles"),
    ("oakland", "california", "unitedstates"): (37.8044, -122.2712, "America/Los_Angeles"),
    ("pomona", "california", "unitedstates"): (34.0551, -117.7500, "America/Los_Angeles"),
    ("sanleandro", "california", "unitedstates"): (37.7249, -122.1561, "America/Los_Angeles"),
    ("sanluisobispo", "california", "unitedstates"): (35.2828, -120.6596, "America/Los_Angeles"),
    ("santabarbara", "california", "unitedstates"): (34.4208, -119.6982, "America/Los_Angeles"),
    ("santamonica", "california", "unitedstates"): (34.0195, -118.4912, "America/Los_Angeles"),
    # United States — DC
    ("washington", "districtofcolumbia", "unitedstates"): (38.9072, -77.0369, "America/New_York"),
    # United States — Hawaii
    ("honolulu", "hawaii", "unitedstates"): (21.3069, -157.8583, "Pacific/Honolulu"),
    # United States — Illinois
    ("chicago", "illinois", "unitedstates"): (41.8781, -87.6298, "America/Chicago"),
    # United States — Massachusetts
    ("boston", "massachusetts", "unitedstates"): (42.3601, -71.0589, "America/New_York"),
    ("fallriver", "massachusetts", "unitedstates"): (41.7015, -71.1550, "America/New_York"),
    ("greenfield", "massachusetts", "unitedstates"): (42.5876, -72.5995, "America/New_York"),
    # United States — Michigan
    ("flint", "michigan", "unitedstates"): (43.0125, -83.6875, "America/Detroit"),
    ("royaloak", "michigan", "unitedstates"): (42.4895, -83.1446, "America/Detroit"),
    ("saginaw", "michigan", "unitedstates"): (43.4195, -83.9508, "America/Detroit"),
    # United States — Mississippi
    ("kosciusko", "mississippi", "unitedstates"): (33.0579, -89.5867, "America/Chicago"),
    ("mccomb", "mississippi", "unitedstates"): (31.2438, -90.4534, "America/Chicago"),
    # United States — New Hampshire
    ("nashua", "newhampshire", "unitedstates"): (42.7654, -71.4676, "America/New_York"),
    # United States — New Jersey
    ("jerseycity", "newjersey", "unitedstates"): (40.7178, -74.0431, "America/New_York"),
    ("newark", "newjersey", "unitedstates"): (40.7357, -74.1724, "America/New_York"),
    # United States — New Mexico
    ("roswell", "newmexico", "unitedstates"): (33.3943, -104.5230, "America/Denver"),
    # United States — New York
    ("bayshore", "newyork", "unitedstates"): (40.7251, -73.2454, "America/New_York"),
    ("brooklyn(kings)", "newyork", "unitedstates"): (40.6782, -73.9442, "America/New_York"),
    ("jamaica", "newyork", "unitedstates"): (40.6915, -73.8068, "America/New_York"),
    ("newyork", "newyork", "unitedstates"): (40.7128, -74.0060, "America/New_York"),
    ("statenisland", "newyork", "unitedstates"): (40.5795, -74.1502, "America/New_York"),
    # United States — Ontario (this is actually Newmarket, Ontario, Canada per Carrey's birth, but spreadsheet has UnitedStates)
    # We'll honor the spreadsheet but use the correct Newmarket, Ontario coords/tz since that's clearly the city.
    ("newmarket", "ontario", "unitedstates"): (44.0592, -79.4613, "America/Toronto"),
    # United States — Pennsylvania
    ("newcastle(lawrence)", "pennsylvania", "unitedstates"): (40.9979, -80.3470, "America/New_York"),
    ("philadelphia", "pennsylvania", "unitedstates"): (39.9526, -75.1652, "America/New_York"),
    # United States — Tennessee
    ("memphis", "tennessee", "unitedstates"): (35.1495, -90.0490, "America/Chicago"),
    ("sevierville", "tennessee", "unitedstates"): (35.8681, -83.5619, "America/New_York"),
    # United States — Texas
    ("dallas", "texas", "unitedstates"): (32.7767, -96.7970, "America/Chicago"),
    ("grandprairie", "texas", "unitedstates"): (32.7460, -96.9978, "America/Chicago"),
    ("longview", "texas", "unitedstates"): (32.5007, -94.7405, "America/Chicago"),
    ("waco", "texas", "unitedstates"): (31.5493, -97.1467, "America/Chicago"),
    # United States — Virginia
    ("tappahannock", "virginia", "unitedstates"): (37.9243, -76.8597, "America/New_York"),
    # United States — Washington
    ("seattle", "washington", "unitedstates"): (47.6062, -122.3321, "America/Los_Angeles"),
    # Yemen
    ("aden", "aden", "yemen"): (12.7855, 45.0187, "Asia/Aden"),
}


def _norm(s):
    return "".join(str(s).lower().split()).replace(",", "").replace(".", "")


def lookup(town, state, country):
    key = (_norm(town), _norm(state), _norm(country))
    if key not in GAZETTEER:
        raise KeyError(f"No gazetteer entry for {key}")
    return GAZETTEER[key]
