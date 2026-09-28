import { useEffect, useState } from "react";
import { api } from "../api";
import DealCard from "../components/DealCard";
import NewDealForm from "../components/NewDealForm";
import Spinner from "../components/Spinner";
import ErrorBanner from "../components/ErrorBanner";

export default function Dashboard() {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getDeals();
      setDeals(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreated = (deal) => {
    setDeals((prev) => [deal, ...prev]);
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Precedent</h1>
          <p className="text-sm text-gray-500 mt-0.5">AI Sales Strategist — Deal Management</p>
        </div>
        <span className="text-xs text-gray-400">{deals.length} deal{deals.length !== 1 ? "s" : ""}</span>
      </div>

      <NewDealForm onCreated={handleCreated} />

      {loading && <Spinner />}
      {error && <ErrorBanner message={error} />}

      {!loading && !error && deals.length === 0 && (
        <p className="text-sm text-gray-400 text-center py-8">
          No deals yet. Create your first deal above.
        </p>
      )}

      {!loading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {deals.map((d) => (
            <DealCard key={d.id} deal={d} />
          ))}
        </div>
      )}
    </div>
  );
}
