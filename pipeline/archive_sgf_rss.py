"""Springfield-Greene County food inspections, archived from the health department's 7-day RSS feed
-> data/raw/official/springfield/rss_archive.jsonl (git-ignored, never public) plus each run's raw XML in .../rss/<date>.xml.

Nick's yes, 2026-11-07: archive the feed from now on. The feed (www1.springfieldmo.gov/foodpermits/rss.aspx) lists the last seven days'
inspections: the establishment's name, address and town, its est id, the inspection date and type, the result as published ("Active",
...), and the counts of priority and nonpriority violations, with the inspector's notes. robots.txt answers 404 (no rules; checked
2026-11-07). The feed only reaches back a week, so this must run at least weekly (daily is safer): see ops/springfield-rss.plist.
One request per run, a generic client name, no email address. The establishment pages (EstInsp.aspx) are never crawled.
Usage: ../.venv/bin/python archive_sgf_rss.py
"""
import datetime, email.utils, html, json, os, re
import xml.etree.ElementTree as ET
import requests

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "data", "raw", "official", "springfield")
FEED = "https://www1.springfieldmo.gov/foodpermits/rss.aspx"
os.makedirs(os.path.join(OUT, "rss"), exist_ok=True)
ARCHIVE = os.path.join(OUT, "rss_archive.jsonl")


def parse_item(it):
    title = (it.findtext("title") or "").strip()
    link = (it.findtext("link") or "").strip()
    est = (re.search(r"est=(\d+)", link) or [None, None])[1]
    when = email.utils.parsedate_to_datetime(it.findtext("pubDate"))
    desc = html.unescape(it.findtext("description") or "")
    head = re.sub(r"<[^>]+>", "\n", desc).split("\n")[0]
    kind = (re.search(r" - ([^;]+);", head) or [None, None])[1]
    result = (re.search(r"Result:\s*([^<\n]+)", desc) or [None, ""])[1].strip() or None
    pri = re.search(r"Priority Violations Found:\s*(\d+)", desc)
    non = re.search(r"Nonpriority Violations Found:\s*(\d+)", desc)
    notes = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", n)).strip() for n in re.findall(r"<li>(.*?)</li>", desc, re.S)]
    name, _, addr = title.partition(" - ")
    return {"est": est, "name": name.strip(), "address_line": re.sub(r"\s+", " ", addr).strip(), "date": when.date().isoformat(),
            "time": when.strftime("%H:%M"), "type": kind.strip() if kind else None, "result": result,
            "priority": int(pri[1]) if pri else None, "nonpriority": int(non[1]) if non else None, "notes": notes, "link": link}


def main():
    r = requests.get(FEED, headers={"User-Agent": "EatsRankedData/1.0"}, timeout=90)
    r.raise_for_status()
    today = datetime.date.today().isoformat()
    open(os.path.join(OUT, "rss", f"{today}.xml"), "wb").write(r.content)
    root = ET.fromstring(r.content.decode("utf-8-sig"))
    items = [parse_item(it) for it in root.iter("item")]
    seen = set()
    if os.path.exists(ARCHIVE):
        for line in open(ARCHIVE):
            d = json.loads(line)
            seen.add((d["est"], d["date"], d["time"], d["type"]))
    new = [d for d in items if (d["est"], d["date"], d["time"], d["type"]) not in seen]
    with open(ARCHIVE, "a") as f:
        for d in sorted(new, key=lambda d: (d["date"], d["time"], d["est"] or "")):
            f.write(json.dumps(d | {"archived": today}) + "\n")
    print(f"{len(items)} items in the feed, {len(new)} new; archive {len(seen) + len(new)} inspections")


if __name__ == "__main__":
    main()
