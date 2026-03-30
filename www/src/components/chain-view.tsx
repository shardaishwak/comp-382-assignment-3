import type { Domino, Symbol } from "@/app/lib/types"

const DOT_COLOR: Record<Symbol, string> = {
  R: "bg-[#e48693]",
  G: "bg-[#bbe486]",
  B: "bg-[#86dee4]"
}

export default function ChainView({ dominos }: { dominos: Domino[] }) {
  if (dominos.length === 0) return null

  return (
    <div className="w-full overflow-x-auto rounded-lg border border-border-normal bg-background2 px-3 py-2.5">
      <div className="flex flex-col gap-1.5 w-fit min-w-full">
        {/* Top row */}
        <Row label="top" dominos={dominos} row="top" />
        <div className="border-t border-border-normal" />
        {/* Bottom row */}
        <Row label="btm" dominos={dominos} row="bottom" />
      </div>
    </div>
  )
}

function Row({
  label,
  dominos,
  row,
}: {
  label: string
  dominos: Domino[]
  row: "top" | "bottom"
}) {
  return (
    <div className="flex items-center">
      <span className="text-[10px] text-gray-500 w-8 shrink-0">{label}</span>
      <div className="flex items-center">
        {dominos.map((d, di) => (
          <div key={di} className="flex items-center">
            {di > 0 && (
              <div className="mx-0.5 w-px h-4 border-l border-dashed border-white/20" />
            )}
            <div className="flex items-center gap-1">
              {d[row].map((s, si) => (
                <div key={si} className={`${DOT_COLOR[s]} w-2.5 h-2.5 rounded-full`} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
