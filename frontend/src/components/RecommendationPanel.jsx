import PropTypes from "prop-types"

const priorityStyles = {
  CRITICAL: "bg-red-500/10 text-red-300",
  HIGH: "bg-orange-500/10 text-orange-300",
  MEDIUM: "bg-yellow-500/10 text-yellow-300",
  LOW: "bg-emerald-500/10 text-emerald-300",
}

function RecommendationPanel({ recommendations }) {
  return (
    <div className="space-y-4">
      {recommendations.length === 0 ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-950 p-5 text-slate-400">Aucune recommandation disponible.</div>
      ) : (
        recommendations.map((item, index) => (
          <div key={`${item.type}-${index}`} className="rounded-3xl border border-slate-800 bg-slate-950 p-5">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <p className="text-sm uppercase tracking-[0.24em] text-slate-400">Recommandation</p>
                <h3 className="text-lg font-semibold text-white">{item.type}</h3>
              </div>
              <span className={`rounded-full px-3 py-1 text-xs font-semibold ${priorityStyles[item.priority] || "bg-slate-800 text-slate-200"}`}>
                {item.priority}
              </span>
            </div>
            <p className="text-sm text-slate-300">{item.explanation}</p>
            <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-300">
              {Object.entries(item.params || {}).map(([key, value]) => (
                <span key={key} className="rounded-full bg-slate-800 px-3 py-1">{key}: {String(value)}</span>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  )
}

RecommendationPanel.propTypes = {
  recommendations: PropTypes.arrayOf(
    PropTypes.shape({
      type: PropTypes.string,
      priority: PropTypes.string,
      params: PropTypes.object,
      explanation: PropTypes.string,
    }),
  ).isRequired,
}

export default RecommendationPanel
