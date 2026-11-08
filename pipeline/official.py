"""Official records for Missouri -> one table of licensed businesses (playbook/12-sources.md).

Missouri has no statewide inspection data: DHSS sets the rules, local agencies inspect, and the jurisdictions that post official grades
or scores (St. Louis City's letter grade, St. Charles County's "Know the Score", Jefferson County's "Scan for the Score") do so behind
browse-only portals and "I am human" checks: linked, never read, until Nick decides. Kansas City's and the other portals are search-only.
The statewide open list is the Division of Alcohol and Tobacco Control's active alcohol licenses (data.mo.gov, mo.gov/data-policy): its
by-the-drink licenses say which places pour alcohol; package licenses mark stores. DBA names only; licensee names are never kept.

load() returns: jur, lic (our id), name, keys (name keys), addr, city, zip, num, street, lat, lon, kind, active, ltype, insp, biz.
"""
import os, re, json, datetime
import numpy as np, pandas as pd
from common import norm_name, RAW, name_sim, _stems, GENERIC, canon_city

OFF = os.path.join(RAW, "official")
DIRS = {"N": "N", "S": "S", "E": "E", "W": "W", "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W"}
TYPES = set("ST STREET AVE AV AVENUE BLVD BOULEVARD RD ROAD DR DRIVE LN LANE CT COURT PL PLACE PKWY PARKWAY TER TRL TRAIL WAY HWY CIR "
            "CIRCLE PLZ SQ MALL BND PASS XING RUN ROW WALK RDG LOOP FWY FREEWAY EXPY EXPRESSWAY PIKE PK PKE".split())


def road(a):
    """One spelling for numbered roads. Missouri writes one road as 'Route 100', 'US 7', 'Rt 2', 'MO 100' or 'MO Route 100', so every
    numbered US or state route is 'SH n' (as in ri-eats); 'N INTERSTATE 95' = 'I-95'; 'COUNTY ROAD 5' = 'CR 5'."""
    a = re.sub(r"(\d)\s*&\s*(\d)", r"\1-\2", a.upper())
    a = re.sub(r"\b(US|MO|SR|SH|CR|I|IH|RT|RTE)-(\w)", r"\1 \2", a)
    a = re.sub(r"\b(?:INTERSTATE(?: HIGHWAY| HWY)?|IH|I H)\s*(?=\d)", "I ", a)
    a = re.sub(r"\b(?:US|U S)\s+(?:HIGHWAY|HWY)\b", "US", a)
    a = re.sub(r"\b(?:FARM[- ]TO[- ]MARKET(?: ROAD| RD)?|FARM (?:ROAD|RD)|F M)\b", "FM", a)
    a = re.sub(r"\b(?:RANCH[- ]TO[- ]MARKET(?: ROAD| RD)?|RANCH (?:ROAD|RD)|RR|RM)\b(?=\s*\d)", "RM", a)
    a = re.sub(r"\b(?:STATE (?:HIGHWAY|HWY|ROAD|RD|ROUTE|RTE)|SR|SH|VERMONT (?:ROUTE|RTE|HIGHWAY|HWY)|MO (?:ROUTE|RTE|RT|HIGHWAY|HWY)|MO|"
               r"US (?:ROUTE|RTE|RT)|US|ROUTE|RTE|RT|HWY)\b\.?(?=\s*\d)", "SH", a)
    a = re.sub(r"\b(?:COUNTY (?:HIGHWAY|HWY|ROAD|RD)|CO RD|CTY (?:HWY|RD)|CR)\b", "CR", a)
    a = re.sub(r"\bHIGHWAY\b", "HWY", a)
    return re.sub(r"\b(US|SH|CR|HWY|FM|RM|I) (\w+)\s*-\s*\w+", r"\1 \2", a)


ORD = {"FIRST": "1ST", "SECOND": "2ND", "THIRD": "3RD", "FOURTH": "4TH", "FIFTH": "5TH", "SIXTH": "6TH", "SEVENTH": "7TH",
       "EIGHTH": "8TH", "NINTH": "9TH", "TENTH": "10TH", "ELEVENTH": "11TH", "TWELFTH": "12TH"}


def street_key(a):
    """'2505 Monroe St' -> ('2505', 'MONROE'); '1000 OSAGE STREET' -> ('1000', 'OSAGE'); 'E Colfax Ave' keeps 'COLFAX'."""
    if not isinstance(a, str):
        return None, None
    a = re.sub(r"[.,#]", " ", road(a))
    # "20940-A North Frederick Ave": a hyphenated unit letter is part of the number (Maryland's Montgomery County wrote them so)
    m = re.match(r"^\s*(\d+)(?:-?[A-Z])?(?:\s*-\s*\d+[A-Z]?)?\s+(.*)$", a)
    if not m:
        return None, None
    words = [w for w in m.group(2).split() if w]
    if len(words) > 1 and words[0] in DIRS:
        words = words[1:]
    core = []
    for w in words:
        if w in TYPES and core:
            break
        core.append(w)
    core = [ORD.get(w, w) for w in core]
    return m.group(1), " ".join(core[:3]) or None


