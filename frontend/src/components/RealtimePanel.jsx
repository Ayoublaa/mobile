import PropTypes from "prop-types"

function RealtimePanel({ events }) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl shadow-slate-950/30">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">Flux temps réel</h2>
          <p className="mt-2 text-sm text-slate-400">Mises à jour de traitement envoyées par WebSocket.</p>
        </div>
      </div>
      <div className="mt-6 space-y-3">
        {events.length === 0 ? (
          <div className="rounded-2xl bg-slate-950 p-4 text-slate-400">Aucune mise à jour en direct pour le moment.</div>
        ) : (
          events.slice(-5).map((event, index) => (
            <div key={`${event.stage}-${index}`} className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-sm uppercase tracking-[0.2em] text-cyan-400">{event.stage}</p>
              <p className="mt-2 text-sm text-slate-300">{event.message}</p>
              <p className="mt-1 text-xs text-slate-500">{event.timestamp}</p>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

RealtimePanel.propTypes = {
  events: PropTypes.arrayOf(
    PropTypes.shape({
      stage: PropTypes.string,
      message: PropTypes.string,
      timestamp: PropTypes.string,
    }),
  ).isRequired,
}

export default RealtimePanel
