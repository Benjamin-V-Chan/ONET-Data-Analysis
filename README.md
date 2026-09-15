# data-science-onet

The **analytics half** of a two-repository O*NET pipeline. It consumes the tidy
tables produced by [ONET-Data-Collector](https://github.com/Benjamin-V-Chan/ONET-Data-Collector)
and turns them into diagnostics and interpretable structure:

- **EDA** — SOC-code coverage and occupation-distribution stats + plots.
- **Clustering** — group occupations into role families via TF-IDF → TruncatedSVD → KMeans.
- **Keyword attribution** — measure where each search keyword lands across the condensed feature fields.

Everything is packaged as `onet_analysis` with a single `onet-analyze` CLI.

---

## How it fits together

```
        ONET-Data-Collector                     data-science-onet (this repo)
  ┌───────────────────────────┐          ┌──────────────────────────────────────┐
  │ search → details → condense│  CSV /   │ EDA  ·  clustering  ·  keyword attrib. │
  │  (onet_data_collector pkg) │──JSON──▶ │        (onet_analysis pkg)            │
  └───────────────────────────┘          └──────────────────────────────────────┘
```

This repo depends on the collector package and re-exposes its ETL stage through
`onet-analyze collect`, so both repositories share exactly one implementation of
the API logic.

---

## Install

```bash
git clone https://github.com/Benjamin-V-Chan/data-science-onet.git
cd data-science-onet
python -m venv .venv && source .venv/bin/activate

# Install the collector (sibling repo) — editable local checkout is best for dev:
pip install -e ../ONET-Data-Collector
#   ...or from Git:  pip install "onet_data_collector @ git+https://github.com/Benjamin-V-Chan/ONET-Data-Collector.git"

pip install -e ".[dev]"     # installs onet_analysis + the `onet-analyze` command
```

`requirements.txt` pins the same set (including a Git reference to the collector)
so `pip install -r requirements.txt` works standalone.

## Credentials

Only the collection stage needs O*NET credentials (free signup at
<https://services.onetcenter.org/developer/signup>). Set `ONET_USERNAME` /
`ONET_PASSWORD`, use a `.env` file (see `.env.example`), or pass
`--username/--password`.

---

## Usage

```bash
# 1. Collect (hits the O*NET API) — writes data/raw and data/processed
onet-analyze collect "healthcare" "technology" "design"

# 2. Analyze the collected data (no network needed)
onet-analyze eda                 # coverage + distribution tables and plots
onet-analyze keywords            # keyword → field attribution matrix + charts
onet-analyze cluster --clusters 6  # role clusters + top terms + scatter plot

# ...or everything at once
onet-analyze all "healthcare" "technology" --clusters 6
```

Use `--base <dir>` to relocate the `data/` and `results/` trees.

### As a library

```python
from onet_analysis.loading import load_csv
from onet_analysis.eda import run_eda
from onet_analysis.clustering import cluster_occupations, plot_clusters
from onet_analysis.keyword_attribution import analyze_keywords

data = load_csv("data/raw/keyword_search_results.csv")
run_eda(data, out_dir="results", processed_dir="data/processed")

result = cluster_occupations(data, n_clusters=6)
plot_clusters(result, "results/occupation_clusters.png")
print(result.top_terms)          # distinctive terms per cluster
```

---

## Outputs

```
data/processed/  soc_code_coverage.csv, occupation_distribution.csv, cluster_assignments.csv
data/results/    keyword_analysis_results.csv, per-keyword bar charts
results/         soc_code_distribution.png, unique_soc_per_keyword.png,
                 occupation_clusters.png, keyword_search_evaluation_summary.txt
```

---

## Method notes (what's real, and why)

- **TF-IDF (unigrams + bigrams)** over occupation titles (and descriptions when
  present) is a transparent, dependency-light baseline — no GPU or model
  download — whose vocabulary makes clusters explainable via top terms.
- **TruncatedSVD (LSA)** reduces the *sparse* TF-IDF matrix without densifying
  it: memory-safe, and the correct PCA analogue for sparse text.
- **KMeans** with fixed `random_state`/`n_init` gives stable, repeatable
  groupings; a silhouette score is reported and `k` is auto-clamped to the
  sample count so tiny inputs never crash.
- **Schema tolerance** — column resolution accepts naming variants
  (`Job Title` / `job_title` / `occupation_title`, etc.) so analysis survives
  export drift.
- These are interpretable **baselines**, not frontier embeddings — chosen
  deliberately for explainability and zero heavy dependencies.

The previous `requirements.txt` pulled in `torch` + `transformers` (~GBs) that
the code never imported; this version depends only on
`pandas`, `numpy`, `scikit-learn`, `matplotlib`, and (optionally) `seaborn`.

---

## Development

```bash
pip install -e ".[dev]"
pytest            # 13 tests, all offline (synthetic fixtures, no network)
```

Legacy scripts under `scripts/` are kept for backwards compatibility and now
delegate to the `onet_analysis` package; prefer the `onet-analyze` CLI.

## License

MIT — see [LICENSE](LICENSE).