def street_compat(a, b):
    """Same street, or one is a whole-word prefix of the other: Boulder's 2025 set sometimes truncates ("1206 CENTAUR" = Centaur Village Dr)."""
    if not isinstance(a, str) or not isinstance(b, str) or not a or not b:
        return False
    return a == b or a.startswith(b + " ") or b.startswith(a + " ")


def street_nums(a):
    """'157-159 W Main St' -> {'157', '159'}; '2505 Monroe St' -> {'2505'}."""
    if not isinstance(a, str):
        return set()
    a = road(a)
    m = re.match(r"^\s*(\d+)[A-Z]?(?:\s*-\s*(\d+)[A-Z]?)?\s", a.upper() + " ")
    if not m:
        return set()
    lo = int(m.group(1)); hi = int(m.group(2)) if m.group(2) else lo
    if hi < lo:   # "1500-02"
        hi = int(str(lo)[: len(str(lo)) - len(m.group(2))] + m.group(2)) if m.group(2) else lo
    return {str(x) for x in range(lo, hi + 1, 2 if (hi - lo) % 2 == 0 else 1)} if 0 <= hi - lo <= 12 else {str(lo)}


def _names(*vals):
    out = []
    for v in vals:
        if not isinstance(v, str):
            continue
        v = re.sub(r"\s*\((?:MOBILE|MOBILE UNIT|COMMISSARY|CATERING|SPECIAL EVENT|SPEC EVENT|TEMP(?:ORARY)? EVENT|CP|INSIDE [^)]*)\)\s*$", "", v, flags=re.I)
        for part in re.split(r"\s*/\s*|\s+\bdba\b\s+|\s+&\s+(?=[A-Z][a-z])", v, flags=re.I):
            k = norm_name(re.sub(r"\b(?:LLC|INC|CORP|CORPORATION|LTD|CO)\b\.?", "", part, flags=re.I))
            if k and k not in out:
                out.append(k)
    return out


META = json.load(open(os.path.join(OFF, "meta.json"))) if os.path.exists(os.path.join(OFF, "meta.json")) else {}
LIST_DATE = (META.get("moatc") or {}).get("edited") or (META.get("moatc") or {}).get("fetched")
FETCHED = (META.get("moatc") or {}).get("fetched")
# DHSS's food-safety page (local agencies publish their own inspections)
MONT_PAGE = "https://health.mo.gov/safety/foodsafety/"
INSPECTIONS_URL = "https://health.mo.gov/safety/foodsafety/"
RESULTS = ()
ONPREM_T = ("Missouri ATC by-the-drink license",)
RETAIL_T = "Missouri ATC package license"
DRINK_TYPES = {"Retail by Drink": ["beer", "wine", "liquor"], "Retail by Drink - Resort": ["beer", "wine", "liquor"],
               "Retail by Drink - Tax Exempt": ["beer", "wine", "liquor"], "Retail by Drink - Boat": ["beer", "wine", "liquor"],
               "Retail by Drink - Railroad": ["beer", "wine", "liquor"], "Retail by Drink - Mall": ["beer", "wine", "liquor"],
               "Retail by Drink - Entertainment District (KC)": ["beer", "wine", "liquor"], "Retail by Drink - Seasonal Resort": ["beer", "wine", "liquor"],
               "Beer & Light Wine by Drink": ["beer", "wine"], "Beer by Drink": ["beer"], "Missouri Produced Wine by the Drink": ["wine"]}
PACKAGE_TYPES = {"Original Package Liquor", "Original Package - Beer Only"}


def liq_kind(t):
    """A license type as shown -> on-premises or retail."""
    if not isinstance(t, str):
        return None
    return "onprem" if t in ONPREM_T else "retail" if "package" in t else None


COLUMNS = ["jur", "lic", "name", "dba", "holder", "keys", "addr", "city", "zip", "num", "street", "lat", "lon", "kind", "active", "ltype",
           "insp", "issued", "biz", "drinks", "county"]


def _zip(z):
    z = re.sub(r"\D", "", str(z or ""))
    return z[:5] if len(z) >= 5 else ""


def _addr(a):
    """'2790 VETERANS MEMORIAL BLVD STE 130' -> '2790 Veterans Memorial Blvd Ste 130'."""
    a = re.sub(r"\s+", " ", a or "").strip()
    return re.sub(r"\b([A-Z]{2,})\b", lambda m: m.group(1).title(), a)


def _city(c):
    return canon_city(" ".join(w.capitalize() for w in str(c or "").split())) if isinstance(c, str) and c.strip() else None


def _ms(v):
    """An ArcGIS date (epoch milliseconds, UTC) -> YYYY-MM-DD in Louisville's time (the inspector's own day)."""
    if not isinstance(v, (int, float)):
        return None
    d = datetime.datetime.fromtimestamp(v / 1000, datetime.timezone.utc) - datetime.timedelta(hours=5)
    return d.date().isoformat()


