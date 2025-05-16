from flask import Flask
from app.config import Config
from app.models import db
from app.routes import init_app as init_routes
from app.utils import format_formula

'''
Flaskアプリケーションのファクトリ関数
アプリケーションのインスタンスを作成し、
設定、DB、ルート、テンプレートフィルターを初期化する
'''
def create_app():
    # Flaskアプリのインスタンスを作成
    app = Flask(__name__)

    # アプリの設定を読み込む(Configクラスの設定を適用)
    app.config.from_object(Config)

    # アプリケーションにDBを紐づけて初期化
    db.init_app(app)

    # ルート(Blueprint)をまとめて登録する関数を実行
    init_routes(app)

    # Jinja2のテンプレートエンジンに分子式フォーマット用のフィルターを追加
    # テンプレート内で {{ formula|formula }} みたいに使えるようになる
    app.jinja_env.filters["formula"] = format_formula

    # 初期化が終わったアプリインスタンスを返す
    return app