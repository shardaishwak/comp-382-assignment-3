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

export interface Level {
    id: number;
    name: number;
    description: number;
    time: number
    // TODO: Any other parameter based on the game generation
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