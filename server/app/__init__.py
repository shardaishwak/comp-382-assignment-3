from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")
    # TODO: In production, the origin should be the client app pointing to the *.vercel.app domain
    CORS(app, resources={r"/*": {"origins": app.config["CORS_ORIGIN"]}})
    socketio.init_app(app, cors_allowed_origins=app.config["CORS_ORIGIN"], async_mode="eventlet")


    from app.sockets import events
    @app.route("/health")
    def health():
        return {"status": "ok"}
    
    return app
