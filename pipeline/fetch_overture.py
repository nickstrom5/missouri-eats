"""Download the Overture Maps extracts that missouri.py reads -> data/mo/

- overture_mo_bbox.parquet     every place in Missouri's bounding box (name, category, address, point)
- overture_mo_sources.parquet  which datasets each Missouri eating/drinking listing came from (Meta, Foursquare, ...)
- mo_shapes.json               simplified state and county outlines for the map
- mo_state_detail.geojson      the state outline at full detail, for the in-state test

Reads the public Overture bucket over S3 with DuckDB (no account needed). Ported from ky-eats/pipeline/fetch_overture.py (2026-11-06).
Missouri: 114 counties and the independent City of St. Louis (a county-equivalent: "City of St. Louis" is not St. Louis County). The
script checks the towns on the lines with Illinois, Kentucky, Tennessee, Arkansas, Oklahoma, Kansas, Nebraska and Iowa (Kansas City,
Missouri is in, Kansas City, Kansas out; St. Louis in, East St. Louis out; the Bootheel in).
"""
import os, re, json, time
import duckdb
from shapely import wkb
from shapely.geometry import mapping, Polygon

RELEASE = "2026-10-21.0"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "mo")
# Missouri (35.99°N–40.61°N, 89.10°W–95.77°W) plus a margin for the border towns (the Bootheel, Kansas City, St. Louis)
BBOX = "bbox.xmin BETWEEN -95.9 AND -89.0 AND bbox.ymin BETWEEN 35.9 AND 40.7"
EAT = "('restaurant','casual_eatery','bar','fast_food_restaurant','coffee_shop','cafe','smoothie_juice_bar','brewery','food_court')"
os.makedirs(OUT, exist_ok=True)

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial; SET s3_region='us-west-2';")
places = f"s3://overturemaps-us-west-2/release/{RELEASE}/theme=places/type=place/*.parquet"

t = time.time()
if not os.path.exists(f"{OUT}/overture_mo_bbox.parquet"):
    con.execute(f"""
COPY (
  SELECT id, names.primary AS name, basic_category AS cat, taxonomy.primary AS tax, taxonomy.hierarchy AS hier, confidence,
         operating_status AS status, brand.names.primary AS brand, addresses[1].freeform AS street, addresses[1].locality AS city,
         addresses[1].postcode AS zip, addresses[1].region AS region, ST_Y(geometry) AS lat, ST_X(geometry) AS lon, websites[1] AS web,
         phones[1] AS phone
  FROM read_parquet('{places}', hive_partitioning=1) WHERE {BBOX}
) TO '{OUT}/overture_mo_bbox.parquet' (FORMAT PARQUET)""")
    print("places in bbox", round(time.time() - t), "s", flush=True)
if not os.path.exists(f"{OUT}/overture_mo_sources.parquet"):
    con.execute(f"""
COPY (
  SELECT id, list_transform(sources, lambda x: x.dataset) AS ds, list_transform(sources, lambda x: x.update_time) AS ut,
         list_transform(sources, lambda x: x.record_id) AS rid,
         len(socials) AS n_soc, len(websites) AS n_web, len(phones) AS n_ph
  FROM read_parquet('{places}', hive_partitioning=1)
  WHERE {BBOX} AND basic_category IN {EAT}
) TO '{OUT}/overture_mo_sources.parquet' (FORMAT PARQUET)""")
    print("sources", round(time.time() - t), "s", flush=True)

areas = f"s3://overturemaps-us-west-2/release/{RELEASE}/theme=divisions/type=division_area/*.parquet"
rows = con.execute(f"""
  SELECT subtype, names.primary AS name, ST_AsWKB(geometry) AS g
  FROM read_parquet('{areas}', hive_partitioning=1)
  WHERE country = 'US' AND region = 'US-MO' AND subtype IN ('region', 'county') AND class = 'land'
    AND bbox.xmin > -96.0 AND bbox.xmax < -88.9 AND bbox.ymin > 35.8 AND bbox.ymax < 40.8""").fetchall()
# the City of St. Louis is its own county-equivalent: "City of St. Louis" is not St. Louis County
def _cname(sub, name):
    name = name.replace("Sainte ", "Ste. ").replace("Saint ", "St. ") if sub != "region" else name   # the counties' own spelling
    return name if sub == "region" or name.endswith(" County") else "City of " + name
