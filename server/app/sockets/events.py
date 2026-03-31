import uuid
import threading
import time as _time

from flask import request
from flask_socketio import emit, join_room, leave_room

from app import socketio
from app.game.pcp_game_state import PCPGameState, generate_structured_instance
from app.game.hint_system import compute_hints

LEVEL_CONFIG = {
    "easy": {
        "id": "easy",
        "name": "Easy",
        "description": "Shorter strings, fewer dominoes",
        "dominoes": 4,
        "stringLength": 8,
        "minSegment": 1,
        "maxSegment": 3,
        "time": 300,
    },
    "medium": {
        "id": "medium",
        "name": "Medium",
        "description": "Balanced challenge",
        "dominoes": 6,
        "stringLength": 12,
        "minSegment": 1,
        "maxSegment": 4,
        "time": 240,
    },
    "hard": {
        "id": "hard",
        "name": "Hard",
        "description": "Longer strings, more dominoes",
        "dominoes": 8,
        "stringLength": 16,
        "minSegment": 2,
        "maxSegment": 4,
        "time": 180,
    },
}

# The data structure that we are working on is the following:
# rooms[room_id] = {
#   "players": { sid: { "name": str, "game": PCPGameState, "moves": 0 } },
#   "instance_dicts": [...],       # shared domino dicts (from structured generation)
#   "dominoes": [Domino, ...],     # actual Domino objects for new players
#   "level": dict,                 # level config dict sent to clients
#   "status": "waiting"|"playing"|"finished",
#   "timer": int (seconds remaining),
#   "timer_thread": Thread | None,
#   "winner": str | None,
# }
rooms: dict = {}

# sid -> room_id mapping for fast disconnect cleanup
sid_to_room: dict = {}

def _generate_room_id() -> str:
    return uuid.uuid4().hex[:6].upper()


def _player_state_dict(sid: str, player: dict, game: PCPGameState) -> dict:
    return {
        "sid": sid,
        "name": player["name"],
        "sequence": [t.to_dict() for t in game.sequence],
        "moves": player["moves"],
        "score": 0,
        "hintsEnabled": 1,
        "connected": 1,
    }


def _move_result(game: PCPGameState, moves: int) -> dict:
    snap = game.snapshot()
    return {
        "sequence": snap["sequence"],
        "topString": snap["topString"],
        "bottomString": snap["bottomString"],
        "validNextIds": snap["validNextIds"],
        "isDeadEnd": snap["isDeadEnd"],
        "isSolved": snap["isSolved"],
        "prefixMatch": snap["prefixMatch"],
        "moves": moves,
    }


def _hints_payload(game: PCPGameState) -> dict:
    hints, best = compute_hints(game)
    hint_list = [
        {"dominoId": h.idx, "score": h.score, "explanation": h.explanation}
        for h in hints
    ]
    best_dict = (
        {"dominoId": best.idx, "score": best.score, "explanation": best.explanation}
        if best
        else None
    )
    return {"hints": hint_list, "bestHint": best_dict}


def _opponent_sid(room_id: str, my_sid: str):
    room = rooms.get(room_id)
    if not room:
        return None
    for sid in room["players"]:
        if sid != my_sid:
            return sid
    return None


def _emit_opponent_update(room_id: str, my_sid: str, game: PCPGameState, moves: int):
    opp = _opponent_sid(room_id, my_sid)
    if opp:
        emit(
            "opponent_update",
            {
                "opponentId": my_sid,
                "sequence": [t.to_dict() for t in game.sequence],
                "moves": moves,
                "prefixMatch": game.prefixMatch,
            },
            to=opp,
        )
