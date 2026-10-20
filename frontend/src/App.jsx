// App.jsx — application root.
//
// Two responsibilities:
//   1. Provide AuthContext — a React context that holds the logged-in
//      user (username + role) and a setter. Components read from this
//      instead of touching localStorage directly.
//
//   2. Define the three routes:
//      /login            → Login page (public)
//      /                 → WorkflowCanvas (protected)
//      /results/:id      → ExecutionResults (protected)
//
//      ProtectedRoute wraps the two authenticated routes; if there is
//      no token it redirects to /login.
//
// useAuth() is exported so any component can consume the context
// without importing the context object directly.

import { createContext, useContext, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router';

import Login              from './pages/Login';
import WorkflowCanvas     from './pages/WorkflowCanvas';
import ExecutionResults   from './pages/ExecutionResults';
import AuditLog           from './pages/AuditLog';
import ProtectedRoute     from './components/ProtectedRoute';
import { getStoredUser }  from './api/auth';

// ── Auth Context ─────────────────────────────────────────────────
// Default value is null — no user logged in.
const AuthContext = createContext(null);

/** Hook for any component to read { user, setUser } */
export function useAuth() {
  return useContext(AuthContext);
}

/** Redirects non-admins away from admin-only routes */
function AdminRoute({ children }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== 'admin') return <Navigate to="/" replace />;
  return children;
}

// ── App ──────────────────────────────────────────────────────────
export default function App() {
  // On first render, try to restore user info from the stored JWT
  // so a page refresh doesn't log the user out.
  const [user, setUser] = useState(() => getStoredUser());

  return (
    <AuthContext.Provider value={{ user, setUser }}>
      <BrowserRouter>
        <Routes>
          {/* Public route */}
          <Route path="/login" element={<Login />} />

          {/* Protected routes — redirect to /login if no token */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <WorkflowCanvas />
              </ProtectedRoute>
            }
          />
          <Route
            path="/results/:workflowId"
            element={
              <ProtectedRoute>
                <ExecutionResults />
              </ProtectedRoute>
            }
          />

          {/* Admin-only route */}
          <Route
            path="/audit"
            element={
              <AdminRoute>
                <AuditLog />
              </AdminRoute>
            }
          />

          {/* Catch-all — redirect unknown URLs to canvas */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthContext.Provider>
  );
}