rows = [(sub, _cname(sub, name), g) for sub, name, g in rows]


def rings(geom, tol, min_area):
    geom = geom.simplify(tol, preserve_topology=True)
    polys = [p for p in getattr(geom, "geoms", [geom]) if p.geom_type == "Polygon" and p.area >= min_area]
    return [[[round(x, 3), round(y, 3)] for x, y in p.exterior.coords] for p in polys]


out = {"state": None, "counties": []}
for sub, name, g in rows:
    geom = wkb.loads(bytes(g)).buffer(0)
    if sub == "region":
        json.dump(mapping(geom.simplify(0.0005, preserve_topology=True)), open(f"{OUT}/mo_state_detail.geojson", "w"))
        out["state"] = [[r] for r in rings(geom, 0.002, 0.000005)]
    else:
        out["counties"].append({"name": name, "c": rings(geom, 0.004, 0.00002)})
# full-detail county polygons for assigning each place to a county (not shipped)
json.dump({name: mapping(wkb.loads(bytes(g)).buffer(0).simplify(0.0003, preserve_topology=True))
           for sub, name, g in rows if sub == "county"}, open(f"{OUT}/mo_counties_detail.geojson", "w"))
json.dump(out, open(f"{OUT}/mo_shapes.json", "w"), separators=(",", ":"))
print("outlines: state", len(out["state"] or []), "rings +", len(out["counties"]), "counties;", round(time.time() - t), "s total")
# islands, shores and border towns: each must fall on the right side of the detailed state outline
from shapely.geometry import shape, Point
st = shape(json.load(open(f"{OUT}/mo_state_detail.geojson")))
for nm, lon, lat, want in [("St. Louis", -90.1994, 38.6270, True), ("East St. Louis, IL", -90.1510, 38.6245, False), ("Kansas City, MO", -94.5786, 39.0997, True),
                           ("Kansas City, KS", -94.6268, 39.1155, False), ("St. Joseph", -94.8467, 39.7675, True), ("Elwood, KS", -94.8722, 39.7558, False),
                           ("Hannibal", -91.3582, 39.7084, True), ("Quincy, IL", -91.4099, 39.9356, False), ("Cape Girardeau", -89.5182, 37.3059, True),
                           ("Cairo, IL", -89.1765, 37.0053, False), ("Kennett", -90.0556, 36.2362, True), ("Blytheville, AR", -89.9190, 35.9273, False),
                           ("Joplin", -94.5133, 37.0842, True), ("Pittsburg, KS", -94.7049, 37.4109, False), ("Branson", -93.2185, 36.6437, True),
                           ("Bentonville, AR", -94.2088, 36.3729, False), ("Kirksville", -92.5833, 40.1948, True), ("Keokuk, IA", -91.3943, 40.3973, False),
                           ("Hayti", -89.7495, 36.2334, True), ("Columbia", -92.3341, 38.9517, True), ("Grandview, MO", -94.5330, 38.8858, True)]:
    ok = st.contains(Point(lon, lat))
    print(f"  {nm}: {'inside' if ok else 'outside'}{'' if ok == want else '  <-- WRONG'}")
print("counties:", len(out["counties"]), sorted(c["name"] for c in out["counties"]))

# the neighbours' land (Illinois, Kentucky, Tennessee, Arkansas, Oklahoma, Kansas, Nebraska, Iowa): listings.py widens Missouri's outline
# ~300 m for river shores, but only where no neighbour's land is, so an East St. Louis or Kansas City, Kansas listing stays out
nb = con.execute(f"""
  SELECT region, ST_AsWKB(geometry) FROM read_parquet('{areas}', hive_partitioning=1)
  WHERE country = 'US' AND region IN ('US-IL', 'US-KY', 'US-TN', 'US-AR', 'US-OK', 'US-KS', 'US-NE', 'US-IA') AND subtype = 'region' AND class = 'land'""").fetchall()
from shapely.ops import unary_union
from shapely.geometry import box
near = box(-96.0, 35.8, -88.9, 40.8)
nbg = unary_union([wkb.loads(bytes(g)).buffer(0).intersection(near) for _, g in nb])
json.dump(mapping(nbg.simplify(0.0002, preserve_topology=True)), open(f"{OUT}/mo_neighbors.geojson", "w"))
print("neighbours:", sorted(r for r, _ in nb))
