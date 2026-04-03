"use client"

import { useEffect, useState, useCallback, useRef } from "react"
import { socket } from "../lib/socket"
import { SOCKET_URL } from "../lib/constants"
import type {
  Domino,
  LevelId,
  Level,
  PlacedDomino,
  HintData,
} from "../lib/types"

export function useGameSocket() {
  const [isConnected, setConnected] = useState(socket.connected)
  const [roomId, setRoomId] = useState<string | null>(null)
  const [status, setStatus] = useState<"idle" | "waiting" | "playing" | "finished">("idle")
  const [level, setLevel] = useState<Level | null>(null)
  const [instance, setInstance] = useState<Domino[]>([])
  const [sequence, setSequence] = useState<PlacedDomino[]>([])
  const [validNextIds, setValidNextIds] = useState<number[]>([])
  const [isDeadEnd, setIsDeadEnd] = useState(false)
  const [isSolved, setIsSolved] = useState(false)
  const [prefixMatch, setPrefixMatch] = useState(0)
  const [moves, setMoves] = useState(0)
  const [timer, setTimer] = useState(0)
  const [topString, setTopString] = useState("")
  const [bottomString, setBottomString] = useState("")
  const [winner, setWinner] = useState<{ id: string; name: string } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [hints, setHints] = useState<HintData[]>([])
  const [bestHint, setBestHint] = useState<HintData | null>(null)
  const [opponentName, setOpponentName] = useState("")
  const [opponentMoves, setOpponentMoves] = useState(0)
  const [opponentPrefixMatch, setOpponentPrefixMatch] = useState(0)
  const [currentTurn, setCurrentTurn] = useState<string | null>(null)
  const [gameOptions, setGameOptions] = useState<{ showHints: boolean; showUndo: boolean; useTimer: boolean }>({ showHints: false, showUndo: false, useTimer: true })

  const roomIdRef = useRef<string | null>(null)

  // Shared updater for move results (used by both event listener and emit callbacks)
  const applyMoveResult = useCallback((data: {
    sequence: PlacedDomino[]
    topString: string
    bottomString: string
    validNextIds: number[]
    isDeadEnd: boolean
    isSolved: boolean
    prefixMatch: number
    moves: number
  }) => {
    console.log("[applyMoveResult]", { seqLen: data.sequence.length, validNext: data.validNextIds, moves: data.moves })
    setSequence(data.sequence)
    setTopString(data.topString)
    setBottomString(data.bottomString)
    setValidNextIds(data.validNextIds)
    setIsDeadEnd(data.isDeadEnd)
    setIsSolved(data.isSolved)
    setPrefixMatch(data.prefixMatch)
    setMoves(data.moves)
  }, [])

  useEffect(() => {
    function onConnect() {
      setConnected(true)
    }
    function onDisconnect() {
      setConnected(false)
    }

    function onRoomCreated(data: { roomId: string; level: Level; instance: Domino[] }) {
      setRoomId(data.roomId)
      roomIdRef.current = data.roomId
      setLevel(data.level)
      setInstance(data.instance)
      setStatus("waiting")
      setValidNextIds(data.instance.map((d) => d.id))
    }

    function onPlayerJoined(data: { roomId: string; playerName: string; playerId: string }) {
      if (data.playerId !== socket.id) {
        setOpponentName(data.playerName)
      }
    }

    function onGameStart(data: {
      roomId: string
      level: Level
      instance: Domino[]
      players: Record<string, { sid: string; name: string }>
      timer: number
    }) {
      setRoomId(data.roomId)
      roomIdRef.current = data.roomId
      setStatus("playing")
      setInstance(data.instance)
      setLevel(data.level)
      setTimer(data.timer)
      setValidNextIds(data.instance.map((d) => d.id))

      // Extract opponent name from players dict
      const myId = socket.id
      for (const [sid, player] of Object.entries(data.players)) {
        if (sid !== myId) {
          setOpponentName(player.name)
          break
        }
      }
    }

    function onMoveResult(data: {
      sequence: PlacedDomino[]
      topString: string
      bottomString: string
      validNextIds: number[]
      isDeadEnd: boolean
      isSolved: boolean
      prefixMatch: number
      moves: number
    }) {
      applyMoveResult(data)
    }

    function onOpponentUpdate(data: {
      opponentId: string
      sequence: PlacedDomino[]
      moves: number
      prefixMatch: number
    }) {
      setOpponentMoves(data.moves)
      setOpponentPrefixMatch(data.prefixMatch)
    }

    function onTimerTick(data: { roomId: string; remaining: number }) {
      setTimer(data.remaining)
    }

    function onTimeUp(data: { roomId: string; winner: string | null }) {
      setStatus("finished")
      setWinner(
        data.winner
          ? { id: data.winner, name: data.winner === socket.id ? "You" : "Opponent" }
          : null
      )
    }

    function onMatchFound(data: {
      roomId: string
      winnerId: string
      winnerName: string
      sequence: PlacedDomino[]
    }) {
      setStatus("finished")
      setIsSolved(true)
      setWinner({
        id: data.winnerId,
        name: data.winnerId === socket.id ? "You" : data.winnerName,
      })
    }

    function onHintUpdate(data: { hints: HintData[]; bestHint: HintData | null }) {
      setHints(data.hints)
      setBestHint(data.bestHint)
    }

    function onError(data: { message: string }) {
      console.error("[socket error]", data.message)
      setError(data.message)
    }

    function onPlayerLeft(_data: { roomId: string; playerId: string; playerName: string }) {
      setOpponentName("")
    }

    socket.on("connect", onConnect)
    socket.on("disconnect", onDisconnect)
    socket.on("room_created", onRoomCreated)
    socket.on("player_joined", onPlayerJoined)
    socket.on("game_start", onGameStart)
    socket.on("move_result", onMoveResult)
    socket.on("opponent_update", onOpponentUpdate)
    socket.on("timer_tick", onTimerTick)
    socket.on("time_up", onTimeUp)
    socket.on("match_found", onMatchFound)
    socket.on("hint_update", onHintUpdate)
    socket.on("error", onError)
    socket.on("player_left", onPlayerLeft)

    return () => {
      socket.off("connect", onConnect)
      socket.off("disconnect", onDisconnect)
      socket.off("room_created", onRoomCreated)
      socket.off("player_joined", onPlayerJoined)
      socket.off("game_start", onGameStart)
      socket.off("move_result", onMoveResult)
      socket.off("opponent_update", onOpponentUpdate)
      socket.off("timer_tick", onTimerTick)
      socket.off("time_up", onTimeUp)
      socket.off("match_found", onMatchFound)
      socket.off("hint_update", onHintUpdate)
      socket.off("error", onError)
      socket.off("player_left", onPlayerLeft)
    }
  }, [])

  // Poll room state when waiting for opponent (host flow)
  useEffect(() => {
    if (status !== "waiting" || !roomIdRef.current) return
    const interval = setInterval(() => {
      fetch(`${SOCKET_URL}/api/room_state/${roomIdRef.current}`)
        .then((r) => r.json())
        .then((result) => {
          if (result.status === "playing") {
            setStatus("playing")
            setInstance(result.instance)
            setLevel(result.level)
            setTimer(result.timer)
            setValidNextIds(result.instance.map((d: Domino) => d.id))
            if (result.currentTurn) setCurrentTurn(result.currentTurn)
            const myId = socket.id
            for (const [sid, player] of Object.entries(result.players as Record<string, { sid: string; name: string }>)) {
              if (sid !== myId) {
                setOpponentName(player.name)
                break
              }
            }
          }
        })
        .catch(() => {})
    }, 1000)
    return () => clearInterval(interval)
  }, [status])

  // Poll shared game state to sync both players' UIs + timer
  useEffect(() => {
    if (status !== "playing" || !roomIdRef.current) return
    const interval = setInterval(() => {
      fetch(`${SOCKET_URL}/api/game_state/${roomIdRef.current}`)
        .then((r) => r.json())
        .then((result) => {
          if (result.error) return
          applyMoveResult(result)
          if (result.timer !== undefined) setTimer(result.timer)
          if (result.currentTurn) setCurrentTurn(result.currentTurn)
          if (result.status === "finished" || result.isSolved) {
            setStatus("finished")
            if (result.winner) {
              setWinner({
                id: result.winner.id,
                name: result.winner.id === socket.id ? "You" : result.winner.name,
              })
            }
          }
        })
        .catch(() => {})
    }, 500)
    return () => clearInterval(interval)
  }, [status, applyMoveResult])

  const createRoom = useCallback((playerName: string, levelId: LevelId, singlePlayer = false, useTimer = true, showHints = false, showUndo = false) => {
    setGameOptions({ showHints, showUndo, useTimer })
    fetch(`${SOCKET_URL}/api/create_room`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sid: socket.id, playerName, level: levelId, singlePlayer, useTimer, showHints, showUndo }),
    })
      .then((r) => r.json())
      .then((result) => {
        if (result.error) { setError(result.error); return }
        setRoomId(result.roomId)
        roomIdRef.current = result.roomId
        setLevel(result.level)
        setInstance(result.instance)
        setTimer(result.timer)
        setValidNextIds(result.instance.map((d: Domino) => d.id))
        setStatus(result.status === "playing" ? "playing" : "waiting")
      })
      .catch((e) => console.error("[createRoom] fetch error", e))
  }, [])

  const joinRoom = useCallback((joinRoomId: string, playerName: string) => {
    fetch(`${SOCKET_URL}/api/join_room`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sid: socket.id, roomId: joinRoomId, playerName }),
    })
      .then((r) => r.json())
      .then((result) => {
        if (result.error) { setError(result.error); return }
        setRoomId(result.roomId)
        roomIdRef.current = result.roomId
        setLevel(result.level)
        setInstance(result.instance)
        setTimer(result.timer)
        setValidNextIds(result.instance.map((d: Domino) => d.id))
        setStatus(result.status === "playing" ? "playing" : "waiting")
        if (result.currentTurn) setCurrentTurn(result.currentTurn)
        setGameOptions({
          showHints: result.showHints ?? false,
          showUndo: result.showUndo ?? false,
          useTimer: result.useTimer ?? true,
        })
        const myId = socket.id
        for (const [sid, player] of Object.entries(result.players as Record<string, { sid: string; name: string }>)) {
          if (sid !== myId) {
            setOpponentName(player.name)
            break
          }
        }
      })
      .catch((e) => console.error("[joinRoom] fetch error", e))
  }, [])

  const placeDomino = useCallback((dominoId: number) => {
    if (!roomIdRef.current) return
    fetch(`${SOCKET_URL}/api/place`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ roomId: roomIdRef.current, sid: socket.id, dominoId }),
    })
      .then((r) => r.json())
      .then((result) => {
        if (result.error) setError(result.error)
        else {
          applyMoveResult(result)
          if (result.currentTurn) setCurrentTurn(result.currentTurn)
          if (result.isSolved) {
            setStatus("finished")
            setWinner({ id: socket.id ?? "", name: "You" })
          }
        }
      })
      .catch((e) => console.error("[placeDomino] fetch error", e))
  }, [applyMoveResult])

  const undoMove = useCallback(() => {
    if (!roomIdRef.current) return
    fetch(`${SOCKET_URL}/api/undo`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ roomId: roomIdRef.current, sid: socket.id }),
    })
      .then((r) => r.json())
      .then((result) => {
        if (result.error) setError(result.error)
        else {
          applyMoveResult(result)
          if (result.currentTurn) setCurrentTurn(result.currentTurn)
        }
      })
      .catch((e) => console.error("[undoMove] fetch error", e))
  }, [applyMoveResult])

  const resetSequence = useCallback(() => {
    if (!roomIdRef.current) return
    fetch(`${SOCKET_URL}/api/reset`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ roomId: roomIdRef.current, sid: socket.id }),
    })
      .then((r) => r.json())
      .then((result) => {
        if (result.error) setError(result.error)
        else {
          applyMoveResult(result)
          if (result.currentTurn) setCurrentTurn(result.currentTurn)
        }
      })
      .catch((e) => console.error("[resetSequence] fetch error", e))
  }, [applyMoveResult])

  const requestHints = useCallback(() => {
    if (!roomIdRef.current) return
    socket.emit("request_hints", { roomId: roomIdRef.current })
  }, [])

  const leaveRoom = useCallback(() => {
    if (!roomIdRef.current) return
    socket.emit("leave_room", { roomId: roomIdRef.current })
    roomIdRef.current = null
    setRoomId(null)
    setStatus("idle")
  }, [])

  const clearError = useCallback(() => setError(null), [])

  const isMyTurn = currentTurn === null || currentTurn === socket.id

  return {
    isConnected,
    roomId,
    status,
    level,
    instance,
    sequence,
    validNextIds,
    isDeadEnd,
    isSolved,
    prefixMatch,
    moves,
    timer,
    topString,
    bottomString,
    winner,
    error,
    hints,
    bestHint,
    opponentName,
    opponentMoves,
    opponentPrefixMatch,
    currentTurn,
    isMyTurn,
    gameOptions,
    createRoom,
    joinRoom,
    placeDomino,
    undoMove,
    resetSequence,
    requestHints,
    leaveRoom,
    clearError,
  }
}
