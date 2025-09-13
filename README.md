# LensKeep

LensKeep is a personal media archiver that downloads and organizes photos and videos from VSCO profiles.
It stores content locally and manages metadata in a way that can later be pushed into a modern data lakehouse (Apache Iceberg on AWS).

---

## 📂 Project Structure
lenskeep/
├── .gitignore
├── README.md
├── requirements.txt
├── scraper/
│   ├── __init__.py
│   └── scrape_vsco.py        # MVP VSCO scraper (downloads files + metadata.json locally)
├── infra/
│   └── terraform/            # AWS infra for Iceberg metadata
│       ├── main.tf
│       ├── providers.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── athena_iceberg.sql
└── docs/
    ├── ARCHITECTURE.md       # overview of local → AWS Iceberg flow
    └── ROADMAP.md

