export default function ProgressBar({ top, bottom }: { top: number; bottom: number }) {
  return (
    <div className="w-full">
      <div className="flex h-2 rounded-full overflow-hidden divide-x divide-border-light">
        <div className="flex-1 bg-border-normal overflow-hidden">
          <div className={`w-[${bottom}%] h-full bg-[#86dee472] rounded-l-full float-right`}></div>
        </div>
        <div className="flex-1 bg-border-normal overflow-hidden">
          <div className={`w-[${top}%] h-full bg-[#e4869377] rounded-r-full`}></div>
        </div>
      </div>
      <div className="mt-1 flex justify-between">
        <p className="text-xs">bottom</p>
        <p className="text-xs">top</p>
      </div>
    </div>
  )
}
