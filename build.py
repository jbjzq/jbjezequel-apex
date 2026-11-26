"""Render index.html from template.html.

Run: python3 build.py
The five latest Substack posts are read from the Substack RSS feed at build time.
A daily GitHub Action (.github/workflows/build.yml) reruns this and commits any change.
"""
import json
import urllib.error
import urllib.request
from datetime import datetime
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
A = ROOT / "assets"
SUBSTACK = "https://jbjezequel.substack.com"

# (label, handle, url, icon file)
SOCIAL = [
    ("YouTube", "@JBEvaboot", "https://www.youtube.com/@JBEvaboot?sub_confirmation=1", "youtube"),
    ("LinkedIn", "JB Jézéquel", "https://www.linkedin.com/in/jb-fullvision/", "linkedin"),
    ("X", "@jb_jezequel", "https://x.com/jb_jezequel", "x"),
    ("Instagram", "@jb_jezequel", "https://www.instagram.com/jb_jezequel/", "instagram"),
    ("TikTok", "@jb_jezequel", "https://www.tiktok.com/@jb_jezequel", "tiktok"),
    ("Facebook", "JB Jézéquel", "https://www.facebook.com/profile.php?id=61586221183698", "facebook"),
    ("Substack", "jbjezequel.substack.com", f"{SUBSTACK}/", "substack"),
]


def path(name):
    return (A / f"{name}.path").read_text().strip()


def social(label, handle, url, name):
    return (f'          <li><a href="{url}" target="_blank" rel="noopener">'
            f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="{path(name)}"/></svg>'
            f'<span class="label">{label}</span><span class="handle">{escape(handle)}</span></a></li>')


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (jbjezequel.com build)"})
    return urllib.request.urlopen(req, timeout=20).read()


def latest_posts(limit=5):
    """Newest posts from the Substack RSS feed.

    Substack answers 403 to GitHub's servers, so the daily job falls back to rss2json,
    a free service that fetches the same feed from its own servers.
    """
    try:
        root = ET.fromstring(fetch(f"{SUBSTACK}/feed"))
        posts = [{
            "title": i.findtext("title", "").strip(),
            "url": i.findtext("link", "").strip(),
            "date": parsedate_to_datetime(i.findtext("pubDate")),
            "subtitle": (i.findtext("description") or "").strip(),
        } for i in root.iter("item")]
    except urllib.error.HTTPError:
        data = json.loads(fetch(f"https://api.rss2json.com/v1/api.json?rss_url={SUBSTACK}/feed"))
        if data.get("status") != "ok":
            raise SystemExit(f"rss2json failed: {data.get('message')}")
        posts = [{
            "title": i["title"].strip(),
            "url": i["link"].strip(),
            "date": datetime.fromisoformat(i["pubDate"]),
            "subtitle": (i.get("description") or "").strip(),
        } for i in data["items"]]
    if not posts:
        raise SystemExit("no posts found; keeping the current page")
    return posts[:limit]


def post(p):
    sub = f'<div class="sub">{escape(p["subtitle"])}</div>' if p["subtitle"] else ""
    return (f'          <li><a href="{escape(p["url"])}" target="_blank" rel="noopener">'
            f'<div class="date">{p["date"].day} {p["date"].strftime("%B %Y")}</div>'
            f'<div class="title">{escape(p["title"])}</div>{sub}</a></li>')


html = (ROOT / "template.html").read_text()
html = html.replace("{{SUBSTACK_PATH}}", path("substack"))
html = html.replace("{{POSTS}}", "\n".join(post(p) for p in latest_posts()))
html = html.replace("{{SOCIAL}}", "\n".join(social(*s) for s in SOCIAL))
(ROOT / "index.html").write_text(html)
print("index.html written")
