"use client"
import { useRouter, useSearchParams } from "next/navigation"
import { useCallback, useState, Suspense, useMemo, useRef, useEffect } from "react"
import { nanoid } from "nanoid"
import { DragDropProvider } from "@dnd-kit/react"
import { isSortable } from "@dnd-kit/react/sortable"

import type { Domino } from "../lib/types"
import { socket } from "../lib/socket"
import soundEffect from "../lib/sound"
import MenuBar from "@/components/menu-bar/menu-bar"
import ProgressBar from "@/components/progress-bar"
import TrayArea from "@/components/tray-area"
import WorkingArea from "@/components/working-area"
import ChainView from "@/components/chain-view"
import { computeScores } from "../lib/scoring"

/*
TAILWIND CSS QUICK CHEATSHEET
https://nerdcave.com/tailwind-cheat-sheet
*/

function MultiplayerContent() {
  const router = useRouter()

  const searchParams = useSearchParams()
  const roomCode = searchParams.get("room")?.trim() ?? ""

  const tray: Domino[] = [
    { id: 0, top: ["R", "G", "B"], bottom: ["R"] },
    { id: 1, top: ["G", "B"], bottom: ["G", "B"] },
    { id: 2, top: ["B", "B", "R"], bottom: ["G", "R"] },
    { id: 3, top: ["R", "R"], bottom: ["R", "B"] },
    { id: 4, top: ["G"], bottom: ["B"] },
    { id: 5, top: ["B", "B"], bottom: ["B", "G"] }
  ]
  const serializeWorking = useCallback(
    (w: (Domino & { placementId: string })[]) =>
      w.map((x) => ({ placementId: x.placementId, dominoId: x.id })),
    []
  )

  const payloadToDomino = useCallback(
    (placements: { placementId: string; dominoId: number }[]): (Domino & { placementId: string })[] =>
      placements.flatMap((p) => {
        const d = tray.find((t) => t.id === p.dominoId)
        if (!d) return []
        return [{ ...d, placementId: p.placementId }]
      }),
    []
  )

  const syncMpWorkingToServer = useCallback(
    (rows: (Domino & { placementId: string })[]) => {
      if (!roomCode) return
      socket.emit("mp_set_working", {
        roomId: roomCode.toUpperCase(),
        placements: serializeWorking(rows),
      })
    },
    [roomCode, serializeWorking]
  )

  const [working, setWorking] = useState<(Domino & { placementId: string })[]>([])
  const [selectedTrayDomino, setSelectedTrayDomino] = useState<Domino | undefined>()
  const scores = useMemo(() => computeScores(working), [working])
  const prevScoreTotal = useRef(0);

  useEffect(() => {
    const total = scores.overallMatch;
    if (total === 100 && prevScoreTotal.current < 100) soundEffect.match();
    prevScoreTotal.current = total;
  }, [scores])

  useEffect(() => {
    if (!roomCode) {
      router.replace("/")
    }
  }, [roomCode, router])

  useEffect(() => {
    if (!roomCode) return
    const code = roomCode.toUpperCase()

    const onWorkingState = (p: {
      roomId: string
      placements: { placementId: string; dominoId: number }[]
    }) => {
      if (p.roomId !== code) return
      setWorking(payloadToDomino(p.placements))
    }

    socket.on("mp_working_state", onWorkingState)
    socket.emit("mp_join", { roomId: code })

    return () => {
      socket.off("mp_working_state", onWorkingState)
    }
  }, [roomCode, payloadToDomino])

  if (!roomCode) {
    return null
  }

  return (
    <div className="h-screen bg-background">
      {/* Top menu bar, this will need more work....*/}
      <MenuBar p1="Player 1" p2="Player 2" time={60000} numMoves={0} />

      <main className="w-full flex-1 px-8 py-8 md:px-16 md:py-16 flex flex-col items-center gap-4 md:gap-8">
        {/* Show current room code */}
        <p className="text-sm text-gray-500">
          Room: <span className="text-gray-300">{roomCode}</span>
        </p>

        {/* Drag and drop system, we will need to make an updater or something to render multiplayer */}
        <DragDropProvider
          onDragStart={(event) => {
            // When dragging starts, store selected domino
            if (event.operation.source) {
              if (!isSortable(event.operation.source)) {
                setSelectedTrayDomino(tray[event.operation.source.id as number])
              }
            }
          }}
          onDragEnd={(event) => {
            if (event.canceled) return

            // If dropped in working area from tray add domino and notify socket
            if (event.operation.target?.id == "working-area") {
              const src = event.operation.source
              if (src && !isSortable(src)) {
                const sourceId = src.id as number
                setWorking((prev) => {
                  const next = [
                    ...prev,
                    { ...tray[sourceId], placementId: nanoid() },
                  ]
                  soundEffect.place()
                  syncMpWorkingToServer(next)
                  return next
                })
              }
            }

            // Clear selection after drop
            setSelectedTrayDomino(undefined)
          }}
        >
          {/* Bottom tray */}
          <TrayArea dominos={tray} />

          {/* Main board */}
          <WorkingArea
            dominos={working}
            setDominos={setWorking}
            selectedTrayDomino={selectedTrayDomino}
            onMpWorkingChange={(next) => syncMpWorkingToServer(next)}
          />
        </DragDropProvider>

        <ChainView dominos={working} />
        <ProgressBar progress={scores.overallMatch} />
      </main>
    </div>
  )
}

// This is the page content. It renders this component when the page is loaded. suspend tells us to wait for it to load fully
export default function MultiplayerPage() { 
  return (
    <Suspense fallback={<p>Loading...</p>}>
      {/* this is a nice little trick i learned before... just in case the page takes a while to load*/}
      <MultiplayerContent />
    </Suspense>
  )
}