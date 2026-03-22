from app import socketio
from flask_socketio import emit
from flask import request


@socketio.on("connect")
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on("disconnect")
def handle_disconnect():
    print(f"client disconnected: {request.sid}")