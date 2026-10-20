// Login.jsx — the sign-in screen.
//
// Fields: username and password only.
// The role is NOT chosen here — the backend determines it from the USERS
// dict (alice = developer, bob = admin) and embeds it in the JWT.
//
// On success: stores the token via auth.js, updates AuthContext,
//             redirects to wherever the user was trying to go (or "/").
// On failure: shows the server's error message inline.

import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router';
import { login } from '../api/auth';
import { useAuth } from '../App';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]       = useState('');
  const [loading, setLoading]   = useState(false);

  const { setUser } = useAuth();
  const navigate    = useNavigate();
  const location    = useLocation();
  // Redirect back to the page the user tried to visit before being sent to login
  const from = location.state?.from?.pathname ?? '/';

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const user = await login(username, password);
      setUser(user);               // write role + username into AuthContext
      navigate(from, { replace: true });
    } catch (err) {
      // Show the backend's detail message if available, otherwise generic
      setError(err.response?.data?.detail ?? 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        {/* Brand header */}
        <div style={styles.brand}>
          <span style={styles.shield}>&#128737;</span>
          <h1 style={styles.title}>Sovereign AI</h1>
        </div>

        <form onSubmit={handleSubmit} style={styles.form}>
          <div className="form-group">
            <label className="form-label" htmlFor="username">Username</label>
            <input
              id="username"
              className={`form-input${error ? ' error' : ''}`}
              type="text"
              placeholder="e.g. alice"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoFocus
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <input
              id="password"
              className={`form-input${error ? ' error' : ''}`}
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>

          {error && (
            <p style={styles.errorMsg} role="alert">{error}</p>
          )}

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginTop: 4 }}
            disabled={loading}
          >
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>

        <p style={styles.hint}>Demo: alice / bob (passwords set in .env)</p>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'var(--color-bg)',
    padding: 16,
  },
  card: {
    background: 'var(--color-surface)',
    border: '1px solid var(--color-border)',
    borderRadius: 12,
    padding: '32px 28px',
    width: '100%',
    maxWidth: 380,
    boxShadow: '0 4px 16px rgba(0,0,0,0.07)',
  },
  brand: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    marginBottom: 24,
  },
  shield: { fontSize: 28 },
  title: { fontSize: '1.375rem', fontWeight: 700, color: 'var(--color-primary)' },
  form: { display: 'flex', flexDirection: 'column', gap: 16 },
  errorMsg: {
    fontSize: '0.8125rem',
    color: 'var(--color-danger)',
    background: '#fee2e2',
    borderRadius: 6,
    padding: '8px 12px',
  },
  hint: {
    marginTop: 20,
    textAlign: 'center',
    fontSize: '0.75rem',
    color: 'var(--color-text-muted)',
  },
};
