"use client"
import Link from "next/link"
import soundEffect from "./lib/sound"

export default function Page() {
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center gap-10 px-6">
      <h1 className="text-xl text-gray-400">Domino Game</h1>
      <nav className="flex flex-col gap-4">
        <Link
          href="/single"
          onClick={() => soundEffect.tick()}
          className="flex-1 text-center py-3 px-4 rounded border border-border-light text-gray-400 hover:bg-background2">
          Single player
        </Link>
        <Link
          href="/multiplayer"
          onClick={() => soundEffect.tick()}
          className="flex-1 text-center py-3 px-4 rounded border border-border-light text-gray-400 hover:bg-background2">
          Multiplayer
        </Link>
      </nav>
    </div>
  )
}
