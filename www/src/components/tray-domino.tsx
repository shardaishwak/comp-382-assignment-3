import { useDraggable } from "@dnd-kit/react"
import type { Domino as DominoType } from "@/app/lib/types"
import Domino from "./domino"

export default function TrayDomino({ dominoId, top, bottom }: DominoType) {
  const { ref } = useDraggable({ id: dominoId })
  return (
    <li ref={ref}>
      <Domino dominoId={dominoId} top={top} bottom={bottom} />
    </li>
  )
}
