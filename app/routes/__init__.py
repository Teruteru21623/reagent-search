from .auth import auth_bp
from .main import main_bp
from .register import register_bp

def init_app(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(register_bp)