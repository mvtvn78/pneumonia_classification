from flask import Flask
from routes.predict import predict_bp
from routes.static import static_bp
from flask_cors import CORS


def create_app():
    app = Flask(
        __name__,
        static_folder="store",
        static_url_path="",
    )
    CORS(app)
    app.register_blueprint(static_bp)
    app.register_blueprint(predict_bp)
    return app
