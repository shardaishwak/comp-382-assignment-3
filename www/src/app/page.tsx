"use client"
import soundEffect from "./lib/sound"
import { useState } from "react"
import { nanoid } from "nanoid"
import { DragDropProvider } from "@dnd-kit/react"
import type { Domino } from "./lib/types"
import TrayArea from "@/components/tray-area"
import WorkingArea from "@/components/working-area"

export default function Home() {
  const tray: Domino[] = [
    { dominoId: 0, top: ["R", "G", "B"], bottom: ["B"] },
    { dominoId: 1, top: ["G", "B"], bottom: ["R", "B"] },
    { dominoId: 2, top: ["B", "B", "R"], bottom: ["G", "R"] },
    { dominoId: 4, top: ["R", "R"], bottom: ["B", "B"] },
    { dominoId: 5, top: ["G"], bottom: ["B"] },
    { dominoId: 6, top: ["B", "B"], bottom: ["G"] }
  ]
  const [working, setWorking] = useState<(Domino & { id: string })[]>([])

  return (
    <div className="h-screen flex items-center justify-center bg-zinc-50 font-sans">
      <main className="w-full max-w-3xl h-full px-8 py-8 md:px-16 md:py-16 flex flex-col lg:flex-row gap-4 md:gap-8 bg-white">
        <DragDropProvider
          onDragEnd={(event) => {
            if (event.operation.target?.id == "working-area") {
              if (event.operation.source) {
                setWorking((prev) => [...prev, { ...tray[event.operation.source?.id as number], id: nanoid() }])
              }
            }
          }}>
          <TrayArea dominos={tray} />
          <WorkingArea dominos={working} setDominos={setWorking} />
        </DragDropProvider>
      </main>
    </div>
  )
}
