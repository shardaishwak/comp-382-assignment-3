"use client"

import { ArrowLeftIcon, ArrowUturnLeftIcon, ArrowPathIcon } from "@heroicons/react/16/solid"
import { useRouter } from "next/navigation"
import Button from "./button"
import OptionsButton from "./options-button"

export default function MenuBar({
  p1,
  p2,
  time,
  numMoves,
  onUndo,
  onReset,
  onRequestHints,
}: {
  p1: string
  p2: string
  time: number
  numMoves: number
  onUndo?: () => void
  onReset?: () => void
  onRequestHints?: () => void
}) {
  const formatTime = (ms: number): string => {
    const totalSeconds = Math.floor(ms / 1000)
    const minutes = Math.floor(totalSeconds / 60)
    const seconds = totalSeconds % 60
    return `${minutes}:${seconds.toString().padStart(2, "0")}`
  }

  const formattedTime = formatTime(time)
  const router = useRouter()

  return (
    <div className="px-8 md:px-16 border-b border-border-normal">
      <div className="h-16 bg-background grid grid-cols-2">
        <div className="flex items-center gap-4 md:gap-6">
          <Button type="button" onClick={() => router.push("/")}>
            <ArrowLeftIcon className="w-4 h-4" />
            <p className="hidden md:inline">Back</p>
          </Button>
          <h1 className="font-bold text-gray-500 text-base whitespace-nowrap">
            {p2 ? `${p1} vs ${p2}` : p1}
          </h1>
        </div>

        <div className="flex gap-4 md:gap-6 items-center justify-end">
          {onUndo && (
            <Button type="button" onClick={onUndo}>
              <ArrowUturnLeftIcon className="w-4 h-4" />
              <p className="hidden md:inline">Undo</p>
            </Button>
          )}
          {onReset && (
            <Button type="button" onClick={onReset}>
              <ArrowPathIcon className="w-4 h-4" />
              <p className="hidden md:inline">Reset</p>
            </Button>
          )}
          <div className="hidden md:inline text-lg font-semibold">{formattedTime}</div>
          <div className="hidden md:inline font-semibold whitespace-nowrap">Moves: {numMoves}</div>
          <OptionsButton onRequestHints={onRequestHints} />
        </div>
      </div>
      <div className="md:hidden float-right rounded-lg border border-border-normal mt-8 py-2 font-semibold flex flex-col gap-1 divide-y divide-border-muted">
        <p className="text-right px-4 pb-1">{formattedTime}</p>
        <p className="text-right px-4">Moves: {numMoves}</p>
      </div>
    </div>
  )
}
