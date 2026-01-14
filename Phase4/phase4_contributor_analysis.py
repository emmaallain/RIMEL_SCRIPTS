import pandas as pd
from pathlib import Path
from utils.path_classifier import PathClassifier
from utils.contributor_classifier import ContributorClassifier


BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"

INPUT_COMMITS = RESULTS_DIR / "commits_detailed.csv"

OUTPUT_ACTIVITY = RESULTS_DIR / "contributors_activity_summary.csv"
OUTPUT_PROFILES = RESULTS_DIR / "contributors_profiles_inferred.csv"
OUTPUT_TIMELINE = RESULTS_DIR / "profiles_activity_over_time.csv"

def main():
    df = pd.read_csv(INPUT_COMMITS)

    # ---- classify each file change
    pathClassifier = PathClassifier()
    df["category"] = df["file_path"].apply(pathClassifier.classify)

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
    contributor_classifier = ContributorClassifier()
    profiles["profile"] = profiles.apply(contributor_classifier.infer, axis=1)

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
