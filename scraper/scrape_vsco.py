import json
import os
import sys
from datetime import datetime, UTC
from pathlib import Path

import requests
from bs4 import BeautifulSoup

import logging

import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from contextlib import asynccontextmanager
import asyncio
from playwright.async_api import async_playwright

from .fetch import fetch_html
from .extract import (
    extract_media_items_from_gallery_html,    # new HTML grid fallback
)


log = logging.getLogger("lenskeep.scraper")


def _try_mkdir(p: Path) -> bool:
    try:
        p.mkdir(parents=True, exist_ok=True)
        test = p / ".writetest"
        test.write_text("ok")
        test.unlink(missing_ok=True)
        return True
    except Exception:
        return False

def resolve_archive_root() -> Path:
    """
    Priority:
      1) $LENSKEEP_ARCHIVE_DIR (respects devcontainer/CI config)
      2) /workspace/archive (works well in the devcontainer with a volume)
      3) ~/lenskeep_archive (container user's home)
      4) /tmp/lenskeep_archive (last-resort)
    """
    candidates = []
    if os.getenv("LENSKEEP_ARCHIVE_DIR"):
        candidates.append(Path(os.getenv("LENSKEEP_ARCHIVE_DIR")).expanduser())
    candidates += [
        Path("/workspace/archive"),
        Path.home() / "lenskeep_archive",
        Path("/tmp/lenskeep_archive"),
    ]

    for p in candidates:
        if _try_mkdir(p):
            log.info(f"Using archive root: {p}")
            return p

    raise RuntimeError("No writable archive directory found; set $LENSKEEP_ARCHIVE_DIR")

def init_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def download_file(url: str, filename: Path) -> Path:
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with filename.open("wb") as fh:
            for chunk in response.iter_content(1024):
                fh.write(chunk)
    return filename


def load_existing_metadata(metadata_path: Path) -> dict:
    if metadata_path.exists():
        with metadata_path.open("r") as fh:
            return {item["vsco_id"]: item for item in json.load(fh)}
    return {}

def scrape_vsco(username: str):
    archive_root = resolve_archive_root()
    save_dir = archive_root / username
    save_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = save_dir / "metadata.json"

    html = fetch_html(username, mode=os.getenv("LENSKEEP_FETCH_MODE", "auto"))
    items = extract_media_items_from_gallery_html(html, username)

    if not items:
        print(f"No photo items found for {username}")
        return []

    # Download each item visible on page 1 (idempotent by filename)
    records = []
    for item in items:
        src_url = item["url"].split("?")[0]
        fname = src_url.rsplit("/", 1)[-1] or f"{item['id']}.jpg"
        file_path = save_dir / fname
        if not file_path.exists():
            download_file(src_url, str(file_path))

        records.append({
            "username": username,
            "vsco_id": item["id"],
            "media_type": "photo",
            "url": src_url,
            "permalink": item["permalink"],
            "file_path": str(file_path),
            "created_at": item.get("date"),
            "downloaded_at": datetime.now(UTC).isoformat(),
        })

    # Write the page-1 snapshot metadata
    with open(metadata_path, "w") as f:
        json.dump(records, f, indent=2)

    print(f"Wrote {len(records)} items (first page) to {metadata_path}")
    return records

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: lenskeep-scrape <username>")
        sys.exit(1)
    username = sys.argv[1]
    scrape_vsco(username)

if __name__ == "__main__":
    main()
