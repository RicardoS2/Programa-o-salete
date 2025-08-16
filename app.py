from flask import Flask, render_template, request, redirect, url_for
import requests, uuid

app = Flask(__name__)
FIREBASE = "https://salete-d88c1-default-rtdb.firebaseio.com".rstrip("/")

def _url(path):
    return f"{FIREBASE}/{path}.json"

def _get(path):
    try:
        r = requests.get(_url(path), timeout=6)
        r.raise_for_status()
        return r.json() or {}
    except Exception:
        return {}

def _put(path, data):
    try:
        requests.put(_url(path), json=data, timeout=6)
    except Exception:
        pass

def _delete(path):
    try:
        requests.delete(_url(path), timeout=6)
    except Exception:
        pass

def categories_map():
    raw = _get("categories")
    if not isinstance(raw, dict):
        return {}
    return raw

def categories_list():
    cmap = categories_map()
    out = []
    for k, v in cmap.items():
        if isinstance(v, str):
            out.append({"id": k, "name": v})
        elif isinstance(v, dict) and "name" in v:
            out.append({"id": k, "name": v["name"]})
    out.sort(key=lambda x: x["name"].lower())
    return out

@app.route("/")
def index():
    items_map = _get("items") or {}
    cats = [c["name"] for c in categories_list()]
    q = (request.args.get("nome") or "").strip().lower()
    cat_filter = (request.args.get("categoria") or "").strip()
    items = []
    for pid, p in (items_map or {}).items():
        name = p.get("name", "")
        cat = p.get("category", "")
        if cat_filter and cat != cat_filter:
            continue
        if q and q not in name.lower():
            continue
        items.append({
            "id": pid,
            "name": name,
            "category": cat,
            "price": p.get("price", ""),
            "image": p.get("image", "https://placehold.co/600x400"),
            "description": p.get("description", "")
        })
    items.sort(key=lambda x: (x["category"].lower() if x["category"] else "", x["name"].lower()))
    return render_template("index.html", items=items, categories=cats, filtro_nome=q, filtro_categoria=cat_filter)

@app.route("/admin")
def admin():
    items = _get("items") or {}
    cats = categories_list()
    return render_template("admin.html", items=items, categories=cats)

@app.route("/admin/add", methods=["POST"])
def admin_add():
    name = (request.form.get("name") or "").strip()
    category = (request.form.get("category") or "").strip()
    price = (request.form.get("price") or "").strip()
    image = (request.form.get("image") or "").strip() or "https://placehold.co/600x400"
    description = (request.form.get("description") or "").strip()
    if not name or not category:
        return redirect(url_for("admin"))
    new_id = uuid.uuid4().hex[:12]
    _put(f"items/{new_id}", {"name": name, "category": category, "price": price, "image": image, "description": description})
    return redirect(url_for("admin"))

@app.route("/admin/edit/<item_id>", methods=["POST"])
def admin_edit(item_id):
    name = (request.form.get("name") or "").strip()
    category = (request.form.get("category") or "").strip()
    price = (request.form.get("price") or "").strip()
    image = (request.form.get("image") or "").strip() or "https://placehold.co/600x400"
    description = (request.form.get("description") or "").strip()
    if not name or not category:
        return redirect(url_for("admin"))
    _put(f"items/{item_id}", {"name": name, "category": category, "price": price, "image": image, "description": description})
    return redirect(url_for("admin"))

@app.route("/admin/delete/<item_id>")
def admin_delete(item_id):
    _delete(f"items/{item_id}")
    return redirect(url_for("admin"))

@app.route("/admin/add_category", methods=["POST"])
def admin_add_category():
    new = (request.form.get("category") or "").strip()
    if not new:
        return redirect(url_for("admin"))
    cmap = categories_map()
    values = {v for v in (cmap.values() if isinstance(cmap, dict) else []) if isinstance(v, str)}
    if new in values:
        return redirect(url_for("admin"))
    new_id = "c_" + uuid.uuid4().hex[:10]
    _put(f"categories/{new_id}", new)
    return redirect(url_for("admin"))

@app.route("/admin/delete_category/<cat_id>")
def admin_delete_category(cat_id):
    _delete(f"categories/{cat_id}")
    return redirect(url_for("admin"))

if __name__ == "__main__":
    port = int(__import__("os").environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
