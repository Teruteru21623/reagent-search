from sqlalchemy.orm import Query

def format_formula(formula):
    import re

    parts = re.findall(r"([A-Z][a-z]*)(\d*)", formula)

    result = ""
    for element, count in parts:
        if count == "" or count == "1":
            result += f"{element}"
        else:
            result += f"{element}<sub>{count}</sub>"
    return result

# SQLiteの正規表現フィルタを追加
def regexp_filter(query: Query, field, pattern):
    return query.filter(field.op("~")(pattern))