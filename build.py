"""Render index.html from template.html.

Run: python3 build.py
The five latest Substack posts are read from the Substack archive API at build time.
A daily GitHub Action (.github/workflows/build.yml) reruns this and commits any change.
"""
import json
import urllib.request
from datetime import datetime
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


def latest_posts(limit=5):
    req = urllib.request.Request(f"{SUBSTACK}/api/v1/archive?sort=new&limit={limit}",
                                 headers={"User-Agent": "jbjezequel.com build"})
    data = json.load(urllib.request.urlopen(req, timeout=20))
    posts = data.get("posts", data) if isinstance(data, dict) else data
    return [p for p in posts if p.get("audience") == "everyone"][:limit]


def post(p):
    date = datetime.fromisoformat(p["post_date"].replace("Z", "+00:00"))
    sub = f'<div class="sub">{escape(p["subtitle"])}</div>' if p.get("subtitle") else ""
    return (f'          <li><a href="{SUBSTACK}/p/{p["slug"]}" target="_blank" rel="noopener">'
            f'<div class="date">{date.strftime("%-d %B %Y")}</div>'
            f'<div class="title">{escape(p["title"])}</div>{sub}</a></li>')


html = (ROOT / "template.html").read_text()
html = html.replace("{{SUBSTACK_PATH}}", path("substack"))
html = html.replace("{{POSTS}}", "\n".join(post(p) for p in latest_posts()))
html = html.replace("{{SOCIAL}}", "\n".join(social(*s) for s in SOCIAL))
(ROOT / "index.html").write_text(html)
print("index.html written")
