// WorkflowCanvas.jsx — the main workflow page (Screen 2).
//
// Layout:
//   Left sidebar  — informational list of the four node types
//   Right area    — the React Flow canvas with the fixed pipeline
//   Top-right     — "Run Workflow" button
//
// The pipeline is fixed (not user-draggable): Input → Retrieval → Validation → Output.
// Each node shows a status badge: idle / running / complete.
//
// How status updates work:
//   1. User fills in query + optional contract text in the Input node
//   2. User clicks "Run Workflow"
//   3. Input node → complete, Retrieval Agent → running  (immediately)
//   4. POST /workflow/trigger fires (blocking — takes 15-30s)
//   5. When response arrives:  Retrieval → complete, Validation → complete,
//      Output → complete, then navigate to /results/:workflowId
//
// Because the backend call is synchronous we cannot get true per-node timing.
// The simulated "running" badge gives the user feedback that something is
// happening rather than a frozen UI for 30 seconds.

import { useState, useCallback, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router';
import {
  ReactFlow,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  addEdge,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import Header from '../components/Header';
import WorkflowNode from '../components/WorkflowNode';
import { triggerWorkflow } from '../api/workflow';

// Tell React Flow to use our custom component for every node.
const nodeTypes = { workflowNode: WorkflowNode };

// ── Initial input form (rendered inside the Input node) ─────────
// Defined outside the component so it isn't recreated on every render.
// The query textarea is deliberately uncontrolled (no value prop) so the DOM
// manages the displayed text independently of React Flow's node state.
function InputForm({ fileContent, onChange }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <div className="form-group">
        <label className="form-label">Upload file(s)</label>
        <input
          type="file"
          accept=".txt,.md,.pdf"
          style={{ fontSize: '0.75rem' }}
          onChange={(e) => {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (ev) => onChange('fileContent', ev.target.result);
            reader.readAsText(file);
          }}
        />
        {fileContent && (
          <span style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>
            {fileContent.length} chars loaded
          </span>
        )}
      </div>
      <div className="form-group">
        <label className="form-label">Enter query</label>
        <textarea
          className="form-input"
          placeholder="e.g. Is this retention clause GDPR compliant?"
          defaultValue=""
          onChange={(e) => onChange('query', e.target.value)}
          style={{ minHeight: 60, fontSize: '0.75rem' }}
        />
      </div>
    </div>
  );
}

// ── Main component ───────────────────────────────────────────────
export default function WorkflowCanvas() {
  const navigate = useNavigate();

  const [query, setQuery]             = useState('');
  const [fileContent, setFileContent] = useState('');
  const [running, setRunning]         = useState(false);
  const [error, setError]             = useState('');
  const [rfInstance, setRfInstance]   = useState(null);
  const nodeIdRef                     = useRef(0);

  // Stable callback so InputForm doesn't re-render on every parent state change
  const handleFormChange = useCallback((field, value) => {
    if (field === 'query')       setQuery(value);
    if (field === 'fileContent') setFileContent(value);
  }, []);

  // Canvas starts empty — users drag nodes onto it to build their workflow
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const onConnect = useCallback(
    (connection) => setEdges((eds) => addEdge({ ...connection, animated: true }, eds)),
    [setEdges],
  );

  // When a file is loaded, refresh any Input Node on the canvas so the
  // "X chars loaded" display stays up to date.
  useEffect(() => {
    setNodes(nds => nds.map(n =>
      n.data.label === 'Input Node'
        ? { ...n, data: { ...n.data, content: <InputForm fileContent={fileContent} onChange={handleFormChange} /> } }
        : n
    ));
  }, [fileContent, handleFormChange]);

  // Update status badges on existing nodes by matching their label.
  // The fixed pipeline IDs no longer exist — nodes are whatever the user dropped.
  function applyStatuses(labelStatusMap) {
    setNodes(nds => nds.map(n => ({
      ...n,
      data: { ...n.data, status: labelStatusMap[n.data.label] ?? n.data.status },
    })));
  }

  async function handleRun() {
    if (!query.trim()) {
      setError('Please enter a query before running.');
      return;
    }
    setError('');
    setRunning(true);

    applyStatuses({ 'Input Node': 'complete', 'Retrieval Agent': 'running' });

    try {
      const result = await triggerWorkflow(query, fileContent);

      applyStatuses({
        'Input Node': 'complete',
        'Retrieval Agent': 'complete',
        'Validation Agent': 'complete',
        'Output Node': 'complete',
      });

      navigate(`/results/${result.workflow_id}`, { state: { result } });

    } catch (err) {
      setError(err.response?.data?.detail ?? 'Workflow failed. Is the backend running?');
      applyStatuses({
        'Input Node': 'idle', 'Retrieval Agent': 'idle',
        'Validation Agent': 'idle', 'Output Node': 'idle',
      });
    } finally {
      setRunning(false);
    }
  }

  return (
    <div style={styles.page}>
      <Header />

      <div style={styles.body}>
        {/* ── Left sidebar ── */}
        <aside style={styles.sidebar}>
          <h3 style={{ marginBottom: 4 }}>Node Types</h3>
          <p style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', marginBottom: 12 }}>
            Drag onto canvas to add
          </p>
          {NODE_TYPE_INFO.map((n) => (
            <div
              key={n.label}
              style={{ ...styles.sidebarItem, cursor: 'grab' }}
              draggable
              onDragStart={(e) => {
                e.dataTransfer.setData(
                  'application/reactflow',
                  JSON.stringify({ label: n.label, icon: n.icon, description: n.description })
                );
                e.dataTransfer.effectAllowed = 'move';
              }}
            >
              <span style={styles.sidebarIcon}>{n.icon}</span>
              <div>
                <p style={styles.sidebarLabel}>{n.label}</p>
                <p className="text-muted text-sm">{n.description}</p>
              </div>
            </div>
          ))}
        </aside>

        {/* ── Canvas area ── */}
        <main style={styles.canvasWrap}>
          <div style={styles.canvasHeader}>
            <h2>Workflow Canvas</h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              {error && <span style={styles.errorMsg}>{error}</span>}
              <button
                className="btn btn-primary"
                onClick={handleRun}
                disabled={running}
              >
                {running ? 'Running…' : 'Run Workflow'}
              </button>
            </div>
          </div>

          <div
            style={styles.canvas}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              const raw = e.dataTransfer.getData('application/reactflow');
              if (!raw || !rfInstance) return;
              const { label, icon, description } = JSON.parse(raw);
              const position = rfInstance.screenToFlowPosition({ x: e.clientX, y: e.clientY });
              const id = `dropped-${++nodeIdRef.current}`;
              const nodeData = { label, icon, status: 'idle', description, deletable: true };
              // Input Node gets the query/file form embedded inside it
              if (label === 'Input Node') {
                nodeData.content = <InputForm fileContent={fileContent} onChange={handleFormChange} />;
              }
              setNodes((nds) => [
                ...nds,
                { id, type: 'workflowNode', position, data: nodeData },
              ]);
            }}
          >
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              nodeTypes={nodeTypes}
              fitView={nodes.length > 0}
              fitViewOptions={{ padding: 0.2 }}
              nodesDraggable={true}
              nodesConnectable={true}
              elementsSelectable={true}
              onConnect={onConnect}
              onInit={setRfInstance}
            >
              <Background color="var(--color-border)" gap={20} />
              <Controls showInteractive={false} />
              {nodes.length === 0 && (
                <div style={styles.emptyHint}>
                  <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--color-text-muted)' }}>
                    Drag node types from the left panel to build your workflow
                  </p>
                  <p style={{ margin: '6px 0 0', fontSize: '0.8rem', color: 'var(--color-text-muted)', opacity: 0.7 }}>
                    Suggested order: Input Node → Retrieval Agent → Validation Agent → Output Node
                  </p>
                </div>
              )}
            </ReactFlow>
          </div>
        </main>
      </div>
    </div>
  );
}

