from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import json, os

app = Flask(__name__)
app.secret_key = "super-secret-key"  # clé pour la session
CORS(app)

COMMANDES_FILE = "commandes.json"
EPUISÉS_FILE = "epuises.json"


# ======= UTILS ========
def load_commandes():
    if not os.path.exists(COMMANDES_FILE):
        with open(COMMANDES_FILE, 'w') as f:
            json.dump([], f)
    with open(COMMANDES_FILE, 'r') as f:
        return json.load(f)


def save_commande(commande):
    commandes = load_commandes()
    commande["id"] = len(commandes) + 1
    commande["livree"] = False
    commandes.append(commande)
    with open(COMMANDES_FILE, 'w') as f:
        json.dump(commandes, f, indent=4)


def load_epuises():
    if not os.path.exists(EPUISÉS_FILE):
        with open(EPUISÉS_FILE, "w") as f:
            json.dump([], f)
    with open(EPUISÉS_FILE, "r") as f:
        return json.load(f)


def save_epuise(plat):
    epuises = load_epuises()
    if plat not in epuises:
        epuises.append(plat)
        with open(EPUISÉS_FILE, "w") as f:
            json.dump(epuises, f, indent=4)


# ======= ROUTES INVITÉS ========
@app.route("/", methods=["GET"])
def menu_page():
    return render_template("menu.html")


@app.route("/commande", methods=["POST"])
def recevoir_commande():
    data = request.get_json()
    save_commande(data)
    return f"Commande de la table {data.get('table')} bien reçue !"


# ======= LOGIN / LOGOUT ========
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Exemple simple (à remplacer par une base plus tard si besoin)
        if username == "admin" and password == "EmmaJhon":
            session["admin"] = True
            return redirect(url_for("admin_page"))
        else:
            return render_template("login.html", error="❌ Identifiants incorrects")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))


# ======= ROUTES ADMIN (protégées) ========
@app.route("/admin")
def admin_page():
    if not session.get("admin"):
        return redirect(url_for("login"))
    return render_template("admin.html")


@app.route("/commandes", methods=["GET"])
def afficher_commandes():
    if not session.get("admin"):
        return jsonify({"error": "Accès refusé"}), 403
    return jsonify(load_commandes())


@app.route("/commandes/<int:cid>/livree", methods=["POST"])
def marquer_livree(cid):
    if not session.get("admin"):
        return jsonify({"error": "Accès refusé"}), 403

    commandes = load_commandes()
    data = request.get_json()
    for c in commandes:
        if c.get("id") == cid:
            c["livree"] = data.get("livree", False)
            break

    with open(COMMANDES_FILE, "w") as f:
        json.dump(commandes, f, indent=4)

    return jsonify({"message": f"Commande {cid} mise à jour"})


# @app.route("/epuises", methods=["GET", "POST"])
# def gerer_epuises():
#     if not session.get("admin"):
#         return jsonify({"error": "Accès refusé"}), 403

#     if request.method == "GET":
#         return jsonify(load_epuises())

#     if request.method == "POST":
#         data = request.get_json()
#         plat = data.get("plat")
#         save_epuise(plat)
#         return jsonify({"message": f"{plat} marqué comme épuisé"})


# --- Lecture publique (invités et admin) ---
@app.route("/epuises", methods=["GET"])
def epuises_public():
    resp = jsonify(load_epuises())
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp

# --- Ajout protégé (réservé à l’admin) ---
@app.route("/epuises", methods=["POST"])
def epuises_add():
    if not session.get("admin"):
        return jsonify({"error": "Accès refusé"}), 403
    data = request.get_json()
    plat = (data.get("plat") or "").strip()
    if not plat:
        return jsonify({"error": "Plat manquant"}), 400
    save_epuise(plat)
    return jsonify({"message": f"{plat} marqué comme épuisé"})


# --- Suppression (réactivation) protégée ---
@app.route("/epuises", methods=["DELETE"])
def epuises_remove():
    if not session.get("admin"):
        return jsonify({"error": "Accès refusé"}), 403

    data = request.get_json() or {}
    plat = (data.get("plat") or "").strip()
    if not plat:
        return jsonify({"error": "Plat manquant"}), 400

    epuises = load_epuises()
    if plat in epuises:
        epuises.remove(plat)
        with open(EPUISÉS_FILE, "w") as f:
            json.dump(epuises, f, indent=4)
        return jsonify({"message": f"{plat} réactivé"})
    else:
        return jsonify({"error": f"{plat} introuvable"}), 404

# ======= MAIN ========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
