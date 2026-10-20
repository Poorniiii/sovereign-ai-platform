// workflow.js — wraps POST /workflow/trigger and GET /audit/logs.
//
// Both endpoints require a valid JWT in the Authorization header.
// We use an Axios instance with request/response interceptors so every
// call automatically carries the token and a 401 clears it.

import axios from 'axios';
import { getToken, logout } from './auth';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

// Axios instance shared by all authenticated API calls.
const api = axios.create({ baseURL: BASE_URL });

// Request interceptor — attach Bearer token to every outgoing request.
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor — on 401 clear the token so ProtectedRoute redirects
// the user to the login page on their next navigation attempt.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      logout();
    }
    return Promise.reject(error);
  },
);

/**
 * POST /workflow/trigger
 * Sends the user's query and optional contract text to the backend which
 * forwards it to the LangGraph worker.
 *
 * @param {string} query       - The compliance question
 * @param {string} fileContent - Contract text (may be empty string)
 * @returns The full response body including verdict, confidence, answer,
 *          retrieved_chunks, workflow_id.
 */
export async function triggerWorkflow(query, fileContent = '') {
  // Truncate before sending — prevents huge JSON payloads that cause 504s.
  // The worker also truncates at this limit when building the LLM prompt.
  const MAX_CHARS = 8000;
  const trimmed = fileContent.length > MAX_CHARS ? fileContent.slice(0, MAX_CHARS) : fileContent;
  const response = await api.post('/workflow/trigger', {
    query,
    file_content: trimmed,
  });
  return response.data;
}

/**
 * GET /audit/logs?limit=50
 * Returns the most recent audit log entries.
 * Only users with the view_audit OPA permission (admins) can call this.
 */
export async function getAuditLogs(limit = 50, offset = 0) {
  const response = await api.get('/audit/logs', { params: { limit, offset } });
  return response.data;
}
