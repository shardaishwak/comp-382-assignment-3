import { useRef } from "react"
import { useDraggable } from "@dnd-kit/react"
import type { Domino as DominoType } from "@/app/lib/types"
import Domino from "./domino"

export default function TrayDomino({ id, top, bottom, isHint = false, onClick, disabled = false }: DominoType & { isHint?: boolean; onClick?: () => void; disabled?: boolean }) {
  const { ref } = useDraggable({ id: id, feedback: "clone", disabled })
  const pointerStart = useRef({ x: 0, y: 0 })

  return (
    <div
      ref={ref}
      onPointerDownCapture={(e) => {
        pointerStart.current = { x: e.clientX, y: e.clientY }
      }}
      onPointerUpCapture={(e) => {
        if (disabled || !onClick) return
        const dx = Math.abs(e.clientX - pointerStart.current.x)
        const dy = Math.abs(e.clientY - pointerStart.current.y)
        if (dx < 5 && dy < 5) onClick()
      }}
      className={`${onClick && !disabled ? "cursor-pointer" : ""} ${disabled && !isHint ? "opacity-50" : ""} ${disabled ? "pointer-events-none" : ""}`}
    >
      <Domino id={id} top={top} bottom={bottom} isHint={isHint} />
    </div>
  )
}
