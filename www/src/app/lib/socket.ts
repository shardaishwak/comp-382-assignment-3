/**
 * Single shared socket instance for the entire app. 
 * Connects to Flask SocketIO instance.
 */

import { io, Socket } from "socket.io-client";
import { SOCKET_URL } from "./constants";

export const socket: Socket = io(SOCKET_URL as string, {
    autoConnect: true,
    transports: ["websocket"]
})