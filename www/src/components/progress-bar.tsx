export default function ProgressBar({ progress }: { progress: number }) {
  return (
    <div className="w-full">
      <div className="h-2 rounded-full bg-border-normal overflow-hidden">
        <div
          className="h-full bg-[#86dee472] rounded-full duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
      <div className="mt-1 flex justify-between">
        <p className="text-xs">0%</p>
        <p className="text-xs text-gray-400">{progress}% match</p>
        <p className="text-xs">100%</p>
      </div>
    </div>
  )
}
