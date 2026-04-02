"use client"

import { Suspense, useEffect, useRef, useState } from "react"
import { useSearchParams } from "next/navigation"
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

function SinglePlayerContent() {
  const searchParams = useSearchParams()
  const difficulty = (searchParams.get("difficulty") || "medium") as LevelId
  const game = useGameSocket()
  const hasCreated = useRef(false)
  const prevSolved = useRef(false)
  const [selectedTrayDomino, setSelectedTrayDomino] = useState<Domino | undefined>()

  useEffect(() => {
    if (game.isConnected && !hasCreated.current) {
      hasCreated.current = true
      game.createRoom("Player 1", difficulty, true)
    }
  }, [game.isConnected, difficulty, game.createRoom])

  useEffect(() => {
    if (game.isSolved && !prevSolved.current) {
      soundEffect.match()
    }
    prevSolved.current = game.isSolved
  }, [game.isSolved])

  const maxLen = Math.max(game.topString.length, game.bottomString.length, 1)
  const progress = game.isSolved ? 100 : Math.round((game.prefixMatch / maxLen) * 100)

  return (
    <div className="h-screen bg-background">
      <MenuBar
        p1="Player 1"
        p2=""
        time={game.timer * 1000}
        numMoves={game.moves}
        onUndo={game.undoMove}
        onReset={game.resetSequence}
        onRequestHints={game.requestHints}
      />
      <main className="w-full flex-1 px-8 py-8 md:px-16 md:py-16 flex flex-col items-center gap-4 md:gap-8">
        {game.status === "playing" && (
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
        )}

        {game.status === "waiting" && (
          <p className="text-gray-400">Connecting...</p>
        )}
        {game.status === "idle" && (
          <p className="text-gray-400">Connecting to server...</p>
        )}

        <ChainView dominos={game.sequence} />
        <ProgressBar progress={progress} />

        {game.isDeadEnd && game.status === "playing" && (
          <p className="text-yellow-400 text-sm">
            Dead end — no valid moves. Try undoing or resetting.
          </p>
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
          winner={game.isSolved ? { id: "you", name: "You" } : null}
          prefixMatch={game.prefixMatch}
          moves={game.moves}
        />
      )}
    </div>
  )
}

export default function SinglePlayerPage() {
  return (
    <Suspense fallback={<p>Loading...</p>}>
      <SinglePlayerContent />
    </Suspense>
  )
}
