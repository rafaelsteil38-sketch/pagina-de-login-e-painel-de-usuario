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
            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]

            # hash da senha
            password_hash = bcrypt.hashpw(
                password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            # verifica se usuário existe
            user_exists = supabase.table("users") \
                .select("*") \
                .eq("email", email) \
                .execute()

            if user_exists.data:
                return "Email já cadastrado"

            # insere usuário
            supabase.table("users").insert({
                "name": name,
                "email": email,
                "password": password_hash
            }).execute()

            return redirect("/login")

        except Exception as e:
            return f"Erro no cadastro: {str(e)}"

    return render_template("cadastro.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        try:
            email = request.form["email"]
            password = request.form["password"]

            user = supabase.table("users") \
                .select("*") \
                .eq("email", email) \
                .execute()

            if not user.data:
                return "Usuário não encontrado"

            user = user.data[0]

            password_ok = bcrypt.checkpw(
                password.encode("utf-8"),
                user["password"].encode("utf-8")
            )

            if not password_ok:
                return "Senha incorreta"

            session["user"] = user["name"]

            return redirect("/dashboard")

        except Exception as e:
            return f"Erro no login: {str(e)}"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    return render_template("dashboard.html", user=session["user"])


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)