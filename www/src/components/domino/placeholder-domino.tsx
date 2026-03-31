export default function PlaceholderDomino({ text }: { text: string }) {
  return (
    <div className="relative w-20 h-28 rounded-xl border border-dashed duration-150 border-border-normal text-xs px-2 flex items-center justify-center text-center">
      {text}
    </div>
  )
}
