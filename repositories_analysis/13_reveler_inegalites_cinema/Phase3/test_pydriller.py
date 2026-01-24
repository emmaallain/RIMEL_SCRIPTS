from pydriller import Repository
from pathlib import Path
import sys

repo_path = Path(sys.argv[1]).resolve()

print("Repo path:", repo_path)
print(".git exists:", (repo_path / ".git").exists())

commits = list(Repository(str(repo_path)).traverse_commits())
print("Commits found:", len(commits))
