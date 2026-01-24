import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(__file__).parent
RESULTS = BASE / "results"

INPUT = RESULTS / "job_activity_over_time.csv"
OUTPUT = RESULTS / "activity_evolution_stacked_area.png"

df = pd.read_csv(INPUT)
df = df.sort_values("month")

activities = [
    "backend",
    "data_processing",
    "db_structuration",
    "exploration",
    "ml_integration",
    "infra",
    "config",
    "docs",
    "other"
]

# --- aggregate per month & activity
pivot = (
    df.groupby(["month", "activity"])["changes"]
      .sum()
      .unstack(fill_value=0)
      .reindex(columns=activities, fill_value=0)
)

months = pivot.index.tolist()

plt.figure(figsize=(14, 7))

plt.stackplot(
    months,
    [pivot[a] for a in activities],
    labels=activities,
    alpha=0.9
)

plt.xlabel("Mois")
plt.ylabel("Nombre de modifications")
plt.title("Évolution des types d’activités dans le projet")
plt.legend(title="Activité", ncol=3)
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

plt.savefig(OUTPUT, dpi=300)
plt.close()

print(f"Wrote {OUTPUT}")
