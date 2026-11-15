"""Render real, cited local data (licensing, permits, Census CBP, BLS OEWS, NOAA normals) as HTML.

Every figure on a page carries its source and the date it was checked. Nothing here is estimated:
if a dataset has no value for a city, the block or row is left out.
"""
import html, json, os, re
from urllib.parse import urlsplit

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "local_data")


def _load(name):
    return json.load(open(os.path.join(D, name)))


PLACES = _load("places.json")
LIC = _load("licensing.json")
PERMITS = _load("permits.json")
_cbp = _load("cbp.json")
CBP, NAICS = _cbp["data"], _cbp["meta"]["naics"]
OEWS = _load("oews.json")
CLIMATE = _load("climate.json")

CHECKED = "November 15, 2026"
CBP_YEAR = "2023"
OEWS_PERIOD = "May 2025"
CBP_URL = "https://www.census.gov/programs-surveys/cbp.html"
NORMALS_URL = "https://www.ncei.noaa.gov/products/land-based-station/us-climate-normals"

# Services with state licensing research. Their city pages carry enough local data to be indexable.
CORE = ("hvac", "plumbing", "electrical", "roofing", "general_contracting", "legal")
CLIMATE_SERVICES = ("hvac", "roofing")
TRADE_NAME = {"hvac": "HVAC", "plumbing": "Plumbing", "electrical": "Electrical", "roofing": "Roofing",
              "general_contracting": "General / home-improvement contracting", "legal": "Attorneys"}

# service -> NAICS industry for "how many firms" (CBP)
SERVICE_NAICS = {
    "hvac": "238220", "plumbing": "238220", "electrical": "238210", "roofing": "238160",
    "general_contracting": "236118", "legal": "541110", "landscaping": "561730", "painting": "238320",
    "flooring": "238330", "pest_control": "561710", "residential_cleaning": "561720",
    "moving": "484210", "home_security": "561621", "auto_repair": "811111", "pet_services": "812910",
    "tutoring": "611691", "accounting": "541211", "mortgage": "522310", "digital_marketing": "541810",
    "it_services": "541512",
}
# Caveats where the Census industry is broader or narrower than the service.
NAICS_NOTE = {
    "hvac": "Census counts HVAC and plumbing contractors together in one industry.",
    "plumbing": "Census counts plumbing and HVAC contractors together in one industry.",
    "general_contracting": "Residential remodelers only; new-home builders are counted separately.",
    "residential_cleaning": "Census counts house cleaning within janitorial services, which also includes commercial cleaning.",
    "moving": "Movers of household and office goods.",
    "home_security": "Alarm and security-system installers and monitors, excluding locksmiths.",
    "auto_repair": "General automotive repair shops only (not body, glass or transmission specialists).",
    "pet_services": "Grooming, boarding, sitting and training; veterinarians are excluded.",
    "mortgage": "Mortgage and loan brokers; banks and direct lenders are counted elsewhere.",
    "digital_marketing": "Advertising agencies; marketing consultancies are counted separately.",
    "it_services": "Computer systems design firms.",
}
# service -> (SOC code, occupation title) for "what workers earn" (OEWS)
SERVICE_SOC = {
    "hvac": ("499021", "Heating, air conditioning and refrigeration mechanics and installers"),
    "plumbing": ("472152", "Plumbers, pipefitters and steamfitters"),
    "electrical": ("472111", "Electricians"),
    "roofing": ("472181", "Roofers"),
    "general_contracting": ("472031", "Carpenters"),
    "legal": ("231011", "Lawyers"),
}


def esc(s):
    return html.escape(str(s), quote=True)


def n(x):
    return f"{x:,}"


def money(x):
    return f"${x:,}"


def county_label(city):
    p = PLACES[city]
    return p["county"]


def cbsa_name(city):
    return PLACES[city]["cbsa_name"].replace(" Metro Area", " metro area")


