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

# Multiplayer tray / working-area syncing
mp_rooms: dict[str, set] = {}  
mp_sid_to_room: dict = {}  
mp_working: dict[str, list] = {}  


def _mp_socket_room(room_id: str) -> str:
    return f"mp_{room_id}"


def _normalize_domino_id(raw) -> int | None:
    # Client sends dominoId if invalid value is None.
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _validate_mp_placements(raw) -> list | None:
    # None -> empty board
    if raw is None:
        return []
    if not isinstance(raw, list):
        return None
    out = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        pid = item.get("placementId")
        if not isinstance(pid, str) or not pid:
            continue
        did = _normalize_domino_id(item.get("dominoId"))
        if did is None:
            continue
        out.append({"placementId": pid, "dominoId": did})
    return out


def _handle_mp_disconnect(sid: str) -> bool:
    # this updates the tray on disconnect
    room_id = mp_sid_to_room.pop(sid, None)
    if not room_id:
        return False
    sock_room = _mp_socket_room(room_id)
    members = mp_rooms.get(room_id)
    if members:
        members.discard(sid)
        leave_room(sock_room)
        if not members:
            mp_rooms.pop(room_id, None)
            mp_working.pop(room_id, None)
        else:
            socketio.emit("mp_peer_left", {"roomId": room_id}, to=sock_room)
    return True


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


def _start_timer(room_id: str):
    def _tick():
        while True:
            _time.sleep(1)
            room = rooms.get(room_id)
            if not room or room["status"] != "playing":
                return
            room["timer"] -= 1
            socketio.emit("timer_tick", {"roomId": room_id, "remaining": room["timer"]}, to=room_id)
            if room["timer"] <= 0:
                room["status"] = "finished"
                # determine winner by most prefix match
                best_sid = None
                best_prefix = -1
                for sid, p in room["players"].items():
                    pm = p["game"].prefixMatch
                    if pm > best_prefix:
                        best_prefix = pm
                        best_sid = sid
                socketio.emit(
                    "time_up",
                    {"roomId": room_id, "winner": best_sid},
                    to=room_id,
                )
                return

    t = threading.Thread(target=_tick, daemon=True)
    t.start()
    rooms[room_id]["timer_thread"] = t


# ── Socket events ───────────────────────────────────────────

@socketio.on("connect")
def handle_connect():
    print(f"Client connected: {request.sid}")


@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    print(f"Client disconnected: {sid}")
    if _handle_mp_disconnect(sid): #tray disconnect
        return
    room_id = sid_to_room.pop(sid, None)
    if not room_id:
        return
    room = rooms.get(room_id)
    if not room:
        return
    player = room["players"].pop(sid, None)
    if player:
        leave_room(room_id)
        socketio.emit(
            "player_left",
            {"roomId": room_id, "playerId": sid, "playerName": player["name"]},
            to=room_id,
        )
    if not room["players"]:
        rooms.pop(room_id, None)


@socketio.on("create_room")
def handle_create_room(data):
    sid = request.sid
    player_name = data.get("playerName", "Player")
    level_id = data.get("level", "medium")
    room_id = _generate_room_id()

    level_cfg = LEVEL_CONFIG.get(level_id)
    if not level_cfg:
        emit("error", {"message": f"Unknown level: {level_id}"})
        return

    structured = generate_structured_instance(
        string_length=level_cfg["stringLength"],
        array_length=level_cfg["dominoes"],
        min_segment_length=level_cfg["minSegment"],
        max_segment_length=level_cfg["maxSegment"],
    )

    game = PCPGameState.from_dominoes(structured.dominoes)
    instance_dicts = [d.to_dict() for d in structured.dominoes]

    rooms[room_id] = {
        "players": {
            sid: {"name": player_name, "game": game, "moves": 0}
        },
        "dominoes": structured.dominoes,
        "instance_dicts": instance_dicts,
        "level": level_cfg,
        "status": "waiting",
        "timer": level_cfg["time"],
        "timer_thread": None,
        "winner": None,
    }
    sid_to_room[sid] = room_id
    join_room(room_id)

    emit("room_created", {
        "roomId": room_id,
        "level": level_cfg,
        "instance": instance_dicts,
    })


@socketio.on("join_room")
def handle_join_room(data):
    sid = request.sid
    room_id = data.get("roomId", "").strip().upper()
    player_name = data.get("playerName", "Player")

    room = rooms.get(room_id)
    if not room:
        emit("error", {"message": f"Room {room_id} not found."})
        return
    if room["status"] != "waiting":
        emit("error", {"message": "Game already in progress."})
        return
    if len(room["players"]) >= 2:
        emit("error", {"message": "Room is full."})
        return

    game = PCPGameState.from_dominoes(room["dominoes"])
    room["players"][sid] = {"name": player_name, "game": game, "moves": 0}
    sid_to_room[sid] = room_id
    join_room(room_id)

    emit(
        "player_joined",
        {"roomId": room_id, "playerName": player_name, "playerId": sid},
        to=room_id,
    )

    # Auto-start when 2 players
    if len(room["players"]) >= 2:
        room["status"] = "playing"
        players_dict = {}
        for s, p in room["players"].items():
            players_dict[s] = _player_state_dict(s, p, p["game"])

        socketio.emit(
            "game_start",
            {
                "roomId": room_id,
                "level": room["level"],
                "instance": room["instance_dicts"],
                "players": players_dict,
                "timer": room["timer"],
            },
            to=room_id,
        )
        _start_timer(room_id)

