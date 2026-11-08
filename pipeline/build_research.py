"""Writes data/research/app/*.json (hand-checked Missouri guides), data/research/michelin.json, jbf.json and closed.json from the
compact lists below. Ported from ky-eats/pipeline/build_research.py (2026-11-06).

Each entry cites the page that names it, read on 2026-11-06: an official Missouri tourism page (visitkc.com, Visit KC; explorestlouis.com,
Explore St. Louis; springfieldmo.org, the Springfield CVB's 2025-26 Cashew Chicken Trail), a page dated 2025-26 on a robots-checked host
(check_sources.py), or jamesbeard.org. The address comes from the map listing we already hold for that name in that town
(site/missouri.json); a name that isn't found exactly once in its town (or at the street number given) is left out and listed in
data/research/app/LEADS.md. A place the map data doesn't show as a place to eat is added only with a street address from its official
listing or our own map data (ADDR).
Usage: ../.venv/bin/python build_research.py   (then missouri.py)"""
import json, os, re
from brands import brand_of
from common import norm_name
ROOT = os.path.join(os.path.dirname(__file__), "..")
R = os.path.join(ROOT, "data", "research")
d = json.load(open(os.path.join(ROOT, "site", "missouri.json")))
C, M = d["cols"], d["meta"]
norm = lambda s: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", (s or "").lower().replace("'", "").replace("’", ""))).strip()

# each dated on its face, or an official tourism page (read 2026-11-06)
VKC = "https://www.visitkc.com/food-drink/barbecue/"                                            # Visit KC barbecue directory (© 2026)
ESL = "https://explorestlouis.com/top-five-st-louis-signature-foods"                           # Explore St. Louis (© 2026)
SGF = "https://www.springfieldmo.org/cashewchicken"                                            # Springfield CVB, trail June 2025 - May 2026
TT_OLDREST = "https://www.tastingtable.com/1975409/oldest-restaurant-every-state-still-open/"          # 2025-09-23
JBF26 = "https://www.jamesbeard.org/stories/james-beard-award-semifinalists-2026"                   # 2026-01-21
JBF26N = "https://www.jamesbeard.org/stories/james-beard-awards-restaurant-and-chef-nominees-2026"  # 2026-03-31
JBF26W = "https://www.jamesbeard.org/stories/james-beard-award-winners-2026"                        # 2026-06-15
JBF25 = "https://www.jamesbeard.org/stories/the-2025-james-beard-award-semifinalists"               # 2025-01-22
JBF25N = "https://www.jamesbeard.org/stories/2025-james-beard-awards-restaurant-and-chef-nominees"  # 2025-04-02
JBF17_GD = "https://www.jamesbeard.org/blog/2017-americas-classic-gioias-deli"                       # 2017 America's Classics
# founding years from the restaurants' own pages (read 2026-11-07)
CCK_ABOUT = "https://www.crowncandykitchen.net/about"    # Crown Candy Kitchen (© 2026): "opened in 1913", in Old North St. Louis
TED_HIST = "https://www.teddrewes.com/history/"          # Ted Drewes: South Grand opened 1931, "the oldest location still in operation"
AB_HIST = "https://www.arthurbryantsbbq.com/history"     # Arthur Bryant's: "moved to its present location at 1727 Brooklyn Avenue in 1958"
MI_UT = "https://guide.michelin.com/us/en"                                                         # no MICHELIN Guide covers Missouri

