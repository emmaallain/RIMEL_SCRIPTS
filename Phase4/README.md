Voici une version complétée et fluide de ton document :

---

# Analyse des contributeurs

* **Étape 1 : Collecte des commits**
  
    Lancez `phase4_contributions.py <repo>` sur un repository GitHub cloné au préalable.
    Deux fichiers sont générés :

    * `commits_detailed.csv` : liste détaillée des commits et fichiers modifiés.
    * `contributors_profiles.csv` : informations des contributeurs enrichies avec leurs profils GitHub.

* **Étape 2 : Analyse des contributeurs**
  
    Lancez `phase4_contributor_analysis.py`, qui lit les résultats précédents et produit :

    * `contributors_activity_summary.csv` : activité brute par contributeur et par catégorie.
    * `contributors_profiles_inferred.csv` : type/profil de contributeur déduit.
    * `profiles_activity_over_time.csv` : activité mensuelle de chaque type de profil.

* **Étape 3 : Analyse par poste / rôle**
  
    Lancez `phase4_job_activity_over_time.py`, qui combine les commits avec les informations de poste des contributeurs (à rechercher à la main) et génère :

    * `job_activity_over_time.csv` : évolution mensuelle des contributions par rôle et par type d’activité.

