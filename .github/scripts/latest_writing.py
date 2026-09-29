"""Refresh the "Latest writing" list in README.md from suganthan.com's RSS feed."""
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEED = "https://suganthan.com/rss.xml"
COUNT = 5
START, END = "<!-- LATEST-WRITING:START -->", "<!-- LATEST-WRITING:END -->"

if len(sys.argv) > 1:  # local test: pass a saved copy of the feed
    with open(sys.argv[1], "rb") as f:
        raw = f.read()
else:
    req = urllib.request.Request(FEED, headers={"User-Agent": "Mozilla/5.0 (compatible; latest-writing; +https://github.com/Suganthan-Mohanadasan)"})
    raw = urllib.request.urlopen(req, timeout=30).read()
root = ET.fromstring(raw)

posts = []
for item in root.findall("./channel/item"):
    title = (item.findtext("title") or "").strip()
    link = (item.findtext("link") or "").strip()
    date = item.findtext("pubDate")
    if title and link and date:
        posts.append((parsedate_to_datetime(date), title.replace("[", "(").replace("]", ")"), link))

posts.sort(reverse=True)
lines = [f"- [{title}]({link}) · {d.day} {d.strftime('%b %Y')}" for d, title, link in posts[:COUNT]]
if not lines:
    raise SystemExit("Feed returned no posts; leaving the README alone.")

with open("README.md", encoding="utf-8") as f:
    readme = f.read()
pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
if not pattern.search(readme):
    raise SystemExit("Markers not found in README.md.")
updated = pattern.sub(START + "\n" + "\n".join(lines) + "\n" + END, readme)
if updated != readme:
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)
    print("README updated")
else:
    print("No change")
