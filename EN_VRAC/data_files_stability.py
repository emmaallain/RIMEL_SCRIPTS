import pandas as pd
from pathlib import Path

INPUT_CSV = Path("analysis_odis/commits_files_enriched.csv")
OUTPUT = Path("analysis_odis/data_files_stability.csv")

DATA_EXTS = {".csv", ".json", ".geojson", ".parquet"}

def main():
    df = pd.read_csv(INPUT_CSV, parse_dates=["commit_date"])

    # On garde que les fichiers de données
    if "file_extension" not in df.columns:
        df["file_extension"] = df["file_path"].str.extract(r"(\.[^./\\]+)$", expand=False)

    data_files = df[df["file_extension"].str.lower().isin(DATA_EXTS)].copy()

    if data_files.empty:
        print("⚠️ Aucun fichier de données trouvé avec les extensions définies.")
        return

    data_files["year_month"] = data_files["commit_date"].dt.to_period("M").astype(str)

    summary = (
        data_files.groupby("file_path")
        .agg(
            n_commits=("commit_hash", "nunique"),
            first_change=("commit_date", "min"),
            last_change=("commit_date", "max"),
            active_months=("year_month", "nunique"),
            total_lines_added=("added_lines", "sum"),
            total_lines_removed=("removed_lines", "sum"),
        )
        .reset_index()
        .sort_values("n_commits", ascending=False)
    )

    summary.to_csv(OUTPUT, index=False)
    print(f"✅ Stabilité des fichiers de données : {OUTPUT}")

if __name__ == "__main__":
    main()
