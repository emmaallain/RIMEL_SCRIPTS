import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from utils.categories import INFRA, DB, DOCS, TESTING, EXPLORATION, ML, DATA, FRONTEND, BACKEND, CONFIG

BASE = Path(__file__).parent
RESULTS = BASE / "results"

INPUT = RESULTS / "job_activity_over_time.csv"
OUTPUT = RESULTS / "activity_evolution_stacked_area.png"

df = pd.read_csv(INPUT)
df = df.sort_values("month")

activities = [
    INFRA,
    DATA,
    DOCS,
    TESTING,
    DB,
    ML,
    EXPLORATION,
    FRONTEND,
    BACKEND,
    CONFIG,
    "other"
]

color_map = {
    INFRA: "#1f77b4",
    DATA: "#ff7f0e",
    DOCS: "#2ca02c",
    TESTING: "#d62728",
    DB: "#9467bd",
    ML: "#8c564b",
    EXPLORATION: "#ffb2e8",
    FRONTEND: "#7f7f7f",
    BACKEND: "#bcbd22",
    CONFIG: "#17becf",
    "other": "#ff00b7" 
}

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
    colors=[color_map[a] for a in activities],
    alpha=0.9
)

plt.xlabel("Mois")
plt.ylabel("Nombre de modifications")
plt.title("Évolution des types d'activités dans le projet")
plt.legend(title="Activité", ncol=3)
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

plt.savefig(OUTPUT, dpi=300)
plt.close()

print(f"Wrote {OUTPUT}")
