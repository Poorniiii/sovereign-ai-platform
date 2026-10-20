// Header.jsx — the top navigation bar shown on every authenticated page.
//
// Displays:
//   - The Sovereign AI brand (shield icon + name)
//   - The logged-in user's role as a badge (developer / admin)
//   - A Logout button that clears the token and redirects to /login

import { useNavigate, useLocation, Link } from 'react-router';
import { useAuth } from '../App';
import { logout } from '../api/auth';

export default function Header() {
  const { user, setUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  function handleLogout() {
    logout();
    setUser(null);
    navigate('/login', { replace: true });
  }

  return (
    <header style={styles.header}>
      <div style={styles.left}>
        <div style={styles.brand}>
          <span style={styles.shield}>&#128737;</span>
          <Link to="/" style={styles.brandText}>Sovereign AI</Link>
        </div>
        {user?.role === 'admin' && (
          <nav style={styles.nav}>
            <Link
              to="/"
              style={{
                ...styles.navLink,
                ...(location.pathname === '/' ? styles.navLinkActive : {}),
              }}
            >
              Workflow
            </Link>
            <Link
              to="/audit"
              style={{
                ...styles.navLink,
                ...(location.pathname === '/audit' ? styles.navLinkActive : {}),
              }}
            >
              Audit Log
            </Link>
          </nav>
        )}
      </div>
      <div style={styles.right}>
        {user && (
          <span
            className={`badge ${user.role === 'admin' ? 'badge-running' : 'badge-complete'}`}
            style={{ marginRight: 12 }}
          >
            {user.role}
          </span>
        )}
        <button className="btn btn-outline" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </header>
  );
}

const styles = {
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 24px',
    height: 56,
    background: 'var(--color-surface)',
    borderBottom: '1px solid var(--color-border)',
    position: 'sticky',
    top: 0,
    zIndex: 100,
  },
  left: { display: 'flex', alignItems: 'center', gap: 32 },
  brand: { display: 'flex', alignItems: 'center', gap: 8 },
  shield: { fontSize: 20 },
  brandText: { fontWeight: 700, fontSize: '1rem', color: 'var(--color-primary)', textDecoration: 'none' },
  nav: { display: 'flex', gap: 4 },
  navLink: {
    padding: '4px 12px',
    borderRadius: 6,
    fontSize: '0.875rem',
    fontWeight: 500,
    color: 'var(--color-text-muted)',
    textDecoration: 'none',
  },
  navLinkActive: {
    background: 'var(--color-primary)',
    color: '#fff',
  },
  right: { display: 'flex', alignItems: 'center' },
};
