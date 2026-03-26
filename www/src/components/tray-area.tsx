import type { Domino as DominoType } from "@/app/lib/types"
import TrayDomino from "@/components/tray-domino"

export default function TrayArea({ dominos }: { dominos: DominoType[] }) {
  return (
    <div className="w-full lg:w-auto flex flex-col">
      <div className="self-start -mb-px rounded-xl rounded-b-none border border-mist-300 p-2 text-xs uppercase font-bold tracking-widest text-mist-400">
        Dominos
      </div>
      <ul className="w-full min-h-24 p-2 flex flex-row lg:flex-col gap-2 overflow-x-scroll lg:overflow-y-scroll border border-b-4 border-mist-300 rounded-xl rounded-tl-none duration-150">
        {dominos?.map((domino, i) => (
          <TrayDomino key={i} dominoId={domino.dominoId} top={domino.top} bottom={domino.bottom} />
        ))}
      </ul>
    </div>
  )
}
