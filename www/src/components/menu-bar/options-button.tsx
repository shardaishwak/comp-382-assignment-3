import { Cog6ToothIcon } from "@heroicons/react/16/solid"
import { useState } from "react"
import Button from "./button"
import soundEffect from "@/app/lib/sound"

export default function OptionsButton({
  onRequestHints,
}: {
  onRequestHints?: () => void
}) {
  const [open, setOpen] = useState<boolean>(false)

  return (
    <div className="relative">
      <Button onClick={() => setOpen(!open)}>
        <Cog6ToothIcon className="w-4 h-4" />
        <p className="hidden md:inline">Options</p>
      </Button>
      {open && (
        <ul className="z-10 absolute top-12 right-0 bg-background border border-border-light rounded-lg divide-y divide-border-normal text-sm">
          {onRequestHints && (
            <li className="px-4 py-2">
              <button
                onClick={() => {
                  soundEffect.tick()
                  onRequestHints()
                  setOpen(false)
                }}
                className="hover:text-gray-300 duration-150"
              >
                Get Hints
              </button>
            </li>
          )}
        </ul>
      )}
    </div>
  )
}
