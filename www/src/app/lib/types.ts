/**
 * Useful types for the game
 */


export type Symbol = "R" | "G" | "B"

export interface Domino {
    id: number;
    top: Symbol[]
    bottom: Symbol[]
}

export interface PlacedDomino extends Domino {
    placementId: string;
    position: number;
}

export interface PlayerState {
    sid: string;
    name: string;
    sequence: PlacedDomino[]
    moves: number;
    score: number;
    hintsEnabled: number;
    connected: number;
}

export type LevelId = "easy" | "medium" | "hard";

export interface Level {
    id: LevelId;
    name: string;
    description: string;
    time: number;
    dominoes: number;
    stringLength: number;
    minSegment: number;
    maxSegment: number;
}

export interface RoomState {
    roomId: string;
    level: Level;
    instance: Domino[];
    players: Record<string, PlayerState>
    timer: number;
    status: "waiting" | "playing" | "finished"
    winner: string | null; // id of the user
}

export interface GameState {
    yourState: PlayerState;
    opponentState: PlayerState;
    instance: Domino[];
    timer: number;
    status: "waiting" | "playing" | "finished"
    validNextIds: number[] // hints of next dominos
    isDeadend: boolean;
    prefixMatch: number;
}

export interface CreateRoomPayload {
    playerName: string;
    level: LevelId;
}

export interface JoinRoomPayload {
    roomId: string;
    playerName: string;
}

export interface PlaceDominoPayload {
    roomId: string;
    dominoId: number;
}

export interface UndoMovePayload {
    roomId: string;
}

export interface ResetSequencePayload {
    roomId: string;
}

export interface RequestHintsPayload {
    roomId: string;
}

export interface LeaveRoomPayload {
    roomId: string;
}

/** Server → Client */
export interface RoomCreatedEvent {
    roomId: string;
    level: Level;
    instance: Domino[];
}

export interface PlayerJoinedEvent {
    roomId: string;
    playerName: string;
    playerId: string;
}

export interface GameStartEvent {
    roomId: string;
    level: Level;
    instance: Domino[];
    players: Record<string, PlayerState>;
    timer: number;
}

export interface MoveResultEvent {
    sequence: PlacedDomino[];
    topString: string;
    bottomString: string;
    validNextIds: number[];
    isDeadEnd: boolean;
    isSolved: boolean;
    prefixMatch: number;
    moves: number;
}

export interface OpponentUpdateEvent {
    opponentId: string;
    sequence: PlacedDomino[];
    moves: number;
    prefixMatch: number;
}

export interface HintData {
    dominoId: number;
    score: number;
    explanation: string;
}

export interface HintUpdateEvent {
    hints: HintData[];
    bestHint: HintData | null;
}

export interface TimerTickEvent {
    roomId: string;
    remaining: number;
}

export interface TimeUpEvent {
    roomId: string;
    winner: string | null;
}

export interface MatchFoundEvent {
    roomId: string;
    winnerId: string;
    winnerName: string;
    sequence: PlacedDomino[];
}

export interface PlayerLeftEvent {
    roomId: string;
    playerId: string;
    playerName: string;
}

export interface ErrorEvent {
    message: string;
}

export interface GameOptions {
    players: string
    difficulty: string
    multiplayer: string
    hints: boolean
    strict: boolean
    timer: boolean
    undo: boolean
}