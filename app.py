from flask import Flask, render_template, request, redirect, url_for
import requests
import os

app = Flask(__name__)

# URL do Firebase Realtime Database (sua URL)
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

# ------------------- Utilitários Firebase (REST) -------------------
def _items_url():
    return FIREBASE_DB_URL.rstrip("/") + "/items.json"

def _item_url(item_id):
    return FIREBASE_DB_URL.rstrip("/") + f"/items/{item_id}.json"

def get_items_dict():
    """Retorna dicionário {id: item} ou {}"""
    try:
        r = requests.get(_items_url(), timeout=6)
        r.raise_for_status()
        data = r.json() or {}
        if isinstance(data, dict):
            return data
        return {}
    except Exception:
        return {}

def add_item_dict(item):
    try:
        requests.post(_items_url(), json=item, timeout=6)
    except Exception:
        pass

def update_item_dict(item_id, item):
    try:
        requests.patch(_item_url(item_id), json=item, timeout=6)
    except Exception:
        pass

def delete_item_dict(item_id):
    try:
        requests.delete(_item_url(item_id), timeout=6)
    except Exception:
        pass

# ------------------- Rotas -------------------
@app.route("/")
def index():
    """
    Filtros via query string:
     - nome (busca parcial, case-insensitive)
     - categoria (igual)
    """
    items_dict = get_items_dict()
    filtro_nome = (request.args.get("nome") or "").strip().lower()
    filtro_categoria = (request.args.get("categoria") or "").strip()

    # Convert dict -> list com id incluso
    items_list = []
    for k, v in (items_dict.items() if isinstance(items_dict, dict) else []):
        # garantir campos
        name = v.get("name", "")
        category = v.get("category", "")
        price = v.get("price", "")
        image = v.get("image", "https://placehold.co/600x400")
        # filtros
        if filtro_categoria and category != filtro_categoria:
            continue
        if filtro_nome and filtro_nome not in name.lower():
            continue
        items_list.append({
            "id": k,
            "name": name,
            "category": category,
            "price": price,
            "image": image
        })

    # ordenar por categoria then name
    items_list.sort(key=lambda x: (x["category"].lower(), x["name"].lower()))
    return render_template("index.html", items=items_list, categories=CATEGORIES, filtro_nome=filtro_nome, filtro_categoria=filtro_categoria)

@app.route("/admin")
def admin():
    items_dict = get_items_dict()
    # manter dict to iterate in template with ids as keys
    return render_template("admin.html", items=items_dict, categories=CATEGORIES)

@app.route("/admin/add", methods=["POST"])
def admin_add():
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    price = request.form.get("price", "").strip()
    image = request.form.get("image", "").strip() or "https://placehold.co/600x400"

    if not name or category not in CATEGORIES:
        return redirect(url_for("admin"))

    item = {"name": name, "category": category, "price": price, "image": image}
    add_item_dict(item)
    return redirect(url_for("admin"))

@app.route("/admin/edit/<item_id>", methods=["POST"])
def admin_edit(item_id):
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    price = request.form.get("price", "").strip()
    image = request.form.get("image", "").strip() or "https://placehold.co/600x400"

    if not name or category not in CATEGORIES:
        return redirect(url_for("admin"))

    item = {"name": name, "category": category, "price": price, "image": image}
    update_item_dict(item_id, item)
    return redirect(url_for("admin"))

@app.route("/admin/delete/<item_id>")
def admin_delete(item_id):
    delete_item_dict(item_id)
    return redirect(url_for("admin"))

# Optional: allow running locally for dev. Vercel ignores this.
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