# (name as the source writes it or as our listing spells it, town as our listing has it, street number to pick the location (or
# None), note, founded, founded_note, [sources])
KC, STL, SGFT = "Kansas City", "St. Louis", "Springfield"
GUIDES = {
 "kc barbecue": [   # Visit KC's barbecue directory, the Missouri side
  ("Arthur Bryant's Barbecue", KC, "1727", "The Brooklyn Avenue original by 18th and Vine; Visit KC credits it with popularizing burnt ends.", None, None, [VKC]),
  ("Gates Bar-B-Q", KC, "1221", "Gates' downtown pit on Brooklyn Avenue.", None, None, [VKC]),
  ("Jack Stack Barbecue", KC, "101", "Jack Stack at the Freight House in the Crossroads.", None, None, [VKC]),
  ("Q39", KC, "1000", "A West 39th Street barbecue restaurant.", None, None, [VKC]),
  ("Burnt End BBQ", KC, "2450", "Burnt ends at Crown Center.", None, None, [VKC]),
  ("Char Bar", KC, "4050", "Smoked meats and games in Westport.", None, None, [VKC]),
  ("Pigwich", KC, "20", "Local Pig's sandwich counter in the River Market.", None, None, [VKC]),
 ],
 "toasted ravioli": [   # Explore St. Louis: toasted ravioli on The Hill
  ("Charlie Gitto's On the Hill", STL, None, "Fine Italian dining on The Hill; it calls its toasted ravioli the original, with housemade pomodoro.", None, None, [ESL]),
  ("Anthonino's Taverna", STL, None, "Classic toasted ravioli on The Hill.", None, None, [ESL]),
  ("Favazza's", STL, None, "Toasted ravioli on The Hill.", None, None, [ESL]),
  ("Mama's on the Hill", STL, None, "Toasted ravioli on The Hill.", None, None, [ESL]),
  ("Rigazzi's", STL, None, "Toasted ravioli on The Hill.", None, None, [ESL]),
  ("Zia's on the Hill", STL, None, "Toasted ravioli on The Hill.", None, None, [ESL]),
 ],
 "st louis classic": [   # Explore St. Louis: slingers, St. Paul sandwiches, St. Louis-style pizza, gooey butter cake, concretes
  ("Courtesy Diner", STL, None, "Slingers around the clock.", None, None, [ESL]),
  ("Chili Mac's Diner", STL, None, "A diner with a long history with the slinger.", None, None, [ESL]),
  ("Mai Lee", "Brentwood", None, "The St. Paul sandwich.", None, None, [ESL]),
  ("Park Chop Suey", STL, None, "The St. Paul sandwich, plain or with extra protein, on Chouteau Avenue.", None, None, [ESL]),
  ("Guido's Pizzeria & Tapas", STL, None, "St. Louis-style pizza: cracker-thin crust, Provel, cut in squares.", None, None, [ESL]),
  ("Farotto's Pasta & Pizzeria", STL, None, "St. Louis-style pizza.", None, None, [ESL]),
  ("Monte Bello Pizzeria", STL, None, "St. Louis-style pizza.", None, None, [ESL]),
  ("Ted Drewes Frozen Custard", STL, "4224", "Frozen custard, family-owned for more than 90 years; its concretes are served upside down. (The Route 66 stand on Chippewa isn't in the map data.)", None, None, [ESL]),
 ],
 "cashew chicken": [   # the Springfield CVB's Cashew Chicken Trail, June 2025 - May 2026
  ("Leong's Asian Diner", SGFT, None, "The Leong family's diner; David Leong's Springfield-style cashew chicken started the dish here in the 1960s, per the city.", None, None, [SGF]),
  ("Bao Bao", SGFT, None, "A stop on Springfield's Cashew Chicken Trail.", None, None, [SGF]),
  ("The Riksha", SGFT, None, "A stop on Springfield's Cashew Chicken Trail.", None, None, [SGF]),
  ("Lucy's Chinese Food", SGFT, None, "A stop on Springfield's Cashew Chicken Trail.", None, None, [SGF]),
  ("Hong Kong Inn", SGFT, "1632", "A stop on Springfield's Cashew Chicken Trail.", None, None, [SGF]),
  ("New House Chinese Food", SGFT, None, "A stop on Springfield's Cashew Chicken Trail.", None, None, [SGF]),
  ("Canton Inn", SGFT, None, "A stop on Springfield's Cashew Chicken Trail.", None, None, [SGF]),
  ("King's Asian Chef", SGFT, None, "A stop on Springfield's Cashew Chicken Trail.", None, None, [SGF]),
  ("Amazin Asian", SGFT, None, "A stop on Springfield's Cashew Chicken Trail.", None, None, [SGF]),
  ("Peking House", SGFT, None, "A stop on Springfield's Cashew Chicken Trail.", None, None, [SGF]),
  ("Chinese Chef", SGFT, None, "A stop on Springfield's Cashew Chicken Trail.", None, None, [SGF]),
  ("Yum Yum Bowl", SGFT, None, "A stop on Springfield's Cashew Chicken Trail.", None, None, [SGF]),
 ],
 "oldest": [
  ("J. Huston Tavern", "Arrow Rock", "305", "A tavern on Arrow Rock's Main Street.", 1834,
   "Tasting Table's oldest restaurant in every state (September 2025): Missouri's is the J. Huston Tavern, which got its start in 1834.", [TT_OLDREST]),
  ("Crown Candy Kitchen", STL, "1401", "A soda fountain and candy kitchen in Old North St. Louis.", 1913,
   "Crown Candy Kitchen's own page: opened in 1913 by Harry Karandzieff and his best friend Pete Jugaloff, in Old North St. Louis, where it stands today.", [CCK_ABOUT]),
  ("Ted Drewes Frozen Custard", STL, "4224", "The South Grand custard stand.", 1931,
   "Ted Drewes' own history: the South Grand store opened in 1931 and is the oldest location still in operation.", [TED_HIST]),
  ("Arthur Bryant's Barbecue", KC, "1727", "The Brooklyn Avenue barbecue landmark.", 1958,
   "Arthur Bryant's own history: it moved to its present location at 1727 Brooklyn Avenue in 1958.", [AB_HIST]),
 ],
}
# street addresses for places the map data doesn't show as a place to eat: from the official listing, or our own map listing for it
ADDR = {("J. Huston Tavern", "Arrow Rock"): "305 Main St"}
CUISINE = {("J. Huston Tavern", "Arrow Rock"): "American & Other"}
KINDS = {k: [k] for k in ("kc barbecue", "toasted ravioli", "st louis classic", "cashew chicken", "oldest")}

