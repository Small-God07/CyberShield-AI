import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


class CyberShieldModel:
    """Modèle IA Random Forest pour la détection de cyberattaques."""

    FEATURES = [
        "duree_connexion",
        "nb_connexions_par_sec",
        "volume_donnees_kb",
        "nb_erreurs",
        "nb_ports_scanes",
        "taux_echec_connexion",
        "taille_paquets_moy",
        "nb_tentatives_auth",
    ]

    ATTACK_TYPES = [
        "Normal",
        "DDoS",
        "Intrusion",
        "Malware",
        "Phishing",
        "SQL_Injection",
    ]

    SOLUTIONS = {
        "Normal": [
            "✅ Trafic réseau normal détecté",
            "Aucune action requise",
            "Continuer la surveillance standard",
        ],
        "DDoS": [
            "🔴 ALERTE CRITIQUE : Attaque DDoS détectée",
            "Activer immédiatement le rate limiting",
            "Bloquer les IP sources via le pare-feu",
            "Contacter le FAI pour filtrage en amont",
            "Activer le mode de protection DDoS (CDN)",
            "Notifier l'équipe de sécurité",
        ],
        "Intrusion": [
            "🟠 ALERTE : Tentative d'intrusion détectée",
            "Isoler le segment réseau concerné",
            "Analyser les logs d'accès immédiatement",
            "Changer les credentials compromis",
            "Appliquer le patch de sécurité manquant",
            "Lancer un scan de vulnérabilité complet",
        ],
        "Malware": [
            "🟣 ALERTE : Activité Malware détectée",
            "Isoler immédiatement le poste infecté",
            "Lancer une analyse antivirus complète",
            "Sauvegarder les données critiques",
            "Réinstaller le système si nécessaire",
            "Analyser les connexions sortantes suspectes",
        ],
        "Phishing": [
            "🟡 ALERTE : Tentative de Phishing détectée",
            "Bloquer l'URL malveillante dans le proxy",
            "Alerter les utilisateurs concernés",
            "Réinitialiser les mots de passe potentiellement volés",
            "Activer l'authentification multi-facteurs",
            "Signaler le domaine aux autorités compétentes",
        ],
        "SQL_Injection": [
            "🔵 ALERTE : Injection SQL détectée",
            "Bloquer l'adresse IP source immédiatement",
            "Vérifier l'intégrité de la base de données",
            "Analyser les logs SQL pour évaluer l'étendue",
            "Appliquer des requêtes paramétrées (ORM)",
            "Mettre à jour le WAF (Web Application Firewall)",
        ],
    }

    CRITICITE = {
        "Normal": "NORMAL",
        "DDoS": "CRITIQUE",
        "Intrusion": "MOYEN",
        "Malware": "CRITIQUE",
        "Phishing": "FAIBLE",
        "SQL_Injection": "MOYEN",
    }

    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.accuracy = 0.0
        self.is_trained = False
        self.nb_samples = 0

    def generer_dataset(self):
        """Génère 4150 connexions réseau simulées avec 6 types d'attaques."""
        np.random.seed(42)
        data = []
        labels = []

        # Normal — 1000 échantillons
        n = 1000
        data.append(np.column_stack([
            np.random.uniform(0.1, 2.0, n),    # duree_connexion
            np.random.uniform(1, 10, n),         # nb_connexions_par_sec
            np.random.uniform(10, 500, n),       # volume_donnees_kb
            np.random.randint(0, 3, n),          # nb_erreurs
            np.random.randint(0, 2, n),          # nb_ports_scanes
            np.random.uniform(0, 0.1, n),        # taux_echec_connexion
            np.random.uniform(64, 1500, n),      # taille_paquets_moy
            np.random.randint(0, 2, n),          # nb_tentatives_auth
        ]))
        labels.extend(["Normal"] * n)

        # DDoS — 750 échantillons
        n = 750
        data.append(np.column_stack([
            np.random.uniform(0.001, 0.1, n),   # duree_connexion très courte
            np.random.uniform(500, 10000, n),    # nb_connexions_par_sec très élevé
            np.random.uniform(1, 50, n),         # volume_donnees_kb faible
            np.random.randint(5, 20, n),         # nb_erreurs élevé
            np.random.randint(0, 3, n),          # nb_ports_scanes
            np.random.uniform(0.6, 1.0, n),      # taux_echec_connexion très élevé
            np.random.uniform(40, 100, n),       # taille_paquets_moy petit
            np.random.randint(0, 2, n),          # nb_tentatives_auth
        ]))
        labels.extend(["DDoS"] * n)

        # Intrusion — 700 échantillons
        n = 700
        data.append(np.column_stack([
            np.random.uniform(5, 60, n),         # duree_connexion longue
            np.random.uniform(1, 5, n),          # nb_connexions_par_sec faible
            np.random.uniform(100, 2000, n),     # volume_donnees_kb élevé
            np.random.randint(3, 15, n),         # nb_erreurs moyen-élevé
            np.random.randint(10, 100, n),       # nb_ports_scanes très élevé
            np.random.uniform(0.2, 0.7, n),      # taux_echec_connexion moyen
            np.random.uniform(200, 800, n),      # taille_paquets_moy moyen
            np.random.randint(5, 30, n),         # nb_tentatives_auth élevé
        ]))
        labels.extend(["Intrusion"] * n)

        # Malware — 700 échantillons
        n = 700
        data.append(np.column_stack([
            np.random.uniform(10, 300, n),       # duree_connexion très longue
            np.random.uniform(0.5, 3, n),        # nb_connexions_par_sec faible
            np.random.uniform(500, 5000, n),     # volume_donnees_kb très élevé
            np.random.randint(0, 5, n),          # nb_erreurs faible
            np.random.randint(0, 5, n),          # nb_ports_scanes faible
            np.random.uniform(0.0, 0.2, n),      # taux_echec_connexion faible
            np.random.uniform(800, 1500, n),     # taille_paquets_moy élevé
            np.random.randint(0, 3, n),          # nb_tentatives_auth faible
        ]))
        labels.extend(["Malware"] * n)

        # Phishing — 500 échantillons
        n = 500
        data.append(np.column_stack([
            np.random.uniform(1, 10, n),         # duree_connexion courte-moyenne
            np.random.uniform(1, 8, n),          # nb_connexions_par_sec faible
            np.random.uniform(5, 100, n),        # volume_donnees_kb faible
            np.random.randint(0, 3, n),          # nb_erreurs faible
            np.random.randint(0, 3, n),          # nb_ports_scanes faible
            np.random.uniform(0.05, 0.3, n),     # taux_echec_connexion faible-moyen
            np.random.uniform(100, 500, n),      # taille_paquets_moy moyen
            np.random.randint(1, 10, n),         # nb_tentatives_auth moyen
        ]))
        labels.extend(["Phishing"] * n)

        # SQL_Injection — 500 échantillons
        n = 500
        data.append(np.column_stack([
            np.random.uniform(0.5, 5, n),        # duree_connexion courte
            np.random.uniform(2, 20, n),         # nb_connexions_par_sec moyen
            np.random.uniform(1, 30, n),         # volume_donnees_kb très faible
            np.random.randint(5, 25, n),         # nb_erreurs élevé
            np.random.randint(0, 2, n),          # nb_ports_scanes faible
            np.random.uniform(0.3, 0.8, n),      # taux_echec_connexion élevé
            np.random.uniform(64, 300, n),       # taille_paquets_moy petit
            np.random.randint(10, 50, n),        # nb_tentatives_auth très élevé
        ]))
        labels.extend(["SQL_Injection"] * n)

        X = np.vstack(data)
        y = np.array(labels)
        self.nb_samples = len(y)
        return X, y

    def entrainer(self):
        """Entraîne le modèle Random Forest."""
        X, y = self.generer_dataset()
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        self.accuracy = round(accuracy_score(y_test, y_pred) * 100, 2)
        self.is_trained = True
        return self.accuracy

    def predire(self, connexion: list) -> dict:
        """Prédit le type d'attaque pour une connexion donnée.

        Args:
            connexion: liste de 8 valeurs correspondant aux FEATURES

        Returns:
            dict avec type_attaque, confiance, criticite, solution
        """
        if not self.is_trained:
            raise RuntimeError("Le modèle n'est pas encore entraîné.")

        X = np.array(connexion).reshape(1, -1)
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        classes = self.model.classes_
        confiance = round(float(probabilities[list(classes).index(prediction)]) * 100, 1)

        return {
            "type_attaque": prediction,
            "confiance": confiance,
            "criticite": self.CRITICITE[prediction],
            "solution": self.SOLUTIONS[prediction],
        }

    def obtenir_solution(self, type_attaque: str) -> list:
        """Retourne les actions de résolution pour un type d'attaque."""
        return self.SOLUTIONS.get(type_attaque, ["Type d'attaque inconnu"])

    def get_stats(self) -> dict:
        """Retourne les statistiques du modèle."""
        return {
            "accuracy": self.accuracy,
            "nb_samples": self.nb_samples,
            "nb_features": len(self.FEATURES),
            "nb_classes": len(self.ATTACK_TYPES),
            "is_trained": self.is_trained,
        }
