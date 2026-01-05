import os
import csv
import requests

# -------------------------------------------------
# CONFIG
# -------------------------------------------------

REPO = "dataforgoodfr/13_odis"   # Le repo ciblé
TOKEN = ""  # Charge ton token dans l'environnement !!!


HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "contrib-analyzer"
}

if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


# -------------------------------------------------
# 1. Récupération des contributeurs du repo
# -------------------------------------------------

def get_repo_contributors(full_repo_name):
    contributors = []
    page = 1

    print(f"🔍 Récupération des contributeurs pour {full_repo_name}...")

    while True:
        url = f"https://api.github.com/repos/{full_repo_name}/contributors"
        resp = requests.get(url, headers=HEADERS, params={"per_page": 100, "page": page})

        if resp.status_code == 404:
            print("⚠️  Repo introuvable ou pas de droits.")
            return contributors

        if resp.status_code == 403:
            print("⛔ Rate limit ou accès refusé.")
            print("Réponse : ", resp.text[:200])
            break

        resp.raise_for_status()
        data = resp.json()

        if not data:
            break

        for user in data:
            contributors.append({
                "login": user["login"],
                "contributions": user.get("contributions", 0)
            })

        if len(data) < 100:
            break

        page += 1

    print(f"✅ {len(contributors)} contributeurs trouvés.")
    return contributors


# -------------------------------------------------
# 2. Récupération du profil GitHub
# -------------------------------------------------

def get_user_profile(login):
    url = f"https://api.github.com/users/{login}"
    resp = requests.get(url, headers=HEADERS)

    if resp.status_code == 404:
        return None

    resp.raise_for_status()
    data = resp.json()

    return {
        "login": login,
        "name": data.get("name"),
        "company": data.get("company"),
        "location": data.get("location"),
        "bio": data.get("bio"),
    }


# -------------------------------------------------
# 3. Inférence du rôle
# -------------------------------------------------

def infer_role(profile):
    text = " ".join([
        profile.get("bio") or "",
        profile.get("company") or "",
    ]).lower()

    keywords = {
        "Data Scientist": ["data scientist", "data science"],
        "Data Engineer": ["data engineer"],
        "ML Engineer": ["machine learning", "ml engineer"],
        "Backend Developer": ["backend"],
        "Frontend Developer": ["frontend"],
        "Fullstack Developer": ["fullstack"],
        "DevOps": ["devops"],
        "Student / Apprentice": ["student", "étudiant", "apprentice"],
        "Researcher": ["research", "chercheur"],
    }

    for role, words in keywords.items():
        if any(w in text for w in words):
            return role

    return "Unknown"


# -------------------------------------------------
# 4. Export CSV
# -------------------------------------------------

def export_to_csv(filepath, repo, contributors, profiles):
    print(f"\n📦 Export CSV → {filepath}")

    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([
            "repository",
            "login",
            "name",
            "company",
            "location",
            "bio",
            "inferred_role",
            "contributions"
        ])

        for c in contributors:
            login = c["login"]
            profile = profiles.get(login, {})

            writer.writerow([
                repo,
                login,
                profile.get("name", ""),
                profile.get("company", ""),
                profile.get("location", ""),
                (profile.get("bio") or "").replace("\n", " "),
                profile.get("inferred_role", "Unknown"),
                c["contributions"]
            ])

    print("🎉 Export terminé !")


# -------------------------------------------------
# MAIN
# -------------------------------------------------

if __name__ == "__main__":

    # 1) Contributeurs
    contributors = get_repo_contributors(REPO)

    # 2) Profils uniques
    print("\n📥 Récupération des profils GitHub...")
    profiles = {}

    for c in contributors:
        login = c["login"]
        p = get_user_profile(login)
        if p:
            p["inferred_role"] = infer_role(p)
            profiles[login] = p

    # 3) CSV final
    export_to_csv("contributors_13_odis.csv", REPO, contributors, profiles)
