from . import db
from sqlalchemy.dialects.postgresql import JSONB

class Reagent(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=True) # 試薬名
    code = db.Column(db.String(50), nullable=True) # 試薬番号
    location = db.Column(db.String(100), nullable=True) # 棚番号
    volume = db.Column(db.String(20), nullable=True) # 容量
    formula = db.Column(db.String(100), nullable=True) # 分子式
    company = db.Column(db.String(255), nullable=True) # 試薬会社
    registrant = db.Column(db.String(50), nullable=True) # 登録者名
    status = db.Column(db.String(20), nullable=False, default="その他") # 劇物/毒物/その他
    element_counts = db.Column(JSONB)

    # デバッグ用
    def __repr__(self):
        return f"<Reagent {self.name}>"