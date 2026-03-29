export default function ProgressBar({ top, bottom }: { top: number; bottom: number }) {
  return (
    <div className="w-full">
      <div className="flex h-2 rounded-full overflow-hidden divide-x divide-border-light">
        <div className="flex-1 bg-border-normal overflow-hidden">
          <div className="h-full bg-[#86dee472] rounded-l-full float-right" style={{ width: `${bottom}%` }}></div>
        </div>
        <div className="flex-1 bg-border-normal overflow-hidden">
          <div className="h-full bg-[#e4869377] rounded-r-full" style={{ width: `${top}%` }}></div>
        </div>
      </div>
      <div className="mt-1 flex justify-between">
        <p className="text-xs">bottom</p>
        <p className="text-xs">top</p>
      </div>
    </div>
  )
}
