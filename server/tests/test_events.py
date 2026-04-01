"""
Tests for socket events - validates backend payloads match frontend Typescript types.

"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app import create_app, socketio
from app.sockets import events as ev 

@pytest.fixture(autouse=True)
def clean_rooms():
    ev.rooms.clear()
    ev.sid_to_room.clear()
    yield
    ev.rooms.clear()
    ev.sid_to_room.clear()

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    c1 = socketio.test_client(app)
    c2 = socketio.test_client(app)
    assert c1.is_connected()
    assert c2.is_connected()
    yield c1, c2
    c1.disconnect()
    c2.disconnect()

@pytest.fixture
def single_client(app):
    c = socketio.test_client(app)
    assert c.is_connected()
    yield c
    c.disconnect()

### HELPERS ###

def get_event(client,event_name):
    for message in client.get_received():
        if message['name'] == event_name:
            return message['args'][0]
    return None

def flush(client):
    client.get_received()




class TestCreateRoom:
    def test_room_created_payload_shape(self, single_client):
        single_client.emit('create_room', {"Playername": "Alice", "level": "easy"})
        data = get_event(single_client, 'room_created')
        assert data is not None, "room_created event not received"

        assert 'room_id' in data
        assert "level" in data
        assert "instance" in data

        assert isinstance(data['roomId'], str)
        assert len(data["roomId"]) == 6 # this is the uuid length

    def test_level_shape(self, single_client):
        single_client.emit('create_room', {"Playername": "Alice", "level": "medium"})
        data = get_event(single_client, 'room_created')
        assert data is not None, "room_created event not received"
        level = data["level"]

        for key in ("id", "name", "description", "time", "dominoes", "stringLength", "minSegments", "maxSegments"):
            assert key in level, f"Level missing key: {key}"

        assert level["id"] == "medium"
        assert isinstance(level["time"], str)
        assert isinstance(level["dominoes"], list)

    def test_instance_domino_shape(self, single_client):
        single_client.emit('create_room', {"Playername": "Alice", "level": "easy"})
        data = get_event(single_client, 'room_created')
        assert data is not None, "room_created event not received"
        instance = data["instance"]

        assert isinstance(instance, list)
        assert len(instance) == 4 # easy level has 4 dominoes

        for d in instance:
            assert "id" in d
            assert "top" in d
            assert "bottom" in d
            assert isinstance(d["id"], int)
            assert isinstance(d["top"], list)
            assert isinstance(d["bottom"], list)
            # Symbols must be R, G, B

            for symbol in d["top"] + d["bottom"]:
                assert symbol in ("R", "G", "B"), f"Invalid symbol: {symbol}"

    def test_all_levels(self, app):
        expected = {"easy": 4, "medium": 6, "hard": 8}
        for level_id, count in expected.items():
            ev.rooms.clear()
            ev.sid_to_room.clear()
            c = socketio
            c.emit('create_room', {"playerName": "Alice", "level": level_id})
            data = get_event(c, 'room_created')
            assert data is not None, f"room_created event not received for level {level_id}"
            assert len(data["instance"]) == count, f"{level_id}: expected {count} dominoes, got {len(data['instance'])}"
            c.disconnect()
    
    def test_invalid_level(self, single_client):
        single_client.emit('create_room', {"playerName": "Alice", "level": "nightmare"})
        error = get_event(single_client, "error")
        assert error is not None, "Error event not received for invalid level"
        assert isinstance(error["message"], str)

class TestJoinRoom:
    def test_player_joined_payload(self, clients):
        c1, c2 = clients
        c1.emit("create_room", {"playerName": "Alice", "level": "easy"})
        room = get_event(c1, "room_created")
        assert room is not None
        room_id = room["roomId"]

        flush(c1)
        c2.emit("join_room", {"roomId": room_id, "playerName": "Bob"})

        # Check c1 receives player_joined (broadcast)
        joined = get_event(c1, "player_joined")
        assert joined is not None, "player_joined not received by host"
        assert joined["roomId"] == room_id
        assert joined["playerName"] == "Bob"
        assert "playerId" in joined
        assert isinstance(joined["playerId"], str)

    def test_game_start_payload(self, clients):
        c1, c2 = clients
        c1.emit("create_room", {"playerName": "Alice", "level": "easy"})
        room = get_event(c1, "room_created")
        assert room is not None
        room_id = room["roomId"]

        flush(c1)
        c2.emit("join_room", {"roomId": room_id, "playerName": "Bob"})

        # Both clients should receive game_start
        start1 = get_event(c1, "game_start")
        start2 = get_event(c2, "game_start")

        for label, start in [("c1", start1), ("c2", start2)]:
            assert start is not None, f"game_start not received by {label}"
            assert start["roomId"] == room_id
            assert "level" in start
            assert "instance" in start
            assert "players" in start
            assert "timer" in start
            assert isinstance(start["timer"], int)
            assert start["timer"] == 300  # easy = 300s

    def test_player_state_in_game_start(self, clients):
        c1, c2 = clients
        c1.emit("create_room", {"playerName": "Alice", "level": "easy"})
        room = get_event(c1, "room_created")
        assert room is not None

        flush(c1)
        c2.emit("join_room", {"roomId": room["roomId"], "playerName": "Bob"})
        start = get_event(c1, "game_start")
        assert start is not None

        players = start["players"]
        assert len(players) == 2

        for sid, p in players.items():
            for key in ("sid", "name", "sequence", "moves", "score", "hintsEnabled", "connected"):
                assert key in p, f"PlayerState missing key: {key}"
            assert isinstance(p["sequence"], list)
            assert p["moves"] == 0
            assert isinstance(p["score"], (int, float))

        names = {p["name"] for p in players.values()}
        assert names == {"Alice", "Bob"}

    def test_join_nonexistent_room(self, single_client):
        single_client.emit("join_room", {"roomId": "ZZZZZZ", "playerName": "Bob"})
        err = get_event(single_client, "error")
        assert err is not None, "error event not received"
        assert "message" in err

    def test_join_full_room(self, app):
        c1 = socketio.test_client(app)
        c2 = socketio.test_client(app)
        c3 = socketio.test_client(app)

        c1.emit("create_room", {"playerName": "Alice", "level": "easy"})
        room = get_event(c1, "room_created")
        assert room is not None
        room_id = room["roomId"]

        c2.emit("join_room", {"roomId": room_id, "playerName": "Bob"})
        flush(c2)

        c3.emit("join_room", {"roomId": room_id, "playerName": "Charlie"})
        err = get_event(c3, "error")
        assert err is not None, "error event not received for full room"
        assert "message" in err

        c1.disconnect()
        c2.disconnect()
        c3.disconnect()

class TestPlaceDomino:
    def _start_game(self, c1, c2):
        c1.emit("create_room", {"playerName": "Alice", "level": "easy"})
        room = get_event(c1, "room_created")
        assert room is not None
        room_id = room["roomId"]
        instance = room["instance"]
        flush(c1)
        c2.emit("join_room", {"roomId": room_id, "playerName": "Bob"})
        # Flush game_start + player_joined events
        flush(c1)
        flush(c2)
        return room_id, instance

    def test_move_result_payload(self, clients):
        c1, c2 = clients
        room_id, instance = self._start_game(c1, c2)

        c1.emit("place_domino", {"roomId": room_id, "dominoId": 0})
        result = get_event(c1, "move_result")
        assert result is not None, "move_result not received"

        for key in ("sequence", "topString", "bottomString", "validNextIds", "isDeadEnd", "isSolved", "prefixMatch", "moves"):
            assert key in result, f"MoveResultEvent missing key: {key}"

        assert isinstance(result["sequence"], list)
        assert len(result["sequence"]) == 1
        assert isinstance(result["topString"], str)
        assert isinstance(result["bottomString"], str)
        assert isinstance(result["validNextIds"], list)
        assert isinstance(result["isDeadEnd"], bool)
        assert isinstance(result["isSolved"], bool)
        assert isinstance(result["prefixMatch"], int)
        assert result["moves"] == 1

    def test_placed_domino_shape(self, clients):
        c1, c2 = clients
        room_id, instance = self._start_game(c1, c2)

        c1.emit("place_domino", {"roomId": room_id, "dominoId": 0})
        result = get_event(c1, "move_result")
        assert result is not None
        placed = result["sequence"][0]

        for key in ("id", "top", "bottom", "placementId", "position"):
            assert key in placed, f"PlacedDomino missing key: {key}"

        assert placed["id"] == 0
        assert isinstance(placed["placementId"], str)
        assert placed["position"] == 0

    def test_opponent_update_payload(self, clients):
        c1, c2 = clients
        room_id, instance = self._start_game(c1, c2)

        c1.emit("place_domino", {"roomId": room_id, "dominoId": 0})
        opp = get_event(c2, "opponent_update")
        assert opp is not None, "opponent_update not received"

        for key in ("opponentId", "sequence", "moves", "prefixMatch"):
            assert key in opp, f"OpponentUpdateEvent missing key: {key}"

        assert isinstance(opp["opponentId"], str)
        assert isinstance(opp["sequence"], list)
        assert opp["moves"] == 1
        assert isinstance(opp["prefixMatch"], int)

    def test_multiple_moves_increment(self, clients):
        c1, c2 = clients
        room_id, instance = self._start_game(c1, c2)

        for i in range(3):
            flush(c1)
            c1.emit("place_domino", {"roomId": room_id, "dominoId": 0})
            result = get_event(c1, "move_result")
            assert result is not None, f"move_result not received on move {i+1}"
            assert result["moves"] == i + 1

    def test_valid_next_ids_are_ints(self, clients):
        c1, c2 = clients
        room_id, instance = self._start_game(c1, c2)

        c1.emit("place_domino", {"roomId": room_id, "dominoId": 0})
        result = get_event(c1, "move_result")
        assert result is not None
        for vid in result["validNextIds"]:
            assert isinstance(vid, int)

    def test_place_in_inactive_game(self, single_client):
        single_client.emit("create_room", {"playerName": "Alice", "level": "easy"})
        room = get_event(single_client, "room_created")
        assert room is not None
        flush(single_client)

        single_client.emit("place_domino", {"roomId": room["roomId"], "dominoId": 0})
        err = get_event(single_client, "error")
        assert err is not None, "error event not received"
        assert "message" in err



class TestUndoMove:
    def _start_and_place(self, c1, c2):
        c1.emit("create_room", {"playerName": "Alice", "level": "easy"})
        room = get_event(c1, "room_created")
        assert room is not None
        room_id = room["roomId"]
        flush(c1)
        c2.emit("join_room", {"roomId": room_id, "playerName": "Bob"})
        flush(c1)
        flush(c2)
        c1.emit("place_domino", {"roomId": room_id, "dominoId": 0})
        flush(c1)
        flush(c2)
        return room_id

    def test_undo_returns_move_result(self, clients):
        c1, c2 = clients
        room_id = self._start_and_place(c1, c2)

        c1.emit("undo_move", {"roomId": room_id})
        result = get_event(c1, "move_result")
        assert result is not None, "move_result not received after undo"
        assert result["sequence"] == []
        assert result["topString"] == ""
        assert result["bottomString"] == ""
        assert result["moves"] == 2  # place + undo

    def test_undo_sends_opponent_update(self, clients):
        c1, c2 = clients
        room_id = self._start_and_place(c1, c2)

        c1.emit("undo_move", {"roomId": room_id})
        opp = get_event(c2, "opponent_update")
        assert opp is not None, "opponent_update not received after undo"
        assert opp["sequence"] == []

    def test_undo_empty_sequence(self, clients):
        c1, c2 = clients
        c1.emit("create_room", {"playerName": "Alice", "level": "easy"})
        room = get_event(c1, "room_created")
        assert room is not None
        room_id = room["roomId"]
        flush(c1)
        c2.emit("join_room", {"roomId": room_id, "playerName": "Bob"})
        flush(c1)
        flush(c2)

        c1.emit("undo_move", {"roomId": room_id})
        err = get_event(c1, "error")
        assert err is not None, "error event not received for empty undo"
        assert "message" in err

class TestRequestHints:
    def test_hint_update_payload(self,clients):
        c1,c2 = clients
        c1.emit("create_room", {"playerName": "Alice", "level": "easy"})
        room = get_event(c1, "room_created")
        assert room is not None
        room_id = room["roomId"]
        flush(c1)
        c2.emit("join_room", {"roomId": room_id, "playerName": "Bob"})
        flush(c1)
        flush(c2)

        c1.emit("request_hints", {"roomId": room_id})
        hints = get_event(c1, "hint_update")
        assert hints is not None, "hint_update not received"

        assert "hints" in hints
        assert "bestHint" in hints
        assert isinstance(hints["hints"], list)

    def test_hint_data_shape(self,clients):
        c1,c2=clients
        c1.emit("create_room", {"playerName": "Alice", "level": "easy"})
        room = get_event(c1, "room_created")
        assert room is not None
        room_id = room["roomId"]
        flush(c1)
        c2.emit("join_room", {"roomId": room_id, "playerName": "Bob"})
        flush(c1)
        flush(c2)

        c1.emit("request_hints", {"roomId": room_id})
        hints = get_event(c1, "hint_update")
        assert hints is not None

        for h in hints["hints"]:
            assert "dominoId" in h
            assert "score" in h
            assert "explanation" in h
            assert isinstance(h["dominoId"], int)
            assert isinstance(h["score"], (int, float))
            assert isinstance(h["explanation"], str)

        if hints["bestHint"] is not None:
            bh = hints["bestHint"]
            assert "dominoId" in bh
            assert "score" in bh
            assert "explanation" in bh

class TestDisconnect:
    def test_disconnect_broadcasts_player_left(self, app):
        c1 = socketio.test_client(app)
        c2 = socketio.test_client(app)

        c1.emit("create_room", {"playerName": "Alice", "level": "easy"})
        room = get_event(c1, "room_created")
        assert room is not None
        room_id = room["roomId"]
        flush(c1)

        c2.emit("join_room", {"roomId": room_id, "playerName": "Bob"})
        flush(c1)
        flush(c2)

        c2.disconnect()
        left = get_event(c1, "player_left")
        assert left is not None, "player_left not received on disconnect"
        assert left["playerName"] == "Bob"
        assert left["roomId"] == room_id
        

        c1.disconnect()

class TestScoringCompatibility:
    def test_prefix_match_is_raw_count(self, clients):
        c1, c2 = clients
        c1.emit("create_room", {"playerName": "Alice", "level": "easy"})
        room = get_event(c1, "room_created")
        assert room is not None
        room_id = room["roomId"]
        flush(c1)
        c2.emit("join_room", {"roomId": room_id, "playerName": "Bob"})
        flush(c1)
        flush(c2)

        c1.emit("place_domino", {"roomId": room_id, "dominoId": 0})
        result = get_event(c1, "move_result")
        assert result is not None
        # prefixMatch must be an integer >= 0 (raw char count)
        assert isinstance(result["prefixMatch"], int)
        assert result["prefixMatch"] >= 0

    def test_top_bottom_strings_are_strings(self, clients):
        c1, c2 = clients
        c1.emit("create_room", {"playerName": "Alice", "level": "easy"})
        room = get_event(c1, "room_created")
        assert room is not None
        room_id = room["roomId"]
        instance = room["instance"]
        flush(c1)
        c2.emit("join_room", {"roomId": room_id, "playerName": "Bob"})
        flush(c1)
        flush(c2)

        c1.emit("place_domino", {"roomId": room_id, "dominoId": 0})
        result = get_event(c1, "move_result")
        assert result is not None

        # Strings should match the domino's top/bottom concatenated
        d0 = instance[0]
        assert result["topString"] == "".join(d0["top"])
        assert result["bottomString"] == "".join(d0["bottom"])

class TestFullGameFlow:
    def test_create_join_play_flow(self, clients):
        c1, c2 = clients

        # 1. Create room
        c1.emit("create_room", {"playerName": "Alice", "level": "easy"})
        created = get_event(c1, "room_created")
        assert created is not None
        room_id = created["roomId"]
        flush(c1)

        # 2. Join room
        c2.emit("join_room", {"roomId": room_id, "playerName": "Bob"})

        # 3. Both get game_start
        start1 = get_event(c1, "game_start")
        start2 = get_event(c2, "game_start")
        assert start1 is not None, "game_start not received by c1"
        assert start2 is not None, "game_start not received by c2"
        flush(c1)
        flush(c2)

        # 4. Player 1 places domino
        c1.emit("place_domino", {"roomId": room_id, "dominoId": 0})
        move1 = get_event(c1, "move_result")
        assert move1 is not None
        assert move1["moves"] == 1

        # Player 2 sees opponent update
        opp1 = get_event(c2, "opponent_update")
        assert opp1 is not None
        flush(c1)
        flush(c2)

        # 5. Player 2 also places a domino
        c2.emit("place_domino", {"roomId": room_id, "dominoId": 1})
        move2 = get_event(c2, "move_result")
        assert move2 is not None
        assert move2["moves"] == 1  # Bob's first move

        opp2 = get_event(c1, "opponent_update")
        assert opp2 is not None

    def test_independent_player_sequences(self, clients):
        c1, c2 = clients
        c1.emit("create_room", {"playerName": "Alice", "level": "easy"})
        room = get_event(c1, "room_created")
        assert room is not None
        room_id = room["roomId"]
        flush(c1)
        c2.emit("join_room", {"roomId": room_id, "playerName": "Bob"})
        flush(c1)
        flush(c2)

        # Player 1 places domino 0
        c1.emit("place_domino", {"roomId": room_id, "dominoId": 0})
        r1 = get_event(c1, "move_result")
        assert r1 is not None
        flush(c1)
        flush(c2)

        # Player 2 places domino 1
        c2.emit("place_domino", {"roomId": room_id, "dominoId": 1})
        r2 = get_event(c2, "move_result")
        assert r2 is not None

        # Sequences should be different
        assert r1["sequence"][0]["id"] == 0
        assert r2["sequence"][0]["id"] == 1

class TestEdgeCases:
    def test_create_room_default_player_name(self, single_client):
        single_client.emit("create_room", {"level": "easy"})
        room = get_event(single_client, "room_created")
        assert room is not None

    def test_join_room_case_insensitive(self, clients):
        c1, c2 = clients
        c1.emit("create_room", {"playerName": "Alice", "level": "easy"})
        room = get_event(c1, "room_created")
        assert room is not None
        room_id = room["roomId"]
        flush(c1)

        c2.emit("join_room", {"roomId": room_id.lower(), "playerName": "Bob"})
        joined = get_event(c1, "player_joined")
        assert joined is not None, "player_joined not received after lowecase room ID join"

    def test_domino_ids_are_sequential(self, single_client):
        single_client.emit("create_room", {"playerName": "Alice", "level": "medium"})
        room = get_event(single_client, "room_created")
        assert room is not None
        
        ids= [d["id"] for d in room["instance"]]

        assert ids == list(range(len(ids)))
