import PlaceholderDomino from "../domino/placeholder-domino"
import OptionDomino from "../domino/option-domino"
import type { GameOptions } from "@/app/lib/types"
import { OPTIONS } from "@/app/lib/constants"
import { useDroppable } from "@dnd-kit/react"

export default function OptionsDropArea({
  selectedOptions,
  curSelected = {}
}: {
  selectedOptions: GameOptions
  curSelected?: Partial<GameOptions>
}) {
  const { ref, isDropTarget } = useDroppable({
    id: "options-drop-area"
  })

  if (!isDropTarget) curSelected = {}
  const display = { ...selectedOptions, ...curSelected }

  const match_p = OPTIONS.players.find((o) => o.id === display.players)
  const { n: n_players, text: text_players } = match_p ?? { n: 0, text: "" }
  const match_m = OPTIONS.multiplayer.find((o) => o.id === display.multiplayer)
  const { n: n_multiplayer, text: text_multiplayer } = match_m ?? { n: 0, text: "" }
  const match_d = OPTIONS.difficulty.find((o) => o.id === display.difficulty)
  const { n: n_difficulty, text: text_difficulty } = match_d ?? { n: 0, text: "" }
  
  const isCurSelected = (key: string) => {
    return isDropTarget && key in curSelected
  }

  return (
    <div ref={ref} className="w-full flex flex-col">
      <div className="self-start -mb-px rounded-xl rounded-b-none border border-border-normal p-2 text-xs uppercase font-bold tracking-widest">
        Selected options
      </div>
      <div className="w-full min-h-24 p-2 flex flex-row gap-2 overflow-x-scroll border border-border-normal rounded-xl rounded-tl-none duration-150">
        {display.players === "" ? (
          <PlaceholderDomino text="# players" />
        ) : (
          <OptionDomino
            id={display.players + "-placed"}
            n={n_players}
            text={text_players}
            opacity={isCurSelected("players")}
            disabled
          />
        )}
        {selectedOptions.players === "players-2" && display.multiplayer === "" ? (
          <PlaceholderDomino text="join/host" />
        ) : (
          selectedOptions.players === "players-2" &&
          display.multiplayer !== "" && (
            <OptionDomino
              id={display.multiplayer + "-placed"}
              n={n_multiplayer}
              text={text_multiplayer}
              opacity={isCurSelected("multiplayer")}
              disabled
            />
          )
        )}
        {display.difficulty === "" &&
        (selectedOptions.players === "players-1" ||
          (selectedOptions.players === "players-2" && selectedOptions.multiplayer === "multiplayer-2")) ? (
          <PlaceholderDomino text="difficulty" />
        ) : (
          display.difficulty !== "" &&
          (selectedOptions.players === "players-1" ||
            (selectedOptions.players === "players-2" && selectedOptions.multiplayer === "multiplayer-2")) && (
            <OptionDomino
              id={display.difficulty + "-placed"}
              n={n_difficulty}
              text={text_difficulty}
              opacity={isCurSelected("difficulty")}
              disabled
            />
          )
        )}
        {display.hints && (
          <OptionDomino id="hints-placed" n={1} text="hints" opacity={isCurSelected("hints")} disabled />
        )}
        {display.timer && (
          <OptionDomino id="timer-placed" n={1} text="timer" opacity={isCurSelected("timer")} disabled />
        )}
      </div>
    </div>
  )
}
