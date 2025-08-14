from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# URL do Firebase Realtime Database
FIREBASE_DB_URL = "https://salete-d88c1-default-rtdb.firebaseio.com/"

# Categorias fixas
CATEGORIES = [
    "Estruturas",
    "Materiais",
    "Topografia",
    "Construção Civil",
    "Projetos",
    "Segurança"
]

# ----------------- Funções -----------------
def get_items():
    response = requests.get(FIREBASE_DB_URL + "items.json")
    if response.status_code == 200 and response.json():
        return response.json()
    return {}

def add_item(item):
    requests.post(FIREBASE_DB_URL + "items.json", json=item)

def update_item(item_id, item):
    requests.patch(FIREBASE_DB_URL + f"items/{item_id}.json", json=item)

def delete_item(item_id):
    requests.delete(FIREBASE_DB_URL + f"items/{item_id}.json")

# ----------------- Rotas -----------------
@app.route("/")
def index():
    items = get_items()
    filtro_categoria = request.args.get("categoria", "")
    filtro_nome = request.args.get("nome", "").lower()
    filtered_items = []

    for key, item in items.items():
        if (filtro_categoria in item["category"] or not filtro_categoria) and \
           (filtro_nome in item["name"].lower() or not filtro_nome):
            item["id"] = key
            filtered_items.append(item)

    return render_template("index.html", items=filtered_items, categories=CATEGORIES)

@app.route("/admin")
def admin():
    items = get_items()
    for key, item in items.items():
        item["id"] = key
    return render_template("admin.html", items=items, categories=CATEGORIES)

@app.route("/admin/add", methods=["POST"])
def admin_add():
    name = request.form.get("name")
    category = request.form.get("category")
    price = request.form.get("price")
    image = request.form.get("image")
    item = {"name": name, "category": category, "price": price, "image": image}
    add_item(item)
    return redirect(url_for("admin"))

@app.route("/admin/edit/<item_id>", methods=["POST"])
def admin_edit(item_id):
    name = request.form.get("name")
    category = request.form.get("category")
    price = request.form.get("price")
    image = request.form.get("image")
    item = {"name": name, "category": category, "price": price, "image": image}
    update_item(item_id, item)
    return redirect(url_for("admin"))

@app.route("/admin/delete/<item_id>")
def admin_delete(item_id):
    delete_item(item_id)
    return redirect(url_for("admin"))
