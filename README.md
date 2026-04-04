# COMP-382-Assignment-3

## Project Board
https://github.com/users/shardaishwak/projects/3

## Production URL (hosted on AWS-EC2)
URL: http://3.87.106.173

## Contributors
- Brayden ([@Blake1332](https://github.com/Blake1332))
- Ryan ([@DarksteelCitadel](https://github.com/DarksteelCitadel))
- Sophie ([@catfetti](https://github.com/catfetti))
- Ishwak ([@shardaishwak](https://github.com/shardaishwak), [@phonkmonk](https://github.com/phonkmonk))
- Darius ([@Darius.Gillingham](https://github.com/Darius.Gillingham))
- Yahya ([@YahyaChebab](https://github.com/YahyaChebab))

## Prerequisites

- Python 3.11
- Node.JS 21+: Preferred 22

## Architecture

### System Overview
<img width="2033" height="2516" alt="mermaid-diagram-2026-04-03-145403" src="https://github.com/user-attachments/assets/8b184dab-ed3a-4c4d-b790-3fe8fa6b6307" />

### Game Flow (Single Player)
<img width="2762" height="2272" alt="mermaid-diagram-2026-04-03-145417" src="https://github.com/user-attachments/assets/fee9d765-3b7d-4aa0-97f5-7de4fef1871b" />

### Multiplayer Flow
<img width="2820" height="1856" alt="mermaid-diagram-2026-04-03-145425" src="https://github.com/user-attachments/assets/2b483758-9bbc-4451-87ca-bdb821f4f798" />


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

## Data Types

The shared TypeScript types used across the project are defined in `www/src/app/lib/types.ts`. These types served as a contract between the backend and frontend teams — since the backend would receive requests and send responses based on these interfaces, the frontend team could work independently using dummy data that matched the same shapes, keeping both teams in sync throughout development.

### Core Types

```typescript
type Symbol = "R" | "G" | "B"

interface Domino {
    id: number;
    top: Symbol[]
    bottom: Symbol[]
}

interface PlacedDomino extends Domino {
    placementId: string;
    position: number;
}

interface PlayerState {
    sid: string;
    name: string;
    sequence: PlacedDomino[]
    moves: number;
    score: number;
    hintsEnabled: number;
    connected: number;
}

type LevelId = "easy" | "medium" | "hard";

interface Level {
    id: LevelId;
    name: string;
    description: string;
    time: number;
    dominoes: number;
    stringLength: number;
    minSegment: number;
    maxSegment: number;
}
```

### Game State

```typescript
interface RoomState {
    roomId: string;
    level: Level;
    instance: Domino[];
    players: Record<string, PlayerState>
    timer: number;
    status: "waiting" | "playing" | "finished"
    winner: string | null;
}

interface GameState {
    yourState: PlayerState;
    opponentState: PlayerState;
    instance: Domino[];
    timer: number;
    status: "waiting" | "playing" | "finished"
    validNextIds: number[]
    isDeadend: boolean;
    prefixMatch: number;
}
```

### Client → Server Payloads

```typescript
interface CreateRoomPayload { playerName: string; level: LevelId; }
interface JoinRoomPayload { roomId: string; playerName: string; }
interface PlaceDominoPayload { roomId: string; dominoId: number; }
interface UndoMovePayload { roomId: string; }
interface ResetSequencePayload { roomId: string; }
interface RequestHintsPayload { roomId: string; }
interface LeaveRoomPayload { roomId: string; }
```

### Server → Client Events

```typescript
interface RoomCreatedEvent { roomId: string; level: Level; instance: Domino[]; }
interface PlayerJoinedEvent { roomId: string; playerName: string; playerId: string; }
interface GameStartEvent { roomId: string; level: Level; instance: Domino[]; players: Record<string, PlayerState>; timer: number; }
interface MoveResultEvent { sequence: PlacedDomino[]; topString: string; bottomString: string; validNextIds: number[]; isDeadEnd: boolean; isSolved: boolean; prefixMatch: number; moves: number; }
interface OpponentUpdateEvent { opponentId: string; sequence: PlacedDomino[]; moves: number; prefixMatch: number; }
interface HintData { dominoId: number; score: number; explanation: string; }
interface HintUpdateEvent { hints: HintData[]; bestHint: HintData | null; }
interface TimerTickEvent { roomId: string; remaining: number; }
interface TimeUpEvent { roomId: string; winner: string | null; }
interface MatchFoundEvent { roomId: string; winnerId: string; winnerName: string; sequence: PlacedDomino[]; }
interface PlayerLeftEvent { roomId: string; playerId: string; playerName: string; }
interface ErrorEvent { message: string; }
```

### Game Options

```typescript
interface GameOptions {
    players: string;
    difficulty: string;
    multiplayer: string;
    hints: boolean;
    strict: boolean;
    timer: boolean;
    undo: boolean;
}
```
## Structured Domino Generation
first takes in the info for the range for the lengths of strings allowed for the dominoes, how many dominoes, 

then it generates a string of roughly the length of Number of dominoes × average string length per top/bottom of dominoe

then it generates 2 arrays both of a length = to the number of dominoes

then each array is populated with random integers inside the range of allowed string lengths on top and bottom

then each array assigns dominoe top and bottom based on reading from the central string. example 

min = 1
max = 3
N = 3

String
RGBRGB

array 1
1, 3, 2

array 2
2, 3, 1

dominoes
R
----
RG

next

GBR
----
BRG

next

GB
---
B
## AI Usage

AI tools (primarily Claude and GitHub Copilot) were used sparingly and exclusively for debugging. Specifically in situations where a bug was taking too long to identify manually. AI was used to **locate** the issue, not to write the fix; all patches were applied through manual intervention.

### Notable cases

1. **AWS CORS issue** — When integrating the backend on AWS, requests from the frontend were being blocked by CORS. After several failed deployment attempts, AI was used to spot that the issue was a missing environment variable in the AWS configuration.

2. **Domino generation bug** — During testing, a specific configuration (a string of length 16 split across 8 dominoes) was producing domino sets that could be solved in a single move. The root cause was subtle and difficult to trace manually. After multiple attempts, AI was used to identify the faulty generation logic.

### References:
- Socket.IO. (n.d.). *Flask-SocketIO Documentation*. https://flask-socketio.readthedocs.io/
- Next.js. (n.d.). *Next.js Documentation*. https://nextjs.org/docs
- Tailwind CSS. (n.d.). *Tailwind CSS Documentation*. https://tailwindcss.com/docs
- Sipser, M. (2013). *Introduction to the Theory of Computation* (3rd ed.). Cengage Learning. Section 5.2, A Simple Undecidable Problem, pp. 227–233.
- pytest. (n.d.). *pytest Documentation*. https://docs.pytest.org/
- MDN Web Docs. (n.d.). *AudioContext*. https://developer.mozilla.org/en-US/docs/Web/API/AudioContext
- Flask. (n.d.). *Flask Documentation*. https://flask.palletsprojects.com/
- Pygame. (n.d.). Pygame Documentation. https://www.pygame.org/docs/

### Work Logs
- Brayden: https://www.youtube.com/watch?v=zTOOrhOVr9o
- Ryan: https://youtu.be/I31j0GDk6SU
- Sophie: https://youtu.be/XyjNzgxFIQk
- Ishwak: https://youtu.be/ZSAzjW7-KGU
- Darius: https://youtu.be/cNbrRsC3N1k
- Yahya: https://youtu.be/CUtnmnYXpic
