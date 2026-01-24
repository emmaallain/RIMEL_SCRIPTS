import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent
RESULTS = BASE / "results"

COMMITS = RESULTS / "commits_detailed.csv"
JOBS = RESULTS / "contributors_jobs.csv"

OUTPUT = RESULTS / "job_activity_over_time.csv"


def classify_path(path: str) -> str:
    path = path.replace("\\", "/").lower()

    # --- exploration ---
    if "database/notebooks/" in path or path.endswith(".ipynb"):
        return "exploration"

    # --- ML integration ---
    if "database/data/machine_learning_predictions/" in path:
        return "ml_integration"

    # --- DB structuration ---
    if "database/alembic/" in path or "database/seed/" in path:
        return "db_structuration"

    # --- data processing ---
    if "database/data/" in path:
        return "data_processing"

    # --- backend ---
    if "backend/" in path:
        return "backend"

    # --- infra (CI/CD, Docker, GitHub Actions) ---
    if any(k in path for k in [
        ".github/workflows",
        "dockerfile",
        "docker-compose",
        "ci",
        "cd"
    ]):
        return "infra"

    # --- config ---
    if path.endswith((".yml", ".yaml", ".toml", ".ini", ".lock")):
        return "config"

    # --- docs ---
    if path.endswith((".md", ".rst")):
        return "docs"

    return "other"


df = pd.read_csv(COMMITS)
jobs = pd.read_csv(JOBS)

df["activity"] = df["file_path"].apply(classify_path)

df = df.merge(jobs, on="author_email", how="left")
df["job"] = df["job"].fillna("Unknown")

table = (
    df.groupby(["month", "job", "activity"])
      .size()
      .reset_index(name="changes")
)

table.to_csv(OUTPUT, index=False)
print(f"Wrote {OUTPUT}")
