import soundEffect from "@/app/lib/sound"

export default function Button({ children, onClick, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      {...props}
      onClick={(e) => {
        soundEffect.tick()
        onClick?.(e)
      }}
      className="p-2 flex items-center gap-2 bg-background2 border border-border-normal hover:border-border-light rounded-lg font-bold uppercase tracking-widest text-xs cursor-pointer duration-150">
      {children}
    </button>
  )
}
