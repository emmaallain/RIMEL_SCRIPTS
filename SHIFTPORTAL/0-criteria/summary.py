"""
Script 1.1 : Extraction des métadonnées du repository GitHub
Objectif : Récupérer les informations générales du projet
"""

import requests
import json
import pandas as pd
from datetime import datetime
import os

# Configuration
#GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')  # Optionnel mais recommandé
REPO_OWNER = 'dataforgoodfr'
REPO_NAME = 'shiftdataportal'

headers = {}
#if GITHUB_TOKEN:
   # headers['Authorization'] = f'token {GITHUB_TOKEN}'

def get_repo_info():
    """Récupère les informations générales du repository"""
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}'
    response = requests.get(url, headers=headers)
    return response.json()

def get_contributors():
    """Récupère la liste des contributeurs"""
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contributors'
    response = requests.get(url, headers=headers)
    return response.json()

def get_languages():
    """Récupère les langages utilisés"""
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/languages'
    response = requests.get(url, headers=headers)
    return response.json()

def get_commits_count():
    """Compte le nombre total de commits"""
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits'
    response = requests.get(url, headers=headers, params={'per_page': 1})
    
    # Le nombre total est dans le header Link
    if 'Link' in response.headers:
        links = response.headers['Link']
        # Extraire le dernier numéro de page
        import re
        match = re.search(r'page=(\d+)>; rel="last"', links)
        if match:
            return int(match.group(1))
    
    return len(response.json())

def main():
    print("=" * 60)
    print("EXTRACTION DES INFORMATIONS DU REPOSITORY")
    print("=" * 60)
    
    # Informations générales
    print("\n1. Récupération des informations générales...")
    repo_info = get_repo_info()
    
    info_data = {
        'Nom du repository': repo_info['name'],
        'Description': repo_info.get('description', 'N/A'),
        'Date de création': repo_info['created_at'],
        'Dernière mise à jour': repo_info['updated_at'],
        'URL': repo_info['html_url'],
        'Site web': repo_info.get('homepage', 'N/A'),
        'Nombre de stars': repo_info['stargazers_count'],
        'Nombre de forks': repo_info['forks_count'],
        'Nombre de watchers': repo_info['watchers_count'],
        'Issues ouvertes': repo_info['open_issues_count'],
        'Langage principal': repo_info['language'],
        'Taille (Ko)': repo_info['size'],
        'Branche par défaut': repo_info['default_branch']
    }
    
    print("\nInformations générales :")
    for key, value in info_data.items():
        print(f"  - {key}: {value}")
    
    # Sauvegarder en CSV
    pd.DataFrame([info_data]).to_csv('phase1_repo_info.csv', index=False)
    print("\n✅ Sauvegardé dans : phase1_repo_info.csv")
    
    # Contributeurs
    print("\n2. Récupération des contributeurs...")
    contributors = get_contributors()
    
    contributors_data = []
    for contrib in contributors:
        contributors_data.append({
            'username': contrib['login'],
            'contributions': contrib['contributions'],
            'profile_url': contrib['html_url'],
            'avatar_url': contrib['avatar_url']
        })
    
    df_contributors = pd.DataFrame(contributors_data)
    df_contributors = df_contributors.sort_values('contributions', ascending=False)
    df_contributors.to_csv('phase1_contributors.csv', index=False)
    
    print(f"\nNombre de contributeurs : {len(contributors)}")
    print("\nTop 5 contributeurs :")
    print(df_contributors.head().to_string(index=False))
    print("\n✅ Sauvegardé dans : phase1_contributors.csv")
    
    # Langages
    print("\n3. Récupération des langages...")
    languages = get_languages()
    
    total_bytes = sum(languages.values())
    languages_data = []
    for lang, bytes_count in languages.items():
        percentage = (bytes_count / total_bytes) * 100
        languages_data.append({
            'langage': lang,
            'bytes': bytes_count,
            'pourcentage': round(percentage, 2)
        })
    
    df_languages = pd.DataFrame(languages_data)
    df_languages = df_languages.sort_values('pourcentage', ascending=False)
    df_languages.to_csv('phase1_languages.csv', index=False)
    
    print("\nRépartition des langages :")
    print(df_languages.to_string(index=False))
    print("\n✅ Sauvegardé dans : phase1_languages.csv")
    
    # Nombre de commits
    print("\n4. Comptage des commits...")
    commits_count = get_commits_count()
    print(f"\nNombre total de commits : {commits_count}")
    
    # Résumé final
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"📊 Projet : {repo_info['name']}")
    print(f"📅 Créé le : {repo_info['created_at'][:10]}")
    print(f"👥 Contributeurs : {len(contributors)}")
    print(f"💻 Commits : ~{commits_count}")
    print(f"⭐ Stars : {repo_info['stargazers_count']}")
    print(f"🔧 Langage principal : {repo_info['language']}")
    print("=" * 60)

if __name__ == '__main__':
    main()