export default function Button({ children, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      {...props}
      className="p-2 flex items-center gap-2 bg-background2 border border-border-normal hover:border-border-light rounded-lg font-bold uppercase tracking-widest text-xs cursor-pointer duration-150">
      {children}
    </button>
  )
}
