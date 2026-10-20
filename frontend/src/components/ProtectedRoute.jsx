// ProtectedRoute.jsx — wraps any route that requires authentication.
//
// If the user has no JWT token stored, they are redirected to /login.
// The current URL is passed as ?next= so Login can redirect back after
// a successful sign-in.
//
// Usage in App.jsx:
//   <Route path="/" element={<ProtectedRoute><WorkflowCanvas /></ProtectedRoute>} />

import { Navigate, useLocation } from 'react-router';
import { getToken } from '../api/auth';

export default function ProtectedRoute({ children }) {
  const location = useLocation();
  const token = getToken();

  if (!token) {
    // Preserve the URL the user was trying to reach so we can redirect
    // back after a successful login.
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}
