import os
from flask import Flask
from config import config_by_name
from app.extensions import db, migrate, jwt, cors, ma


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    ma.init_app(app)

    # Register error handlers
    from app.middleware.error_handlers import register_error_handlers
    register_error_handlers(app)

    # Register JWT callbacks
    from app.middleware.auth_middleware import register_jwt_callbacks
    register_jwt_callbacks(jwt)

    # Register blueprints
    from app.api.auth.routes import auth_bp
    from app.api.users.routes import users_bp
    from app.api.documents.routes import documents_bp
    from app.api.categories.routes import categories_bp
    from app.api.chat.routes import chat_bp
    from app.api.analytics.routes import analytics_bp
    from app.api.config_rag.routes import config_rag_bp

    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(users_bp, url_prefix='/api/v1/users')
    app.register_blueprint(documents_bp, url_prefix='/api/v1/documents')
    app.register_blueprint(categories_bp, url_prefix='/api/v1/categories')
    app.register_blueprint(chat_bp, url_prefix='/api/v1/chat')
    app.register_blueprint(analytics_bp, url_prefix='/api/v1/analytics')
    app.register_blueprint(config_rag_bp, url_prefix='/api/v1/config/rag')

    # Health check
    @app.route('/api/v1/health')
    def health():
        return {'status': 'ok', 'message': 'UPAO RAG API funcionando'}

    # Register CLI commands
    register_seed_commands(app)

    return app


def register_seed_commands(app):
    @app.cli.group()
    def seed():
        """Comandos de seeds."""
        pass

    @seed.command()
    def run():
        """Ejecutar todos los seeds."""
        from app.seeds.seed_admin import seed_admin
        from app.seeds.seed_categories import seed_categories
        seed_admin()
        seed_categories()
        print("Seeds ejecutados correctamente.")

    @seed.command()
    def admin():
        """Crear admin por defecto."""
        from app.seeds.seed_admin import seed_admin
        seed_admin()

    @seed.command()
    def categories():
        """Crear categorias por defecto."""
        from app.seeds.seed_categories import seed_categories
        seed_categories()
