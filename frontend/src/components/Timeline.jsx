import { SENTIMENT_COLORS } from "../constants";

function formatDate(iso) {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

const TYPE_ICON = {
  call: "📞",
  meeting: "🤝",
  email: "✉️",
  note: "📝",
};

const OUTCOME_LABEL = {
  worked: { label: "Worked", cls: "text-green-600" },
  failed: { label: "Failed", cls: "text-red-600" },
  neutral: { label: "Neutral", cls: "text-gray-500" },
};

export default function Timeline({ interactions }) {
  if (!interactions || interactions.length === 0) {
    return (
      <p className="text-sm text-gray-400 py-4">
        No interactions yet. Add one below.
      </p>
    );
  }

  return (
    <ol className="relative border-l border-gray-200 space-y-6 pl-4">
      {interactions.map((ix) => {
        const sentCls = SENTIMENT_COLORS[ix.sentiment] || "text-gray-500";
        const outcomeMeta = ix.outcome ? OUTCOME_LABEL[ix.outcome] : null;

        return (
          <li key={ix.id} className="ml-4">
            <span className="absolute -left-2 flex h-4 w-4 items-center justify-center rounded-full bg-white border-2 border-indigo-400 text-xs">
              {TYPE_ICON[ix.type] || "•"}
            </span>
            <div className="rounded-lg border border-gray-100 bg-white p-4 shadow-sm">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="text-xs font-medium text-gray-400 uppercase tracking-wide">
                  {ix.type}
                  {ix.stakeholder && ` · ${ix.stakeholder.name} (${ix.stakeholder.role})`}
                </span>
                <span className="text-xs text-gray-400">{formatDate(ix.occurred_at)}</span>
              </div>
              <p className="mt-2 text-sm text-gray-700 leading-relaxed">{ix.summary}</p>
              <div className="mt-2 flex flex-wrap items-center gap-3 text-xs">
                <span className={`font-medium capitalize ${sentCls}`}>
                  {ix.sentiment}
                </span>
                {outcomeMeta && (
                  <span className={`font-medium ${outcomeMeta.cls}`}>
                    {outcomeMeta.label}
                  </span>
                )}
                {ix.strategy && (
                  <span className="text-gray-500 italic">Strategy: {ix.strategy}</span>
                )}
              </div>
            </div>
          </li>
        );
      })}
    </ol>
  );
}
