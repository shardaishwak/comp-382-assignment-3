/**
 * Constants
 */

export const SOCKET_URL = process.env.NEXT_PUBLIC_SOCKET_URL || "http://localhost:5001"

export const OPTIONS = {
  players: [
    { id: "players-1", n: 1, text: "1p" },
    { id: "players-2", n: 2, text: "2p" }
  ],
  difficulty: [
    { id: "difficulty-1", n: 1, text: "easy" },
    { id: "difficulty-2", n: 2, text: "medium" },
    { id: "difficulty-3", n: 3, text: "hard" }
  ],
  multiplayer: [
    { id: "multiplayer-1", n: 2, text: "join" },
    { id: "multiplayer-2", n: 2, text: "host" }
  ],
  optional: [
    { id: "hints", n: 1, text: "hints" },
    { id: "timer", n: 1, text: "timer" }
  ]
}

export const EMPTY_OPTIONS = {
  players: "",
  difficulty: "",
  multiplayer: "",
  hints: false,
  timer: false
}
