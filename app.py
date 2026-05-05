from flask import Flask, render_template, request, redirect, session
from supabase import create_client
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        senha_hash = bcrypt.hashpw(
            senha.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        usuario_existente = supabase.table("usuarios") \
            .select("*") \
            .eq("email", email) \
            .execute()

        if usuario_existente.data:
            return "Email já cadastrado"

        supabase.table("usuarios").insert({
            "nome": nome,
            "email": email,
            "senha": senha_hash
        }).execute()

        return redirect("/login")

    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        senha = request.form["senha"]

        usuario = supabase.table("usuarios") \
            .select("*") \
            .eq("email", email) \
            .execute()

        if not usuario.data:
            return "Usuário não encontrado"

        usuario = usuario.data[0]

        senha_correta = bcrypt.checkpw(
            senha.encode("utf-8"),
            usuario["senha"].encode("utf-8")
        )

        if not senha_correta:
            return "Senha incorreta"

        session["usuario"] = usuario["nome"]

        return redirect("/dashboard")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "usuario" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        usuario=session["usuario"]
    )


@app.route("/logout")
def logout():

    session.pop("usuario", None)

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)