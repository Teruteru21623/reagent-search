from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.reagent import Reagent
from app.models import db
from app.utils import validate_register_form, login_required, clean_formula, parse_formula
import re

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
        number_input = request.form.get("code_number")  # ← ユーザー入力の数字を受け取る
        
        if number_input and number_input.isdigit():
            code = f"{prefix}{number_input}"

        else:
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

        """
        formula_parts = [f"{el}{cnt}" for el, cnt in zip(elements, counts)]
        formula = "".join(formula_parts)
        """

        formula_parts = []
        for el, cnt in zip(elements, counts):
            if cnt and cnt.strip():  # 入力がある場合のみ
                formula_parts.append(f"{el}{cnt}")

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

# 容量の正規化
def parse_volume(volume_str):
    if not volume_str:
        return "", "g"  # デフォルト
    match = re.match(r"^(\d+)\s*([a-zA-Z]*)$", volume_str.strip())
    if match:
        num = match.group(1)
        unit = match.group(2) if match.group(2) else "g"
        return num, unit
    return volume_str, "g"  # 数字以外ならそのまま

@register_bp.route("/edit_reagent/<int:reagent_id>", methods=["GET", "POST"])
@login_required
def edit_reagent(reagent_id):
    reagent = Reagent.query.get(reagent_id)

    # volume を分解
    volume_num, volume_unit = parse_volume(reagent.volume)
    if request.method == "POST":
        errors = validate_register_form(request.form)
        if errors:
            elements = request.form.getlist("elements[]")
            counts = request.form.getlist("counts[]")
            zipped_formula = zip(elements, counts)
            return render_template("register.html", errors=errors, form=request.form)
        
        # 試薬名
        reagent.name = request.form.get("name")

        # 試薬番号（アルファベット + 数字）
        prefix = request.form.get("code_prefix")
        number_input = request.form.get("code_number")
        if number_input and number_input.isdigit():
            reagent.code = f"{prefix}{number_input}"
        else:
            existing_codes = (
                db.session.query(Reagent.code)
                .filter(Reagent.code.like(f"{prefix}%"))
                .all()
            )
            used_numbers = [int(code[0].replace(prefix, "")) for code in existing_codes if code[0].replace(prefix, "").isdigit()]

            next_number = 1
            while next_number in used_numbers:
                next_number += 1

            reagent.code = f"{prefix}{next_number}"

        # 棚番号
        location_type = request.form.get("location_type")
        if location_type == "numeric":
            row = request.form.get("location_row")
            col = request.form.get("location_col")
            reagent.location = f"{row}-{col}"
        else:
            preset_location = request.form.get("preset_location")
            if preset_location == "その他":
                reagent.location = request.form.get("custom_location")
            else:
                reagent.location = preset_location

        # 容量
        volume = request.form.get("volume")
        unit = request.form.get("volume_unit")
        reagent.volume = f"{volume} {unit}"

        # 分子式
        elements = request.form.getlist("elements[]")
        counts = request.form.getlist("counts[]")
        formula_parts = []
        for el, cnt in zip(elements, counts):
            if cnt and cnt.strip():
                formula_parts.append(f"{el}{cnt}")
        reagent.formula = "".join(formula_parts)
        formula_clean = clean_formula(reagent.formula)
        reagent.element_counts = parse_formula(formula_clean)

        # 状態
        reagent.status = request.form.get("status", "その他")

        # 試薬会社
        company = request.form.get("company")
        if company == "その他":
            company = request.form.get("custom_company")
        reagent.company = company

        # 登録者
        reagent.registrant = request.form.get("registrant")

        # DB に反映
        db.session.commit()
        flash("更新が完了しました")

        # hidden input から絞り込み・ソートを取得して redirect
        name_filter = request.form.get("name", "")
        formula_filter = request.form.get("formula", "")

        return redirect(url_for("main.results",
                                name=name_filter,
                                formula=formula_filter,
                                sort="code"))

    return render_template("edit.html", reagent=reagent, volume_num=volume_num, volume_unit=volume_unit)

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