# MICHELIN: no guide covers Missouri
MICHELIN = []
MI_MATCH = {}
# James Beard (facts with sources): Gioia's Deli (America's Classics 2017), the 2026 winner and Missouri's 2025-26 nominees and semifinalists
MW = "Best Chef: Midwest"
JBF = [{"name": "Gioia's Deli", "city": STL, "address": "1934 Macklind Ave", "honors": ["America's Classics 2017"], "sources": [JBF17_GD]},
       {"name": "Balkan Treat Box", "city": "Webster Groves", "honors": [f"{MW} winner 2026 (Loryn Nalic)", f"{MW} finalist 2025 (Loryn Nalic)"], "sources": [JBF26W, JBF26N, JBF25N]},
       {"name": "Vicia", "city": STL, "honors": ["Outstanding Restaurant finalist 2026", "Emerging Chef finalist 2025 (Jane Sacro Chatham)"], "sources": [JBF26N, JBF25N]},
       {"name": "Anjin", "city": KC, "honors": ["Best New Restaurant finalist 2026"], "sources": [JBF26N]},
       {"name": "Robin", "city": STL, "honors": ["Best New Restaurant finalist 2026"], "sources": [JBF26N]},
       {"name": "Louie", "city": "Clayton", "honors": ["Outstanding Hospitality finalist 2026"], "sources": [JBF26N]},
       {"name": "Sado", "city": STL, "honors": [f"{MW} finalist 2026 (Nick Bognar)"], "sources": [JBF26N, JBF25]},
       {"name": "The Town Company", "city": KC, "honors": [f"{MW} semifinalist 2026 (Johnny Leach)", "Outstanding Pastry Chef or Baker semifinalist 2026 (Helen Jo Leach)"], "sources": [JBF26, JBF25]},
       {"name": "Fern Bar", "city": KC, "honors": ["Outstanding Professional in Cocktail Service semifinalist 2026 (Diana Condori)"], "sources": [JBF26]},
       {"name": "Root Food + Wine", "city": "Augusta", "honors": [f"{MW} semifinalist 2026 (Philip Day)"], "sources": [JBF26], "match_names": ["ROOT FOOD WINE"]},
       {"name": "El Molino del Sureste", "city": STL, "honors": [f"{MW} semifinalist 2026 (Alex Henry)"], "sources": [JBF26]},
       {"name": "Nathaniel Reid Bakery", "city": "Kirkwood", "honors": ["Outstanding Bakery semifinalist 2025"], "sources": [JBF25]},
       {"name": "JJ's Restaurant", "city": KC, "honors": ["Outstanding Wine and Other Beverages Program semifinalist 2025"], "sources": [JBF25]},
       {"name": "Madrina", "city": "Webster Groves", "honors": ["Outstanding Professional in Beverage Service semifinalist 2025 (Alisha Blackwell-Calvert)"], "sources": [JBF25]},
       {"name": "The Gin Room", "city": STL, "honors": ["Outstanding Professional in Beverage Service semifinalist 2025 (Natasha Bahrami)"], "sources": [JBF25]},
       {"name": "Chewology", "city": KC, "honors": [f"{MW} semifinalist 2025 (Katie Liu-Sung)"], "sources": [JBF25]}]
# closed, each with a source (none verified this pass)
CLOSED = []


def key(s):
    """The name key without a leading "the": "Varsity" is our "The Varsity"."""
    return re.sub(r"^the ", "", norm(s))


