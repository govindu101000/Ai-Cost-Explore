import { useEffect, useState } from "react";
import api from "../utils/api";
import Navbar from "../components/Navbar";
import ProgressTracker from "../components/ProgressTracker";
import { createSocket } from "../utils/websocket";
import { v4 as uuidv4 } from "uuid";

export default function Dashboard() {
  const [resourceGroups, setResourceGroups] = useState<any[]>([]);
  const [selectedRG, setSelectedRG] = useState("");
  const [analysisId, setAnalysisId] = useState("");
  const [progress, setProgress] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadRG = async () => {
      try {
        const res = await api.get("/resource-groups");
        setResourceGroups(res.data.resource_groups || []);
      } catch (err) {
        console.error("Failed to load RGs", err);
        setResourceGroups([]);
      }
    };

    loadRG();
  }, []);

  const runAnalysis = async () => {
    const id = uuidv4();

    setAnalysisId(id);
    setProgress([]);
    setLoading(true);

    const ws = createSocket(id);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProgress((prev) => [...prev, data.message]);
    };

    ws.onopen = async () => {
      await api.post("/analyze", {
        resource_group: selectedRG,
        analysis_id: id,
      });
    };

    ws.onclose = () => setLoading(false);
  };

  return (
    <div>
      <Navbar />

      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">Dashboard</h1>

        <div className="mb-4">
          <label className="block mb-2">Select Resource Group</label>

          <select
            className="p-2 border rounded text-black w-64"
            onChange={(e) => setSelectedRG(e.target.value)}
          >
            <option value="">Select</option>
            {resourceGroups.map((rg) => (
              <option key={rg.name} value={rg.name}>
                {rg.name}
              </option>
            ))}
          </select>
        </div>

        <button
          disabled={!selectedRG || loading}
          onClick={runAnalysis}
          className="bg-blue-600 px-4 py-2 rounded text-white"
        >
          {loading ? "Analyzing..." : "Run Analysis"}
        </button>

        {progress.length > 0 && (
          <ProgressTracker messages={progress} />
        )}
      </div>
    </div>
  );
}