import { Routes, Route, Navigate } from "react-router-dom";
import AttendanceCapture from "./components/AttendanceCapture";
import UserRegistration  from "./components/UserRegistration";
import { AuthProvider, useAuth } from "./context/AuthContext";

// Guard: redirects to "/" if not admin, preserving clean UX
const AdminRoute = ({ children }) => {
  const { isAdmin } = useAuth();
  return isAdmin ? children : <Navigate to="/" replace />;
};

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/"         element={<AttendanceCapture />} />
        <Route path="/register" element={
          <AdminRoute>
            <UserRegistration />
          </AdminRoute>
        }/>
      </Routes>
    </AuthProvider>
  );
}
