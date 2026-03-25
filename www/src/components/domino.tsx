import type { Domino } from "@/app/lib/types"

export default function Domino({ id, top, bottom }: Domino) {
  return (
    <div className="w-24 h-36 rounded-xl bg-white p-2 grid grid-rows-2 divide-y divide-solid divide-mist-300 border border-b-4 border-mist-300 hover:-translate-y-2 duration-150">
      <div className="px-2 flex gap-2 justify-between items-center">
        {top.map((symbol, i) => (
          <div
            key={i}
            className={`${symbol[0] == "R" ? "bg-[#e48693]" : symbol[0] == "G" ? "bg-[#bbe486]" : "bg-[#86dee4]"} w-4 h-4 rounded-full `}></div>
        ))}
      </div>
      <div className="px-2 flex gap-2 justify-between items-center">
        {bottom.map((symbol, i) => (
          <div
            key={i}
            className={`${symbol[0] == "R" ? "bg-[#e48693]" : symbol[0] == "G" ? "bg-[#bbe486]" : "bg-[#86dee4]"} w-4 h-4 rounded-full `}></div>
        ))}
      </div>
    </div>
  )
}
