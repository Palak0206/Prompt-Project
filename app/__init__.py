
from flask import Flask

from app.routes import api


def create_app():

    app = Flask(__name__)

    app.register_blueprint(api)

    @app.get("/health")
    def health_check():
        return {
            "status": "ok",
            "message": "Timetable API is running"
        }, 200

    return app
