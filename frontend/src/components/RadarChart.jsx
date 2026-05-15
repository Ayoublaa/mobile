import { Radar } from "react-chartjs-2"
import PropTypes from "prop-types"
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js"

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend)

function RadarChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="text-slate-400">Aucune donnée de profil.</div>
  }

  const chartData = {
    labels: data.map((item) => item.label),
    datasets: [
      {
        label: "Score de menace",
        data: data.map((item) => item.value),
        backgroundColor: "rgba(59, 130, 246, 0.2)",
        borderColor: "#3b82f6",
        borderWidth: 2,
        pointBackgroundColor: "#38bdf8",
      },
    ],
  }

  return (
    <Radar
      data={chartData}
      options={{
        responsive: true,
        plugins: {
          legend: { labels: { color: "#cbd5e1" } },
        },
        scales: {
          r: {
            grid: { color: "rgba(148, 163, 184, 0.25)" },
            angleLines: { color: "rgba(148, 163, 184, 0.3)" },
            pointLabels: { color: "#cbd5e1" },
            ticks: {
              display: false,
            },
          },
        },
      }}
    />
  )
}

RadarChart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string,
      value: PropTypes.number,
    }),
  ),
}

export default RadarChart
