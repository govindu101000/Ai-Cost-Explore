import { useState } from "react";
import api from "../utils/api";
import { saveToken } from "../utils/auth";
import { useNavigate } from "react-router-dom";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const nav = useNavigate();

  const signup = async () => {
    const res = await api.post("/auth/signup", {
      email,
      password
    });

    saveToken(res.data.token);

    nav("/dashboard");
  };

  return (
    <div className="p-10">
      <h1>Signup</h1>

      <input onChange={(e) => setEmail(e.target.value)} />
      <input onChange={(e) => setPassword(e.target.value)} />

      <button onClick={signup}>
        Create Account
      </button>
    </div>
  );
}