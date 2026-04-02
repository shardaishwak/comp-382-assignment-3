import type { Domino as DominoType } from "@/app/lib/types"
import TrayDomino from "@/components/domino/tray-domino"

export default function TrayArea({
  dominos,
  validNextIds = [],
  onDominoClick,
}: {
  dominos: DominoType[]
  validNextIds?: number[]
  onDominoClick?: (dominoId: number) => void
}) {
  return (
    <div className="w-full flex flex-col">
      <div className="self-start -mb-px rounded-xl rounded-b-none border border-border-normal p-2 text-xs uppercase font-bold tracking-widest">
        Dominos
      </div>
      <div className="w-full min-h-24 p-2 flex flex-row gap-2 overflow-x-scroll border border-border-normal rounded-xl rounded-tl-none duration-150">
        {dominos?.map((domino, i) => (
          <TrayDomino
            key={i}
            id={domino.id}
            top={domino.top}
            bottom={domino.bottom}
            isHint={validNextIds.includes(domino.id)}
            onClick={onDominoClick ? () => onDominoClick(domino.id) : undefined}
          />
        ))}
      </div>
    </div>
  )
}
