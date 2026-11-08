"""Missouri's open official records -> data/raw/official/ (git-ignored, never public).

Checked 2026-11-06 (playbook/12-sources.md). The one statewide open feed is the Missouri Division of Alcohol and Tobacco Control's
"Missouri Active Alcohol License Data" (data.mo.gov, yyhn-562y, Socrata, nightly): DBA, address, county and license types for every
active licensee. Terms: mo.gov/data-policy (an app must carry the State's disclaimer, with "the State of Missouri" as the source; the
About screen and the site's terms quote it verbatim). Person names (licensee contacts) are never kept. Inspections: no statewide data;
St. Louis City, St. Charles and Jefferson post official grades or scores behind browse-only portals and bot checks (Nick's call).
One request at a time, a second apart.
"""
import datetime, json, os, time
import requests

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "official")
os.makedirs(os.path.join(OUT, "moatc"), exist_ok=True)
UA = "MissouriEatsDataCheck/1.0 (+https://nickstrom5.github.io/missouri-eats/; nick@eatsranked.com)"
URL = "https://data.mo.gov/resource/yyhn-562y.json"
S = requests.Session(); S.headers["User-Agent"] = UA
FIELDS = "dbaname,street_number,street,city,state,zipcode,primary_license,secondary_license,primary_type,secondary_type,county"
rows, off = [], 0
while True:
    for attempt in range(4):
        r = S.get(URL, params={"$select": FIELDS, "$order": "primary_license", "$limit": 20000, "$offset": off}, timeout=120)
        if r.status_code == 200:
            break
        time.sleep(5 * (attempt + 1))
    r.raise_for_status()
    page = r.json()
    rows += page
    if len(page) < 20000:
        break
    off += len(page); time.sleep(1)
view = S.get("https://data.mo.gov/api/views/yyhn-562y.json", timeout=60).json()
upd = view.get("rowsUpdatedAt")
meta = {"moatc": {"name": "Missouri Division of Alcohol and Tobacco Control: Missouri Active Alcohol License Data", "url": "https://data.mo.gov/d/yyhn-562y",
                  "fetched": datetime.date.today().isoformat(),
                  "edited": datetime.datetime.fromtimestamp(upd, datetime.timezone.utc).date().isoformat() if upd else None,
                  "terms": "mo.gov/data-policy: the State of Missouri's disclaimer must accompany the data"}}
json.dump(rows, open(os.path.join(OUT, "moatc", "licenses.json"), "w"))
json.dump(meta, open(os.path.join(OUT, "meta.json"), "w"), indent=1)
print("Missouri ATC active licenses:", len(rows), "| updated:", meta["moatc"]["edited"])
