// ExecutionResults.jsx — shows the result of a completed workflow run.
//
// URL: /results/:workflowId
//
// The result payload was stored in location.state by WorkflowCanvas after
// graph.invoke() returned. We read it from there so we don't need
// a separate GET /workflow/:id endpoint.
//
// Left panel:  Agent Output — the LLM's full answer + confidence score
// Right panel: Evidence Log — recent audit entries from GET /audit/logs

import { useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router';
import Header from '../components/Header';
import { getAuditLogs } from '../api/workflow';
import { useAuth } from '../App';

export default function ExecutionResults() {
  const { workflowId }       = useParams();
  const location             = useLocation();
  const navigate             = useNavigate();
  const { user }             = useAuth();
  const result               = location.state?.result;  // passed by WorkflowCanvas
  const [logs, setLogs]      = useState([]);
  const [logsError, setLogsError] = useState('');

  // Admins can see audit logs; developers see a 403 from the backend.
  useEffect(() => {
    if (user?.role === 'admin') {
      getAuditLogs(20)
        .then((data) => setLogs(data.items || []))
        .catch(() => setLogsError('Could not load audit logs.'));
    }
  }, [user]);

  if (!result) {
    // User navigated directly to this URL without a result in state
    return (
      <div style={{ padding: 40, textAlign: 'center' }}>
        <p className="text-muted">No result found. <button className="btn btn-outline" onClick={() => navigate('/')}>Go back</button></p>
      </div>
    );
  }

  const confidencePct = Math.round((result.confidence ?? 0) * 100);
  const verdictClass  = result.verdict === 'COMPLIANT'
    ? 'badge-complete'
    : result.verdict === 'NON-COMPLIANT'
      ? 'badge-error'
      : 'badge-idle';

  return (
    <div style={styles.page}>
      <Header />

      {/* Workflow metadata bar */}
      <div style={styles.metaBar}>
        <div style={styles.metaItem}>
          <span className="text-muted text-sm">Workflow ID:</span>
          <span className="fw-600">{workflowId}</span>
        </div>
        <div style={styles.metaItem}>
          <span className="text-muted text-sm">User:</span>
          <span className="fw-600">{user?.username}</span>
        </div>
        <span className="badge badge-complete">Completed</span>
        <button className="btn btn-outline" onClick={() => navigate('/')}>New Workflow</button>
      </div>

      <div style={styles.body}>
        {/* ── Left: Agent Output ── */}
        <div className="card" style={styles.outputCard}>
          <div style={styles.outputHeader}>
            <h2>Agent Output</h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className="text-muted text-sm">Confidence</span>
              <span className="fw-600" style={{ fontSize: '1rem' }}>{confidencePct}%</span>
            </div>
          </div>

          <div style={{ marginBottom: 12 }}>
            <span className={`badge ${verdictClass}`} style={{ fontSize: '0.875rem', padding: '4px 14px' }}>
              {result.verdict || 'UNCERTAIN'}
            </span>
          </div>

          <p style={styles.answerText}>{result.answer || 'No answer returned.'}</p>

          {result.retrieved_chunks?.length > 0 && (
            <details style={{ marginTop: 16 }}>
              <summary className="text-sm text-muted" style={{ cursor: 'pointer' }}>
                Evidence chunks ({result.retrieved_chunks.length})
              </summary>
              <div style={styles.chunkList}>
                {result.retrieved_chunks.map((chunk, i) => (
                  <p key={i} style={styles.chunk}>{chunk}</p>
                ))}
              </div>
            </details>
          )}
        </div>

        {/* ── Right: Evidence Log ── */}
        <div className="card" style={styles.logCard}>
          <div style={styles.logHeader}>
            <h2>Evidence Log</h2>
            <span className="text-muted text-sm">Recent actions recorded by agents</span>
          </div>

          {user?.role !== 'admin' && (
            <p className="text-muted text-sm" style={{ marginTop: 8 }}>
              Audit log access requires Admin role.
            </p>
          )}

          {logsError && <p className="text-danger text-sm">{logsError}</p>}

          {logs.length > 0 && (
            <div style={{ overflowX: 'auto' }}>
              <table style={styles.table}>
                <thead>
                  <tr>
                    {['Timestamp', 'User', 'Role', 'Action', 'Policy Decision', 'Agent Output'].map(h => (
                      <th key={h} style={styles.th}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {logs.map((entry, i) => (
                    <tr key={i} style={i % 2 === 0 ? styles.rowEven : {}}>
                      <td style={styles.td}>{new Date(entry.timestamp).toLocaleTimeString()}</td>
                      <td style={styles.td}>{entry.user}</td>
                      <td style={styles.td}>{entry.role}</td>
                      <td style={styles.td}>{entry.action}</td>
                      <td style={styles.td}>
                        <span className={`badge ${entry.policy_decision === 'allow' ? 'badge-complete' : 'badge-error'}`}>
                          {entry.policy_decision}
                        </span>
                      </td>
                      <td style={styles.td}>{entry.agent_output || 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: { minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--color-bg)' },
  metaBar: {
    display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap',
    padding: '12px 24px',
    background: 'var(--color-surface)',
    borderBottom: '1px solid var(--color-border)',
  },
  metaItem: { display: 'flex', flexDirection: 'column', gap: 1 },
  body: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: 20,
    padding: 20,
    flex: 1,
    alignItems: 'start',
  },
  outputCard: { display: 'flex', flexDirection: 'column', gap: 10 },
  outputHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  answerText: { fontSize: '0.875rem', lineHeight: 1.6, color: 'var(--color-text)', whiteSpace: 'pre-wrap' },
  chunkList: { marginTop: 8, display: 'flex', flexDirection: 'column', gap: 8 },
  chunk: {
    fontSize: '0.75rem',
    lineHeight: 1.5,
    background: 'var(--color-bg)',
    borderLeft: '3px solid var(--color-primary)',
    padding: '6px 10px',
    borderRadius: '0 4px 4px 0',
    color: 'var(--color-text-muted)',
  },
  logCard: { display: 'flex', flexDirection: 'column', gap: 10 },
  logHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', flexWrap: 'wrap', gap: 4 },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: '0.75rem' },
  th: {
    textAlign: 'left', padding: '6px 8px',
    borderBottom: '2px solid var(--color-border)',
    color: 'var(--color-text-muted)', fontWeight: 600, whiteSpace: 'nowrap',
  },
  td: { padding: '6px 8px', borderBottom: '1px solid var(--color-border)', verticalAlign: 'top' },
  rowEven: { background: 'var(--color-bg)' },
};
