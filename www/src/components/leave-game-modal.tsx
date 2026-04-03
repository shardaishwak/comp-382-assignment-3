"use client"

import { useRouter } from "next/navigation"
import Button from "./menu-bar/button"

export default function LeaveGameModal({
  onStay,
  onLeave,
}: {
  onStay: () => void
  onLeave: () => void
}) {
  const router = useRouter()

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-background border border-border-normal rounded-xl p-8 max-w-md w-full mx-4 text-center">
        <h2 className="text-xl font-bold mb-2">Leave game?</h2>
        <p className="text-sm text-gray-400 mb-6">
          You can leave and resume later, or quit and end the game.
        </p>
        <div className="flex justify-center gap-4">
          <Button onClick={onStay}>Stay</Button>
          <Button onClick={() => { router.push("/") }}>
            Resume later
          </Button>
          <Button onClick={onLeave}>
            Quit game
          </Button>
        </div>
      </div>
    </div>
  )
}
