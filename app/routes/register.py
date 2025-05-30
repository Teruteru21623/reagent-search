from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.reagent import Reagent
from app.models import db
from app.utils import validate_register_form, login_required, clean_formula, parse_formula

register_bp = Blueprint("register", __name__)

@register_bp.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if request.method == "POST":
        errors = validate_register_form(request.form)
        if errors:
            elements = request.form.getlist("elements[]")
            counts = request.form.getlist("counts[]")
            zipped_formula = zip(elements, counts)
            return render_template("register.html", errors=errors, form=request.form)
        
        # 試薬名
        name = request.form.get("name")

        # 試薬番号（アルファベット + 数字）
        prefix = request.form.get("code_prefix")

        
        existing_codes = (
            db.session.query(Reagent.code)
            .filter(Reagent.code.like(f"{prefix}%"))
            .all()
        )
        used_numbers = [int(code[0].replace(prefix, "")) for code in existing_codes if code[0].replace(prefix, "").isdigit()]

        next_number = 1
        while next_number in used_numbers:
            next_number += 1

        code = f"{prefix}{next_number}"
        

        
        # 必要になったらこの2行をコメントアウトする
        '''
        number = request.form.get("code_number")
        code = f"{prefix}{number}"
        '''
        

        # 棚番号（形式に応じて組み立て）
        location_type = request.form.get("location_type")
        if location_type == "numeric":
            row = request.form.get("location_row")
            col = request.form.get("location_col")
            location = f"{row}-{col}"
        else:
            preset_location = request.form.get("preset_location")
            if preset_location == "その他":
                location = request.form.get("custom_location")
            else:
                location = preset_location

        # 容量（g または mL）
        volume = request.form.get("volume")
        unit = request.form.get("volume_unit")
        volume_str = f"{volume} {unit}"

        # 分子式（元素と数のリストを結合）
        elements = request.form.getlist("elements[]")
        counts = request.form.getlist("counts[]")

        formula_parts = [f"{el}{cnt}" for el, cnt in zip(elements, counts)]
        formula = "".join(formula_parts)

        formula_clean = clean_formula(formula)
        element_counts = parse_formula(formula_clean)

        # 毒劇物
        status = request.form.get("status", "その他")

        # 試薬会社
        company = request.form.get("company")
        if company == "その他":
            company = request.form.get("custom_company")

        # 登録者
        registrant = request.form.get("registrant")

        # 登録処理
        reagent = Reagent(
            name=name,
            code=code,
            location=location,
            volume=volume_str,
            formula=formula,
            company=company,
            registrant=registrant,
            status=status,
            element_counts=element_counts
        )

        db.session.add(reagent)
        db.session.commit()

        flash("登録が完了しました")
        return redirect(url_for("register.register"))

    return render_template("register.html")

@register_bp.route("/register/next_number")
@login_required
def get_next_number():
    prefix = request.args.get("alphabet")
    if not prefix:
        return jsonify({"number": None})

    existing_codes = (
        db.session.query(Reagent.code)
        .filter(Reagent.code.like(f"{prefix}%"))
        .all()
    )
    used_numbers = [int(code[0].replace(prefix, "")) for code in existing_codes if code[0].replace(prefix, "").isdigit()]

    next_number = 1
    while next_number in used_numbers:
        next_number += 1

    return jsonify({"number": next_number})


@register_bp.route("/delete/<int:reagent_id>", methods=["POST"])
@login_required
def delete_reagent(reagent_id):
    # 試薬をデータベースから取得
    reagent = Reagent.query.get_or_404(reagent_id)
    
    # 試薬を削除
    db.session.delete(reagent)
    db.session.commit()
    
    # 削除後、mainページにリダイレクト
    return redirect(request.referrer or url_for("main.main"))

@register_bp.route("/api/get_next_code_number")
@login_required
def get_next_code_number():
    prefix = request.args.get("prefix", "")
    if not prefix or len(prefix) != 1:
        return jsonify({"next_number": None})

    # prefixで始まる既存コードを取得
    existing_codes = (
        db.session.query(Reagent.code)
        .filter(Reagent.code.like(f"{prefix}%"))
        .all()
    )
    # 数字部分を抽出し、整数に変換できるものだけリストに
    used_numbers = [int(code[0].replace(prefix, "")) for code in existing_codes if code[0].replace(prefix, "").isdigit()]

    next_number = 1
    while next_number in used_numbers:
        next_number += 1

    return jsonify({"next_number": next_number})