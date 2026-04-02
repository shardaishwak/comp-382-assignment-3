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
    from app.sockets.events import (
        rooms, sid_to_room, _move_result, _emit_opponent_update,
        _generate_room_id, _start_timer, LEVEL_CONFIG,
    )
    from app.game.pcp_game_state import PCPGameState, generate_structured_instance
    from flask import request as flask_request, jsonify

    @app.route("/api/create_room", methods=["POST"])
    def api_create_room():
        body = flask_request.get_json(force=True)
        sid = body.get("sid")
        player_name = body.get("playerName", "Player")
        level_id = body.get("level", "medium")
        single_player = body.get("singlePlayer", False)
        use_timer = body.get("useTimer", True)
        show_hints = body.get("showHints", False)
        show_undo = body.get("showUndo", False)

        # If this sid already has a room, return it (idempotent for React Strict Mode)
        existing_room_id = sid_to_room.get(sid)
        if existing_room_id and existing_room_id in rooms:
            room = rooms[existing_room_id]
            return jsonify({
                "roomId": existing_room_id,
                "level": room["level"],
                "instance": room["instance_dicts"],
                "status": room["status"],
                "timer": room["timer"],
            })

        level_cfg = LEVEL_CONFIG.get(level_id)
        if not level_cfg:
            return jsonify({"error": f"Unknown level: {level_id}"}), 400

        room_id = _generate_room_id()
        structured = generate_structured_instance(
            string_length=level_cfg["stringLength"],
            array_length=level_cfg["dominoes"],
            min_segment_length=level_cfg["minSegment"],
            max_segment_length=level_cfg["maxSegment"],
        )
        game = PCPGameState.from_dominoes(structured.dominoes)
        instance_dicts = [d.to_dict() for d in structured.dominoes]

        rooms[room_id] = {
            "players": {sid: {"name": player_name, "game": game, "moves": 0}},
            "game": game,
            "moves": 0,
            "dominoes": structured.dominoes,
            "instance_dicts": instance_dicts,
            "level": level_cfg,
            "status": "playing" if single_player else "waiting",
            "timer": level_cfg["time"] if use_timer else 0,
            "use_timer": use_timer,
            "timer_thread": None,
            "winner": None,
            "turn_order": [sid] if single_player else [],
            "current_turn_index": 0,
            "show_hints": show_hints,
            "show_undo": show_undo,
        }
        sid_to_room[sid] = room_id

        # Join socket.io room for broadcast events (timer, opponent updates)
        socketio.server.enter_room(sid, room_id, namespace='/')

        if single_player and use_timer:
            _start_timer(room_id)

        return jsonify({
            "roomId": room_id,
            "level": level_cfg,
            "instance": instance_dicts,
            "status": "playing" if single_player else "waiting",
            "timer": level_cfg["time"] if use_timer else 0,
        })

    @app.route("/api/join_room", methods=["POST"])
    def api_join_room():
        body = flask_request.get_json(force=True)
        sid = body.get("sid")
        room_id = body.get("roomId", "").strip().upper()
        player_name = body.get("playerName", "Player")

        room = rooms.get(room_id)
        if not room:
            return jsonify({"error": f"Room {room_id} not found."}), 400

        # Already in this room — return current state (idempotent)
        if sid in room["players"]:
            players_dict = {s: {"sid": s, "name": p["name"]} for s, p in room["players"].items()}
            return jsonify({
                "roomId": room_id,
                "level": room["level"],
                "instance": room["instance_dicts"],
                "status": room["status"],
                "timer": room["timer"],
                "players": players_dict,
            })

        if room["status"] != "waiting":
            return jsonify({"error": "Game already in progress."}), 400
        if len(room["players"]) >= 2:
            return jsonify({"error": "Room is full."}), 400

        room["players"][sid] = {"name": player_name, "game": room["game"], "moves": 0}
        sid_to_room[sid] = room_id

        # Join socket.io room for broadcast events
        socketio.server.enter_room(sid, room_id, namespace='/')

        # Auto-start when 2 players
        if len(room["players"]) >= 2:
            room["status"] = "playing"
            room["turn_order"] = list(room["players"].keys())  # host first
            room["current_turn_index"] = 0
            if room.get("use_timer", True):
                _start_timer(room_id)

        players_dict = {s: {"sid": s, "name": p["name"]} for s, p in room["players"].items()}
        turn_order = room.get("turn_order", [])
        current_turn = turn_order[room.get("current_turn_index", 0)] if turn_order else None
        return jsonify({
            "roomId": room_id,
            "level": room["level"],
            "instance": room["instance_dicts"],
            "status": room["status"],
            "timer": room["timer"],
            "players": players_dict,
            "currentTurn": current_turn,
            "showHints": room.get("show_hints", False),
            "showUndo": room.get("show_undo", False),
            "useTimer": room.get("use_timer", True),
        })

    @app.route("/api/room_state/<room_id>", methods=["GET"])
    def api_room_state(room_id):
        room = rooms.get(room_id)
        if not room:
            return jsonify({"error": "Room not found."}), 404
        players_dict = {s: {"sid": s, "name": p["name"]} for s, p in room["players"].items()}
        turn_order = room.get("turn_order", [])
        current_turn = turn_order[room.get("current_turn_index", 0)] if turn_order else None
        return jsonify({
            "roomId": room_id,
            "status": room["status"],
            "level": room["level"],
            "instance": room["instance_dicts"],
            "timer": room["timer"],
            "players": players_dict,
            "currentTurn": current_turn,
            "showHints": room.get("show_hints", False),
            "showUndo": room.get("show_undo", False),
            "useTimer": room.get("use_timer", True),
        })

    @app.route("/api/game_state/<room_id>", methods=["GET"])
    def api_game_state(room_id):
        room = rooms.get(room_id)
        if not room:
            return jsonify({"error": "Room not found."}), 404
        game = room["game"]
        result = _move_result(game, room.get("moves", 0))
        result["status"] = room["status"]
        result["timer"] = room["timer"]
        turn_order = room.get("turn_order", [])
        result["currentTurn"] = turn_order[room.get("current_turn_index", 0)] if turn_order else None
        winner_sid = room.get("winner")
        if winner_sid and winner_sid in room["players"]:
            result["winner"] = {"id": winner_sid, "name": room["players"][winner_sid]["name"]}
        else:
            result["winner"] = None
        return jsonify(result)

    @app.route("/api/place", methods=["POST"])
    def api_place():
        body = flask_request.get_json(force=True)
        room_id = body.get("roomId")
        sid = body.get("sid")
        domino_id = body.get("dominoId")

        room = rooms.get(room_id)
        if not room or sid not in room["players"]:
            return jsonify({"error": "Invalid room or player."}), 400
        if room["status"] != "playing":
            return jsonify({"error": "Game is not active."}), 400

        # Turn validation (skip for single player)
        turn_order = room.get("turn_order", [])
        if len(turn_order) > 1:
            current_turn = turn_order[room.get("current_turn_index", 0)]
            if sid != current_turn:
                return jsonify({"error": "Not your turn."}), 400

        game = room["game"]
        try:
            game.place_domino(domino_id)
        except (ValueError, RuntimeError) as e:
            return jsonify({"error": str(e)}), 400

        room["moves"] = room.get("moves", 0) + 1

        # Advance turn
        if len(turn_order) > 1:
            room["current_turn_index"] = (room.get("current_turn_index", 0) + 1) % len(turn_order)

        result = _move_result(game, room["moves"])
        result["currentTurn"] = turn_order[room.get("current_turn_index", 0)] if turn_order else None
        _emit_opponent_update(room_id, sid, game, room["moves"])

        if game.is_solved:
            room["status"] = "finished"
            room["winner"] = sid
            socketio.emit("match_found", {
                "roomId": room_id,
                "winnerId": sid,
                "winnerName": room["players"][sid]["name"],
                "sequence": [t.to_dict() for t in game.sequence],
            }, to=room_id)

        return jsonify(result)

    @app.route("/api/undo", methods=["POST"])
    def api_undo():
        body = flask_request.get_json(force=True)
        room_id = body.get("roomId")
        sid = body.get("sid")

        room = rooms.get(room_id)
        if not room or sid not in room["players"]:
            return jsonify({"error": "Invalid room or player."}), 400

        # Turn validation (skip for single player)
        turn_order = room.get("turn_order", [])
        if len(turn_order) > 1:
            current_turn = turn_order[room.get("current_turn_index", 0)]
            if sid != current_turn:
                return jsonify({"error": "Not your turn."}), 400

        game = room["game"]
        removed = game.undo()
        if removed is None:
            return jsonify({"error": "Nothing to undo."}), 400

        room["moves"] = room.get("moves", 0) + 1
        result = _move_result(game, room["moves"])
        result["currentTurn"] = turn_order[room.get("current_turn_index", 0)] if turn_order else None
        _emit_opponent_update(room_id, sid, game, room["moves"])
        return jsonify(result)

    @app.route("/api/reset", methods=["POST"])
    def api_reset():
        body = flask_request.get_json(force=True)
        room_id = body.get("roomId")
        sid = body.get("sid")

        room = rooms.get(room_id)
        if not room or sid not in room["players"]:
            return jsonify({"error": "Invalid room or player."}), 400
        if room["status"] != "playing":
            return jsonify({"error": "Game is not active."}), 400

        # Turn validation (skip for single player)
        turn_order = room.get("turn_order", [])
        if len(turn_order) > 1:
            current_turn = turn_order[room.get("current_turn_index", 0)]
            if sid != current_turn:
                return jsonify({"error": "Not your turn."}), 400

        game = room["game"]
        game.reset()
        room["moves"] = room.get("moves", 0) + 1
        result = _move_result(game, room["moves"])
        result["currentTurn"] = turn_order[room.get("current_turn_index", 0)] if turn_order else None
        _emit_opponent_update(room_id, sid, game, room["moves"])
        return jsonify(result)

    return app
