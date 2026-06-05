import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../utils/api";
import Navbar from "../components/Navbar";

export default function Report() {
  const { id } = useParams();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await api.get(`/history/${id}`);
        setData(res.data);
      } catch (err) {
        setData(null);
      }
    };

    load();
  }, [id]);

  if (!data) {
    return (
      <div className="p-6 text-white">
        Loading report...
      </div>
    );
  }

  const analysis = data.analysis_result || {
    summary: "No data available",
    issues: []
  };

  return (
    <div>
      <Navbar />

      <div className="p-6 text-white">
        <div className="bg-slate-900 p-4 rounded mb-6">
          <h1 className="text-xl font-bold">
            Cost Analysis Report
          </h1>

          <p>Resource Group: {data.resource_group}</p>
          <p>Resources: {data.resources_scanned}</p>
          <p>Issues: {data.issues_found}</p>
          <p className="text-green-400">
            Savings: {data.estimated_savings}
          </p>
        </div>

        <div className="bg-slate-900 p-4 rounded mb-6">
          <h2 className="font-bold mb-2">Summary</h2>
          <p>{analysis.summary}</p>
        </div>

        {analysis.issues && analysis.issues.length > 0 ? (
          analysis.issues.map((issue: any, i: number) => (
            <div key={i} className="bg-slate-900 p-4 rounded mb-4">
              <h3 className="font-bold">
                {issue.resource_name}
              </h3>

              <p>{issue.description}</p>
            </div>
          ))
        ) : (
          <p className="text-gray-400">
            No issues found 🎉
          </p>
        )}
      </div>
    </div>
  );
}