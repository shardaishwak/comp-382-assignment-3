"use client"

import { useRouter, useSearchParams } from "next/navigation"
import { Suspense, useEffect, useRef, useState } from "react"
import { DragDropProvider } from "@dnd-kit/react"
import { isSortable } from "@dnd-kit/react/sortable"

import type { Domino, LevelId } from "../lib/types"
import { useGameSocket } from "../hooks/useGameSocket"
import soundEffect from "../lib/sound"
import MenuBar from "@/components/menu-bar/menu-bar"
import ProgressBar from "@/components/progress-bar"
import TrayArea from "@/components/tray-area"
import WorkingArea from "@/components/working-area"
import ChainView from "@/components/chain-view"
import GameOverModal from "@/components/game-over-modal"

function MultiplayerContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const mode = searchParams.get("mode") // "host" or null
  const roomCode = searchParams.get("room")?.trim() ?? ""
  const difficulty = (searchParams.get("difficulty") || "medium") as LevelId

  const game = useGameSocket()
  const hasInitialized = useRef(false)
  const prevSolved = useRef(false)
  const [selectedTrayDomino, setSelectedTrayDomino] = useState<Domino | undefined>()

  useEffect(() => {
    if (!game.isConnected || hasInitialized.current) return
    hasInitialized.current = true

    if (mode === "host") {
      game.createRoom("Player 1", difficulty)
    } else if (roomCode) {
      game.joinRoom(roomCode, "Player 2")
    } else {
      router.replace("/")
    }
  }, [game.isConnected, mode, roomCode, difficulty, router, game.createRoom, game.joinRoom])

  useEffect(() => {
    if (game.isSolved && !prevSolved.current) {
      soundEffect.match()
    }
    prevSolved.current = game.isSolved
  }, [game.isSolved])

  if (!mode && !roomCode) return null

  const maxLen = Math.max(game.topString.length, game.bottomString.length, 1)
  const progress = game.isSolved ? 100 : Math.round((game.prefixMatch / maxLen) * 100)

  return (
    <div className="h-screen bg-background">
      <MenuBar
        p1="Player 1"
        p2={game.opponentName || "Waiting..."}
        time={game.timer * 1000}
        numMoves={game.moves}
        onUndo={game.status === "playing" ? game.undoMove : undefined}
        onReset={game.status === "playing" ? game.resetSequence : undefined}
        onRequestHints={game.status === "playing" ? game.requestHints : undefined}
      />

      <main className="w-full flex-1 px-8 py-8 md:px-16 md:py-16 flex flex-col items-center gap-4 md:gap-8">
        {game.roomId && (
          <p className="text-sm text-gray-500">
            Room: <span className="text-gray-300 font-mono">{game.roomId}</span>
          </p>
        )}

        {game.status === "waiting" && (
          <div className="text-gray-400 text-center">
            <p>Waiting for opponent to join...</p>
            {game.roomId && (
              <p className="mt-2 text-lg font-mono text-gray-200">
                Share this room code: {game.roomId}
              </p>
            )}
          </div>
        )}

        {game.status === "playing" && (
          <>
            {game.opponentName && (
              <div className="flex gap-6 text-sm text-gray-400">
                <span>Opponent moves: {game.opponentMoves}</span>
                <span>Opponent prefix match: {game.opponentPrefixMatch}</span>
              </div>
            )}

            <DragDropProvider
              onDragStart={(event) => {
                if (event.operation.source && !isSortable(event.operation.source)) {
                  const dominoId = event.operation.source.id as number
                  const domino = game.instance.find((d) => d.id === dominoId)
                  setSelectedTrayDomino(domino)
                }
              }}
              onDragEnd={(event) => {
                if (event.canceled) return
                if (event.operation.target?.id === "working-area") {
                  const src = event.operation.source
                  if (src && !isSortable(src)) {
                    game.placeDomino(src.id as number)
                    soundEffect.place()
                  }
                }
                setSelectedTrayDomino(undefined)
              }}
            >
              <TrayArea dominos={game.instance} validNextIds={game.validNextIds} onDominoClick={(id) => { game.placeDomino(id); soundEffect.place() }} />
              <WorkingArea dominos={game.sequence} selectedTrayDomino={selectedTrayDomino} />
            </DragDropProvider>

            <ChainView dominos={game.sequence} />
            <ProgressBar progress={progress} />

            {game.isDeadEnd && (
              <p className="text-yellow-400 text-sm">
                Dead end — no valid moves. Try undoing or resetting.
              </p>
            )}
          </>
        )}

        {game.status === "idle" && (
          <p className="text-gray-400">Connecting to server...</p>
        )}

        {game.error && (
          <button className="text-red-400 text-sm" onClick={game.clearError}>
            {game.error} (click to dismiss)
          </button>
        )}

        {game.hints.length > 0 && (
          <div className="w-full max-w-md text-sm text-gray-400 border border-border-normal rounded-lg p-3">
            <p className="font-semibold mb-2">Hints:</p>
            {game.hints.map((h, i) => (
              <p key={i} className="mb-1">
                {h.dominoId >= 0 ? `Domino ${h.dominoId}: ` : ""}
                {h.explanation}
              </p>
            ))}
          </div>
        )}
      </main>

      {game.status === "finished" && (
        <GameOverModal
          isSolved={game.isSolved}
          winner={game.winner}
          prefixMatch={game.prefixMatch}
          moves={game.moves}
        />
      )}
    </div>
  )
}

export default function MultiplayerPage() {
  return (
    <Suspense fallback={<p>Loading...</p>}>
      <MultiplayerContent />
    </Suspense>
  )
}
