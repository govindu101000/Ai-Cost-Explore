import React, { useEffect, useState } from "react";
import ProgressTracker from "../components/ProgressTracker";

function authFetch(input: RequestInfo, init?: RequestInit) {
  const token = localStorage.getItem("token");
  const headers = Object.assign({}, init?.headers || {}, { Authorization: `Bearer ${token}` });
  return fetch(input, Object.assign({}, init || {}, { headers }));
}

export default function Dashboard() {
  const [rgs, setRgs] = useState<string[]>([]);
  const [selected, setSelected] = useState("");
  const [messages, setMessages] = useState<string[]>([]);
  const [analysisId, setAnalysisId] = useState<number | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);

  useEffect(() => {
    (async () => {
      const res = await authFetch("/api/resource-groups");
      if (res.ok) {
        const data = await res.json();
        setRgs(data.resource_groups.map((g: any) => g.name));
        if (data.resource_groups.length) setSelected(data.resource_groups[0].name);
      } else {
        console.error("Failed to load resource groups");
      }
    })();
  }, []);

  const runAnalysis = async () => {
    setMessages([]);
    setAnalysis(null);
    const res = await authFetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resource_group: selected }),
    });
    const data = await res.json();
    if (res.ok) {
      setAnalysisId(data.analysis_id);
      const ws = new WebSocket(`ws://localhost:8000/ws/progress/${data.analysis_id}`);
      ws.onmessage = (ev) => {
        setMessages((m) => [...m, ev.data]);
        if (ev.data === "Analysis complete") {
          ws.close();
          // fetch history and show the analysis details
          (async () => {
            const hr = await authFetch("/api/history");
            if (hr.ok) {
              const json = await hr.json();
              const found = json.history.find((h: any) => h.id === data.analysis_id);
              setAnalysis(found || null);
            }
          })();
        }
      };
    } else {
      alert(data.detail || "Failed to start analysis");
    }
  };

  return (
    <div>
      <div className="mb-4">
        <label className="block text-sm mb-1">Resource Group</label>
        <select className="p-2 bg-gray-800 rounded w-full" value={selected} onChange={(e) => setSelected(e.target.value)}>
          {rgs.map((rg) => (
            <option key={rg} value={rg}>{rg}</option>
          ))}
        </select>
      </div>
      <div>
        <button className="px-4 py-2 bg-green-600 rounded" onClick={runAnalysis}>Run Analysis</button>
      </div>

      <ProgressTracker messages={messages} />

      {analysis && (
        <div className="mt-4 p-4 bg-gray-800 rounded">
          <h3 className="font-semibold">Analysis Result</h3>
          <pre className="text-sm mt-2 overflow-auto max-h-64">{JSON.stringify(analysis, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
