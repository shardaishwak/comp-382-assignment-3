import type { Domino } from "@/app/lib/types"
import PlacedDomino from "./placed-domino"
import { DragDropProvider, useDroppable } from "@dnd-kit/react"
import { move } from "@dnd-kit/helpers"

export default function WorkingArea({
  dominos,
  setDominos
}: {
  dominos: (Domino & { id: string })[]
  setDominos: React.Dispatch<React.SetStateAction<(Domino & { id: string })[]>>
}) {
  const { ref, isDropTarget } = useDroppable({
    id: "working-area"
  })

  return (
    <div ref={ref} className="w-full min-w-0 h-full flex flex-col">
      <div
        className={`${isDropTarget ? "border-[#86dee4]" : "border-mist-300"} self-start -mb-px rounded-xl rounded-b-none border p-2 text-xs uppercase font-bold tracking-widest text-mist-400`}>
        Working Area
      </div>
      <DragDropProvider
        onDragEnd={(event) => {
          setDominos((items) => move(items, event))
        }}>
        <ul
          className={`${isDropTarget ? "border-[#86dee4]" : "border-mist-300"} w-full min-h-24 flex-1 p-2 flex items-start gap-2 overflow-x-scroll border border-b-4 rounded-xl rounded-tl-none duration-150`}>
          {dominos?.map((domino, i) => (
            <PlacedDomino
              key={domino.id}
              id={domino.id}
              index={i}
              dominoId={domino.dominoId}
              top={domino.top}
              bottom={domino.bottom}
            />
          ))}
        </ul>
      </DragDropProvider>
    </div>
  )
}
