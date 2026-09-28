const API_BASE_URL = (
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
).replace(/\/+$/, "");

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      Accept: "application/json",
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...(options.headers || {}),
    },
    ...options,
  });

  const text = await response.text();

  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!response.ok) {
    const detail =
      data?.detail ||
      data?.message ||
      (typeof data === "string" ? data : null) ||
      `Request failed with status ${response.status}`;

    throw new Error(
      Array.isArray(detail)
        ? detail.map((item) => item.msg || JSON.stringify(item)).join(", ")
        : String(detail)
    );
  }

  return data;
}

export async function getDeals() {
  return request("/deals");
}

export async function getDeal(dealId) {
  return request(`/deal/${encodeURIComponent(dealId)}`);
}

export async function createDeal(payload) {
  return request("/deal", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateDeal(dealId, payload) {
  return request(`/deal/${encodeURIComponent(dealId)}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function createInteraction(payload) {
  return request("/interaction", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getTimeline(dealId) {
  return request(`/timeline/${encodeURIComponent(dealId)}`);
}

export async function getIntelligenceBrief(deal) {
  const params = new URLSearchParams();

  params.set("deal_id", String(deal.id));
  params.set("deal_title", deal.title || "");
  params.set("customer_name", deal.customer?.name || "");
  params.set("deal_stage", deal.stage || "");
  params.set("deal_value", String(deal.value ?? 0));
  params.set("risk_level", deal.risk_level || "MEDIUM");

  if (deal.customer?.industry) {
    params.set("customer_industry", deal.customer.industry);
  }

  return request(
    `/intelligence/brief/${encodeURIComponent(deal.id)}?${params.toString()}`
  );
}

export async function getAgents() {
  return request("/agents/agents");
}

export async function analyzeDeal(deal, timeline = []) {
  const interactions = Array.isArray(timeline)
    ? timeline.map((interaction) => ({
        id: interaction.id ?? 0,
        type: interaction.type || "call",
        summary: interaction.summary || "",
        sentiment: interaction.sentiment || "neutral",
        strategy: interaction.strategy || "",
        outcome: interaction.outcome || "neutral",
        stakeholder_id:
          interaction.stakeholder_id == null
            ? 0
            : Number(interaction.stakeholder_id),
      }))
    : [];

  const stakeholders = Array.isArray(deal.stakeholders)
    ? deal.stakeholders.map((stakeholder) => ({
        id: stakeholder.id ?? 0,
        name: stakeholder.name || "",
        role: stakeholder.role || "",
        concern: stakeholder.concern || "",
      }))
    : [];

  return request("/agents/analyze", {
    method: "POST",
    body: JSON.stringify({
      deal_id: deal.id,
      deal_title: deal.title || "",
      customer_name: deal.customer?.name || "",
      customer_industry: deal.customer?.industry || "",
      deal_stage: deal.stage || "Prospecting",
      deal_value: Number(deal.value ?? 0),
      risk_level: deal.risk_level || "MEDIUM",
      interactions,
      stakeholders,
    }),
  });
}

export const api = {
  getDeals,
  getDeal,
  createDeal,
  updateDeal,
  createInteraction,
  getTimeline,
  getIntelligenceBrief,
  getAgents,
  analyzeDeal,

  // Backward-compatible aliases
  listDeals: getDeals,

  deals: {
    list: getDeals,
    get: getDeal,
    create: createDeal,
    update: updateDeal,
  },

  interactions: {
    create: createInteraction,
    timeline: getTimeline,
  },

  intelligence: {
    brief: getIntelligenceBrief,
  },

  agents: {
    list: getAgents,
    analyze: analyzeDeal,
  },

  // Generic helpers for any existing components using api.get/api.post/api.patch
  get: (path) => request(path),

  post: (path, payload) =>
    request(path, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  patch: (path, payload) =>
    request(path, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
};