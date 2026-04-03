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

## Hint System

The hint system (`backend/app/game/hint_system.py`) provides intelligent move suggestions by simulating future game states using BFS (Breadth-First Search). It integrates with `PCPGameState` to analyze the current board and recommend optimal domino placements.

### How It Works

The system doesn't just guess — it **actually finds real solutions** behind the scenes:

1. **BFS Simulation** – From the current game state, it explores all possible domino placements up to a configurable depth.
2. **Solution Detection** – Only paths where top and bottom strings match as prefixes are followed; complete matches are recorded as solutions.
3. **Scoring Algorithm** – Each domino is evaluated based on:
   - Does it complete the match immediately? (Perfect match)
   - Does it appear in any BFS-discovered solution? (Exact prefix)
   - Does it create a good partial match? (Partial prefix)
   - Does it reduce the length gap between top and bottom? (Balancing)
   - Is it just exploratory when no solutions exist? (Exploratory)
  
### Video

https://github.com/user-attachments/assets/48dd18f9-6418-49e2-8e25-39ba3f55e14d

### Hint Types & Priorities

| Type | Priority | Score Range | Description |
|------|----------|-------------|-------------|
| `PERFECT_MATCH` | 5 | 100 | Completes the puzzle immediately |
| `EXACT_PREFIX` | 4 | 75-98 | Part of a known solution path |
| `PARTIAL_PREFIX` | 3 | 55-65 | Creates promising prefix match |
| `BALANCING` | 2 | 50-60 | Reduces the top/bottom length gap |
| `EXPLORATORY` | 1 | 0 | No solution found; suggests resetting |

### Key Functions

| Function | Description |
|----------|-------------|
| `find_all_solutions()` | BFS that simulates future placements and returns all solutions within depth limit |
| `score_with_bfs()` | Evaluates a single domino against BFS results; returns score, type, and explanation |
| `compute_hints()` | Main entry point — runs BFS, scores all dominoes, returns ranked hints + best hint |

### Integration with Frontend

When the frontend calls `request_hints`, the socket layer invokes `compute_hints()` on the current `PCPGameState`.

### Work Logs
- Brayden: https://www.youtube.com/watch?v=zTOOrhOVr9o
- Ryan:
- Sophie:
- Ishwak: https://youtu.be/ZSAzjW7-KGU
- Darius:
- Yahya:


### References:
- Socket.IO. (n.d.). *Flask-SocketIO Documentation*. https://flask-socketio.readthedocs.io/
- Next.js. (n.d.). *Next.js Documentation*. https://nextjs.org/docs
- Tailwind CSS. (n.d.). *Tailwind CSS Documentation*. https://tailwindcss.com/docs
- Sipser, M. (2013). *Introduction to the Theory of Computation* (3rd ed.). Cengage Learning. Section 5.2, A Simple Undecidable Problem, pp. 227–233.
- pytest. (n.d.). *pytest Documentation*. https://docs.pytest.org/
- MDN Web Docs. (n.d.). *AudioContext*. https://developer.mozilla.org/en-US/docs/Web/API/AudioContext
- Flask. (n.d.). *Flask Documentation*. https://flask.palletsprojects.com/
