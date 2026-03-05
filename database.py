import sqlite3
import os
from datetime import datetime

DB_PATH = "cybershield.db"

def init_db():
    """Initialise la base de données et crée les tables si elles n'existent pas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_heure TEXT NOT NULL,
            type_attaque TEXT NOT NULL,
            niveau_criticite TEXT NOT NULL,
            ip_simulee TEXT,
            duree_connexion REAL,
            nb_connexions_par_sec REAL,
            volume_donnees_kb REAL,
            nb_erreurs REAL,
            nb_ports_scanes REAL,
            taux_echec_connexion REAL,
            taille_paquets_moy REAL,
            nb_tentatives_auth REAL,
            actions_resolution TEXT,
            confiance_modele REAL,
            statut TEXT DEFAULT 'Traité'
        )
    ''')
    conn.commit()
    conn.close()

def sauvegarder_detection(detection_data):
    """Sauvegarde une détection dans la base de données"""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO detections (
                date_heure, type_attaque, niveau_criticite, ip_simulee,
                duree_connexion, nb_connexions_par_sec, volume_donnees_kb,
                nb_erreurs, nb_ports_scanes, taux_echec_connexion,
                taille_paquets_moy, nb_tentatives_auth, actions_resolution,
                confiance_modele, statut
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            detection_data.get('date_heure', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            detection_data.get('type_attaque', 'Inconnu'),
            detection_data.get('niveau_criticite', 'INCONNU'),
            detection_data.get('ip_simulee', '0.0.0.0'),
            detection_data.get('duree_connexion', 0),
            detection_data.get('nb_connexions_par_sec', 0),
            detection_data.get('volume_donnees_kb', 0),
            detection_data.get('nb_erreurs', 0),
            detection_data.get('nb_ports_scanes', 0),
            detection_data.get('taux_echec_connexion', 0),
            detection_data.get('taille_paquets_moy', 0),
            detection_data.get('nb_tentatives_auth', 0),
            detection_data.get('actions_resolution', ''),
            detection_data.get('confiance_modele', 0),
            detection_data.get('statut', 'Traité')
        ))
        conn.commit()
    finally:
        conn.close()

def recuperer_toutes_detections():
    """Récupère toutes les détections depuis la base de données"""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM detections ORDER BY date_heure DESC')
        colonnes = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(colonnes, row)) for row in rows]
    finally:
        conn.close()

def recuperer_stats():
    """Récupère les statistiques globales"""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM detections')
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM detections WHERE type_attaque != 'Normal'")
        attaques = cursor.fetchone()[0]
        cursor.execute('SELECT type_attaque, COUNT(*) as nb FROM detections GROUP BY type_attaque')
        par_type = dict(cursor.fetchall())
        return {'total': total, 'attaques': attaques, 'normal': total - attaques, 'par_type': par_type}
    finally:
        conn.close()

def vider_historique():
    """Vide toutes les détections"""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM detections')
        conn.commit()
    finally:
        conn.close()
