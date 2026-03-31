import OptionDomino from "../domino/option-domino"

export default function OptionsGroup({
  title,
  options
}: {
  title: string
  options: { id: string; n: number; text: string }[]
}) {
  return (
    <div className="w-full flex flex-col">
      <div className="self-start -mb-px rounded-xl rounded-b-none border border-border-normal p-2 text-xs uppercase font-bold tracking-widest">
        {title}
      </div>
      <div className="w-full min-h-24 p-2 flex flex-row gap-2 overflow-x-scroll border border-border-normal rounded-xl rounded-tl-none duration-150">
        {options?.map((op, i) => (
          <OptionDomino key={i} id={op.id} n={op.n} text={op.text} />
        ))}
      </div>
    </div>
  )
}
