import pandas as pd
from pathlib import Path
from utils.path_classifier import PathClassifier

BASE = Path(__file__).parent
RESULTS = BASE / "results"

COMMITS = RESULTS / "commits_detailed.csv"
JOBS = RESULTS / "contributors_jobs.csv"

OUTPUT = RESULTS / "job_activity_over_time.csv"

df = pd.read_csv(COMMITS)
jobs = pd.read_csv(JOBS)

pathClassifier = PathClassifier()
df["activity"] = df["file_path"].apply(pathClassifier.classify)

df = df.merge(jobs, on="author_email", how="left")
df["job"] = df["job"].fillna("Unknown")

table = (
    df.groupby(["month", "job", "activity"])
      .size()
      .reset_index(name="changes")
)

table.to_csv(OUTPUT, index=False)
print(f"Wrote {OUTPUT}")
