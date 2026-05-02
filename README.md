# E-Commerce Customer Behaviour & Sales Intelligence Dashboard
**NCI MSc Data Analytics

**Team:**
- Amber — Member 3 — Criteo Attribution Dataset
- Ibrahim — Member 1 — Amazon Purchase History
- Araf — Member 2 — UCI Online Shoppers Intention

---

## Prerequisites

Install these before starting:

| Tool | Mac | Windows / Linux |
|---|---|---|
| Python 3.11+ | `brew install python@3.11` or [python.org](https://www.python.org/downloads/) | [python.org](https://www.python.org/downloads/) |
| Docker Desktop | [docker.com](https://www.docker.com/products/docker-desktop) | [docker.com](https://www.docker.com/products/docker-desktop) |
| Git | `brew install git` or pre-installed | [git-scm.com](https://git-scm.com/downloads) |

After installing Docker Desktop, **launch the Docker Desktop application** before continuing. The whale icon must be visible in your menu/taskbar.

---

## Setup — run in this exact order

### 1. Clone the repository
https://github.com/AmberYasin/ecommerce-dashboard.git

### 2. Create virtual environment and install dependencies

**Mac / Linux:**

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

**Windows (PowerShell or Command Prompt):**

python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

### 3. Start the databases (Docker)
**Same on all platforms:**

docker-compose up -d
docker ps

Both `postgres` and `mongo` containers must show status `Up` before continuing. Wait ~10 seconds after `docker-compose up -d` for the databases to fully accept connections.

### 4. Load data into PostgreSQL
**Same on all platforms:**

jupyter notebook

In the Jupyter browser tab that opens:
1. Navigate to `notebooks/verification.ipynb`
2. Run the single cell (Shift+Enter)
3. Confirm the output shows row counts for all four tables (`amazon_clean`, `amazon_rfm`, `uci_clean`, `criteo_clean`)
4. Close the Jupyter tab

### 5. (Optional) Review the Dagster ETL orchestration

The dashboard does NOT depend on Dagster materialization — PostgreSQL is fully populated by the verification notebook in step 4 and the dashboard reads directly from those tables. This step is for reviewing the orchestration architecture only.

To explore the Dagster pipeline:
Open http://localhost:3000 and click "View lineage" to see the asset dependency graph. The pipeline implements raw → clean → postgres flows for all three datasets (Amazon, UCI, Criteo) under unified Dagster orchestration.

When done reviewing, stop Dagster with Ctrl+C in the terminal.

### 6. Launch the dashboard
**Mac / Linux:**

python3 -m streamlit run dashboard/app.py

**Windows:**

python -m streamlit run dashboard/app.py

Open http://localhost:8501 in your browser. Explore all 5 dashboard pages.

---

## Project Structure
ecommerce-dashboard/
├── notebooks/                     — Jupyter notebooks for each stage
│   ├── m1_amazon_ingestion.ipynb
│   ├── m1_amazon_etl.ipynb
│   ├── m1_amazon_analysis.ipynb
│   ├── m2_uci_ingestion.ipynb
│   ├── m2_uci_etl.ipynb
│   ├── m2_uci_analysis.ipynb
│   ├── m3_criteo_ingestion.ipynb
│   ├── m3_criteo_etl.ipynb
│   ├── m3_criteo_noise_injection.ipynb
│   ├── m3_criteo_analysis.ipynb
│   └── verification.ipynb         — Loads CSVs into PostgreSQL
├── pipeline/                      — Dagster orchestration
│   ├── assets.py
│   ├── definitions.py
│   └── resources.py
├── dashboard/                     — Streamlit dashboard
│   └── app.py
├── charts/                        — All generated chart files
├── amazon_clean.csv               — Shared dataset
├── amazon_rfm.csv                 — Shared dataset
├── criteo_clean.csv               — Shared dataset
├── uci_clean.csv                  — Shared dataset
├── docker-compose.yml             — PostgreSQL and MongoDB
├── requirements.txt               — Python dependencies
└── README.md                      — This file

---

## Datasets

| Dataset | Source | Records |
|---|---|---|
| Amazon US Purchase History | Consumer panel survey | 100,000 |
| UCI Online Shoppers Intention | archive.ics.uci.edu/dataset/468 | 12,330 |
| Criteo Attribution | huggingface.co/datasets/criteo | 100,000 |

---

## Architecture
Raw Data → MongoDB (raw storage)
→ ETL Notebooks (transform)
→ Dagster Pipeline (orchestrate)
→ PostgreSQL (analytical storage)
→ Streamlit Dashboard (visualise)

---

## Notes for evaluators

- The four cleaned CSV files are committed directly to the repo so the dashboard can be evaluated immediately after step 4 without needing the original raw data.
- The full ingestion pipeline from raw data is documented in the `m*_ingestion.ipynb` notebooks for methodology review.
- Estimated time from `git clone` to running dashboard on a fresh machine: 10–15 minutes.
- The Dagster pipeline (`pipeline/`) provides the orchestration architecture and is viewable in the Dagster UI. The verification notebook in step 4 is the fast path for loading pre-validated cleaned data into PostgreSQL, which the dashboard reads from directly.
---

## Troubleshooting

**Docker containers won't start**
Ensure Docker Desktop is running (whale icon visible). Run `docker-compose down` and retry `docker-compose up -d`.

**Port already in use (5432, 27017, 8501, or 3000)**
Another process is using the port. Mac/Linux: `lsof -i :PORT`. Windows: `netstat -ano | findstr :PORT`. Stop the conflicting process or restart your machine.

**Jupyter command not found**
Confirm the virtual environment is activated (you should see `(venv)` in your terminal prompt). If missing, re-run the activation command from step 2.

**Dagster assets fail to materialize**
Confirm step 4 completed successfully — Dagster reads from PostgreSQL tables that the verification notebook creates.

**Dashboard shows "no data" or errors**
Confirm both step 4 (verification notebook) and step 5 (Dagster materialization) completed before launching the dashboard.