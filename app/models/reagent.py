from . import db

class Reagent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) #試薬名
    code = db.Column(db.String(50), nullable=False) #試薬番号
    location = db.Column(db.String(100), nullable=False) #棚番号
    volume = db.Column(db.String(20), nullable=True) #容量
    formula = db.Column(db.String(100), nullable=True) #分子式
    company = db.Column(db.String(100), nullable=True) #試薬会社
    registrant = db.Column(db.String(50), nullable=False) #登録者名

    # デバッグ用
    def __repr__(self):
        return f"<Reagent {self.name}>"