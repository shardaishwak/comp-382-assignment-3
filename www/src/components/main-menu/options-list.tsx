import OptionsGroup from "./options-group"
import { OPTIONS } from "@/app/lib/constants"

export default function OptionsList({
  selectedOptions
}: {
  selectedOptions: { players: string; difficulty: string; multiplayer: string; hints: boolean; timer: boolean }
}) {
  const { players, multiplayer, difficulty } = selectedOptions

  const showPlayers = players === ""
  const showMultiplayer = players === "players-2" && multiplayer === ""
  const showDifficulty =
    difficulty === "" && (players === "players-1" || (players === "players-2" && multiplayer === "multiplayer-2"))
  const showOptional = difficulty !== ""

  return (
    <div className="flex flex-col gap-4 md:gap-8">
      {showPlayers && <OptionsGroup title="number of players" options={OPTIONS.players} />}
      {showMultiplayer && <OptionsGroup title="multiplayer" options={OPTIONS.multiplayer} />}
      {showDifficulty && <OptionsGroup title="difficulty" options={OPTIONS.difficulty} />}
      {showOptional && <OptionsGroup title="optional" options={OPTIONS.optional} />}
    </div>
  )
}
