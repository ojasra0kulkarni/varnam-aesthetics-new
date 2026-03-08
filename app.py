from flask import Flask, render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config
from models import db, User
import os

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'admin.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from flask_cors import CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from routes.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from routes.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        # Create a default admin if none exists
        if not User.query.filter_by(email='admin@varnamaesthetics.com').first():
            hashed_pw = bcrypt.generate_password_hash('password').decode('utf-8')
            default_admin = User(email='admin@varnamaesthetics.com', password_hash=hashed_pw, role='ADMIN')
            db.session.add(default_admin)
            db.session.commit()
    app.run(debug=True)
