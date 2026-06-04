export function TypingIndicator({ text }: { text: string }) {
  return (
    <div className="flex items-center gap-3 px-4 py-3">
      <div className="flex gap-1">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-2 h-2 rounded-full bg-orange-400 animate-bounce"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </div>
      <span className="text-sm text-gray-400 italic">{text}</span>
    </div>
  )
}
