interface Props {
  messages: string[];
}

export default function ProgressTracker({
  messages
}: Props) {
  return (
    <div className="mt-4 p-4 bg-slate-900 rounded">
      <h2 className="font-bold mb-2">
        Live Progress
      </h2>

      <ul className="space-y-2">
        {messages.map((msg, i) => (
          <li key={i} className="text-green-400">
            ✓ {msg}
          </li>
        ))}
      </ul>
    </div>
  );
}