import { useEffect, useState } from "react";
import api from "../utils/api";
import Navbar from "../components/Navbar";
import { useNavigate } from "react-router-dom";

export default function History() {
  const [history, setHistory] = useState<any[]>([]);
  const nav = useNavigate();

  useEffect(() => {
    const load = async () => {
      const res = await api.get("/history");
      setHistory(res.data);
    };

    load();
  }, []);

  return (
    <div>
      <Navbar />

      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">
          Analysis History
        </h1>

        <div className="space-y-4">
          {history.map((item) => (
            <div
              key={item.id}
              className="p-4 bg-slate-900 rounded border border-slate-800"
            >
              <h2 className="font-bold">
                {item.resource_group}
              </h2>

              <p>Issues: {item.issues_found}</p>
              <p>Savings: {item.estimated_savings}</p>
              <p>Date: {item.created_at}</p>

              <button
                className="mt-2 bg-blue-600 px-3 py-1 rounded"
                onClick={() =>
                  nav(`/report/${item.id}`)
                }
              >
                View Report
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}