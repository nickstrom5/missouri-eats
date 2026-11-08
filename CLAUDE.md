# Missouri Eats (mo-eats) — notes for Claude Code sessions

Built 2026-11-06 by a side session for Nick's "build the 17 states left" (group: Kentucky, Indiana, Missouri, Kansas), ported from
`../ky-eats/` (itself from `../va-eats/`) with every fix through 2026-11-05 (delivery-only brands hidden, the website blocklist and
`link_blocklist.py`, the Share link `Links.site + explore/#p=<id>`, over-the-air data, the adult-venue rules, the Denny's check,
`playbook/app-store/listing.json`). Local only: git-ignored data, no repo, no remote, nothing published. Sources: `playbook/12-sources.md`.
Brand: `playbook/05-naming.md` — **provisional**, every choice waits for Nick ("Missouri Eats: Restaurants", subtitle "BBQ, Toasted Ravs &
Custard", Home Screen "Missouri Eats"; two toasted ravioli and marinara on flag navy #0A3161, red #B31942 cards, river blue #8DB8DE fill
only; the Missouri River band).

## Missouri is different
- **Official data: the State's active alcohol licenses** (data.mo.gov yyhn-562y; `pipeline/fetch_official.py`, `official.py`). By-the-drink
  licenses mark "Serves alcohol" statewide; package licenses mark stores; no place is added from them. The State's disclaimer is
  required and quoted verbatim (About screen; site terms via `MO_DISCLAIMER`). Licensee and contact names are never kept.
- **No inspection results:** no statewide data; St. Louis City, St. Charles and Jefferson post official grades or scores behind
  browse-only portals and bot checks (Nick's call). Every place links DHSS's food-safety page.
- **The City of St. Louis** is its own county-equivalent ("City of St. Louis", apart from "St. Louis County"); counties use "St." and
  "Ste." spellings. Town names drop a parenthesized suffix ("Springfield (Sw)", "Kansas City (Gentry Co.)").
- **No Google data at all.** **ZIPs** 630xx-658xx. **One region** ("Missouri", one detail file); the site groups lists by county.
- **Guides** (tags in `missouri.py` TAGS; bits 1..16): kcbbq 7 (Visit KC, Missouri side), toasted 6 (The Hill), stlclassics 8 (Explore
  St. Louis), cashew 12 (Springfield CVB trail 2025-26), oldest 1 (J. Huston Tavern, Arrow Rock, 1834). Honors: James Beard only (no
  MICHELIN Guide covers Missouri): Gioia's Deli (America's Classics 2017), Balkan Treat Box (Best Chef: Midwest 2026), the 2025-26
  finalists and semifinalists (El Molino del Sureste isn't in the map data).
- **Venues:** Lambert (10701 Lambert International Blvd and the terminal box), KCI (601 Brasilia Ave), SGF, Busch Stadium, Enterprise
  Center, Arrowhead/GEHA Field, Kauffman, T-Mobile Center, CPKC Stadium, Faurot Field, Mizzou Arena, the State Fairgrounds, Fort Leonard
  Wood, Whiteman AFB, the prisons.

## Rebuild
```bash
cd pipeline
../.venv/bin/python fetch_overture.py && ../.venv/bin/python fetch_extras.py && ../.venv/bin/python fetch_official.py
../.venv/bin/python geocode_official.py && ../.venv/bin/python geocode_census.py && ../.venv/bin/python listings.py
../.venv/bin/python calibrate.py && ../.venv/bin/python missouri.py && ../.venv/bin/python build_research.py && ../.venv/bin/python missouri.py
MO_APP=1 ../.venv/bin/python missouri.py && cd .. && cp data/app/places.json data/app/detail-*.json MissouriEats/Resources/
.venv/bin/python pipeline/check_websites.py && .venv/bin/python pipeline/check_websites.py --retry-transient   # then re-export
.venv/bin/python scripts/make-site.py && .venv/bin/python scripts/publish_app_data.py && .venv/bin/python scripts/publish_app_data.py --check
.venv/bin/python scripts/qa-site.py --static
```
`geocode_census.py` places the ATC licenses too (about 7,800 addresses, a few minutes). The `.venv` is a copy of va-eats'.
Run `xcodegen generate` when the set of `Resources/*.json` changes.

## App, site, screenshots
- App: `MissouriEats/` (bundle `com.missourieats.ios`), tests in `MissouriEatsTests/` (fixture, outline with Kansas City MO, St. Louis and
  the Bootheel in and Kansas City KS, East St. Louis and Cairo out, the City and County of St. Louis apart, bundled-data guards) and
  `MissouriEatsUITests/`. Archive only with Xcode 1.app (27.2, 27B52).
- Site: `scripts/make-site.py` (15 pages; nickstrom5.github.io/missouri-eats until a CNAME exists), `scripts/explore.js`, `scripts/qa-site.py`.
- Screenshots: `scripts/capture-screenshots.sh` (ScreenshotMode: downtown St. Louis; 18th and Vine for barbecue, The Hill for toasted
  ravioli, Springfield for cashew chicken; detail = Charlie Gitto's), then `scripts/site-images.sh`, `scripts/appstore-screenshots.py`.

## Status (2026-11-06, ready to publish; nothing public)
- Pipeline: app 13,477 places / 12,766 restaurants in 629 towns; research 49/50 matched; websites link-checked and re-exported.
  Official: Missouri ATC's active alcohol licenses (data.mo.gov, the State's disclaimer quoted on About and the site's terms) mark
  "Serves alcohol" on about 3,800 restaurants. **No inspection data** (no statewide source; the local ones are Nick's call).
- Tests (Xcode 1.app, iOS 27.0): unit 49/49 on iPhone 17 Pro Max and iPad Pro 13" M5; UI 5/6 on both (testLaunchIsQuick skipped itself
  under load). MissouriEatsTests now reads the places' counties (AppModel has no `counties`).
- Site: 15 pages, `qa-site.py --static` OK; OTA 2026-11-06.2 `--check` OK (local only). Screens: docs/screenshots (11), App Store frames
  playbook/app-store/iphone (8) and ipad (6). Icon A passes check.swift. `playbook/app-store/listing.json` (support/privacy URLs on
  nickstrom5.github.io/missouri-eats/, 404 until Pages is on).
- The Oldest Places guide has 1 place (J Huston Tavern, 1834): its Home card shows "1"; more dated founding years, or hiding the card
  below 4, would help (the site already skips that page).
- **Nick decides:** name, icon and palette (playbook/05-naming.md); a local inspection source (St. Louis City, Springfield-Greene's RSS);
  the repo, Pages, App Store Connect record and upload.

## Rules
No commits, pushes, public repos, App Store Connect or DNS changes without Nick's yes each time; never submit for review or accept
agreements; never publish Google-derived data. Support email nick@eatsranked.com. Commit author "Nick Soderstrom"
<329204362+nickstrom5@users.noreply.github.com> via `-c user.name -c user.email`.
