from flask import Blueprint, render_template, request
from app.models.reagent import Reagent
from app.utils import login_required, regexp_filter

main_bp = Blueprint("main", __name__)

@main_bp.route("/main", methods=["GET", "POST"])
@login_required
def main():
    # フォームが送信された場合
    if request.method == "POST":

        # HTMLのname,C,H,O,N,othersからフォームデータを取得、
        name = request.form.get("name", "") #nameの値、もしくは空文字
        c = request.form.get("C", "") #Cの値、もしくは空文字
        h = request.form.get("H", "") #Hの値、もしくは空文字
        o = request.form.get("O", "") #Oの値、もしくは空文字
        n = request.form.get("N", "") #Nの値、もしくは空文字
        others = request.form.get("others", "") #othersの値、もしくは空文字

        # Reagentモデルを使ったクエリの準備。条件に合うものがqueryに追加される。
        query = Reagent.query

        # nameを部分一致検索
        if name:
            
            query = query.filter(Reagent.name.ilike(f"%{name}%"))

        # C,H,O,Nが入力されてたらその元素と数の完全一致を検索
        for element, count in [("C", c), ("H", h), ("O", o), ("N", n)]:
            if count:
                pattern = f"{element}{count}"
                query = regexp_filter(query, Reagent.formula, pattern)

        # 周期表からの元素選択
        if others:
            for el in [e.strip() for e in others.split(",") if e.strip()]:
                # 元素の後に1回以上数字が出てくるものを検索
                pattern = f"{el}[0-9]+"
                query = regexp_filter(query, Reagent.formula, pattern)

        results = query.all()
        return render_template("results.html", results=results)
    return render_template("main.html")

# 結果表示ページ
@main_bp.route("/results", methods=["GET"])
@login_required
def results():
    name_query = request.form.get("name", "")
    formula_query = request.form.get("formula", "")

    query = Reagent.query

    if name_query:
        query = query.filter(Reagent.name.ilike(f"%{name_query}%"))
    if formula_query:
        query = query.filter(Reagent.formula.ilike(f"%{formula_query}%"))

    results = query.all()

    return render_template("results.html", results=results)
