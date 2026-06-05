import { Navigate } from "react-router-dom";
import { isAuthenticated } from "../utils/auth";

export default function ProtectedRoute({
  children
}: any) {
  if (!isAuthenticated()) {
    return <Navigate to="/" />;
  }

  return children;
}