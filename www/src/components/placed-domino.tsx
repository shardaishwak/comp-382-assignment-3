import { useSortable } from "@dnd-kit/react/sortable"
import type { PlacedDomino } from "@/app/lib/types"
import Domino from "./domino"

export default function PlacedDomino({ placementId, position, id, top, bottom }: PlacedDomino) {
  const { ref } = useSortable({ id: placementId, index: position })
  return (
    <div ref={ref}>
      <Domino id={id} top={top} bottom={bottom} />
    </div>
  )
}
