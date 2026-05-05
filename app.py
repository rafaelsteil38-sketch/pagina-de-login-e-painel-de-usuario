from flask import Flask, render_template, request, redirect, session
from supabase import create_client
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# ---------------- SUPABASE ----------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# DEBUG (aparece nos logs do Vercel)
print("SUPABASE_URL:", SUPABASE_URL)
print("SUPABASE_KEY OK:", bool(SUPABASE_KEY))

supabase = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ---------------- HOME ----------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------- CADASTRO ----------------
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        try:
            if not supabase:
                return "Erro: Supabase não configurado"

            nome = request.form["nome"]
            email = request.form["email"]
            senha = request.form["senha"]

            senha_hash = bcrypt.hashpw(
                senha.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            # verifica usuário
            usuario_existente = supabase.table("usuarios") \
                .select("*") \
                .eq("email", email) \
                .execute()

            if usuario_existente.data:
                return "Email já cadastrado"

            # insert
            res = supabase.table("usuarios").insert({
                "nome": nome,
                "email": email,
                "senha": senha_hash
            }).execute()

            print("INSERT OK:", res)

            return redirect("/login")

        except Exception as e:
            print("ERRO CADASTRO:", e)
            return f"Erro no cadastro: {e}"


    return render_template("cadastro.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        try:
            if not supabase:
                return "Erro: Supabase não configurado"

            email = request.form["email"]
            senha = request.form["senha"]

            usuario = supabase.table("usuarios") \
                .select("*") \
                .eq("email", email) \
                .execute()

            if not usuario.data:
                return "Usuário não encontrado"

            user = usuario.data[0]

            senha_correta = bcrypt.checkpw(
                senha.encode("utf-8"),
                user["senha"].encode("utf-8")
            )

            if not senha_correta:
                return "Senha incorreta"

            session["usuario"] = user["nome"]

            return redirect("/dashboard")

        except Exception as e:
            print("ERRO LOGIN:", e)
            return f"Erro no login: {e}"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    if "usuario" not in session:
        return redirect("/login")

    return render_template("dashboard.html", usuario=session["usuario"])


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- LOCAL RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)