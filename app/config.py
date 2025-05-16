# アプリケーションの設定用クラスを定義
class Config:
    # セッションやCSRF対策に使う秘密鍵
    SECRET_KEY = "your_secret_key"

    # SQLiteデータベースの保存先（相対パス指定）
    # SQLiteファイルは instance/ フォルダ内に reagents.db として保存される
    SQLALCHEMY_DATABASE_URI = "postgresql://reagent_user:Tenor623@localhost/reagent_search_dev"

    # SQLAlchemyの変更通知機能を無効化（不要な警告を防ぐ）
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ログインに使うユーザー名とパスワード
    USERNAME = "chem"
    PASSWORD = "yuki"
