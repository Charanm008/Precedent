import { useEffect, useState, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../api";
import DealHeader from "../components/DealHeader";
import Timeline from "../components/Timeline";
import AddInteractionForm from "../components/AddInteractionForm";
import PlaceholderCard from "../components/PlaceholderCard";
import Spinner from "../components/Spinner";
import ErrorBanner from "../components/ErrorBanner";

export default function DealPage() {
  const { id } = useParams();
  const [deal, setDeal] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const [dealData, timelineData] = await Promise.all([
        api.getDeal(id),
        api.getTimeline(id),
      ]);
      setDeal(dealData);
      setTimeline(timelineData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  const handleInteractionAdded = (ix) => {
    setTimeline((prev) => [ix, ...prev]);
  };

  if (loading) return <div className="max-w-4xl mx-auto px-4 py-8"><Spinner /></div>;
  if (error) return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-4">
      <Link to="/" className="text-sm text-indigo-600 hover:underline">← Back to Dashboard</Link>
      <ErrorBanner message={error} />
    </div>
  );
  if (!deal) return null;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      <Link to="/" className="text-sm text-indigo-600 hover:underline">
        ← Back to Dashboard
      </Link>

      {/* Deal header with inline edit */}
      <DealHeader deal={deal} onUpdated={setDeal} />

      {/* Stakeholders */}
      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="text-base font-semibold text-gray-700 mb-4">
          Stakeholders <span className="text-gray-400 font-normal">({deal.stakeholders.length})</span>
        </h2>
        {deal.stakeholders.length === 0 ? (
          <p className="text-sm text-gray-400">No stakeholders added yet.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {deal.stakeholders.map((s) => (
              <div key={s.id} className="rounded-lg border border-gray-100 bg-gray-50 p-3">
                <p className="font-semibold text-gray-800 text-sm">{s.name}</p>
                <p className="text-xs text-indigo-600">{s.role}</p>
                {s.concern && (
                  <p className="text-xs text-gray-500 mt-1">
                    Concern: <span className="italic">{s.concern}</span>
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Interaction */}
      <AddInteractionForm deal={deal} onAdded={handleInteractionAdded} />

      {/* Timeline */}
      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="text-base font-semibold text-gray-700 mb-4">
          Timeline <span className="text-gray-400 font-normal">({timeline.length} interaction{timeline.length !== 1 ? "s" : ""})</span>
        </h2>
        <Timeline interactions={timeline} />
      </div>

      {/* Placeholder cards for Phase 2 */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <PlaceholderCard
          title="Memory"
          description="Hindsight-powered persistent memory will surface relevant context from past deals."
          icon="🧠"
        />
        <PlaceholderCard
          title="Competitive Intelligence"
          description="Automated competitor tracking and battlecard generation."
          icon="🔍"
        />
        <PlaceholderCard
          title="Next Best Action"
          description="AI-recommended follow-up actions based on deal history and sentiment."
          icon="⚡"
        />
      </div>
    </div>
  );
}
