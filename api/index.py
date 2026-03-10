import os
import sys
# Ensure the root directory is in the python path so absolute `api.*` imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, jsonify
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from api.config import Config
from api.models import db, User

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'admin.login'

def create_app(config_class=Config):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask(__name__,
                template_folder=os.path.join(base_dir, 'templates'),
                static_folder=os.path.join(base_dir, 'public', 'static'))
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Ensure upload folder exists (may fail on read-only filesystem like Vercel)
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except Exception:
        pass

    from flask_cors import CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from api.routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from api.routes.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from api.routes.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Lazy DB initialization on first request
    @app.before_request
    def ensure_db_initialized():
        if not getattr(app, '_db_initialized', False):
            try:
                db.create_all()
                if not User.query.filter_by(email='admin@varnamaesthetics.com').first():
                    hashed_pw = bcrypt.generate_password_hash('password').decode('utf-8')
                    default_admin = User(email='admin@varnamaesthetics.com', password_hash=hashed_pw, role='ADMIN')
                    db.session.add(default_admin)
                    db.session.commit()
                app._db_initialized = True
            except Exception as e:
                print(f"DB init error: {e}")

    @app.route('/health')
    def health_check():
        try:
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            return jsonify({'status': 'ok', 'db': 'connected'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'db': str(e)}), 500

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
