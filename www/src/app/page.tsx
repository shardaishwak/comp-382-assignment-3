"use client"
import soundEffect from "./lib/sound"
import Domino from "@/components/domino"
import type { Domino as DominoType } from "@/app/lib/types"

export default function Home() {
  const domino_list: DominoType[] = [
    { id: 0, top: ["R", "G", "B"], bottom: ["B"] },
    { id: 1, top: ["G", "B"], bottom: ["R", "B"] },
    { id: 2, top: ["B", "B", "R"], bottom: ["G", "R"] }
  ]

  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex flex-1 w-full max-w-3xl flex-col items-center justify-between py-32 px-16 bg-white dark:bg-black sm:items-start">
        <button onClick={soundEffect.place}>Place</button>
        <button onClick={soundEffect.remove}>Remove</button>
        <button onClick={soundEffect.match}>Match</button>
        <button onClick={soundEffect.error}>Error</button>
        <button onClick={soundEffect.tick}>Tick</button>
        <div className="w-full p-2 flex gap-2 overflow-y-scroll">
          {domino_list.map((domino) => (
            <Domino key={domino.id} id={domino.id} top={domino.top} bottom={domino.bottom} />
          ))}
        </div>
      </main>
    </div>
  )
}
