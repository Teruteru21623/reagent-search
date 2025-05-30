from app.utils import VALID_ELEMENTS

# バリデーションチェック
def validate_register_form(form):
    errors = []

    # 試薬名
    if not form.get("name"):
        errors.append("試薬名を入力してください")

    # 試薬番号
    if not form.get("code_prefix") or not form.get("code_number"):
        errors.append("試薬番号を正しく入力してください")
    else:
        try:
            if int(form.get("code_number")) < 1:
                errors.append("試薬番号の数字は1以上にしてください")
        except ValueError:
            errors.append("試薬番号の数字が不正です")

    # 棚番号
    location_type = form.get("location_type")
    if location_type == "numeric":
        row = form.get("location_row")
        col = form.get("location_col")
        if not row or not col:
            errors.append("棚番号（数字形式）は両方の数字を入力してください。")
    elif location_type == "preset":
        if not form.get("preset_location"):
            errors.append("棚番号（場所）を選択してください。")
    else:
        errors.append("棚番号の形式が不正です。")

    # 容量
    volume = form.get("volume")
    try:
        if float(volume) < 0:
            errors.append("容量は0以上の値にしてください。")
    except (ValueError, TypeError):
        errors.append("容量の値が不正です。")

    if not form.get("volume_unit"):
        errors.append("容量の単位を選択してください。")

    # 分子式
    elements = form.getlist("elements[]")
    counts = form.getlist("counts[]")

    for el in elements:
        if el:  # 空欄でなければ
            if el not in VALID_ELEMENTS:
                errors.append(f"{el} は無効な元素記号です。")

    for cnt in counts:
        if cnt:  # 空欄でなければ
            if not cnt.isdigit() or int(cnt) <= 0:
                errors.append(f"{cnt} は無効な数値です。")

    return errors