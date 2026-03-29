"use client"
import soundEffect from "./lib/sound"
import { useState } from "react"
import { nanoid } from "nanoid"
import { DragDropProvider } from "@dnd-kit/react"
import { isSortable } from "@dnd-kit/react/sortable"
import type { Domino } from "./lib/types"
import MenuBar from "@/components/menu-bar"
import ProgressBar from "@/components/progress-bar"
import TrayArea from "@/components/tray-area"
import WorkingArea from "@/components/working-area"

export default function Home() {
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

  // game states
  const [p1, setP1] = useState<string>("Player 1")
  const [p2, setP2] = useState<string>("Player 2")
  const [time, setTime] = useState<number>(60000) // milliseconds
  const [numMoves, setNumMoves] = useState<number>(0)
  const [topPercentage, setTopPercentage] = useState<number>(25)
  const [bottomPercentage, setBottomPercentage] = useState<number>(50)

  return (
    <div className="h-screen bg-background">
      <MenuBar p1={p1} p2={p2} time={time} numMoves={numMoves} />
      <main className="w-full flex-1 px-8 py-8 md:px-16 md:py-16 flex flex-col items-center gap-4 md:gap-8">
        <DragDropProvider
          onDragStart={(event) => {
            if (event.operation.source) {
              if (!isSortable(event.operation.source)) {
                setSelectedTrayDomino(tray[event.operation.source.id as number])
              }
            }
          }}
          onDragEnd={(event) => {
            if (event.canceled) return
            if (event.operation.target?.id == "working-area") {
              if (event.operation.source) {
                const sourceId = event.operation.source.id as number
                setWorking((prev) => [...prev, { ...tray[sourceId], placementId: nanoid() }])
              }
            }
            setSelectedTrayDomino(undefined)
          }}>
          <TrayArea dominos={tray} />
          <WorkingArea dominos={working} setDominos={setWorking} selectedTrayDomino={selectedTrayDomino} />
        </DragDropProvider>
        <ProgressBar top={topPercentage} bottom={bottomPercentage} />
      </main>
    </div>
  )
}
