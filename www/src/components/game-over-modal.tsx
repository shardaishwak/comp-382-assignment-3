"use client"

import { useRouter } from "next/navigation"
import Button from "./menu-bar/button"

export default function GameOverModal({
  isSolved,
  winner,
  prefixMatch,
  moves,
}: {
  isSolved: boolean
  winner: { id: string; name: string } | null
  prefixMatch: number
  moves: number
}) {
  const router = useRouter()

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-background border border-border-normal rounded-xl p-8 max-w-md w-full mx-4 text-center">
        <h2 className="text-2xl font-bold mb-4">
          {isSolved ? "Puzzle Solved!" : "Time's Up!"}
        </h2>
        {isSolved && winner && (
          <p className="text-lg mb-2">{winner.name} found the solution!</p>
        )}
        {!isSolved && winner && (
          <p className="text-lg mb-2">Winner: {winner.name}</p>
        )}
        {!isSolved && (
          <p className="text-sm text-gray-400 mb-2">
            Best prefix match: {prefixMatch} characters
          </p>
        )}
        <p className="text-sm text-gray-400 mb-6">Total moves: {moves}</p>
        <Button onClick={() => router.push("/")}>Back to Menu</Button>
      </div>
    </div>
  )
}