def oews_url(city):
    return f"https://data.bls.gov/oes/#/area/00{PLACES[city]['cbsa']}/2025"


def station_url(city):
    return f"https://www.ncei.noaa.gov/data/normals-annualseasonal/1991-2020/access/{CLIMATE[city]['station']}.csv"


def ext(url, text):
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(text)}</a>'


def host(url):
    return urlsplit(url).netloc.replace("www.", "")


def src(*parts):
    return '<p class="g-src">' + " ".join(parts) + "</p>"


# ---------------------------------------------------------------- licensing

def lic(st, cat):
    return LIC.get(st, {}).get(cat)


# Several cities share a county (and so the same Census and climate figures). Only the largest city in
# each shared county is indexable; the others keep their page (own permit office) but stay noindex so
# Google does not see near-identical data pages.
COUNTY_PRINCIPAL = {
    "06059": "anaheim", "48439": "fortworth", "12071": "capecoral", "04013": "phoenix", "12103": "stpetersburg",
    "48113": "dallas", "06067": "sacramento", "06071": "fontana", "06001": "oakland", "48085": "plano",
    "06037": "losangeles", "32003": "lasvegas", "12086": "miami", "06065": "riverside",
}


def principal(city):
    return COUNTY_PRINCIPAL.get(str(PLACES[city]["county_fips"]), city)


def is_indexable(city, cat):
    return has_core_data(city, cat) and principal(city) == city


def has_core_data(city, cat):
    st = PLACES[city]["st"]
    return cat in CORE and lic(st, cat) is not None and SERVICE_NAICS[cat] in CBP.get(city, {})


def licensing_block(city, cat, state, heading):
    e = lic(PLACES[city]["st"], cat)
    if not e:
        return ""
    out = [f"<h2>{esc(heading)}</h2>"]
    rows = []
    if e.get("level") == "state" and e.get("agency"):
        agency = ext(e["agency_url"], e["agency"]) if e.get("agency_url") else esc(e["agency"])
        rows.append(("Who licenses it", agency))
    else:
        rows.append(("Who licenses it", f"No statewide license in {esc(state)}; cities and counties set the rules"))
    if e.get("threshold"):
        rows.append(("When a license is required", esc(e["threshold"])))
    if e.get("insurance_bond"):
        rows.append(("Insurance / bond", esc(e["insurance_bond"])))
    if e.get("lookup_url"):
        rows.append(("Check a license", ext(e["lookup_url"], "Official license lookup") +
                     f' <span class="g-small">({esc(host(e["lookup_url"]))})</span>'))
    out.append(f"<p>{esc(e['summary'])}</p>")
    out.append('<table class="g-table g-facts"><tbody>' +
               "".join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a, b in rows) + "</tbody></table>")
    s = e.get("source_url") or e.get("agency_url")
    if s:
        out.append(src(f"Source: {ext(s, host(s))}, checked {CHECKED}. Rules change; confirm with the agency before you sign a contract."))
    return "".join(out)


def permit_block(city, name, cat):
    p = PERMITS.get(city)
    if not p or not p.get("url"):
        return ""
    what = {"hvac": "replacing or adding heating and cooling equipment",
            "plumbing": "water heaters, gas lines and repiping",
            "electrical": "panel upgrades, new circuits and EV chargers",
            "roofing": "re-roofing and structural roof repairs",
            "general_contracting": "remodels, additions and structural work"}.get(cat)
    body = (f"Residential building permits for {esc(name)} are issued by {ext(p['url'], p['issuer'])}. ")
    if what:
        body += (f"Permits are commonly required for {what}. Ask your contractor who will pull the permit "
                 f"and book the inspections; a contractor who asks you to pull it yourself is a warning sign.")
    return (f"<h2>Building permits in {esc(name)}</h2><p>{body}</p>" +
            src(f"Official permit office page, checked {CHECKED}."))


# ---------------------------------------------------------------- market (CBP + OEWS)

