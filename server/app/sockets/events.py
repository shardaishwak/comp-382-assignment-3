import uuid
import threading
import time as _time

from flask import request
from flask_socketio import emit, join_room, leave_room

from app import socketio
from app.game.pcp_game_state import PCPGameState
from app.game.hint_system import compute_hints

# The data structure that we are working on is the following:
# rooms[room_id] = {
#   "players": { sid: { "name": str, "game": PCPGameState, "moves": 0 } },
#   "instance_dicts": [...],       # shared domino dicts
#   "status": "waiting"|"playing"|"finished",
#   "timer": int (seconds remaining),
#   "timer_thread": Thread | None,
#   "winner": str | None,
#   "seed": int,
# }
rooms: dict = {}

# sid -> room_id mapping for fast disconnect cleanup
sid_to_room: dict = {}

DEFAULT_TIMER = 300

