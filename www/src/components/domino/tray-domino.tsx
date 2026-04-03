import { useRef, useState } from "react"
import { useDraggable } from "@dnd-kit/react"
import type { Domino as DominoType } from "@/app/lib/types"
import Domino from "./domino"

export default function TrayDomino({ id, top, bottom, isHint = false, onClick, disabled = false, onReject }: DominoType & { isHint?: boolean; onClick?: () => void; disabled?: boolean; onReject?: () => void }) {
  const { ref } = useDraggable({ id: id, feedback: "clone", disabled })
  const pointerStart = useRef({ x: 0, y: 0 })
  const [shaking, setShaking] = useState(false)

  const triggerReject = () => {
    if (onReject) onReject()
    setShaking(true)
    setTimeout(() => setShaking(false), 400)
  }

  return (
    <div
      ref={ref}
      onPointerDownCapture={(e) => {
        pointerStart.current = { x: e.clientX, y: e.clientY }
      }}
      onPointerUpCapture={(e) => {
        if (disabled) return
        const dx = Math.abs(e.clientX - pointerStart.current.x)
        const dy = Math.abs(e.clientY - pointerStart.current.y)
        if (dx < 5 && dy < 5) {
          if (onReject && !isHint) {
            triggerReject()
          } else if (onClick) {
            onClick()
          }
        }
      }}
      className={`${onClick && !disabled ? "cursor-pointer" : ""} ${disabled && !isHint ? "opacity-50" : ""} ${disabled ? "pointer-events-none" : ""} ${shaking ? "animate-shake" : ""}`}
    >
      <Domino id={id} top={top} bottom={bottom} isHint={isHint} />
    </div>
  )
}
