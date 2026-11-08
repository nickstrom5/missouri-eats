# Missouri sources (checked 2026-11-06)

## Official data used
- **Missouri Active Alcohol License Data** (Division of Alcohol and Tobacco Control; data.mo.gov yyhn-562y, Socrata, nightly; 37,026
  rows on 2026-11-06, one row per secondary permit, so 12,966 Missouri retail licenses after de-duplicating by license number). Terms:
  mo.gov/data-policy: the State's disclaimer must accompany the data; it is quoted verbatim in the app's About screen and the site's
  terms (scripts/make-site.py MO_DISCLAIMER). Used: retail by-the-drink types (Retail by Drink and its Resort, Tax Exempt, Boat, Railroad,
  Mall and KC Entertainment District forms; Beer & Light Wine by Drink; Beer by Drink; Missouri Produced Wine by the Drink) mark "Serves
  alcohol"; Original Package licenses mark stores. Skipped: solicitors, shippers, wholesalers, temporary, caterer, picnic and fair
  permits. DBA names only; licensee and contact names are never kept. 11,326 placed (Overture address points, then the Census geocoder);
  4,490 matched to map listings; about 3,800 app restaurants show "Serves alcohol".

## Inspections (Nick's yes, 2026-11-07)
- **Springfield-Greene County** (www1.springfieldmo.gov/foodpermits/rss.aspx; robots.txt 404, no posted terms): the 7-day RSS feed is
  archived by `pipeline/archive_sgf_rss.py` (one request per run, generic client name, no email) into
  data/raw/official/springfield/rss_archive.jsonl, from 2026-11-07 (50 inspections, Nov 2-6). Each inspection's result ("Active",
  "Permitted with Reinspection") and its priority and nonpriority violation counts are shown as the feed states them, dated, never a
  grade (official.py `load_springfield`). The feed only reaches back a week: `ops/springfield-rss.plist` runs it daily once Nick
  installs it (not installed by this session). The establishment pages (EstInsp.aspx) are never crawled.
- **St. Louis City** (HealthSpace): Nick said yes, but www.healthspace.com answers 403 Forbidden to an honest client name (its
  robots.txt included) and healthspace.com's certificate has expired (2026-11-07). Getting past that would mean posing as a browser, so
  it isn't scripted: **back to Nick** (an export from the City, or HealthSpace's permission).
- **Not used:** St. Charles County and Jefferson County (Citizenserve "I am human" check), Kansas City (search-only).

## Research sources (robots-checked with pipeline/check_sources.py)
visitkc.com (barbecue directory, © 2026), explorestlouis.com (signature foods, © 2026), springfieldmo.org (Cashew Chicken Trail, June 2025
– May 2026), tastingtable.com (oldest restaurant 2025-09-23), jamesbeard.org (Gioia's Deli 2017 America's Classic; 2025-26 winners,
nominees, semifinalists). Blocked: stltoday.com and stlpr.org (robots), kansascity.com (unreachable). Leads: data/research/app/LEADS.md.

## Map data and calibration
- Overture 2026-10-21.0: 26,907 eating/drinking listings with a Missouri address; 114 counties plus the City of St. Louis; border checks
  pass (Kansas City MO, St. Louis, the Bootheel in; Kansas City KS, East St. Louis, Cairo, Blytheville, Keokuk out). No Google data.
- App: 13,477 places, about 12,765 restaurants (BLS QCEW 2025: 12,616 private NAICS 722 establishments).
