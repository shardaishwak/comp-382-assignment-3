import type { Domino } from "@/app/lib/types"

export default function Domino({ dominoId, top, bottom }: Domino) {
  return (
    <div className="min-w-20 min-h-28 rounded-xl bg-white p-2 grid grid-rows-2 divide-y divide-solid divide-mist-300 border border-b-4 border-mist-300 hover:-translate-y-2 duration-150">
      <div className={`px-1 flex gap-1 items-center ${top.length === 1 ? "justify-center" : "justify-between"}`}>
        {top.map((symbol, i) => (
          <div
            key={i}
            className={`${symbol[0] == "R" ? "bg-[#e48693]" : symbol[0] == "G" ? "bg-[#bbe486]" : "bg-[#86dee4]"} w-3 h-3 rounded-full `}></div>
        ))}
      </div>
      <div className={`px-1 flex gap-1 items-center ${bottom.length === 1 ? "justify-center" : "justify-between"}`}>
        {bottom.map((symbol, i) => (
          <div
            key={i}
            className={`${symbol[0] == "R" ? "bg-[#e48693]" : symbol[0] == "G" ? "bg-[#bbe486]" : "bg-[#86dee4]"} w-3 h-3 rounded-full `}></div>
        ))}
      </div>
    </div>
  )
}
