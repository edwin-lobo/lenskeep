
---

### In `docs/ARCHITECTURE.md` (detailed)

```markdown
# 📐 LensKeep Architecture

LensKeep combines Python (scraper + Iceberg loader), Go (infra orchestration), and AWS (S3, Glue, Athena, Iceberg).

---

## 📂 Repository Structure

```mermaid
flowchart TD
    A[lenskeep/] --> B[.gitignore]
    A --> C[README.md]
    A --> D[requirements.txt]
    A --> E[scraper/]
    A --> F[iceberg/]
    A --> G[go/]
    A --> H[infra/]
    A --> I[docs/]

    E --> E1[__init__.py]
    E --> E2[scrape_vsco.py]

    F --> F1[loader.py]
    F --> F2[sample_metadata.json]

    G --> G1[main.go]

    H --> H1[terraform/]
    H1 --> H2[main.tf]
    H1 --> H3[providers.tf]
    H1 --> H4[variables.tf]
    H1 --> H5[outputs.tf]
    H1 --> H6[athena_iceberg.sql]

    I --> I1[ARCHITECTURE.md]
    I --> I2[ROADMAP.md]
