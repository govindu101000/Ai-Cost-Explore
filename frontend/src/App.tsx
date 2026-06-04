import React from "react";
import Login from "./pages/Login";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="max-w-3xl mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">AI Cloud Cost Detective</h1>
        <Login />
      </div>
    </div>
  );
}