def load_moatc():
    """One row per license (the feed repeats a license once per secondary permit)."""
    rows, seen = [], set()
    for r in json.load(open(os.path.join(OFF, "moatc", "licenses.json"))):
        if r.get("primary_license") in seen:
            continue
        seen.add(r.get("primary_license"))
        if (r.get("state") or "").strip() != "Missouri":
            continue
        t = (r.get("primary_type") or "").strip()
        if t not in DRINK_TYPES and t not in PACKAGE_TYPES:
            continue
        name = re.sub(r"\s+", " ", r.get("dbaname") or "").strip()
        if not name:
            continue
        addr = _addr(" ".join(x for x in ((r.get("street_number") or "").strip(), (r.get("street") or "").strip()) if x))
        num, st = street_key(addr)
        rows.append({"jur": "moatc", "lic": f"moatc-{r.get('primary_license')}", "name": name, "dba": name, "holder": None, "keys": _names(name),
                     "addr": addr, "city": _city(r.get("city")), "zip": _zip(r.get("zipcode")), "num": num, "street": st, "lat": None, "lon": None,
                     "kind": "liquor", "active": True, "ltype": ONPREM_T[0] if t in DRINK_TYPES else RETAIL_T, "insp": [], "issued": None,
                     "drinks": DRINK_TYPES.get(t), "county": None})
    return rows


SGF_ARCHIVE = os.path.join(OFF, "springfield", "rss_archive.jsonl")
SGF_HD = "Springfield-Greene County Health Department"
# Greene County's towns, longest first: the feed writes "1821 W GRAND ST SPRINGFIELD" with the town last
SGF_TOWNS = sorted(["SPRINGFIELD", "REPUBLIC", "STRAFFORD", "WILLARD", "BATTLEFIELD", "ASH GROVE", "FAIR GROVE", "WALNUT GROVE",
                    "ROGERSVILLE", "BOIS D ARC", "BRIGHTON", "CAVE SPRING", "BROOKLINE", "NIXA", "OZARK"], key=len, reverse=True)


def sgf_result(d):
    """The feed's own words: 'Active; priority violations 1, nonpriority 1'."""
    return f"{d.get('result') or 'Inspected'}; priority violations {d.get('priority') or 0}, nonpriority {d.get('nonpriority') or 0}"


def load_springfield():
    """Springfield-Greene County's inspections, archived from its 7-day RSS feed (archive_sgf_rss.py, Nick's yes 2026-11-07): one
    record per establishment id with each archived inspection, the result and violation counts as the feed states them. The feed covers
    schools and stores too, so these rows only ever attach to a listing they match (kind "inspected")."""
    if not os.path.exists(SGF_ARCHIVE):
        return []
    by = {}
    for line in open(SGF_ARCHIVE):
        d = json.loads(line)
        al = re.sub(r"\s+", " ", d.get("address_line") or "").strip().upper()
        town = next((t for t in SGF_TOWNS if al.endswith(" " + t)), None)
        street = al[: -len(town)].strip() if town else al
        name = d["name"]
        m = re.match(r"^(.*?) - (\d.*)$", street)       # "JYMS INVESTMENTS LLC - COUNTRY MART - 5505 ...": the name had a dash
        if m:
            name, street = f"{name} - {m.group(1)}", m.group(2)
        rec = by.setdefault(d.get("est") or d["name"], {"name": name, "addr": street, "town": town, "insp": []})
        rec["insp"].append([d["date"], sgf_result(d), d.get("type") or "Inspection", f"sgf-{d.get('est')}-{d['date']}-{d.get('time')}"])
    rows = []
    for est, r in by.items():
        name = re.sub(r"\s+", " ", r["name"]).strip().title()
        addr = _addr(r["addr"])
        num, st = street_key(addr)
        rows.append({"jur": "sgf", "lic": f"sgf-{est}", "name": name, "dba": name, "holder": None, "keys": _names(r["name"]), "addr": addr,
                     "city": _city(r["town"]), "zip": "", "num": num, "street": st, "lat": None, "lon": None, "kind": "inspected",
                     "active": True, "ltype": SGF_HD + " inspection", "issued": None, "drinks": None, "county": "Greene County",
                     "insp": sorted(r["insp"], key=lambda v: v[0], reverse=True)})
    return rows


def load():
    """Missouri ATC's active retail alcohol licenses and Springfield-Greene's archived inspections (see the docstring)."""
    rows = load_moatc() if os.path.exists(os.path.join(OFF, "moatc", "licenses.json")) else []
    rows += load_springfield()
    df = pd.DataFrame(rows) if rows else pd.DataFrame({c: pd.Series(dtype=object) for c in COLUMNS})
    for c_ in COLUMNS:
        if c_ not in df.columns:
            df[c_] = None
    df["lat"] = df["lat"].astype(float); df["lon"] = df["lon"].astype(float); df["active"] = df["active"].astype(bool)
    df["biz"] = np.arange(len(df))
    return df
