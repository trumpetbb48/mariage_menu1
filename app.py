from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json, os

app = Flask(__name__)
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

@app.route("/commande", methods=["POST", "OPTIONS"])
def recevoir_commande():
    if request.method == "OPTIONS":
        return '', 200  # Réponse vide mais OK pour le preflight

    data = request.get_json()
    save_commande(data)
    return f"Commande de la table {data.get('table')} bien reçue !"

# ======= ROUTES ADMIN ========
@app.route("/admin")
def admin_page():
    return render_template("admin.html")

@app.route("/commandes", methods=["GET"])
def afficher_commandes():
    return jsonify(load_commandes())

# ======= MAIN ========
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
