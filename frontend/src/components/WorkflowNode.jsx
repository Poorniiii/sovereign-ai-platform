// WorkflowNode.jsx — custom node component for @xyflow/react.
//
// React Flow lets you replace its default node rendering with any
// React component. This component renders each pipeline stage as
// a card with:
//   - An icon and a label
//   - A status badge (idle / running / complete)
//   - Optional content slot (used by the Input node to show the form,
//     and by the Output node to show a link to results)
//
// The node receives its data via the `data` prop that React Flow passes
// automatically. We put status and content into data when building the
// nodes array in WorkflowCanvas.jsx.
//
// React Flow requires Handle components to mark where edges connect.
// We use Position.Right for the source and Position.Left for the target.

import { Handle, Position, useReactFlow } from '@xyflow/react';

export default function WorkflowNode({ id, data }) {
  const { deleteElements } = useReactFlow();
  const { label, icon, status = 'idle', description, content, deletable } = data;

  return (
    <div style={styles.node}>
      {/* Left handle — where incoming edges connect */}
      <Handle type="target" position={Position.Left} style={styles.handle} />

      {deletable && (
        <button
          style={styles.deleteBtn}
          onClick={() => deleteElements({ nodes: [{ id }] })}
          title="Remove node"
        >
          ×
        </button>
      )}

      <div style={styles.top}>
        <span style={styles.icon}>{icon}</span>
        <div style={styles.labelGroup}>
          <span style={styles.label}>{label}</span>
          <span className={`badge badge-${status}`}>{status}</span>
        </div>
      </div>

      {description && (
        <p style={styles.description}>{description}</p>
      )}

      {/* Slot for the Input node's form or the Output node's result link */}
      {content && <div style={styles.content}>{content}</div>}

      {/* Right handle — where outgoing edges connect */}
      <Handle type="source" position={Position.Right} style={styles.handle} />
    </div>
  );
}

const styles = {
  node: {
    position: 'relative',
    background: 'var(--color-surface)',
    border: '1px solid var(--color-border)',
    borderRadius: 8,
    padding: '12px 16px',
    minWidth: 180,
    maxWidth: 220,
    boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
  },
  top: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    marginBottom: 6,
  },
  icon: { fontSize: 18 },
  labelGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: 3,
  },
  label: { fontWeight: 600, fontSize: '0.8125rem', color: 'var(--color-text)' },
  description: {
    fontSize: '0.75rem',
    color: 'var(--color-text-muted)',
    lineHeight: 1.4,
  },
  content: { marginTop: 10 },
  deleteBtn: {
    position: 'absolute',
    top: 4,
    right: 6,
    background: 'transparent',
    border: 'none',
    cursor: 'pointer',
    fontSize: '1rem',
    color: 'var(--color-text-muted)',
    lineHeight: 1,
    padding: '0 2px',
  },
  handle: {
    background: 'var(--color-border)',
    width: 8,
    height: 8,
    border: '2px solid var(--color-primary)',
  },
};
