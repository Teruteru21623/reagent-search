from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.config import Config
from app.utils import login_required

auth_bp = Blueprint("auth", __name__)

# ルート(トップページ → ログイン済みならメインへ)
@auth_bp.route("/")
def home():
    if "user" in session:
        return redirect(url_for("main.main"))
    return redirect(url_for("auth.login"))

# ログイン画面
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == Config.USERNAME and password == Config.PASSWORD:
            session["user"] = username
            return redirect(url_for("main.main")) #TODO
        else:
            flash("ユーザー名またはパスワードが間違っています")
    return render_template("login.html")

# ログアウト
@auth_bp.route("/logout")
@login_required
def logout():
    session.pop("user", None)
    return redirect(url_for("auth.login")) #TODO