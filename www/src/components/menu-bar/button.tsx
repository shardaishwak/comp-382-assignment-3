import soundEffect from "@/app/lib/sound"

export default function Button({
  children,
  onClick,
  disabled = false,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      {...props}
      onClick={(e) => {
        soundEffect.tick()
        onClick?.(e)
      }}
      className={`p-2 flex items-center gap-2 bg-background2 border border-border-normal ${!disabled && "hover:border-border-light"} ${disabled && "opacity-50"} rounded-lg font-bold uppercase tracking-widest text-xs cursor-pointer duration-150`}
      disabled={disabled}>
      {children}
    </button>
  )
}
