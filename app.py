import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for

from model import CyberShieldModel

app = Flask(__name__)

# ── Modèle IA ──────────────────────────────────────────────────────────────
model = CyberShieldModel()
model.entrainer()

# ── Historique en mémoire (max 100 entrées) ─────────────────────────────────
historique: list = []

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


def _generer_ip() -> str:
    """Génère une adresse IP aléatoire simulée."""
    return ".".join(str(random.randint(1, 254)) for _ in range(4))


def _ajouter_historique(result: dict) -> None:
    """Ajoute une entrée dans l'historique (max 100)."""
    entry = {
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type_attaque": result["type_attaque"],
        "criticite": result["criticite"],
        "ip": _generer_ip(),
        "confiance": result["confiance"],
        "badge": ATTACK_BADGE.get(result["type_attaque"], "secondary"),
        "statut": "Résolu" if result["type_attaque"] != "Normal" else "Normal",
    }
    historique.insert(0, entry)
    if len(historique) > 100:
        historique.pop()


# ── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    stats = model.get_stats()
    attaques = [e for e in historique if e["type_attaque"] != "Normal"]
    recentes = historique[:10]

    # Comptage par type pour le graphique
    comptage = {t: 0 for t in model.ATTACK_TYPES}
    for entry in historique:
        comptage[entry["type_attaque"]] = comptage.get(entry["type_attaque"], 0) + 1

    return render_template(
        "index.html",
        stats=stats,
        nb_detections=len(historique),
        nb_attaques=len(attaques),
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
            _ajouter_historique(result)
        except (ValueError, RuntimeError) as e:
            result = {"error": str(e)}
    return render_template("analyser.html", result=result)


@app.route("/historique")
def historique_page():
    return render_template("historique.html", historique=historique, badge_map=ATTACK_BADGE)


@app.route("/historique/vider", methods=["POST"])
def vider_historique():
    historique.clear()
    return redirect(url_for("historique_page"))


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
    _ajouter_historique(result)
    entry = historique[0]
    return jsonify({
        "success": True,
        "entry": entry,
        "stats": _build_stats(),
    })


@app.route("/api/stats")
def api_stats():
    return jsonify(_build_stats())


def _build_stats() -> dict:
    attaques = [e for e in historique if e["type_attaque"] != "Normal"]
    comptage = {t: 0 for t in model.ATTACK_TYPES}
    for entry in historique:
        comptage[entry["type_attaque"]] = comptage.get(entry["type_attaque"], 0) + 1
    model_stats = model.get_stats()
    return {
        "nb_detections": len(historique),
        "nb_attaques": len(attaques),
        "accuracy": model_stats["accuracy"],
        "nb_normal": comptage.get("Normal", 0),
        "comptage": comptage,
        "recentes": historique[:10],
    }


if __name__ == "__main__":
    app.run(debug=True)
