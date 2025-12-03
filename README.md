# LensKeep

LensKeep is a personal media archiver that downloads and organizes photos and videos from VSCO profiles. Media lands in a local workspace first so the flow can be validated before wiring everything up to cloud storage.

---

## Storage Layout

- Default archive root: `/Users/edwinlobo/Documents/.build/lenskeep`
- Override with `LENSKEEP_ARCHIVE_DIR=/custom/path` to target a different local mount or staging area.

Each VSCO username gets its own folder under the archive root. Downloaded files sit beside a `metadata.json` file that tracks historical records, making deduplication idempotent when the scraper reruns.

---

## Usage

```bash
# Install dependencies (requires uv)
uv sync

# Run the scraper for a specific VSCO profile
uv run python -m scraper.scrape_vsco <username>

# Start the scheduler to run on an interval
uv run python -m scheduler.job_runner
```

Run tests to validate metadata persistence and deduplication behaviour:

```bash
uv run pytest
```

---

## Project Structure

```text
lenskeep/
├── .devcontainer/
│   ├── devcontainer.json
│   └── Dockerfile
├── .gitignore
├── README.md
├── docs/
│   └── ARCHITECTURE.md
├── infra/
│   └── terraform/
│       ├── main.tf
│       ├── outputs.tf
│       ├── providers.tf
│       └── variables.tf
├── pyproject.toml
├── scraper/
│   ├── __init__.py
│   └── scrape_vsco.py
├── scheduler/
│   ├── __init__.py
│   └── job_runner.py
├── state/
│   └── last_run.json
├── tests/
│   ├── __init__.py
│   └── test_scraper.py
└── uv.lock
```
