import csv
import io
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, make_response
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm

from model import CyberShieldModel
from database import (
    init_db,
    sauvegarder_detection,
    recuperer_toutes_detections,
    recuperer_stats,
    vider_historique as db_vider_historique,
)

app = Flask(__name__)

# ── Modèle IA ──────────────────────────────────────────────────────────────
model = CyberShieldModel()
model.entrainer()

# ── Initialisation de la base de données ───────────────────────────────────
init_db()

ATTACK_BADGE = {
    "Normal": "success",
    "DDoS": "danger",
    "Intrusion": "warning",
    "Malware": "purple",
    "Phishing": "phishing",
    "SQL_Injection": "primary",
}

CRITICITE_BADGE = {
    "NORMAL": "success",
    "FAIBLE": "warning",
    "MOYEN": "orange",
    "CRITIQUE": "danger",
}


SIMULATION_NOISE_FACTOR = 0.15
MAX_PDF_ROWS = 50


def _generer_ip() -> str:
    """Génère une adresse IP aléatoire simulée."""
    return ".".join(str(random.randint(1, 254)) for _ in range(4))


def _db_to_entry(db_row: dict) -> dict:
    """Convertit une ligne de la base de données au format attendu par les templates et l'API."""
    return {
        "datetime": db_row["date_heure"],
        "type_attaque": db_row["type_attaque"],
        "criticite": db_row["niveau_criticite"],
        "ip": db_row["ip_simulee"],
        "confiance": db_row["confiance_modele"],
        "badge": ATTACK_BADGE.get(db_row["type_attaque"], "secondary"),
        "statut": db_row["statut"],
    }


def _ajouter_historique(result: dict, connexion: list = None) -> None:
    """Sauvegarde une détection dans la base de données."""
    detection_data = {
        "date_heure": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type_attaque": result["type_attaque"],
        "niveau_criticite": result["criticite"],
        "ip_simulee": _generer_ip(),
        "confiance_modele": result["confiance"],
        "statut": "Résolu" if result["type_attaque"] != "Normal" else "Normal",
        "actions_resolution": " | ".join(result.get("solution", [])),
    }
    if connexion and len(connexion) >= 8:
        detection_data.update({
            "duree_connexion": connexion[0],
            "nb_connexions_par_sec": connexion[1],
            "volume_donnees_kb": connexion[2],
            "nb_erreurs": connexion[3],
            "nb_ports_scanes": connexion[4],
            "taux_echec_connexion": connexion[5],
            "taille_paquets_moy": connexion[6],
            "nb_tentatives_auth": connexion[7],
        })
    sauvegarder_detection(detection_data)


# ── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    stats = model.get_stats()
    db_stats = recuperer_stats()
    all_entries = recuperer_toutes_detections()
    recentes = [_db_to_entry(row) for row in all_entries[:10]]

    comptage = {t: 0 for t in model.ATTACK_TYPES}
    for t, count in db_stats["par_type"].items():
        if t in comptage:
            comptage[t] = count

    return render_template(
        "index.html",
        stats=stats,
        nb_detections=db_stats["total"],
        nb_attaques=db_stats["attaques"],
        recentes=recentes,
        comptage=comptage,
        badge_map=ATTACK_BADGE,
    )


@app.route("/analyser", methods=["GET", "POST"])
def analyser():
    result = None
    if request.method == "POST":
        try:
            connexion = [
                float(request.form.get("duree_connexion", 0)),
                float(request.form.get("nb_connexions_par_sec", 0)),
                float(request.form.get("volume_donnees_kb", 0)),
                float(request.form.get("nb_erreurs", 0)),
                float(request.form.get("nb_ports_scanes", 0)),
                float(request.form.get("taux_echec_connexion", 0)),
                float(request.form.get("taille_paquets_moy", 0)),
                float(request.form.get("nb_tentatives_auth", 0)),
            ]
            result = model.predire(connexion)
            result["badge"] = ATTACK_BADGE.get(result["type_attaque"], "secondary")
            result["criticite_badge"] = CRITICITE_BADGE.get(result["criticite"], "secondary")
            _ajouter_historique(result, connexion=connexion)
        except (ValueError, RuntimeError) as e:
            result = {"error": str(e)}
    return render_template("analyser.html", result=result)


@app.route("/historique")
def historique_page():
    all_entries = recuperer_toutes_detections()
    entries = [_db_to_entry(row) for row in all_entries]
    return render_template("historique.html", historique=entries, badge_map=ATTACK_BADGE)


@app.route("/historique/vider", methods=["POST"])
def vider_historique():
    db_vider_historique()
    return jsonify({"success": True})


@app.route("/documentation")
def documentation():
    return render_template("documentation.html")


# ── API JSON ─────────────────────────────────────────────────────────────────

