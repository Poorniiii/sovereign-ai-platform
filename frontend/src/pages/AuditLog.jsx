// AuditLog.jsx — admin-only full audit log page.
// Route: /audit  (only reachable by users with role === 'admin')

import { useEffect, useState } from 'react';
import Header from '../components/Header';
import { getAuditLogs } from '../api/workflow';

export default function AuditLog() {
  const [logs, setLogs]       = useState([]);
  const [total, setTotal]     = useState(0);
  const [offset, setOffset]   = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');
  const LIMIT = 50;

  useEffect(() => {
    setLoading(true);
    setError('');
    getAuditLogs(LIMIT, offset)
      .then((data) => {
        setLogs(data.items || []);
        setTotal(data.total || 0);
      })
      .catch(() => setError('Could not load audit logs. Is the backend running?'))
      .finally(() => setLoading(false));
  }, [offset]);

  return (
    <div style={styles.page}>
      <Header />

      <div style={styles.content}>
        <div style={styles.titleRow}>
          <h2 style={{ margin: 0 }}>Audit Log</h2>
          <span className="text-muted text-sm">
            {total > 0 ? `${total} total entries` : ''}
          </span>
        </div>

        {error && (
          <p style={styles.errorMsg}>{error}</p>
        )}

        {loading && (
          <p className="text-muted text-sm" style={{ padding: '20px 0' }}>Loading…</p>
        )}

        {!loading && logs.length === 0 && !error && (
          <p className="text-muted text-sm" style={{ padding: '20px 0' }}>No audit entries found.</p>
        )}

        {logs.length > 0 && (
          <>
            <div style={{ overflowX: 'auto' }}>
              <table style={styles.table}>
                <thead>
                  <tr>
                    {['Timestamp', 'User', 'Role', 'Workflow ID', 'Action', 'Policy Decision', 'Execution Status', 'Agent Output'].map(h => (
                      <th key={h} style={styles.th}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {logs.map((entry, i) => (
                    <tr key={i} style={i % 2 === 0 ? styles.rowEven : {}}>
                      <td style={styles.td}>
                        {new Date(entry.timestamp).toLocaleString()}
                      </td>
                      <td style={styles.td}>{entry.user}</td>
                      <td style={styles.td}>
                        <span className={`badge ${entry.role === 'admin' ? 'badge-running' : 'badge-complete'}`}>
                          {entry.role}
                        </span>
                      </td>
                      <td style={{ ...styles.td, fontFamily: 'monospace', fontSize: '0.7rem' }}>
                        {entry.workflow_id || '—'}
                      </td>
                      <td style={styles.td}>{entry.action}</td>
                      <td style={styles.td}>
                        <span className={`badge ${entry.policy_decision === 'allow' ? 'badge-complete' : 'badge-error'}`}>
                          {entry.policy_decision}
                        </span>
                      </td>
                      <td style={styles.td}>{entry.execution_status || '—'}</td>
                      <td style={styles.td}>{entry.agent_output || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div style={styles.pagination}>
              <button
                className="btn btn-outline"
                onClick={() => setOffset(Math.max(0, offset - LIMIT))}
                disabled={offset === 0}
              >
                ← Previous
              </button>
              <span className="text-muted text-sm">
                {offset + 1}–{Math.min(offset + LIMIT, total)} of {total}
              </span>
              <button
                className="btn btn-outline"
                onClick={() => setOffset(offset + LIMIT)}
                disabled={offset + LIMIT >= total}
              >
                Next →
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

const styles = {
  page: { minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--color-bg)' },
  content: { padding: 24, flex: 1 },
  titleRow: {
    display: 'flex', alignItems: 'baseline', gap: 12,
    marginBottom: 16,
  },
  errorMsg: {
    color: 'var(--color-danger)',
    background: '#fee2e2',
    borderRadius: 6,
    padding: '8px 12px',
    fontSize: '0.875rem',
  },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: '0.75rem', background: 'var(--color-surface)' },
  th: {
    textAlign: 'left', padding: '8px 10px',
    borderBottom: '2px solid var(--color-border)',
    color: 'var(--color-text-muted)', fontWeight: 600, whiteSpace: 'nowrap',
    background: 'var(--color-surface)',
  },
  td: { padding: '8px 10px', borderBottom: '1px solid var(--color-border)', verticalAlign: 'top' },
  rowEven: { background: 'var(--color-bg)' },
  pagination: {
    display: 'flex', alignItems: 'center', gap: 12,
    marginTop: 16, justifyContent: 'flex-end',
  },
};