def _rank_pct(value, values):
    below = sum(1 for v in values if v < value)
    return round(100 * below / max(1, len(values) - 1))


_ALL_WAGES = {soc: sorted(v[soc] for v in OEWS.values() if soc in v) for soc, _ in SERVICE_SOC.values()}


def market_block(city, cat, name, label):
    naics = SERVICE_NAICS.get(cat)
    c = CBP.get(city, {}).get(naics) if naics else None
    wage = None
    if cat in SERVICE_SOC:
        soc, occ = SERVICE_SOC[cat]
        wage = OEWS.get(PLACES[city]["cbsa"], {}).get(soc)
    if not c and not wage:
        return ""
    county = county_label(city)
    rows, notes = [], []
    if c:
        ind = NAICS[naics]
        rows.append((f"Business locations ({esc(ind.lower())}) in {esc(county)}", n(c["est"])))
        rows.append(("People employed at those locations", n(c["emp"]) + ("*" if c["noisy"] else "")))
        if c["est"]:
            share = round(100 * c["small"] / c["est"])
            rows.append(("Share with fewer than 10 employees", f"{share}%"))
        if c["emp"] and c["payroll_k"]:
            rows.append(("Average annual payroll per employee", money(int(round(c["payroll_k"] * 1000 / c["emp"], -2)))))
    if wage:
        rows.append((f"Median annual wage, {esc(occ.lower())}, {esc(cbsa_name(city))}", money(wage)))
    out = [f"<h2>{esc(name)}'s {esc(label.lower() if label != 'HVAC' else label)} market: firms and pay</h2>"]
    intro = []
    if c:
        intro.append(f"Census County Business Patterns counted {n(c['est'])} business locations with paid employees "
                     f"in {esc(county)} in {CBP_YEAR} in the industry “{esc(NAICS[naics].lower())},” "
                     f"employing {n(c['emp'])} people.")
    if wage:
        pct = _rank_pct(wage, _ALL_WAGES[soc])
        rel = ("higher than in most of" if pct >= 60 else "lower than in most of" if pct <= 40 else "close to the middle of")
        intro.append(f"The median annual wage for {esc(occ.lower())} in the {esc(cbsa_name(city))} was {money(wage)} "
                     f"({OEWS_PERIOD}), {rel} the {len(_ALL_WAGES[soc])} metro areas we cover. "
                     + ("Local pay levels feed into the hourly rates firms charge." if cat == "legal" else "Local pay levels feed directly into labor rates on quotes."))
    out.append(f"<p>{' '.join(intro)}</p>")
    out.append('<table class="g-table g-facts"><tbody>' +
               "".join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a, b in rows) + "</tbody></table>")
    if NAICS_NOTE.get(cat):
        notes.append(esc(NAICS_NOTE[cat]))
    if c and c["noisy"]:
        notes.append("*Census adds noise to protect confidentiality; this employment figure is less precise.")
    s = []
    if c:
        s.append(f"{ext(CBP_URL, 'U.S. Census Bureau, County Business Patterns ' + CBP_YEAR)} (NAICS {naics}; employer establishments only, so self-employed one-person businesses are not counted)")
    if wage:
        s.append(f"{ext(oews_url(city), 'BLS Occupational Employment and Wage Statistics, ' + OEWS_PERIOD)} (SOC {soc[:2]}-{soc[2:]})")
    out.append(src(" ".join(notes) + (" " if notes else "") + "Sources: " + "; ".join(s) + f". Checked {CHECKED}."))
    return "".join(out)


# ---------------------------------------------------------------- climate (NOAA normals)

_HDD = sorted(v["hdd"] for v in CLIMATE.values())
_CDD = sorted(v["cdd"] for v in CLIMATE.values())


