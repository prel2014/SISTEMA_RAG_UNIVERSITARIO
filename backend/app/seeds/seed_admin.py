import os
from app.extensions import db
from app.models.user import User


def seed_admin():
    email = os.getenv('ADMIN_EMAIL', 'admin@upao.edu.pe')
    password = os.getenv('ADMIN_PASSWORD', 'Admin123!')
    full_name = os.getenv('ADMIN_FULL_NAME', 'Administrador UPAO')

    existing = User.query.filter_by(email=email).first()
    if existing:
        print(f"Admin ya existe: {email}")
        return

    admin = User(
        email=email,
        full_name=full_name,
        role='admin',
        is_active=True,
    )
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print(f"Admin creado: {email}")
