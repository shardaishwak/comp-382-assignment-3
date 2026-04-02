# COMP-382-Assignment-3


## Prerequisites

- Python 3.11
- Node.JS 21+: Preferred 22

## Game State Manager
The game state manager (`backend/app/game/pcp_game_state.py`) is the single
source of truth for all PCP game logic. It tracks the domino set, the player's
placed sequence, and computes `validNextIds`, `isDeadend`, and `prefixMatch`
after every move. It exposes a `snapshot()` method that the socket layer emits
directly to the frontend.

## Backend set-up

```bash
cd backend

python3 -m venv venv

source venv bin/activate # for macOS
venv\Scripts\activate.bat # for windows

pip install -r requirements.txt

python run.py # Project running on 5001
```

Server starts at http://localhost:5001

To check that it is working property: visit http://localhost:5001/health

## Frontend setup

```bash
cd www

npm install

npm run dev
```

The frontend will start at http://localhost:3000

## Frontend environment variables
```
NEXT_PUBLIC_SOCKET_URL=http://localhost:5001
```

You can copy the .env.example into a new .env file.

## Running both server and frontend

To run both frontend and server in parallel: open two terminals

```
# Terminal one
cd backend && source venv/bin/activate && python run.py

# Terminal two
cd www && npm run dev
```

Then open the http://localhost:3000 in the browser

NOTE: Replace `source venv/bin/activate` with `venv\Scripts\activate.bat` for windows.

## Tests

The `tests/test_socket_events.py` file validates that all backend socket event 
payloads match the expected frontend TypeScript types.

### Running the tests
```bash
cd backend
source venv/bin/activate  # macOS
venv\Scripts\activate.bat  # Windows
pytest tests/test_socket_events.py
```

### What's covered
- `create_room` → `room_created`: room ID, level shape, domino instance shape
- `join_room` → `player_joined`, `game_start`: player state, timer, full payload shape
- `place_domino` → `move_result`, `opponent_update`: sequence, strings, scoring
- `undo_move` → `move_result`, `opponent_update`: undo behaviour and empty sequence errors
- `request_hints` → `hint_update`: hint list and best hint shape
- `leave_room` / disconnect → `player_left`: broadcast payload
- Edge cases: invalid level, full room, case-insensitive room ID, default player name
