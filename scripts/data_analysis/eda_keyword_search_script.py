import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

# Avoid seaborn dependency (you imported it, but it's optional). If you want seaborn, keep it.
try:
    import seaborn as sns
    SEABORN_OK = True
except ImportError:
    SEABORN_OK = False

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

# -----------------------
# Paths + folders
# -----------------------
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
RESULTS_DIR = "results"

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

CSV_PATH = os.path.join(RAW_DIR, "keyword_search_results.csv")

# -----------------------
# Load data
# -----------------------
if not os.path.exists(CSV_PATH):
    print(f"File not found: {CSV_PATH}")
    sys.exit(1)

data = pd.read_csv(CSV_PATH)

print(data.head())
print(data.info())

# -----------------------
# Column normalization (fix common schema mismatches)
# -----------------------
# Your code assumes: 'Keyword', 'SOC Code', 'Job Title'
# Some exports use variants like 'keyword', 'soc_code', 'occupation_title', etc.
col_map = {c.strip().lower(): c for c in data.columns}

def require_column(*candidates: str) -> str:
    """Return the real column name that matches one of candidates (case-insensitive)."""
    for cand in candidates:
        key = cand.strip().lower()
        if key in col_map:
            return col_map[key]
    raise KeyError(f"Missing required column. Tried: {candidates}. Found columns: {list(data.columns)}")

keyword_col = require_column("Keyword", "keyword")
soc_col = require_column("SOC Code", "soc code", "soc_code", "soc")
title_col = require_column("Job Title", "job title", "job_title", "occupation_title", "occupation title", "title")

# Clean key text columns
data[keyword_col] = data[keyword_col].astype(str).str.strip()
data[title_col] = data[title_col].astype(str).fillna("").str.strip()
data[soc_col] = data[soc_col].astype(str).str.strip()

# Drop rows with empty titles (TF-IDF will break / become useless)
data = data[data[title_col].str.len() > 0].copy()

# -----------------------
# SOC Code Coverage
# -----------------------
soc_code_coverage = (
    data.groupby(keyword_col)[soc_col]
    .nunique()
    .reset_index()
    .rename(columns={keyword_col: "Keyword", soc_col: "Unique SOC Codes"})
)

print("SOC Code Coverage:")
print(soc_code_coverage)

# -----------------------
# Plots (with safe fallbacks)
# -----------------------
def savefig(path: str):
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()

# 1) SOC Code Distribution by Keyword
if SEABORN_OK:
    plt.figure(figsize=(14, 10))
    sns.countplot(
        y=soc_col,
        hue=keyword_col,
        data=data,
        order=data[soc_col].value_counts().index,
    )
    plt.title("SOC Code Distribution by Keyword")
    plt.xlabel("Count")
    plt.ylabel("SOC Code")
    plt.legend(title="Keyword", bbox_to_anchor=(1.05, 1), loc="upper left")
    savefig(os.path.join(RESULTS_DIR, "soc_code_distribution_by_keyword.png"))
else:
    # Basic fallback: stacked counts table saved as CSV instead of plot
    dist = pd.crosstab(data[soc_col], data[keyword_col]).sort_index()
    dist.to_csv(os.path.join(PROCESSED_DIR, "soc_code_distribution_by_keyword_table.csv"))

# 2) Keyword-Specific Occupation Distribution (heatmap)
occupation_distribution = (
    data.groupby([keyword_col, title_col])
    .size()
    .reset_index(name="Counts")
)

occupation_distribution_pivot = (
    occupation_distribution
    .pivot(index=title_col, columns=keyword_col, values="Counts")
    .fillna(0)
)

if SEABORN_OK and occupation_distribution_pivot.shape[0] > 0 and occupation_distribution_pivot.shape[1] > 0:
    plt.figure(figsize=(14, 10))
    sns.heatmap(occupation_distribution_pivot, cmap="YlGnBu")
    plt.title("Occupation Distribution by Keyword")
    plt.xlabel("Keyword")
    plt.ylabel("Job Title")
    savefig(os.path.join(RESULTS_DIR, "occupation_distribution_by_keyword.png"))
else:
    occupation_distribution_pivot.to_csv(os.path.join(PROCESSED_DIR, "occupation_distribution_pivot.csv"))

# 3) SOC Code Distribution (overall)
if SEABORN_OK:
    plt.figure(figsize=(14, 10))
    sns.countplot(
        y=soc_col,
        data=data,
        order=data[soc_col].value_counts().index,
    )
    plt.title("SOC Code Distribution")
    plt.xlabel("Count")
    plt.ylabel("SOC Code")
    savefig(os.path.join(RESULTS_DIR, "soc_code_distribution.png"))

# -----------------------
# Clustering Analysis (fixes)
# -----------------------
# Fix 1: Don't name the TF-IDF matrix "vectorizer" (confusing). Keep the object.
# Fix 2: Use sparse matrix directly; avoid .toarray() (can explode memory).
# Fix 3: Use TruncatedSVD (PCA for sparse is better via SVD). If you want PCA, densify carefully.
# Fix 4: Set random_state + n_init for stable KMeans behavior.

from sklearn.decomposition import TruncatedSVD

titles = data[title_col].fillna("").astype(str).tolist()

tfidf = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=2
)
X = tfidf.fit_transform(titles)

# Reduce dimensions (works on sparse)
svd = TruncatedSVD(n_components=2, random_state=42)
reduced = svd.fit_transform(X)

kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
clusters = kmeans.fit_predict(reduced)

# Plot clustering
plt.figure(figsize=(12, 8))
plt.scatter(reduced[:, 0], reduced[:, 1], c=clusters, alpha=0.5)
plt.title("Clustering based on Occupation Titles (TF-IDF → SVD → KMeans)")
plt.xlabel("Component 1")
plt.ylabel("Component 2")
savefig(os.path.join(RESULTS_DIR, "keyword_clustering.png"))

# -----------------------
# Save outputs
# -----------------------
soc_code_coverage.to_csv(os.path.join(PROCESSED_DIR, "soc_code_coverage.csv"), index=False)
occupation_distribution.to_csv(os.path.join(PROCESSED_DIR, "occupation_distribution.csv"), index=False)

with open(os.path.join(RESULTS_DIR, "keyword_search_evaluation_summary.txt"), "w", encoding="utf-8") as f:
    f.write("Keyword Search Evaluation Summary\n")
    f.write("================================\n\n")
    f.write("SOC Code Coverage:\n")
    f.write(soc_code_coverage.to_string(index=False))
    f.write("\n\nClustering Analysis:\n")
    f.write("TF-IDF vectorization + 2D TruncatedSVD + KMeans clustering were performed on occupation titles.\n")
    f.write("See: results/keyword_clustering.png\n")

print("Enhanced EDA completed. Findings saved to processed/ and results/.")
