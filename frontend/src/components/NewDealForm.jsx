import { useState } from "react";
import { api } from "../api";
import { STAGES } from "../constants";

export default function NewDealForm({ onCreated }) {
  const [form, setForm] = useState({
    customer_name: "",
    customer_industry: "",
    title: "",
    value: "",
    stage: "Prospecting",
    deal_score: 50,
    risk_level: "MEDIUM",
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
      const deal = await api.createDeal({
        ...form,
        value: parseFloat(form.value) || 0,
        deal_score: parseInt(form.deal_score, 10),
      });
      setForm({
        customer_name: "",
        customer_industry: "",
        title: "",
        value: "",
        stage: "Prospecting",
        deal_score: 50,
        risk_level: "MEDIUM",
      });
      onCreated(deal);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={submit} className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm space-y-4">
      <h2 className="text-base font-semibold text-gray-700">New Deal</h2>

      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <input
          name="customer_name"
          required
          placeholder="Customer name *"
          value={form.customer_name}
          onChange={handle}
          className="input"
        />
        <input
          name="customer_industry"
          placeholder="Industry"
          value={form.customer_industry}
          onChange={handle}
          className="input"
        />
        <input
          name="title"
          required
          placeholder="Deal title *"
          value={form.title}
          onChange={handle}
          className="input sm:col-span-2"
        />
        <input
          name="value"
          type="number"
          min="0"
          step="1000"
          placeholder="Value ($)"
          value={form.value}
          onChange={handle}
          className="input"
        />
        <select name="stage" value={form.stage} onChange={handle} className="input">
          {STAGES.map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>
        <input
          name="deal_score"
          type="number"
          min="0"
          max="100"
          placeholder="Score (0–100)"
          value={form.deal_score}
          onChange={handle}
          className="input"
        />
        <select name="risk_level" value={form.risk_level} onChange={handle} className="input">
          <option>LOW</option>
          <option>MEDIUM</option>
          <option>HIGH</option>
        </select>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-lg bg-indigo-600 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
      >
        {loading ? "Creating…" : "Create Deal"}
      </button>
    </form>
  );
}
