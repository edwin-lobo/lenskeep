import json
from unittest.mock import Mock

import pytest

from scraper.scrape_vsco import scrape_vsco


@pytest.fixture
def archive_dir(tmp_path, monkeypatch):
    """Point the scraper at a temporary archive location."""
    archive_root = tmp_path / "lenskeep"
    monkeypatch.setenv("LENSKEEP_ARCHIVE_DIR", str(archive_root))
    return archive_root


def test_scrape_vsco_writes_metadata_and_skips_duplicates(archive_dir, monkeypatch):
    page_response = Mock(status_code=200, text="<html></html>")
    download_response = Mock(status_code=200)
    download_response.iter_content.return_value = [b"image-bytes"]

    requests_get = Mock(side_effect=[page_response, download_response, page_response])
    monkeypatch.setattr("scraper.scrape_vsco.requests.get", requests_get)

    records = scrape_vsco("test_user")
    metadata_path = archive_dir / "test_user" / "metadata.json"

    with metadata_path.open() as fh:
        persisted = json.load(fh)

    assert len(records) == 1
    assert persisted[0]["vsco_id"] == "abc123"
    assert requests_get.call_count == 2

    records_second_run = scrape_vsco("test_user")
    with metadata_path.open() as fh:
        persisted_again = json.load(fh)

    assert records_second_run == []
    assert persisted_again == persisted
    assert requests_get.call_count == 3
