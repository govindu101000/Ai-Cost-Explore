import { logout } from "../utils/auth";
import { useNavigate } from "react-router-dom";

export default function Navbar() {
  const nav = useNavigate();

  const handleLogout = () => {
    logout();
    nav("/");
  };

  return (
    <div className="flex justify-between p-4 bg-slate-900 border-b border-slate-800">
      <h1 className="text-lg font-bold">
        AI Cost Detective
      </h1>

      <div className="flex gap-4">
        <button onClick={() => nav("/dashboard")}>
          Dashboard
        </button>

        <button onClick={() => nav("/history")}>
          History
        </button>

        <button onClick={handleLogout}>
          Logout
        </button>
      </div>
    </div>
  );
}