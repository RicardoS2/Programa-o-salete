from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, db
import os

# --- Config Firebase ---
cred_path = os.path.join(os.path.dirname(__file__), "../serviceAccountKey.json")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://salete-d88c1-default-rtdb.firebaseio.com/'
})

app = Flask(__name__)

# --- Categorias fixas ---
CATEGORIAS = [
    "Materiais de Construção",
    "Máquinas e Equipamentos",
    "Projetos Estruturais",
    "Ferramentas de Medição",
    "Segurança do Trabalho",
    "Tecnologia em Engenharia"
]

# --- Rotas --- 
@app.route("/", methods=["GET"])
def index():
    ref = db.reference("/catalogo")
    itens = ref.get() or []

    filtro_categoria = request.args.get("categoria", "")
    filtro_nome = request.args.get("nome", "")
    filtro_preco = request.args.get("preco", "")

    # Filtros
    if filtro_categoria:
        itens = [i for i in itens if i["categoria"] == filtro_categoria]
    if filtro_nome:
        itens = [i for i in itens if filtro_nome.lower() in i["nome"].lower()]
    if filtro_preco:
        try:
            preco_val = float(filtro_preco)
            itens = [i for i in itens if float(i["preco"]) <= preco_val]
        except:
            pass

    return render_template("index.html", itens=itens, categorias=CATEGORIAS,
                           filtro_categoria=filtro_categoria,
                           filtro_nome=filtro_nome,
                           filtro_preco=filtro_preco)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    ref = db.reference("/catalogo")
    itens = ref.get() or []

    if request.method == "POST":
        nome = request.form.get("nome")
        categoria = request.form.get("categoria")
        preco = request.form.get("preco")
        descricao = request.form.get("descricao")
        uso = request.form.get("uso")
        imagem = "https://placehold.co/600x400"

        novo_id = max([i.get("id", 0) for i in itens], default=0) + 1

        item = {
            "id": novo_id,
            "nome": nome,
            "categoria": categoria,
            "preco": preco,
            "descricao": descricao,
            "uso": uso,
            "imagem": imagem
        }
        itens.append(item)
        ref.set(itens)
        return redirect(url_for("admin"))

    # Remover item
    remover_id = request.args.get("remover")
    if remover_id:
        itens = [i for i in itens if str(i["id"]) != remover_id]
        ref.set(itens)
        return redirect(url_for("admin"))

    return render_template("admin.html", itens=itens, categorias=CATEGORIAS)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
