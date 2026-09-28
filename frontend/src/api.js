const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(method, path, body) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body !== undefined) opts.body = JSON.stringify(body);
  const res = await fetch(`${BASE_URL}${path}`, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  getDeals: () => request("GET", "/deals"),
  createDeal: (data) => request("POST", "/deal", data),
  getDeal: (id) => request("GET", `/deal/${id}`),
  updateDeal: (id, data) => request("PATCH", `/deal/${id}`, data),
  createInteraction: (data) => request("POST", "/interaction", data),
  getTimeline: (dealId) => request("GET", `/timeline/${dealId}`),
};
