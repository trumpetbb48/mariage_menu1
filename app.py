from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import json, os

app = Flask(__name__)
app.secret_key = "super-secret-key"  # clé pour la session
CORS(app)

COMMANDES_FILE = "commandes.json"

# ======= UTILS ========
def load_commandes():
    if not os.path.exists(COMMANDES_FILE):
        with open(COMMANDES_FILE, 'w') as f:
            json.dump([], f)
    with open(COMMANDES_FILE, 'r') as f:
        return json.load(f)

def save_commande(commande):
    commandes = load_commandes()
    commandes.append(commande)
    with open(COMMANDES_FILE, 'w') as f:
        json.dump(commandes, f, indent=4)

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

# ======= MAIN ========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
