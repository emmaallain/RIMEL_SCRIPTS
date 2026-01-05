import pandas as pd

# ==============================
# 1. Load commit-level data
# ==============================

df = pd.read_excel("Annotation_Ready.xlsx", sheet_name="Contributeurs")
df["commit_date"] = pd.to_datetime(df["commit_date"])

# ==============================
# 2. Extract file extension
# ==============================

def ext_from_path(p):
    if not isinstance(p, str) or "." not in p:
        return "unknown"
    ext = p.split(".")[-1].lower()
    return "yml" if ext in ["yaml", "yml"] else ext

df["ext"] = df["file_path"].apply(ext_from_path)

# ==============================
# 3. Monthly aggregation
# ==============================

df["month"] = df["commit_date"].dt.to_period("M").astype(str)
df["month_dt"] = pd.to_datetime(df["month"])

monthly = df.groupby(["month", "ext"]).size().unstack(fill_value=0)
monthly["total"] = monthly.sum(axis=1)

for col in monthly.columns:
    if col != "total":
        monthly[f"pct_{col}"] = monthly[col] / monthly["total"] * 100

# Documentation = markdown + yaml
monthly["pct_docs"] = (
    monthly.get("pct_md", 0) + monthly.get("pct_yml", 0)
)

monthly = monthly.reset_index()
monthly["month_dt"] = pd.to_datetime(monthly["month"])

# ==============================
# 4. Detect phase boundaries from data
# ==============================
# These dates are NOT arbitrary:
# they correspond to the first sustained appearance
# of new dominant activities in the repository.

phase2_start = monthly[monthly["pct_sql"] >= 20]["month_dt"].min()
phase3_start = monthly[monthly["pct_ipynb"] >= 10]["month_dt"].min()
phase4_start = monthly[monthly["pct_docs"] >= 30]["month_dt"].min()




# ==============================
# 4bis. Build explicit phase periods
# ==============================

project_start = monthly["month_dt"].min()
project_end = monthly["month_dt"].max()

phase_periods = pd.DataFrame([
    {
        "phase": "Phase 1 – Setup & Ingestion",
        "start_date": project_start,
        "end_date": phase2_start - pd.offsets.MonthBegin(1)
    },
    {
        "phase": "Phase 2 – Processing & Modeling",
        "start_date": phase2_start,
        "end_date": phase3_start - pd.offsets.MonthBegin(1)
    },
    {
        "phase": "Phase 3 – Analysis & Exploration",
        "start_date": phase3_start,
        "end_date": phase4_start - pd.offsets.MonthBegin(1)
    },
    {
        "phase": "Phase 4 – Stabilization & Docs",
        "start_date": phase4_start,
        "end_date": project_end
    }
])

# Format dates nicely for export / slides
phase_periods["start_date"] = phase_periods["start_date"].dt.strftime("%Y-%m")
phase_periods["end_date"] = phase_periods["end_date"].dt.strftime("%Y-%m")





# ==============================
# 5. Assign chronological project phases
# ==============================

def assign_project_phase(date):
    if date < phase2_start:
        return "Phase 1 – Setup & Ingestion"
    elif date < phase3_start:
        return "Phase 2 – Processing & Modeling"
    elif date < phase4_start:
        return "Phase 3 – Analysis & Exploration"
    else:
        return "Phase 4 – Stabilization & Docs"

df["project_phase"] = df["month_dt"].apply(assign_project_phase)

# ==============================
# 6. Contributors per phase (ranked)
# ==============================

contributors = (
    df.groupby(["project_phase", "author_name"])
      .size()
      .reset_index(name="file_changes")
)

contributors["rank_in_phase"] = (
    contributors
    .groupby("project_phase")["file_changes"]
    .rank(method="dense", ascending=False)
    .astype(int)
)

TOP_N = 5
contributors = contributors[
    contributors["rank_in_phase"] <= TOP_N
].sort_values(["project_phase", "rank_in_phase"])

# ==============================
# 7. Export result
# ==============================

with pd.ExcelWriter("Contributors_By_Phase_Ranked_3.xlsx") as writer:
    contributors.to_excel(
        writer,
        sheet_name="contributors_by_phase",
        index=False
    )
    phase_periods.to_excel(
        writer,
        sheet_name="phase_periods",
        index=False
    )

print("Phase boundaries detected:")
print("Phase 2 start:", phase2_start)
print("Phase 3 start:", phase3_start)
print("Phase 4 start:", phase4_start)
print("✔ File generated: Contributors_By_Phase_Ranked.xlsx")
