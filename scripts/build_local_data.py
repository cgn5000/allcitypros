"""Build the compact federal datasets the guide generator reads.

    python3 scripts/build_local_data.py RAW_DIR

RAW_DIR must hold the raw downloads (not committed, too large):
  cbp23co.txt          Census County Business Patterns 2023, county file
                       https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23co.zip
  oews.json            BLS OEWS May 2025 annual median wages, one value per series id
                       (OEUM00<CBSA>000000<SOC>13), pulled from the BLS Public Data API
                       https://api.bls.gov/publicAPI/v1/timeseries/data/
  noaa.json            NOAA NCEI U.S. Climate Normals 1991-2020 (annual/seasonal), nearest
                       first-order station per city, from
                       https://www.ncei.noaa.gov/data/normals-annualseasonal/1991-2020/access/<STATION>.csv

Inputs already committed in scripts/local_data/:
  places.json      city -> Census place, county FIPS, CBSA (Census Gazetteer 2024 + Census Geocoder)
  licensing.json   state -> trade -> licensing body, lookup URL, rules (hand-researched, official sources)
  permits.json     city -> official building-permit page (hand-researched, official sources)

Writes scripts/local_data/cbp.json, oews.json, climate.json. Nothing is estimated: a missing
value stays missing and the page omits it.
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "local_data")

# NAICS 2022 codes used for "how many firms" (CBP). Labels are Census's industry titles.
NAICS = {
    "238220": "Plumbing, heating and air-conditioning contractors",
    "238210": "Electrical contractors and other wiring installation contractors",
    "238160": "Roofing contractors",
    "236118": "Residential remodelers",
    "541110": "Offices of lawyers",
    "561730": "Landscaping services",
    "238320": "Painting and wall covering contractors",
    "238330": "Flooring contractors",
    "561710": "Exterminating and pest control services",
    "561720": "Janitorial services",
    "484210": "Used household and office goods moving",
    "561621": "Security systems services (except locksmiths)",
    "811111": "General automotive repair",
    "812910": "Pet care (except veterinary) services",
    "611691": "Exam preparation and tutoring",
    "541211": "Offices of certified public accountants",
    "522310": "Mortgage and nonmortgage loan brokers",
    "541810": "Advertising agencies",
    "541512": "Computer systems design services",
}
SOC = ["499021", "472152", "472111", "472181", "472031", "231011"]


def num(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def build_cbp(raw, places):
    want = {}
    for slug, p in places.items():
        f = p["county_fips"]
        for code in (f if isinstance(f, list) else [f]):
            want.setdefault(code, []).append(slug)
    rows = {}
    with open(os.path.join(raw, "cbp23co.txt"), newline="") as fh:
        for r in csv.DictReader(fh):
            fips = r["fipstate"] + r["fipscty"]
            if fips in want and r["naics"] in NAICS:
                small = sum(num(r[k]) or 0 for k in ("n<5", "n5_9"))
                rows[(fips, r["naics"])] = dict(est=num(r["est"]), emp=num(r["emp"]),
                                                 emp_flag=r["emp_nf"], small=small,
                                                 payroll_k=num(r["ap"]))
    out = {}
    for slug, p in places.items():
        f = p["county_fips"]
        codes = f if isinstance(f, list) else [f]
        out[slug] = {}
        for n in NAICS:
            parts = [rows[(c, n)] for c in codes if (c, n) in rows]
            if not parts:
                continue  # no published row: say nothing rather than print 0
            agg = {k: sum(x[k] or 0 for x in parts) for k in ("est", "emp", "small", "payroll_k")}
            agg["noisy"] = any(x["emp_flag"] == "J" for x in parts)
            out[slug][n] = agg
    return out


def build_oews(raw, places):
    series = json.load(open(os.path.join(raw, "oews.json")))
    out = {}
    for cbsa in sorted({p["cbsa"] for p in places.values()}):
        vals = {}
        for soc in SOC:
            v = series.get(f"OEUM00{cbsa}000000{soc}13")
            if v and v.replace(".", "").isdigit():
                vals[soc] = int(float(v))
        out[cbsa] = vals
    return out


def main():
    raw = sys.argv[1]
    places = json.load(open(os.path.join(OUT, "places.json")))
    meta = {"naics": NAICS}
    cbp = build_cbp(raw, places)
    json.dump({"meta": meta, "data": cbp}, open(os.path.join(OUT, "cbp.json"), "w"), indent=0, sort_keys=True)
    json.dump(build_oews(raw, places), open(os.path.join(OUT, "oews.json"), "w"), indent=0, sort_keys=True)
    noaa = json.load(open(os.path.join(raw, "noaa.json")))
    json.dump(noaa, open(os.path.join(OUT, "climate.json"), "w"), indent=0, sort_keys=True)
    print("cbp cities", len(cbp), "oews metros", len(json.load(open(os.path.join(OUT, "oews.json")))),
          "climate", len(noaa))


if __name__ == "__main__":
    main()
