from flask import Flask
from blueprint import index_bp

def create_app() -> Flask:
    app = Flask(
        import_name = __name__,
        template_folder = 'template'
    )

    app.register_blueprint(index_bp)

    return app
