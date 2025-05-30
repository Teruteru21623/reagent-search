from typing import Counter
import pandas as pd
from sqlalchemy.orm import Query
import re
import chemparse

def format_formula(formula):
    if not isinstance(formula, str) or not formula.strip():
        return ""

    return re.sub(r"([A-Z][a-z]*)(\d*)", lambda m: f"{m.group(1)}<sub>{m.group(2)}</sub>" if m.group(2) else m.group(1), formula)

# SQLiteの正規表現フィルタを追加
def regexp_filter(query: Query, field, pattern):
    return query.filter(field.op("~")(pattern))

# クレンジング関数
def clean_formula(formula):
    if pd.isnull(formula):
        return ""
    
    formula = str(formula).replace("・", ".").replace("．", ".")
    formula = re.sub(r"[≡:=]", "", formula)
    formula = formula.replace("[", "(").replace("]", ")").replace("〔", "(").replace("〕", ")")
    formula = formula.replace(" ", "")
    formula = re.sub(r"[^A-Za-z0-9().]", "", formula)

    return formula

def parse_formula(formula):
    if formula == "":
        return {}

    total_counts = Counter()

    # ピリオド区切り（例：C16H36FN.3H2O）
    for part in formula.split("."):
        if not part:
            continue

        # 先頭に数字がある場合（例：3H2O）
        match = re.match(r"^(\d+)([A-Za-z0-9()]+)$", part)
        if match:
            multiplier = int(match.group(1))
            subformula = match.group(2)
        else:
            multiplier = 1
            subformula = part

        # chemparseで読ませる（例：CH3CH2OH）
        try:
            counts = chemparse.parse_formula(subformula)
            counts_int = {k: int(v) * multiplier for k, v in counts.items()}
            total_counts.update(counts_int)
        except ValueError:
            # chemparseで読めない場合、括弧前の係数付き（例：(CH3(CH2)3)4）
            bracket_match = re.match(r"^(\(*[A-Za-z0-9]+\)*)(\d+)$", subformula)
            if bracket_match:
                subformula_inner = bracket_match.group(1)
                inner_multiplier = int(bracket_match.group(2))
                try:
                    counts = chemparse.parse_formula(subformula_inner)
                    counts_int = {k: int(v) * inner_multiplier * multiplier for k, v in counts.items()}
                    total_counts.update(counts_int)
                except ValueError:
                    pass
            else:
                pass  # それ以外は無視

    return dict(total_counts)