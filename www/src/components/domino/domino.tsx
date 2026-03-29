import type { Domino } from "@/app/lib/types"

export default function Domino({ id, top, bottom, isHint = false }: Domino & { isHint?: boolean }) {
  return (
    <div className={`brightness-115 min-w-20 min-h-28 rounded-xl p-2 grid grid-rows-2 divide-y divide-solid  border border-b-4 hover:-translate-y-2 duration-150 ${isHint ? "bg-[#0f1e21] divide-[#1b292c] border-[#447d8a]" : "bg-background2 divide-border-muted border-border-normal"}`}>
      <div className={`px-1 flex gap-1 items-center ${top.length === 1 ? "justify-center" : "justify-between"}`}>
        {top.map((symbol, i) => (
          <div
            key={i}
            className={`${symbol[0] == "R" ? "bg-[#e4869377]" : symbol[0] == "G" ? "bg-[#bbe4867a]" : "bg-[#86dee472]"} w-3 h-3 rounded-full`}></div>
        ))}
      </div>
      <div className={`px-1 flex gap-1 items-center ${bottom.length === 1 ? "justify-center" : "justify-between"}`}>
        {bottom.map((symbol, i) => (
          <div
            key={i}
            className={`${symbol[0] == "R" ? "bg-[#e4869377]" : symbol[0] == "G" ? "bg-[#bbe4867a]" : "bg-[#86dee472]"} w-3 h-3 rounded-full`}></div>
        ))}
      </div>
    </div>
  )
}
