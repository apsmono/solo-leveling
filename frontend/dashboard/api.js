import { API_BASE } from "../shared/firebase-config.js";
import { getIdToken } from "./auth.js";

async function _headers() {
  const token = await getIdToken();
  const h = { "Content-Type": "application/json" };
  if (token) h["Authorization"] = `Bearer ${token}`;
  return h;
}

export async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`, { headers: await _headers() });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiPost(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: await _headers(),
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiDelete(path) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "DELETE",
    headers: await _headers(),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function sendCommand(text) {
  const res = await fetch(`${API_BASE}/command`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