def climate_block(city, cat, name):
    k = CLIMATE.get(city)
    if not k or cat not in CLIMATE_SERVICES:
        return ""
    hdd, cdd = k["hdd"], k["cdd"]
    more_heat = sum(1 for v in _HDD if v < hdd)
    more_cool = sum(1 for v in _CDD if v < cdd)
    total = len(_HDD)
    if hdd >= 2 * max(cdd, 1):
        balance = "Heating demand is far larger than cooling demand here"
    elif cdd >= 2 * max(hdd, 1):
        balance = "Cooling demand is far larger than heating demand here"
    else:
        balance = "Heating and cooling demand are both significant here"
    rows = [("Heating degree days (base 65&deg;F)", n(hdd)),
            ("Cooling degree days (base 65&deg;F)", n(cdd))]
    if k.get("tavg") is not None:
        rows.append(("Average annual temperature", f"{k['tavg']:.1f}&deg;F"))
    if k.get("prcp") is not None:
        rows.append(("Average annual precipitation", f"{k['prcp']:.1f} in"))
    if k.get("snow") is not None:
        rows.append(("Average annual snowfall", f"{k['snow']:.1f} in"))
    if cat == "hvac":
        why = (f"{balance}. {esc(name)} has more heating degree days than {more_heat} of the {total} cities we cover "
               f"and more cooling degree days than {more_cool}. Degree days track how hard a system works over a year, "
               "so they are a fair guide to whether to prioritize furnace or heat-pump heating capacity, cooling "
               "capacity and dehumidification, and how quickly an efficiency upgrade pays back.")
    else:
        bits = []
        if k.get("prcp") is not None:
            pr = [v["prcp"] for v in CLIMATE.values() if v.get("prcp") is not None]
            wetter = sum(1 for v in pr if v < k["prcp"])
            bits.append(f"{esc(name)} averages {k['prcp']:.1f} inches of precipitation a year, more than {wetter} of the {len(pr)} cities we have this figure for")
        if k.get("snow"):
            bits.append(f", and about {k['snow']:.0f} inches of snow, so ask about ice-and-water shield at eaves and valleys and the roof's snow-load rating" if k["snow"] >= 10
                        else f", and only about {k['snow']:.0f} inches of snow")
        why = (("".join(bits) + ". ") if bits else "") + (
            f"With {n(cdd)} cooling degree days, heat and UV exposure {'are a major factor in shingle aging and attic ventilation' if cdd >= 2000 else 'are a moderate factor'}; "
            f"with {n(hdd)} heating degree days, {'freeze-thaw cycles and ice dams deserve attention' if hdd >= 4000 else 'freeze-thaw damage is less of a concern'}.")
    st_name = re.sub(r",\s*[A-Z]{2}\s+US$", "", k["station_name"]).title()
    st_name = re.sub(r"\bAp\b", "Airport", st_name).replace(" Intl", " International")
    return (f"<h2>{esc(name)} climate and what it means for {'heating and cooling' if cat == 'hvac' else 'your roof'}</h2>"
            f"<p>{why}</p>"
            '<table class="g-table g-facts"><tbody>' +
            "".join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a, b in rows) + "</tbody></table>" +
            src(f"Source: {ext(station_url(city), 'NOAA NCEI U.S. Climate Normals 1991-2020')}, station {esc(st_name)} ({k['station']}). "
                f"30-year averages, not a forecast. Checked {CHECKED}."))


# ---------------------------------------------------------------- city hub blocks

def city_license_table(city, state):
    st = PLACES[city]["st"]
    rows = []
    for cat in CORE:
        e = lic(st, cat)
        if not e:
            continue
        who = esc(e["agency"]) if e.get("level") == "state" and e.get("agency") else "Cities and counties (no state license)"
        look = ext(e["lookup_url"], "Check a license") if e.get("lookup_url") else '<span class="g-small">No online state lookup</span>'
        rows.append(f'<tr><td><a href="/guides/{city}-{cat.replace("_", "-")}">{esc(TRADE_NAME[cat])}</a></td><td>{who}</td><td>{look}</td></tr>')
    if not rows:
        return ""
    return (f"<h2>Who licenses contractors and lawyers in {esc(state)}</h2>"
            '<table class="g-table g-wide"><thead><tr><th>Trade</th><th>Licensed by</th><th>Verify</th></tr></thead>'
            f"<tbody>{''.join(rows)}</tbody></table>" +
            src(f"Compiled from each state agency's official site, checked {CHECKED}. Details and sources are on each trade page."))


