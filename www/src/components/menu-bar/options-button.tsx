import { Cog6ToothIcon } from "@heroicons/react/16/solid"
import { useState } from "react"
import Button from "./button"

export default function OptionsButton() {
  const [open, setOpen] = useState<boolean>(false)
  const [hint, setHint] = useState<boolean>(false)

  return (
    <div className="relative">
      <Button onClick={() => setOpen(!open)}>
        <Cog6ToothIcon className="w-4 h-4" />
        <p className="hidden md:inline">Options</p>
      </Button>
      {open && (
        <ul className="z-10 absolute top-12 right-0 bg-background border border-border-light rounded-lg divide-y divide-border-normal text-sm">
          <li className="px-4 py-2 flex gap-3 items-center">
            <input onChange={() => setHint(!hint)} className="accent-[#447d8a]" type="checkbox" checked={hint} />
            Hints
          </li>
        </ul>
      )}
    </div>
  )
}
