from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        from app.models import Admin
        db.create_all()

        if not Admin.query.filter_by(username="admin").first():
            admin = Admin(
                name="System Admin",
                username="admin",
                password="admin123",
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()

    return app
