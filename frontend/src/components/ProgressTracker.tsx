import React from "react";

export default function ProgressTracker({ messages }: { messages: string[] }) {
  return (
    <div className="mt-4 p-3 bg-gray-800 rounded">
      <h3 className="font-semibold mb-2">Progress</h3>
      <ul className="space-y-1 text-sm">
        {messages.map((m, i) => (
          <li key={i} className="opacity-90">{m}</li>
        ))}
      </ul>
    </div>
  );
}
