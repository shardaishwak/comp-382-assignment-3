"use client"
import soundEffect from "./lib/sound"
import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { DragDropProvider } from "@dnd-kit/react"
import { ArrowRightIcon, ArrowUturnLeftIcon } from "@heroicons/react/16/solid"
import Button from "@/components/menu-bar/button"
import OptionsList from "@/components/main-menu/options-list"
import OptionsDropArea from "@/components/main-menu/options-drop-area"
import type { GameOptions } from "./lib/types"
import { EMPTY_OPTIONS } from "./lib/constants"

export default function Page() {
  const [playerName, setPlayerName] = useState("")
  const [joinInput, setJoinInput] = useState<string>("")
  const [selectedOptions, setSelectedOptions] = useState<GameOptions>(EMPTY_OPTIONS)
  const [curSelected, setCurSelected] = useState<Partial<GameOptions>>({})
  const router = useRouter()

  useEffect(() => {
    const saved = localStorage.getItem("playerName") || ""
    setPlayerName(saved)
  }, [])

  const savePlayerName = (name: string) => {
    setPlayerName(name)
    localStorage.setItem("playerName", name)
  }

  const BOOL_OPTIONS = new Set(["hints", "timer", "undo"])

  const getOptionKey = (sourceId: string) =>
    BOOL_OPTIONS.has(sourceId) ? sourceId : sourceId.split("-")[0]

  const getOptionValue = (sourceId: string): string | boolean =>
    BOOL_OPTIONS.has(sourceId) ? true : sourceId

  const difficultyToLevel = (d: string): string => {
    switch (d) {
      case "difficulty-1": return "easy"
      case "difficulty-2": return "medium"
      case "difficulty-3": return "hard"
      default: return "medium"
    }
  }

  const handleStart = () => {
    const level = difficultyToLevel(selectedOptions.difficulty)
    const opts = new URLSearchParams()
    if (selectedOptions.timer) opts.set("timer", "1")
    if (selectedOptions.hints) opts.set("hints", "1")
    if (selectedOptions.undo) opts.set("undo", "1")
    const optStr = opts.toString() ? `&${opts.toString()}` : ""

    if (selectedOptions.players === "players-1") {
      router.push(`/single?difficulty=${level}${optStr}`)
      return
    }
    if (selectedOptions.multiplayer === "multiplayer-1") { //join room
      router.push(`/multiplayer?room=${encodeURIComponent(joinInput)}${optStr}`)
      return
    }
    if (selectedOptions.multiplayer === "multiplayer-2") { //host room
      router.push(`/multiplayer?mode=host&difficulty=${level}${optStr}`)
    }
  }

  const isResetDisabled =
    selectedOptions.players === "" &&
    selectedOptions.difficulty === "" &&
    !selectedOptions.hints &&
    !selectedOptions.timer &&
    !selectedOptions.undo

  const isStartDisabled =
    !playerName.trim() ||
    selectedOptions.players === "" ||
    (selectedOptions.multiplayer === "multiplayer-1" && !joinInput.trim()) || //disable join button if no room code
    (selectedOptions.multiplayer !== "multiplayer-1" && selectedOptions.difficulty === "")

  return (
    <div className="min-h-screen bg-background">
      {/* menu bar */}
      <div className="px-8 md:px-16 border-b border-border-normal">
        <div className="h-16 bg-background grid grid-cols-2">
          <div className="flex items-center gap-4 md:gap-6">
            <h1 className="font-bold text-gray-500 text-base whitespace-nowrap">PCP Domino Game</h1>
          </div>
          <div className="flex items-center justify-end gap-2">
            <label className="text-sm text-gray-500 hidden md:inline">Name:</label>
            <input
              value={playerName}
              onChange={(e) => savePlayerName(e.target.value)}
              placeholder="Enter your name"
              className="py-1 px-3 rounded-lg border border-border-normal text-sm text-gray-300 bg-transparent w-40 focus:outline-none focus:border-border-light"
            />
          </div>
        </div>
      </div>

      <main className="w-full px-8 py-8 md:px-16 md:py-16 flex flex-col gap-4 md:gap-8">
        <DragDropProvider
          onDragStart={({ operation: { source } }) => {
            const id = source?.id as string
            setCurSelected({ [getOptionKey(id)]: getOptionValue(id) })
          }}
          onDragEnd={({ operation: { source, target }, canceled }) => {
            if (canceled || target?.id !== "options-drop-area") return
            const id = source?.id as string
            soundEffect.place()
            setSelectedOptions((prev) => ({ ...prev, [getOptionKey(id)]: getOptionValue(id) }))
            setCurSelected({})
          }}>
          <div className="w-full flex flex-col items-end gap-4 md:gap-8">
            <OptionsDropArea selectedOptions={selectedOptions} curSelected={curSelected} />

            {/* room code input area */}
            {selectedOptions.multiplayer === "multiplayer-1" && (
              <div>
                <input
                  value={joinInput}
                  onChange={(e) => setJoinInput(e.target.value)}
                  placeholder="room code"
                  className="flex-1 py-2 px-3 rounded-lg border border-border-normal text-sm hover:border-border-light text-gray-500 duration-150"
                />
              </div>
            )}

            {/* reset / start / join buttons */}
            <div className="flex gap-4">
              <Button onClick={() => setSelectedOptions(EMPTY_OPTIONS)} disabled={isResetDisabled}>
                Reset <ArrowUturnLeftIcon className="w-4 h-4" />
              </Button>
              <Button onClick={handleStart} disabled={isStartDisabled}>
                {selectedOptions.multiplayer === "multiplayer-1" ? "join" : "start"}
                <ArrowRightIcon className="w-4 h-4" />
              </Button>
            </div>
          </div>

          <OptionsList selectedOptions={selectedOptions} />
        </DragDropProvider>
      </main>
    </div>
  )
}
