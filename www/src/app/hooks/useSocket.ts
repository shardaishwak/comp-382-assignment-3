/**
 * Hook for managing socket connection and lifecycle
 * 
 * For example:
 * const { isConnected, roomState, gameState, ... } = useSocket()
 */

import { useEffect, useState, useCallback } from "react";
import { socket } from "../lib/socket";


export function useSocket() {
    const [isConnected, setConnected] = useState(false);

    useEffect(() => {
        socket.connect();
        socket.on("connect", () => setConnected(true));
        socket.on("disconnect", () => setConnected(false))
        // TODO: Add all socket events here based on the types.
    }, [])

    // All the methods such as creating a room, changing game etc.

    return { isConnected }; 
}