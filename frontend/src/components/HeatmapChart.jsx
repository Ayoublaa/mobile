import PropTypes from "prop-types"

function HeatmapChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="text-slate-400">Aucune donnée pour la heatmap.</div>
  }

  return (
    <div className="grid grid-cols-4 gap-2">
      {data.map((row) => (
        <div key={row.label} className="space-y-1">
          <div className="text-sm text-slate-400">{row.label}</div>
          <div className="grid grid-cols-3 gap-1">
            {row.values.map((cell, index) => (
              <div
                key={`${row.label}-${index}`}
                className="h-12 rounded-xl"
                style={{
                  backgroundColor: `rgba(59, 130, 246, ${Math.min(1, 0.2 + cell * 0.15)})`,
                }}
              >
                <div className="h-full flex items-center justify-center text-xs text-white">{cell}</div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

HeatmapChart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string,
      values: PropTypes.arrayOf(PropTypes.number),
    }),
  ),
}

export default HeatmapChart
