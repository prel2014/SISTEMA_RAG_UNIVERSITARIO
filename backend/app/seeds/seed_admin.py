import os
from werkzeug.security import generate_password_hash
from app.db import call_fn


def seed_admin():
    email = os.getenv('ADMIN_EMAIL', 'admin@upao.edu.pe')
    password = os.getenv('ADMIN_PASSWORD', 'Admin123!')
    full_name = os.getenv('ADMIN_FULL_NAME', 'Administrador UPAO')

    password_hash = generate_password_hash(password)
    created = call_fn('fn_seed_admin', (email, password_hash, full_name), fetch_one=True)

    if created and created['fn_seed_admin']:
        print(f"Admin creado: {email}")
    else:
        print(f"Admin ya existe: {email}")
