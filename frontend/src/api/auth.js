// auth.js — wraps all calls to POST /auth/login and manages the JWT in localStorage.
//
// The backend (routes/auth.py) accepts { username, password } only.
// The role is determined server-side from the USERS dict and embedded in the JWT.
// We decode the role from the token payload (the middle base64 segment) so
// the UI can display it without a separate /me endpoint.

import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

// JWT payloads are base64url-encoded (RFC 7519), which uses - and _ instead
// of + and / and omits = padding. The browser's atob() only handles standard
// base64, so we normalise the string before decoding.
function decodeJwtPayload(token) {
  const b64url = token.split('.')[1];
  const b64 = b64url.replace(/-/g, '+').replace(/_/g, '/');
  const padded = b64 + '='.repeat((4 - (b64.length % 4)) % 4);
  return JSON.parse(atob(padded));
}

const TOKEN_KEY = 'sovereign_token';

/**
 * POST /auth/login
 * Returns { token, role, username } on success.
 * Throws an Error with a human-readable message on failure.
 */
export async function login(username, password) {
  const response = await axios.post(`${BASE_URL}/auth/login`, { username, password });
  const { access_token } = response.data;

  // Decode the JWT payload (second segment, base64url-encoded JSON)
  // to extract role and sub without a round-trip to the backend.
  const payload = decodeJwtPayload(access_token);

  localStorage.setItem(TOKEN_KEY, access_token);

  return {
    token: access_token,
    role: payload.role,
    username: payload.sub,
  };
}

/** Remove the stored JWT — user is now logged out. */
export function logout() {
  localStorage.removeItem(TOKEN_KEY);
}

/** Returns the raw JWT string, or null if not logged in. */
export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Returns { username, role } decoded from the stored token,
 * or null if there is no token or it cannot be decoded.
 */
export function getStoredUser() {
  const token = getToken();
  if (!token) return null;
  try {
    const payload = decodeJwtPayload(token);
    return { username: payload.sub, role: payload.role };
  } catch {
    return null;
  }
}
