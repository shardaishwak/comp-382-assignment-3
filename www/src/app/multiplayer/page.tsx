"use client"
import { useRouter, useSearchParams } from "next/navigation"
import { useCallback, useState, Suspense } from "react"
import { nanoid } from "nanoid"
import { DragDropProvider } from "@dnd-kit/react"
import { isSortable } from "@dnd-kit/react/sortable"

import type { Domino } from "../lib/types"
import soundEffect from "../lib/sound"
import MenuBar from "@/components/menu-bar/menu-bar"
import ProgressBar from "@/components/progress-bar"
import TrayArea from "@/components/tray-area"
import WorkingArea from "@/components/working-area"
import ChainView from "@/components/chain-view"

/*
TAILWIND CSS QUICK CHEATSHEET
https://nerdcave.com/tailwind-cheat-sheet
*/

function MultiplayerContent() {
  const router = useRouter()

  // Get the room code 
  const searchParams = useSearchParams()
  const roomFromUrl = searchParams.get("room")

  // State for the lobby
  const [createdCode, setCreatedCode] = useState<string | null>(null)
  const [joinInput, setJoinInput] = useState("")

  const tray: Domino[] = [
    { id: 0, top: ["R", "G", "B"], bottom: ["B"] },
    { id: 1, top: ["G", "B"], bottom: ["R", "B"] },
    { id: 2, top: ["B", "B", "R"], bottom: ["G", "R"] },
    { id: 3, top: ["R", "R"], bottom: ["B", "B"] },
    { id: 4, top: ["G"], bottom: ["B"] },
    { id: 5, top: ["B", "B"], bottom: ["G"] }
  ]


  const [working, setWorking] = useState<(Domino & { placementId: string })[]>([])
  const [selectedTrayDomino, setSelectedTrayDomino] = useState<Domino | undefined>()

  // Create a new room go into it
  const createRoom = useCallback(() => {
    const code = nanoid(10)
    setCreatedCode(code)
    router.push(`/multiplayer?room=${code}`)
  }, [router])

  // Join an existing room
  const joinRoom = useCallback(() => {
    const code = joinInput.trim()
    if (!code) return
    router.push(`/multiplayer?room=${encodeURIComponent(code)}`)
  }, [joinInput, router])


  if (roomFromUrl) {
    return (
      <div className="h-screen bg-background">
        {/* Top menu bar, this will need more work....*/}
        <MenuBar p1="Player 1" p2="Player 2" time={60000} numMoves={0} />

        <main className="w-full flex-1 px-8 py-8 md:px-16 md:py-16 flex flex-col items-center gap-4 md:gap-8">
          {/* Show current room code */}
          <p className="text-sm text-gray-500">
            Room: <span className="text-gray-300">{roomFromUrl}</span>
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

              // If dropped in working area, add domino to board
              if (event.operation.target?.id == "working-area") {
                if (event.operation.source) {
                  const sourceId = event.operation.source.id as number
                  setWorking((prev) => [
                    ...prev,
                    { ...tray[sourceId], placementId: nanoid() }
                  ])
                  soundEffect.place()
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
            />
          </DragDropProvider>

          <ChainView dominos={working} />
          <ProgressBar top={25} bottom={50} />
        </main>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center gap-8 px-6">
      {/* Go back home */}
      <button
        type="button"
        onClick={() => { soundEffect.tick(); router.push("/") }}
        className="text-sm text-gray-500 hover:text-gray-400 self-start max-w-md w-full text-left ">
        Back
      </button>

      <h1 className="text-xl text-gray-400">Multiplayer</h1>

      <div className="gap-6 w-full max-w-md">
        {/* Create room section */}
        <div className="flex flex-col gap-2">
          <span className="text-sm text-gray-500">Create a room</span>
          <button
            onClick={() => { soundEffect.tick(); createRoom() }}
            className="py-3 px-4 rounded border border-border-light text-gray-400 hover:bg-background2">
            Create room
          </button>

          {/* Show the generated room code only if its there*/}
          {createdCode && (
            <p className="text-sm text-gray-500 break-all">
              Code: <span className="text-gray-300">{createdCode}</span>
            </p>
          )}
        </div>

        {/* Join room section */}
        <div className="flex flex-col gap-2">
          <span className="text-sm text-gray-500">Join a room</span>
          <div className="flex flex-col sm:flex-row">
            <input
              value={joinInput}
              onChange={(e) => setJoinInput(e.target.value)}
              placeholder="Room code"
              className="flex-1 py-2 px-3 rounded border border-border-light bg-background2 text-gray-300"
            />
            <button
              onClick={() => { soundEffect.tick(); joinRoom() }}
              className="py-2 px-4 rounded border border-border-light text-gray-400 hover:bg-background2">
              Join
            </button>
          </div>
        </div>
      </div>
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