@app.route("/api/simulate")
def api_simulate():
    """Simule une détection aléatoire et l'ajoute à l'historique."""
    scenarios = {
        "Normal":        [1.2, 5, 150, 1, 0, 0.05, 512, 1],
        "DDoS":          [0.02, 8000, 10, 15, 1, 0.95, 60, 0],
        "Intrusion":     [30, 2, 800, 8, 50, 0.45, 400, 20],
        "Malware":       [120, 1, 3000, 2, 2, 0.05, 1200, 1],
        "Phishing":      [3, 4, 40, 1, 1, 0.15, 250, 5],
        "SQL_Injection": [2, 10, 15, 18, 0, 0.65, 120, 35],
    }
    attack_type = random.choice(list(scenarios.keys()))
    # Ajouter du bruit pour varier les simulations
    base = scenarios[attack_type]
    noisy = [max(0, v + v * random.uniform(-SIMULATION_NOISE_FACTOR, SIMULATION_NOISE_FACTOR)) for v in base]
    result = model.predire(noisy)
    result["badge"] = ATTACK_BADGE.get(result["type_attaque"], "secondary")
    result["criticite_badge"] = CRITICITE_BADGE.get(result["criticite"], "secondary")
    _ajouter_historique(result, connexion=noisy)
    all_entries = recuperer_toutes_detections()
    entry = _db_to_entry(all_entries[0]) if all_entries else {}
    return jsonify({
        "success": True,
        "entry": entry,
        "stats": _build_stats(),
    })


@app.route("/api/stats")
def api_stats():
    return jsonify(_build_stats())


def _build_stats() -> dict:
    db_stats = recuperer_stats()
    all_entries = recuperer_toutes_detections()
    recentes = [_db_to_entry(row) for row in all_entries[:10]]
    comptage = {t: 0 for t in model.ATTACK_TYPES}
    for t, count in db_stats["par_type"].items():
        if t in comptage:
            comptage[t] = count
    model_stats = model.get_stats()
    return {
        "nb_detections": db_stats["total"],
        "nb_attaques": db_stats["attaques"],
        "accuracy": model_stats["accuracy"],
        "nb_normal": db_stats["normal"],
        "comptage": comptage,
        "recentes": recentes,
    }


# ── Export ───────────────────────────────────────────────────────────────────

@app.route("/export/csv")
def export_csv():
    detections = recuperer_toutes_detections()
    output = io.StringIO()
    writer = csv.writer(output)

    # En-têtes
    writer.writerow([
        'ID', 'Date/Heure', 'Type Attaque', 'Niveau Criticité', 'IP Simulée',
        'Durée Connexion', 'Nb Connexions/sec', 'Volume Données (KB)',
        'Nb Erreurs', 'Ports Scannés', 'Taux Échec', 'Taille Paquets',
        'Tentatives Auth', 'Actions Résolution', 'Confiance Modèle (%)', 'Statut'
    ])

    for d in detections:
        writer.writerow([
            d['id'], d['date_heure'], d['type_attaque'], d['niveau_criticite'],
            d['ip_simulee'], d['duree_connexion'], d['nb_connexions_par_sec'],
            d['volume_donnees_kb'], d['nb_erreurs'], d['nb_ports_scanes'],
            d['taux_echec_connexion'], d['taille_paquets_moy'], d['nb_tentatives_auth'],
            d['actions_resolution'], d['confiance_modele'], d['statut']
        ])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=cybershield_rapport.csv'
    response.headers['Content-type'] = 'text/csv'
    return response


@app.route("/export/pdf")
def export_pdf():
    detections = recuperer_toutes_detections()
    stats = recuperer_stats()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                             rightMargin=2*cm, leftMargin=2*cm,
                             topMargin=2*cm, bottomMargin=2*cm)

    elements = []
    styles = getSampleStyleSheet()

    # Titre
    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                  fontSize=20, textColor=colors.HexColor('#00d4ff'),
                                  spaceAfter=20)
    elements.append(Paragraph("CyberShield AI — Rapport de Détections", title_style))
    elements.append(Paragraph(f"Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Statistiques
    elements.append(Paragraph("Statistiques Globales", styles['Heading2']))
    stats_data = [
        ['Métrique', 'Valeur'],
        ['Total détections', str(stats['total'])],
        ['Attaques détectées', str(stats['attaques'])],
        ['Trafic normal', str(stats['normal'])],
        ['Taux de détection', f"{round(stats['attaques']/max(stats['total'],1)*100, 1)}%"]
    ]
    stats_table = Table(stats_data, colWidths=[8*cm, 8*cm])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#00d4ff')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f0f8ff')]),
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 20))

    # Tableau des détections
    elements.append(Paragraph("Historique des Détections", styles['Heading2']))
    if detections:
        table_data = [['Date/Heure', 'Type Attaque', 'Niveau', 'IP', 'Confiance', 'Statut']]
        for d in detections[:MAX_PDF_ROWS]:  # Max MAX_PDF_ROWS lignes
            table_data.append([
                d['date_heure'][:16],
                d['type_attaque'],
                d['niveau_criticite'],
                d['ip_simulee'],
                f"{d['confiance_modele']}%",
                d['statut']
            ])
        det_table = Table(table_data, colWidths=[3.5*cm, 3*cm, 2.5*cm, 3*cm, 2.5*cm, 2.5*cm])
        det_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0a0e1a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f0f8ff')]),
        ]))
        elements.append(det_table)
    else:
        elements.append(Paragraph("Aucune détection enregistrée.", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=cybershield_rapport.pdf'
    response.headers['Content-Type'] = 'application/pdf'
    return response


if __name__ == "__main__":
    app.run(debug=True)