def find(name, town, num):
    k = key(name)
    hits = [i for i, n in enumerate(C["name"]) if C["city"][i] is not None and M["cities"][C["city"][i]] == town
            and (key(n) == k or key(n).startswith(k + " ") or k.startswith(key(n) + " ") or key(n).replace(" ", "") == k.replace(" ", "")
                 or (key(n).split()[:2] == k.split()[:2] and len(k.split()) >= 2))]
    if num:
        hits = [i for i in hits if (C["addr"][i] or "").split(" ")[0] == num]
    return hits


leads, n_out = [], {}
for kind, rows in GUIDES.items():
    out = []
    for name, town, num, note, founded, fnote, srcs in rows:
        hits = find(name, town, num)
        if not hits and (name, town) in ADDR:
            out.append({"name": name, "address": ADDR[(name, town)], "city": town, "zip": None, "kinds": KINDS[kind], "dishes": [], "note": note,
                        "founded": founded, "founded_note": fnote, "website": None, "open": True, "evidence_date": "2026-10",
                        "sources": srcs, "match_names": []} | ({"cuisine": CUISINE[(name, town)]} if (name, town) in CUISINE else {}))
            continue
        if len(hits) != 1:
            leads.append(f"- {kind}: {name} ({town}{', ' + num if num else ''}) — {len(hits)} matches in our data; not added"); continue
        i = hits[0]
        out.append({"name": C["name"][i], "address": C["addr"][i], "city": town, "zip": str(C["zip"][i]) if C["zip"][i] else None,
                    "kinds": KINDS[kind], "dishes": [], "note": note, "founded": founded, "founded_note": fnote, "website": None, "open": True,
                    "evidence_date": "2026-10", "sources": srcs, "match_names": [name.upper()] if norm(name) != norm(C["name"][i]) else []})
        if brand_of(norm_name(name)):   # a chain shows under its own spelling at every branch, whatever the listing says
            out[-1]["display"] = name
        if (name, town) in CUISINE:
            out[-1]["cuisine"] = CUISINE[(name, town)]
    fn = re.sub(r"[^a-z]+", "_", kind).strip("_")
    json.dump(out, open(f"{R}/app/{fn}.json", "w"), indent=1, ensure_ascii=False)
    n_out[kind] = len(out)

MI_ADDR = {}
json.dump({"restaurants": [{"name": n, "address": MI_ADDR.get(n), "city": t, "zip": None, "distinction": dist, "cuisine": cu, "green_star": False,
                             "michelin_url": MI_UT, "sources": [MI_UT], "match_names": [x.upper() for x in MI_MATCH.get(n, [])], "open": True}
                            for n, t, dist, cu in MICHELIN]}, open(f"{R}/michelin.json", "w"), indent=1, ensure_ascii=False)
json.dump([dict({"address": None}, **j, zip=None, open=True) for j in JBF], open(f"{R}/jbf.json", "w"), indent=1, ensure_ascii=False)
json.dump(CLOSED, open(f"{R}/closed.json", "w"), indent=1, ensure_ascii=False)
open(f"{R}/app/LEADS.md", "w").write("# Missouri research leads (not yet verified)\n\nWritten by pipeline/build_research.py.\n\n" + "\n".join(leads) + """

## Waiting for a source we may use, or for the map data
- Stroud's (America's Classics 1998, pan-fried chicken): its jamesbeard.org page wasn't read this pass, and its 1933 founding isn't at
  today's address. Joe's Kansas City's original is in Kansas (Visit KC lists it on the Kansas side).
- Pirrone's Pizzeria (Explore St. Louis) has two locations (St. Peters, Florissant); the page names neither.
- Gooey butter cake: Gooey Louie and Park Avenue Coffee (Explore St. Louis) are bakeries/cafés; add them with a gooey-butter guide.
- Bosnian St. Louis (Grbić, J's Pitaria, Sana Bakery around Bevo Mill): the sources found are 2023 or older; stltoday.com and stlpr.org
  disallow Claude's fetcher.
- Oldest: only the J. Huston Tavern (1834) has a dated source tied to its address; O'Malley's Pub in Weston has no year.
- Honors: Gerard Craft (Niche Food Group, Outstanding Restaurateur semifinalist 2025) is a group honor.
- Official data: St. Louis City's letter grades (HealthSpace, browse-only), St. Charles County's "Know the Score" and Jefferson County's
  "Scan for the Score" (Citizenserve behind an "I am human" check), Springfield-Greene's 7-day RSS feed: Nick's call.
""")
print(n_out, "| leads:", len(leads))
for l in leads: print(l)