@socketio.on("place_domino")
def handle_place_domino(data):
    sid = request.sid
    room_id = data.get("roomId")
    domino_id = data.get("dominoId")

    room = rooms.get(room_id)
    if not room or sid not in room["players"]:
        emit("error", {"message": "Invalid room or player."})
        return
    if room["status"] != "playing":
        emit("error", {"message": "Game is not active."})
        return

    player = room["players"][sid]
    game = player["game"]

    try:
        game.place_domino(domino_id)
    except (ValueError, RuntimeError) as e:
        emit("error", {"message": str(e)})
        return

    player["moves"] += 1
    result = _move_result(game, player["moves"])
    emit("move_result", result)

    _emit_opponent_update(room_id, sid, game, player["moves"])

    # Win detection
    if game.is_solved:
        room["status"] = "finished"
        room["winner"] = sid
        socketio.emit(
            "match_found",
            {
                "roomId": room_id,
                "winnerId": sid,
                "winnerName": player["name"],
                "sequence": [t.to_dict() for t in game.sequence],
            },
            to=room_id,
        )

# TODO: Should we add this to the options?
@socketio.on("undo_move")
def handle_undo_move(data):
    sid = request.sid
    room_id = data.get("roomId")

    room = rooms.get(room_id)
    if not room or sid not in room["players"]:
        emit("error", {"message": "Invalid room or player."})
        return

    player = room["players"][sid]
    game = player["game"]
    removed = game.undo()

    if removed is None:
        emit("error", {"message": "Nothing to undo."})
        return

    player["moves"] += 1
    result = _move_result(game, player["moves"])
    emit("move_result", result)
    _emit_opponent_update(room_id, sid, game, player["moves"])


# TODO: Do we need reset sequence?

@socketio.on("request_hints")
def handle_request_hints(data):
    sid = request.sid
    room_id = data.get("roomId")

    room = rooms.get(room_id)
    if not room or sid not in room["players"]:
        emit("error", {"message": "Invalid room or player."})
        return

    game = room["players"][sid]["game"]
    emit("hint_update", _hints_payload(game))


@socketio.on("leave_room")
def handle_leave_room(data):
    sid = request.sid
    room_id = data.get("roomId")

    room = rooms.get(room_id)
    if not room:
        return

    player = room["players"].pop(sid, None)
    sid_to_room.pop(sid, None)
    leave_room(room_id)

    if player:
        socketio.emit(
            "player_left",
            {"roomId": room_id, "playerId": sid, "playerName": player["name"]},
            to=room_id,
        )

    if not room["players"]:
        rooms.pop(room_id, None)

@socketio.on("mp_create")
def handle_mp_create(_data=None):
    sid = request.sid
    room_id = _generate_room_id()
    mp_rooms[room_id] = {sid}
    mp_working[room_id] = []
    mp_sid_to_room[sid] = room_id
    join_room(_mp_socket_room(room_id))
    emit("mp_room_created", {"roomId": room_id})


@socketio.on("mp_join")
def handle_mp_join(data):
    sid = request.sid
    room_id = (data or {}).get("roomId", "").upper()
    if room_id not in mp_rooms:
        emit("error", {"message": f"Room {room_id or '?'} not found."})
        return
    members = mp_rooms[room_id]
    if len(members) >= 2:
        emit("error", {"message": "Room is full."})
        return
    if sid in members:
        placements = mp_working.get(room_id, [])
        emit("mp_working_state", {"roomId": room_id, "placements": placements})
        return
    members.add(sid)
    mp_sid_to_room[sid] = room_id
    join_room(_mp_socket_room(room_id))
    emit("mp_joined", {"roomId": room_id})
    emit(
        "mp_working_state",
        {"roomId": room_id, "placements": mp_working.get(room_id, [])},
    )
    socketio.emit("mp_peer_joined", {"roomId": room_id}, to=_mp_socket_room(room_id))


@socketio.on("mp_set_working")
def handle_mp_set_working(data):
    sid = request.sid
    room_id = (data or {}).get("roomId", "").upper()
    validated = _validate_mp_placements((data or {}).get("placements"))
    if validated is None:
        emit("error", {"message": "Invalid placements."})
        return
    if room_id not in mp_rooms:
        emit("error", {"message": "Invalid room."})
        return
    if sid not in mp_rooms[room_id]:
        emit("error", {"message": "Not in this room."})
        return
    mp_working[room_id] = validated
    socketio.emit(
        "mp_working_state",
        {"roomId": room_id, "placements": validated},
        to=_mp_socket_room(room_id),
    )
