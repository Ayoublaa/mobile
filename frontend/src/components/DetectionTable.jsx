import PropTypes from "prop-types"

function DetectionTable({ detections }) {
  return (
    <div className="mt-6 overflow-hidden rounded-3xl border border-slate-800 bg-slate-950">
      <table className="min-w-full divide-y divide-slate-800 text-sm">
        <thead className="bg-slate-900 text-slate-400">
          <tr>
            <th className="px-4 py-3 text-left">IP</th>
            <th className="px-4 py-3 text-left">Type</th>
            <th className="px-4 py-3 text-left">Sévérité</th>
            <th className="px-4 py-3 text-left">Count</th>
            <th className="px-4 py-3 text-left">User-Agent</th>
            <th className="px-4 py-3 text-left">Timestamp</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800 bg-slate-950">
          {detections.map((item) => (
            <tr key={`${item.ip}-${item.timestamp}`} className="hover:bg-slate-900/80">
              <td className="px-4 py-3 font-medium text-white">{item.ip}</td>
              <td className="px-4 py-3 text-slate-300">{item.type}</td>
              <td className="px-4 py-3 text-cyan-300">{item.severity}</td>
              <td className="px-4 py-3 text-slate-300">{item.count ?? item.details?.failed_attempts ?? "--"}</td>
              <td className="px-4 py-3 text-slate-300">{item.user_agent}</td>
              <td className="px-4 py-3 text-slate-400">{item.timestamp}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

DetectionTable.propTypes = {
  detections: PropTypes.arrayOf(
    PropTypes.shape({
      ip: PropTypes.string,
      type: PropTypes.string,
      severity: PropTypes.string,
      count: PropTypes.number,
      user_agent: PropTypes.string,
      timestamp: PropTypes.string,
      details: PropTypes.object,
    }),
  ).isRequired,
}

export default DetectionTable
