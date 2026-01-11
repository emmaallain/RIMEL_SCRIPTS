import pandas as pd
from pathlib import Path

INPUT_CSV = Path("analysis_odis/commits_files_enriched.csv")
OUTPUT_FILE = Path("analysis_odis/file_ownership.csv")
OUTPUT_DIR = Path("analysis_odis")

def main():
    df = pd.read_csv(INPUT_CSV, parse_dates=["commit_date"])

    # On enlève les doublons commit/fichier
    df_unique = df[["commit_hash", "file_path", "author_name"]].drop_duplicates()

    # 1) Ownership par fichier
    file_author_counts = (
        df_unique.groupby(["file_path", "author_name"])
        .agg(n_commits=("commit_hash", "nunique"))
        .reset_index()
    )

    # Auteur principal par fichier
    file_owner = (
        file_author_counts.sort_values(["file_path", "n_commits"], ascending=[True, False])
        .groupby("file_path")
        .head(1)
        .rename(columns={"author_name": "main_author", "n_commits": "main_author_commits"})
    )

    # Nombre total de commits par fichier (pour calculer un ratio)
    file_totals = (
        file_author_counts.groupby("file_path")
        .agg(total_commits=("n_commits", "sum"))
        .reset_index()
    )

    ownership = file_owner.merge(file_totals, on="file_path")
    ownership["main_author_share"] = ownership["main_author_commits"] / ownership["total_commits"]

    ownership.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Ownership par fichier : {OUTPUT_FILE}")

    # 2) Ownership par dossier (ex: 'data/', 'src/' etc.)
    # On récupère le "top level" (le premier dossier dans le chemin)
    df_unique["top_dir"] = df_unique["file_path"].str.split("/").str[0]

    dir_author_counts = (
        df_unique.groupby(["top_dir", "author_name"])
        .agg(n_commits=("commit_hash", "nunique"))
        .reset_index()
    )

    dir_owner = (
        dir_author_counts.sort_values(["top_dir", "n_commits"], ascending=[True, False])
        .groupby("top_dir")
        .head(1)
        .rename(columns={"author_name": "main_author", "n_commits": "main_author_commits"})
    )

    dir_totals = (
        dir_author_counts.groupby("top_dir")
        .agg(total_commits=("n_commits", "sum"))
        .reset_index()
    )

    dir_ownership = dir_owner.merge(dir_totals, on="top_dir")
    dir_ownership["main_author_share"] = dir_ownership["main_author_commits"] / dir_ownership["total_commits"]

    dir_ownership_csv = OUTPUT_DIR / "dir_ownership.csv"
    dir_ownership.to_csv(dir_ownership_csv, index=False)
    print(f"✅ Ownership par dossier : {dir_ownership_csv}")

if __name__ == "__main__":
    main()
