import { useState } from "react";
import api from "../utils/api";
import { saveToken } from "../utils/auth";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const nav = useNavigate();

  const login = async () => {
    try {
      setError("");

      const res = await api.post("/auth/login", {
        email,
        password,
      });

      saveToken(res.data.token);
      nav("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Login failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-black text-white">

      {/* Background glow */}
      <div className="absolute w-[500px] h-[500px] bg-blue-600 opacity-20 blur-3xl rounded-full top-10 left-10"></div>
      <div className="absolute w-[400px] h-[400px] bg-purple-600 opacity-20 blur-3xl rounded-full bottom-10 right-10"></div>

      {/* Card */}
      <div className="relative w-[420px] p-8 rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-slate-700 shadow-2xl">

        {/* Header */}
        <h1 className="text-3xl font-bold text-center text-white">
          AI Cost Detective
        </h1>

        <p className="text-center text-slate-400 mt-2 text-sm">
          Enterprise Cloud Cost Intelligence Platform
        </p>

        {/* Error */}
        {error && (
          <div className="mt-4 p-2 bg-red-500/20 border border-red-500 text-red-300 text-sm rounded">
            {error}
          </div>
        )}

        {/* Email */}
        <div className="mt-6">
          <label className="text-sm text-slate-300">Email</label>
          <input
            className="w-full mt-1 p-3 rounded-lg bg-slate-800 text-white border border-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        {/* Password */}
        <div className="mt-4">
          <label className="text-sm text-slate-300">Password</label>
          <input
            type="password"
            className="w-full mt-1 p-3 rounded-lg bg-slate-800 text-white border border-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        {/* Button */}
        <button
          onClick={login}
          className="w-full mt-6 bg-blue-600 hover:bg-blue-700 transition-all py-3 rounded-lg font-semibold shadow-lg"
        >
          Sign In
        </button>

        {/* Footer */}
        <p className="text-center text-xs text-slate-500 mt-4">
          Secure authentication powered by JWT
        </p>
      </div>
    </div>
  );
}