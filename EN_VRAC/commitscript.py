from pydriller import Repository
import pandas as pd
from pathlib import Path

# ------------ CONFIG ------------

# Si ton script est dans le dossier RIMEL et le repo dans RIMEL/13_odis :
REPO_PATH = Path(".")

# Si ton script est DANS le repo (RIMEL/13_odis/script.py), alors utilise :
# REPO_PATH = Path(".")

OUTPUT_DIR = Path("analysis_odis")

# ------------ SCRIPT ------------

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    rows = []

    print(f"Analyse du dépôt : {REPO_PATH.resolve()}")

    # Parcours de tous les commits
    for commit in Repository(str(REPO_PATH)).traverse_commits():
        # ⚠️ ICI la correction : modified_files (et plus modifications)
        for mod in commit.modified_files:
            file_path = mod.new_path or mod.old_path
            if file_path is None:
                continue

            rows.append(
                {
                    "commit_hash": commit.hash,
                    "commit_date": commit.author_date,
                    "author_name": commit.author.name,
                    "author_email": commit.author.email,
                    "message": commit.msg,
                    "file_path": file_path,
                    # ⚠️ ICI aussi : added_lines / deleted_lines
                    "added_lines": mod.added_lines,
                    "removed_lines": mod.deleted_lines,
                    "change_type": mod.change_type.name,  # ADD, MODIFY, DELETE, RENAME
                }
            )

    df = pd.DataFrame(rows)
    df.sort_values("commit_date", inplace=True)

    # CSV brut
    raw_csv = OUTPUT_DIR / "commits_files_raw.csv"
    df.to_csv(raw_csv, index=False)
    print(f"📄 Fichier brut sauvegardé : {raw_csv}")

    # Colonnes enrichies
    df["file_extension"] = df["file_path"].str.extract(r"(\.[^./\\]+)$", expand=False)
    # 👇 partie corrigée
    df["commit_date"] = pd.to_datetime(df["commit_date"], utc=True)
    df["commit_date"] = df["commit_date"].dt.tz_convert(None)
    df["year"] = df["commit_date"].dt.year
    df["month"] = df["commit_date"].dt.to_period("M").astype(str)

    enriched_csv = OUTPUT_DIR / "commits_files_enriched.csv"
    df.to_csv(enriched_csv, index=False)
    print(f"🎉 Fichier enrichi sauvegardé : {enriched_csv}")

if __name__ == "__main__":
    main()
