import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# --- Config ---
USERNAME = "example_user"  # replace with the VSCO username you want to scrape
SAVE_DIR = os.path.expanduser(f"~/lenskeep_archive/{USERNAME}")

def init_dir():
    os.makedirs(SAVE_DIR, exist_ok=True)

def download_file(url, filename):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(filename, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
    return filename

def scrape_vsco(username):
    url = f"https://vsco.co/{username}/gallery"
    r = requests.get(url)
    if r.status_code != 200:
        print(f"Failed to fetch {url}, status {r.status_code}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    # ⚠️ NOTE: VSCO injects JSON with media details in <script> tags.
    # This is placeholder logic until you wire actual parsing.
    # Replace this with JSON extraction logic.
    media_items = [
        {
            "id": "abc123",
            "url": "https://dummyimage.com/600x400/000/fff.jpg",
            "type": "photo",
            "date": "2025-08-01T12:00:00Z"
        }
    ]

    records = []
    for item in media_items:
        media_url = item["url"]
        media_type = item["type"]
        vsco_id = item["id"]
        created_at = datetime.fromisoformat(item["date"].replace("Z", "+00:00"))

        filename = os.path.join(SAVE_DIR, os.path.basename(media_url))
        download_file(media_url, filename)

        record = {
            "username": username,
            "vsco_id": vsco_id,
            "media_type": media_type,
            "url": media_url,
            "file_path": filename,
            "created_at": created_at.isoformat(),
            "downloaded_at": datetime.utcnow().isoformat()
        }
        records.append(record)

    # Save metadata JSON locally
    metadata_path = os.path.join(SAVE_DIR, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(records, f, indent=2)

    print(f"Downloaded {len(records)} items for {username}. Metadata saved to {metadata_path}")
    return records

if __name__ == "__main__":
    init_dir()
    scrape_vsco(USERNAME)
