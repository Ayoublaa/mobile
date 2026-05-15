import { Line } from "react-chartjs-2"
import PropTypes from "prop-types"
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js"

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend)

function LineChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="text-slate-400">Aucune donnée disponible pour le graphe.</div>
  }

  const chartData = {
    labels: data.map((item) => item.timestamp),
    datasets: [
      {
        label: "Anomalies détectées",
        data: data.map((item) => item.count),
        borderColor: "#38bdf8",
        backgroundColor: "rgba(56, 189, 248, 0.2)",
        tension: 0.35,
        fill: false,
        pointRadius: 4,
      },
    ],
  }

  return (
    <Line
      data={chartData}
      options={{
        responsive: true,
        plugins: {
          legend: { labels: { color: "#cbd5e1" } },
        },
        scales: {
          x: { ticks: { color: "#cbd5e1" } },
          y: { ticks: { color: "#cbd5e1" }, beginAtZero: true },
        },
      }}
    />
  )
}

LineChart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      timestamp: PropTypes.string,
      count: PropTypes.number,
    }),
  ),
}

export default LineChart
