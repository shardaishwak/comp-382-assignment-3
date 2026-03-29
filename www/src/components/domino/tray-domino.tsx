import { useDraggable } from "@dnd-kit/react"
import type { Domino as DominoType } from "@/app/lib/types"
import Domino from "./domino"

export default function TrayDomino({ id, top, bottom }: DominoType) {
  const { ref } = useDraggable({ id: id, feedback: "clone" })
  return (
    <div ref={ref}>
      <Domino id={id} top={top} bottom={bottom} />
    </div>
  )
}
