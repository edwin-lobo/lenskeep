# scraper/extract.py
from __future__ import annotations
import json, re
from datetime import datetime, UTC
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

CANDIDATE_PATTERNS = [
    r"__PRELOADED_STATE__\s*=\s*(\{.*?\})\s*;?\s*$",
    r"__NEXT_DATA__\s*=\s*(\{.*?\})\s*;?\s*$",
]

def _iso_or_none(s: str | None):
    if not s:
        return None
    # try a few common shapes
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%S.%f%z"):
        try:
            return datetime.strptime(s, fmt).astimezone(UTC)
        except Exception:
            continue
    # last resort: fromisoformat with Z tweak
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(UTC)
    except Exception:
        return None

# ... keep your JSON-based extractor if you have one ...

def _pick_best_from_srcset(srcset: str) -> Optional[str]:
    try:
        parts = [p.strip() for p in srcset.split(",") if p.strip()]
        if not parts:
            return None
        candidate = parts[-1].split()[0]  # URL before DPR token
        if candidate.startswith("//"):
            candidate = "https:" + candidate
        return candidate
    except Exception:
        return None

def extract_media_items_from_gallery_html(html: str, username: str) -> List[Dict]:
    """
    Parse *only* the first (initially rendered) page of the gallery.
    Keeps source order (usually newest -> oldest).
    """
    soup = BeautifulSoup(html, "html.parser")
    root = soup.find("div", {"data-testid": "UserProfileGallery"})
    items: List[Dict] = []
    if not root:
        return items

    for fig in root.find_all("figure"):
        a = fig.find("a", href=True)
        img = fig.find("img")
        if not a or not img:
            continue

        href = a["href"]                                  # /<user>/media/<id>
        m = re.search(rf"/{re.escape(username)}/media/([A-Za-z0-9]+)", href)
        media_id = m.group(1) if m else href.strip("/").split("/")[-1]

        # choose best candidate from srcset then fallback to src
        url = None
        if img.has_attr("srcset") and img["srcset"]:
            url = _pick_best_from_srcset(img["srcset"])
        if not url and img.has_attr("src") and img["src"]:
            url = img["src"]
            if url.startswith("//"):
                url = "https:" + url

        if not url:
            continue

        permalink = href if href.startswith("http") else f"https://vsco.co{href}"

        items.append({
            "id": media_id,
            "url": url,                 # thumbnail/480-sized image on first page
            "permalink": permalink,     # add permalink to metadata
            "type": "photo",
            "date": None,               # not available from grid HTML
        })

    return items
