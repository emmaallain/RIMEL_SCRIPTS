import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"

INPUT_COMMITS = RESULTS_DIR / "commits_detailed.csv"

OUTPUT_ACTIVITY = RESULTS_DIR / "contributors_activity_summary.csv"
OUTPUT_PROFILES = RESULTS_DIR / "contributors_profiles_inferred.csv"
OUTPUT_TIMELINE = RESULTS_DIR / "profiles_activity_over_time.csv"


def classify_path(path: str) -> str:
    path = path.replace("\\", "/")

    if "database/notebooks/" in path and path.endswith(".ipynb"):
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


def infer_profile(row: pd.Series) -> str:
    total = row["total_changes"]
    if total == 0:
        return "inactive"

    if row.get("ml_integration", 0) / total >= 0.3:
        return "ML-oriented"

    if row.get("exploration", 0) / total >= 0.4:
        return "Data exploration"

    if row.get("db_structuration", 0) / total >= 0.4:
        return "Data engineering"

    if row.get("backend", 0) / total >= 0.4:
        return "Backend-oriented"

    return "Mixed / support"


def main():
    df = pd.read_csv(INPUT_COMMITS)

    # ---- classify each file change
    df["category"] = df["file_path"].apply(classify_path)

    # ---- aggregate activity per contributor
    activity = (
        df.groupby(["author_email", "category"])
          .size()
          .unstack(fill_value=0)
    )

    activity["total_changes"] = activity.sum(axis=1)

    activity.to_csv(OUTPUT_ACTIVITY)

    # ---- infer contributor profiles
    profiles = activity.copy()
    profiles["profile"] = profiles.apply(infer_profile, axis=1)

    profiles.to_csv(OUTPUT_PROFILES)

    # ---- profile activity over time
    timeline = (
        df.merge(
            profiles[["profile"]],
            left_on="author_email",
            right_index=True
        )
        .groupby(["month", "profile"])
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )

    timeline.to_csv(OUTPUT_TIMELINE)

    print("Written:")
    print(f"- {OUTPUT_ACTIVITY}")
    print(f"- {OUTPUT_PROFILES}")
    print(f"- {OUTPUT_TIMELINE}")


if __name__ == "__main__":
    main()
