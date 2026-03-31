from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

socketio = SocketIO()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "pcp-game-secret"

    CORS(app, resources={r"/*": {"origins": "*"}})
    socketio.init_app(app, cors_allowed_origins="*", async_mode="eventlet")

    @app.route("/health")
    def health():
        return {"status": "ok"}

    from app.sockets import events

    return app
