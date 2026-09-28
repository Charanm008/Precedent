import { RISK_COLORS, STAGE_COLORS } from "../constants";
import { Link } from "react-router-dom";

export default function DealCard({ deal }) {
  const riskCls = RISK_COLORS[deal.risk_level] || "bg-gray-100 text-gray-700";
  const stageCls = STAGE_COLORS[deal.stage] || "bg-gray-100 text-gray-700";

  return (
    <Link
      to={`/deal/${deal.id}`}
      className="block rounded-xl border border-gray-200 bg-white p-5 shadow-sm hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-xs text-gray-400 font-medium uppercase tracking-wide">
            {deal.customer.name}
          </p>
          <h3 className="mt-0.5 text-base font-semibold text-gray-800 leading-snug">
            {deal.title}
          </h3>
        </div>
        <span className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium ${stageCls}`}>
          {deal.stage}
        </span>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <span className="text-xl font-bold text-gray-900">
          ${(deal.value / 1_000_000).toFixed(1)}M
        </span>
        <div className="flex items-center gap-2">
          <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${riskCls}`}>
            {deal.risk_level}
          </span>
          <span className="flex items-center gap-1 text-sm text-gray-600">
            <span className="font-semibold text-indigo-600">{deal.deal_score}</span>
            <span className="text-gray-400">/100</span>
          </span>
        </div>
      </div>
    </Link>
  );
}
