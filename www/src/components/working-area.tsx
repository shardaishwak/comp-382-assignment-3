import type { Domino as DominoType } from "@/app/lib/types"
import Domino from "./domino/domino"
import { useDroppable } from "@dnd-kit/react"

export default function WorkingArea({
  dominos,
  selectedTrayDomino,
}: {
  dominos: (DominoType & { placementId: string })[]
  selectedTrayDomino?: DominoType | undefined
}) {
  const { ref, isDropTarget } = useDroppable({
    id: "working-area",
  })

  return (
    <div ref={ref} className="w-full min-w-0 h-full flex flex-col">
      <div className="self-start -mb-px rounded-xl rounded-b-none border border-border-normal p-2 text-xs uppercase font-bold tracking-widest">
        Working Area
      </div>
      <div className="w-full min-h-32.5 flex-1 p-2 flex items-start gap-2 overflow-x-scroll border border-border-normal rounded-xl rounded-tl-none duration-150">
        {dominos?.map((domino) => (
          <Domino
            key={domino.placementId}
            id={domino.id}
            top={domino.top}
            bottom={domino.bottom}
          />
        ))}
        {isDropTarget && selectedTrayDomino && (
          <div className="opacity-50">
            <Domino
              id={selectedTrayDomino.id}
              top={selectedTrayDomino.top}
              bottom={selectedTrayDomino.bottom}
            />
          </div>
        )}
      </div>
    </div>
  )
}
