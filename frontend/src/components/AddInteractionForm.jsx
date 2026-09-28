import { useState } from "react";
import { api } from "../api";

export default function AddInteractionForm({ deal, onAdded }) {
  const [form, setForm] = useState({
    type: "call",
    summary: "",
    sentiment: "neutral",
    stakeholder_id: "",
    strategy: "",
    outcome: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handle = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const payload = {
        deal_id: deal.id,
        type: form.type,
        summary: form.summary,
        sentiment: form.sentiment,
        strategy: form.strategy || null,
        outcome: form.outcome || null,
        stakeholder_id: form.stakeholder_id ? parseInt(form.stakeholder_id, 10) : null,
      };
      const ix = await api.createInteraction(payload);
      setForm({ type: "call", summary: "", sentiment: "neutral", stakeholder_id: "", strategy: "", outcome: "" });
      onAdded(ix);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={submit} className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm space-y-4">
      <h3 className="text-base font-semibold text-gray-700">Add Interaction</h3>
      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <select name="type" value={form.type} onChange={handle} className="input">
          <option value="call">Call</option>
          <option value="meeting">Meeting</option>
          <option value="email">Email</option>
          <option value="note">Note</option>
        </select>
        <select name="stakeholder_id" value={form.stakeholder_id} onChange={handle} className="input">
          <option value="">No specific stakeholder</option>
          {deal.stakeholders.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name} ({s.role})
            </option>
          ))}
        </select>
        <textarea
          name="summary"
          required
          placeholder="Summary *"
          value={form.summary}
          onChange={handle}
          rows={3}
          className="input sm:col-span-2 resize-none"
        />
        <select name="sentiment" value={form.sentiment} onChange={handle} className="input">
          <option value="positive">Positive</option>
          <option value="neutral">Neutral</option>
          <option value="negative">Negative</option>
        </select>
        <select name="outcome" value={form.outcome} onChange={handle} className="input">
          <option value="">Outcome (optional)</option>
          <option value="worked">Worked</option>
          <option value="failed">Failed</option>
          <option value="neutral">Neutral</option>
        </select>
        <input
          name="strategy"
          placeholder="Strategy / next step (optional)"
          value={form.strategy}
          onChange={handle}
          className="input sm:col-span-2"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-lg bg-indigo-600 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
      >
        {loading ? "Saving…" : "Add Interaction"}
      </button>
    </form>
  );
}