const NODE_TYPE_INFO = [
  { icon: '📄', label: 'Input Node',       description: 'Starts the workflow with a file and a user query' },
  { icon: '📋', label: 'Retrieval Agent',  description: 'Search and fetch relevant data' },
  { icon: '✅', label: 'Validation Agent', description: 'Verify decisions and policies' },
  { icon: '📤', label: 'Output Node',      description: 'Final output delivery' },
];

const styles = {
  page: { minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--color-bg)' },
  body: { display: 'flex', flex: 1, overflow: 'hidden' },
  sidebar: {
    width: 200,
    minWidth: 180,
    background: 'var(--color-surface)',
    borderRight: '1px solid var(--color-border)',
    padding: '20px 16px',
    display: 'flex',
    flexDirection: 'column',
    gap: 4,
  },
  sidebarItem: {
    display: 'flex', alignItems: 'flex-start', gap: 10,
    padding: '10px 0',
    borderBottom: '1px solid var(--color-border)',
  },
  sidebarIcon: { fontSize: 18, marginTop: 1 },
  sidebarLabel: { fontWeight: 600, fontSize: '0.8125rem', marginBottom: 2 },
  canvasWrap: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
  },
  canvasHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '14px 20px',
    borderBottom: '1px solid var(--color-border)',
    background: 'var(--color-surface)',
  },
  canvas: { flex: 1, position: 'relative' },
  emptyHint: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    textAlign: 'center',
    pointerEvents: 'none',
    userSelect: 'none',
  },
  errorMsg: {
    fontSize: '0.8125rem',
    color: 'var(--color-danger)',
    background: '#fee2e2',
    borderRadius: 6,
    padding: '6px 10px',
  },
};

