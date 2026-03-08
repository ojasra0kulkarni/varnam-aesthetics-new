from app import create_app, bcrypt
from models import db, User

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    admin = User(
        email='admin@varnamaesthetics.com',
        password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
        role='ADMIN'
    )
    db.session.add(admin)
    db.session.commit()
    print("Database re-initialized successfully with customer_address column!")
