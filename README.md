# 🛡️ CyberShield AI

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-black?logo=flask)](https://flask.palletsprojects.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3.2-orange?logo=scikit-learn)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> **Système de détection et de résolution automatique de cyberattaques basé sur l'IA (Random Forest)**  
> **AI-powered cyber-attack detection and automated remediation system (Random Forest)**

---

## 🇫🇷 Description

CyberShield AI est une application web Flask qui analyse les métriques réseau en temps réel pour
identifier six types de menaces cybernétiques et proposer des actions de remédiation adaptées.
Le modèle d'intelligence artificielle (Random Forest) est entraîné sur 4 150 connexions simulées
et atteint une précision supérieure à 98 %.

## 🇬🇧 Description

CyberShield AI is a Flask web application that analyses network metrics in real time to detect six
types of cyber threats and automatically recommend remediation actions. The Random Forest model is
trained on 4 150 simulated connections and achieves over 98 % accuracy.

---

## ✨ Fonctionnalités principales

- 🖥️ **Dashboard temps réel** — statistiques globales et graphique en donut (mise à jour toutes les 5 s)
- 🔍 **Analyseur de connexion** — formulaire avec 8 métriques et scénarios rapides
- 📋 **Historique** — 100 dernières détections avec filtres par type d'attaque
- 📚 **Documentation** — architecture, algorithme, glossaire
- 🤖 **API REST** — `/api/simulate` et `/api/stats` (JSON)

---

## 🦠 Types d'attaques détectées

| Type | Criticité | Description |
|------|-----------|-------------|
| Normal | 🟢 NORMAL | Trafic réseau légitime |
| DDoS | 🔴 CRITIQUE | Saturation par flood de requêtes |
| Intrusion | 🟠 MOYEN | Accès non autorisé via scan de ports |
| Malware | 🔴 CRITIQUE | Exfiltration de données / C2 |
| Phishing | 🟡 FAIBLE | Tentative de vol d'identifiants |
| SQL_Injection | 🟠 MOYEN | Injection SQL dans les requêtes web |

---

## 🤖 Algorithme — Random Forest

Le **Random Forest** est un ensemble de 100 arbres de décision (`n_estimators=100, random_state=42`).
Chaque arbre est entraîné sur un sous-ensemble aléatoire des données et des features.
La prédiction finale est la classe majoritaire parmi tous les arbres, avec une estimation de
confiance via les probabilités moyennées.

**Features utilisées (8) :**
`duree_connexion`, `nb_connexions_par_sec`, `volume_donnees_kb`, `nb_erreurs`,
`nb_ports_scanes`, `taux_echec_connexion`, `taille_paquets_moy`, `nb_tentatives_auth`

---

## 📁 Structure du projet

```
CyberShield-AI/
├── app.py                        # Application Flask principale
├── model.py                      # Modèle IA Random Forest
├── requirements.txt              # Dépendances Python
├── README.md                     # Cette documentation
├── .gitignore
├── templates/
│   ├── base.html                 # Navbar + Footer
│   ├── index.html                # Dashboard
│   ├── analyser.html             # Analyseur de connexion
│   ├── historique.html           # Historique des détections
│   └── documentation.html       # Documentation
├── static/
│   ├── css/style.css             # Thème cybersécurité sombre
│   └── js/dashboard.js          # Chart.js + simulation temps réel
└── data/
    └── generate_dataset.py       # Génération du dataset CSV
```

---

## 🚀 Installation et lancement

### Prérequis

- Python 3.10 ou supérieur
- pip

### Étapes

```bash
# 1. Cloner le dépôt
git clone https://github.com/Small-God07/CyberShield-AI.git
cd CyberShield-AI

# 2. Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
python app.py
```

L'application est disponible sur **http://127.0.0.1:5000**

---

## 🛠️ Technologies utilisées

| Technologie | Version | Rôle |
|-------------|---------|------|
| Python | 3.10+ | Langage principal |
| Flask | 3.0.0 | Framework web |
| scikit-learn | 1.3.2 | Modèle Random Forest |
| NumPy | 1.26.2 | Génération du dataset |
| Bootstrap | 5.3.2 | Interface graphique |
| Chart.js | 4.4.2 | Graphiques interactifs |

---

## 👤 Auteur

**Small-God07** — Projet scolaire de cybersécurité IA

---

## 📄 Licence

Ce projet est distribué sous la licence **MIT**.

