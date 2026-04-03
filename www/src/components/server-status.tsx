"use client"

import { useEffect, useState } from "react"
import { SOCKET_URL } from "@/app/lib/constants"

export default function ServerStatus() {
  const [online, setOnline] = useState(false)

  useEffect(() => {
    let mounted = true
    const ping = () => {
      fetch(`${SOCKET_URL}/health`, { mode: "cors", referrerPolicy: "no-referrer" })
        .then((r) => { if (mounted) setOnline(r.ok) })
        .catch(() => { if (mounted) setOnline(false) })
    }
    ping()
    const id = setInterval(ping, 5000)
    return () => { mounted = false; clearInterval(id) }
  }, [])

  return (
    <div className="fixed bottom-4 right-4 z-50" title={online ? "Server online" : "Server offline"}>
      <span
        className={`block w-3 h-3 rounded-full ${online ? "bg-green-500 animate-pulse" : "bg-red-500"}`}
      />
    </div>
  )
}
