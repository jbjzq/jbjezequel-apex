"""Render index.html from template.html. Run: python3 build.py"""
from pathlib import Path

ROOT = Path(__file__).parent
A = ROOT / "assets"

# (label, url, icon file)
SOCIAL = [
    ("Substack", "https://jbjezequel.substack.com/", "substack"),
    ("YouTube", "https://www.youtube.com/@JBEvaboot?sub_confirmation=1", "youtube"),
    ("LinkedIn", "https://www.linkedin.com/in/jb-fullvision/", "linkedin"),
    ("X", "https://x.com/jb_jezequel", "x"),
    ("Instagram", "https://www.instagram.com/jb_jezequel/", "instagram"),
    ("TikTok", "https://www.tiktok.com/@jb_jezequel", "tiktok"),
]


def social(label, url, name):
    d = (A / f"{name}.path").read_text().strip()
    return (f'        <a class="social" href="{url}" target="_blank" rel="noopener">'
            f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="{d}"/></svg><span>{label}</span></a>')


html = (ROOT / "template.html").read_text().replace("{{SOCIAL}}", "\n".join(social(*s) for s in SOCIAL))
(ROOT / "index.html").write_text(html)
print("index.html written")
