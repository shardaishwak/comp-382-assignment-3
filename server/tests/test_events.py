"""
Tests for socket events - validates backend payloads match frontend Typescript types.

"""

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

