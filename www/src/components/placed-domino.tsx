import { useSortable } from "@dnd-kit/react/sortable"
import type { PlacedDomino } from "@/app/lib/types"
import Domino from "./domino"

export default function PlacedDomino({ id, index, dominoId, top, bottom }: PlacedDomino) {
  const { ref } = useSortable({ id, index })
  return (
    <li ref={ref}>
      <Domino dominoId={dominoId} top={top} bottom={bottom} />
    </li>
  )
}
