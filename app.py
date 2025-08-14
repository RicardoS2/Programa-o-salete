from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

FIREBASE_DB_URL = "https://salete-d88c1-default-rtdb.firebaseio.com/"

CATEGORIES = [
    "Estruturas",
    "Materiais",
    "Topografia",
    "Construção Civil",
    "Projetos",
    "Segurança"
]

# ===================== Classes =====================
class Item:
    def __init__(self, id, name, category, price, image):
        self.id = id
        self.name = name
        self.category = category
        self.price = price
        self.image = image

class FirebaseDB:
    @staticmethod
    def get_items():
        response = requests.get(FIREBASE_DB_URL + "items.json")
        data = response.json() if response.status_code == 200 and response.json() else {}
        return [Item(id=k, **v) for k, v in data.items()]

    @staticmethod
    def add_item(item):
        requests.post(FIREBASE_DB_URL + "items.json", json=item.__dict__)

    @staticmethod
    def update_item(item_id, item):
        requests.patch(FIREBASE_DB_URL + f"items/{item_id}.json", json=item.__dict__)

    @staticmethod
    def delete_item(item_id):
        requests.delete(FIREBASE_DB_URL + f"items/{item_id}.json")

# ===================== Rotas =====================
@app.route("/")
def index():
    items = FirebaseDB.get_items()
    filtro_nome = request.args.get("nome", "").lower()
    filtro_categoria = request.args.get("categoria", "")

    filtered_items = [
        item for item in items
        if (filtro_nome in item.name.lower() or not filtro_nome)
        and (item.category == filtro_categoria or not filtro_categoria)
    ]
    return render_template("index.html", items=filtered_items, categories=CATEGORIES)

@app.route("/admin")
def admin():
    items = FirebaseDB.get_items()
    return render_template("admin.html", items=items, categories=CATEGORIES)

@app.route("/admin/add", methods=["POST"])
def admin_add():
    item = Item(
        id=None,
        name=request.form.get("name"),
        category=request.form.get("category"),
        price=request.form.get("price"),
        image=request.form.get("image")
    )
    FirebaseDB.add_item(item)
    return redirect(url_for("admin"))

@app.route("/admin/edit/<item_id>", methods=["POST"])
def admin_edit(item_id):
    item = Item(
        id=item_id,
        name=request.form.get("name"),
        category=request.form.get("category"),
        price=request.form.get("price"),
        image=request.form.get("image")
    )
    FirebaseDB.update_item(item_id, item)
    return redirect(url_for("admin"))

@app.route("/admin/delete/<item_id>")
def admin_delete(item_id):
    FirebaseDB.delete_item(item_id)
    return redirect(url_for("admin"))

# ===================== Run =====================
if __name__ == "__main__":
    app.run(debug=True)
