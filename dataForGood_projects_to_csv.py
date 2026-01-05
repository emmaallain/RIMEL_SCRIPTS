from github import Github
import pandas as pd
from dotenv import load_dotenv
import os
from tqdm import tqdm

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ORG_NAME = "dataforgoodfr"

g = Github(GITHUB_TOKEN)
org = g.get_organization(ORG_NAME)
repos = org.get_repos()

results = []

for repo in tqdm(repos, desc="Processing repos"):
    try:
        commits = repo.get_commits().totalCount
        contributors = repo.get_contributors().totalCount
    except:
        commits = 0
        contributors = 0

    results.append({
        "repo_name": repo.name,
        "nb_commits": commits,
        "nb_contributors": contributors,
        "last_update": repo.pushed_at,
        "created_at": repo.created_at
    })

df = pd.DataFrame(results)

df_sorted = df.sort_values(
    by=["nb_commits","last_update", "nb_contributors"],
    ascending=[False, False, False]
)

df_sorted.to_csv("data_for_good_summary_sorted.csv", index=False)
print("CSV généré et trié : data_for_good_summary_sorted.csv")
