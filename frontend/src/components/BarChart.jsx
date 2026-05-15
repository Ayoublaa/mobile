import { Bar } from "react-chartjs-2"
import PropTypes from "prop-types"
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from "chart.js"

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

function BarChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="text-slate-400">Aucune donnée pour le bar chart.</div>
  }

  const chartData = {
    labels: data.map((item) => item.label),
    datasets: [
      {
        label: "Événements par catégorie",
        data: data.map((item) => item.value),
        backgroundColor: "rgba(245, 158, 11, 0.8)",
        borderColor: "rgba(245, 158, 11, 1)",
        borderWidth: 1,
      },
    ],
  }

  return (
    <Bar
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

BarChart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string,
      value: PropTypes.number,
    }),
  ),
}

export default BarChart
