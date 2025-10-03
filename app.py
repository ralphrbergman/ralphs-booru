from flask import Flask

def create_app() -> Flask:
    app = Flask(
        import_name = __name__,
        template_folder = 'template'
    )

    return app
