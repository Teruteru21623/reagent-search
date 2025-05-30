from flask import Blueprint, render_template, request
from app.models.reagent import Reagent
from app.utils import login_required, regexp_filter
from sqlalchemy import Text, and_, cast

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
        reagent_letter = request.form.get("reagent_letter", "")
        danger_toggle = request.form.get("danger_toggle", "")
        others = request.form.get("others", "") #othersの値、もしくは空文字

        # Reagentモデルを使ったクエリの準備。条件に合うものがqueryに追加される。
        query = Reagent.query
        conditions = []

        # nameを部分一致検索
        if name:
            conditions.append(Reagent.name.ilike(f"%{name}%"))

        # C,H,O,Nが入力されてたらその元素と数の完全一致を検索
        for el, count in [("C", c), ("H", h), ("O", o), ("N", n)]:
            if count:
                conditions.append(Reagent.element_counts.contains({el: int(count)}))

        # 試薬番号のアルファベット
        if reagent_letter:
            conditions.append(Reagent.code.startswith(reagent_letter))

        if danger_toggle == "on":
            conditions.append(Reagent.status.in_(["毒物", "劇物"]))
            
        # 周期表からの元素選択
        print(others)
        if others:
            for el in [e.strip() for e in others.split(",") if e.strip()]:
                pattern = f'"{el}": [0-9]+'
                conditions.append(cast(Reagent.element_counts, Text).op("~")(pattern))

        if conditions:
            query = query.filter(and_(*conditions))

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
