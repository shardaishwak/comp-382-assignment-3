import { useDraggable } from "@dnd-kit/react"

export default function OptionDomino({
  id,
  n,
  text = "",
  opacity = false,
  disabled = false
}: {
  id: string
  n: number
  text?: string
  opacity?: boolean
  disabled?: boolean
}) {
  const { ref } = useDraggable({ id: id, disabled: disabled })

  return (
    <div
      ref={ref}
      className={`relative brightness-115 w-20 h-28 rounded-xl p-2 flex items-center justify-center border border-b-4 ${!disabled && "hover:-translate-y-2"} ${opacity && "opacity-50"} duration-150 bg-background2 border-border-normal`}>
      {n === 1 ? (
        <div className="px-1 flex items-center justify-center">
          <div className="bg-[#e4869377] w-3 h-3 rounded-full"></div>
        </div>
      ) : (
        <div className="w-full px-1 flex items-center justify-between">
          <div className="bg-[#e4869377] w-3 h-3 rounded-full"></div>
          <div className="bg-[#86dee472] w-3 h-3 rounded-full"></div>
          {n === 3 && <div className="bg-[#bbe4867a] w-3 h-3 rounded-full"></div>}
        </div>
      )}
      <p className="absolute bottom-2 left-0 w-full text-center text-xs">{text}</p>
    </div>
  )
}
