import { useState } from "react";
import { api } from "../api";
import { STAGES, RISK_COLORS, STAGE_COLORS } from "../constants";

export default function DealHeader({ deal, onUpdated }) {
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({
    stage: deal.stage,
    deal_score: deal.deal_score,
    risk_level: deal.risk_level,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handle = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const save = async () => {
    setLoading(true);
    setError(null);
    try {
      const updated = await api.updateDeal(deal.id, {
        ...form,
        deal_score: parseInt(form.deal_score, 10),
      });
      onUpdated(updated);
      setEditing(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const riskCls = RISK_COLORS[deal.risk_level] || "bg-gray-100 text-gray-700";
  const stageCls = STAGE_COLORS[deal.stage] || "bg-gray-100 text-gray-700";

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">
            {deal.customer.name}
            {deal.customer.industry && ` · ${deal.customer.industry}`}
          </p>
          <h1 className="mt-1 text-2xl font-bold text-gray-900">{deal.title}</h1>
          <p className="mt-1 text-2xl font-semibold text-indigo-700">
            ${(deal.value / 1_000_000).toFixed(2)}M
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span className={`rounded-full px-3 py-1 text-sm font-medium ${stageCls}`}>
            {deal.stage}
          </span>
          <span className={`rounded-full px-3 py-1 text-sm font-medium ${riskCls}`}>
            {deal.risk_level}
          </span>
          <span className="rounded-full bg-indigo-50 px-3 py-1 text-sm font-semibold text-indigo-700">
            Score: {deal.deal_score}
          </span>
          <button
            onClick={() => setEditing(!editing)}
            className="rounded-lg border border-gray-200 px-3 py-1 text-sm text-gray-600 hover:bg-gray-50 transition-colors"
          >
            {editing ? "Cancel" : "Edit"}
          </button>
        </div>
      </div>

      {editing && (
        <div className="mt-4 border-t pt-4 space-y-3">
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div className="flex flex-wrap gap-3">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Stage</label>
              <select name="stage" value={form.stage} onChange={handle} className="input">
                {STAGES.map((s) => (
                  <option key={s}>{s}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Score</label>
              <input
                name="deal_score"
                type="number"
                min="0"
                max="100"
                value={form.deal_score}
                onChange={handle}
                className="input w-24"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Risk</label>
              <select name="risk_level" value={form.risk_level} onChange={handle} className="input">
                <option>LOW</option>
                <option>MEDIUM</option>
                <option>HIGH</option>
              </select>
            </div>
          </div>
          <button
            onClick={save}
            disabled={loading}
            className="rounded-lg bg-indigo-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            {loading ? "Saving…" : "Save Changes"}
          </button>
        </div>
      )}
    </div>
  );
}