def city_market_table(city, cats_labels):
    data = CBP.get(city, {})
    rows = []
    for cat, label in cats_labels:
        nc = SERVICE_NAICS.get(cat)
        if nc and nc in data and cat != "plumbing":  # plumbing shares HVAC's industry; list it once
            lab = "HVAC &amp; plumbing" if cat == "hvac" else esc(label)
            rows.append(f'<tr><td><a href="/guides/{city}-{cat.replace("_", "-")}">{lab}</a></td>'
                        f'<td>{esc(NAICS[nc])}</td><td>{n(data[nc]["est"])}</td><td>{n(data[nc]["emp"])}</td></tr>')
    if not rows:
        return ""
    return (f"<h2>Local businesses by trade in {esc(county_label(city))}</h2>"
            "<p>How many employer businesses each trade has locally, from the Census Bureau's County Business Patterns.</p>"
            '<table class="g-table g-wide"><thead><tr><th>Service</th><th>Census industry</th><th>Locations</th><th>Employees</th></tr></thead>'
            f"<tbody>{''.join(rows)}</tbody></table>" +
            src(f"Source: {ext(CBP_URL, 'U.S. Census Bureau, County Business Patterns ' + CBP_YEAR)}. Employer establishments only. Checked {CHECKED}."))


def city_climate_line(city, name):
    k = CLIMATE.get(city)
    if not k:
        return ""
    return (f"<h2>{esc(name)} climate at a glance</h2><p>{esc(name)} averages {n(k['hdd'])} heating degree days and "
            f"{n(k['cdd'])} cooling degree days a year"
            + (f", with {k['prcp']:.1f} inches of precipitation" if k.get("prcp") is not None else "") +
            ". That shapes HVAC sizing and roofing choices; see the HVAC and roofing pages for what it means.</p>" +
            src(f"Source: {ext(station_url(city), 'NOAA NCEI U.S. Climate Normals 1991-2020')}, station {k['station']}. Checked {CHECKED}."))


# ---------------------------------------------------------------- service hub block

def state_license_table(cat, state_names, cities_by_state):
    rows = []
    for st in sorted(LIC, key=lambda s: state_names[s]):
        e = LIC[st].get(cat)
        if not e:
            continue
        who = esc(e["agency"]) if e.get("level") == "state" and e.get("agency") else "Local (cities and counties)"
        look = ext(e["lookup_url"], "Check a license") if e.get("lookup_url") else "&mdash;"
        cities = cities_by_state.get(st, [])
        links = ", ".join(f'<a href="/guides/{c}-{cat.replace("_", "-")}">{esc(nm)}</a>' for c, nm in cities[:4])
        more = f" +{len(cities) - 4} more" if len(cities) > 4 else ""
        rows.append(f"<tr><td><strong>{esc(state_names[st])}</strong><br><span class=\"g-small\">{links}{more}</span></td>"
                    f"<td>{who}</td><td>{look}</td></tr>")
    return ("<h2>Licensing by state</h2><p>Who issues the license in each state we cover, and where to check one. "
            "City pages add the rules, thresholds, local permit office, firm counts and wages.</p>"
            '<table class="g-table g-wide"><thead><tr><th>State</th><th>Licensed by</th><th>Verify</th></tr></thead>'
            f"<tbody>{''.join(rows)}</tbody></table>" +
            src(f"Compiled from official state agency and state bar sites, checked {CHECKED}."))
