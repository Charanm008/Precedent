export default function PlaceholderCard({ title, description, icon }) {
  return (
    <div className="rounded-xl border border-dashed border-gray-300 bg-gray-50 p-6 flex flex-col items-center justify-center text-center gap-2 min-h-[140px]">
      {icon && <span className="text-3xl">{icon}</span>}
      <h3 className="font-semibold text-gray-500">{title}</h3>
      {description && (
        <p className="text-xs text-gray-400 max-w-xs">{description}</p>
      )}
      <span className="mt-1 rounded-full bg-gray-200 px-3 py-0.5 text-xs text-gray-500">
        Coming in Phase 2
      </span>
    </div>
  );
}
