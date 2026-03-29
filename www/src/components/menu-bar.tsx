import { ArrowLeftIcon, Cog6ToothIcon } from "@heroicons/react/16/solid"

export default function MenuBar({ p1, p2, time, numMoves }: { p1: string; p2: string; time: number; numMoves: number }) {
  const formatTime = (ms: number): string => {
    const totalSeconds = Math.floor(ms / 1000)
    const minutes = Math.floor(totalSeconds / 60)
    const seconds = totalSeconds % 60
    return `${minutes}:${seconds.toString().padStart(2, "0")}`
  }

  const formattedTime = formatTime(time)

  return (
    <div className="px-8 md:px-16">
      <div className="h-16 bg-background grid grid-cols-2">
        <div className="flex items-center gap-4 md:gap-6">
          <button className="p-2 flex items-center gap-2 bg-background2 border border-border-light hover:brightness-125 rounded-lg font-bold uppercase tracking-widest text-xs cursor-pointer duration-150">
            <ArrowLeftIcon className="w-4 h-4" />
            <p className="hidden md:inline">Back</p>
          </button>

          <h1 className="font-bold text-gray-500 text-base whitespace-nowrap">
            {p1} vs {p2}
          </h1>
        </div>

        <div className="flex gap-4 md:gap-6 items-center justify-end">
          <div className="hidden md:inline text-lg font-semibold">{formattedTime}</div>
          <div className="hidden md:inline font-semibold whitespace-nowrap">Moves: {numMoves}</div>
          <button className="p-2 flex items-center gap-2 bg-background2 border border-border-light hover:brightness-125 rounded-lg font-bold uppercase tracking-widest text-xs cursor-pointer duration-150">
            <Cog6ToothIcon className="w-4 h-4" />
            <p className="hidden md:inline">Options</p>
          </button>
        </div>
      </div>
      <div className="md:hidden float-right rounded-lg border border-border-normal py-2 font-semibold flex flex-col gap-1 divide-y divide-border-muted">
        <p className="text-right px-4 pb-1">{formattedTime}</p>
        <p className="text-right px-4">Moves: {numMoves}</p>
      </div>
    </div>
  )
}
