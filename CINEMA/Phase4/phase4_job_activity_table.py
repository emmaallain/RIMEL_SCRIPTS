import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent
RESULTS = BASE / "results"

COMMITS = RESULTS / "commits_detailed.csv"
JOBS = RESULTS / "contributors_jobs.csv"

OUTPUT = RESULTS / "job_activity_over_time.csv"


def classify_path(path: str) -> str:
    path = path.replace("\\", "/")

    if "database/notebooks/" in path:
        return "exploration"
    if "database/data/machine_learning_predictions/" in path:
        return "ml_integration"
    if "database/alembic/" in path or "database/seed/" in path:
        return "db_structuration"
    if "database/data/" in path:
        return "data_processing"
    if "backend/" in path:
        return "backend"
    return "infra"


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
