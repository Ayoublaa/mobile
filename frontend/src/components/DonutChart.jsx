import { Doughnut } from "react-chartjs-2"
import PropTypes from "prop-types"
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js"

ChartJS.register(ArcElement, Tooltip, Legend)

function DonutChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="text-slate-400">Aucune donnée pour le donut.</div>
  }

  const chartData = {
    labels: data.map((item) => item.status),
    datasets: [
      {
        data: data.map((item) => item.count),
        backgroundColor: ["#22c55e", "#f97316", "#ef4444", "#38bdf8"].slice(0, data.length),
        borderWidth: 0,
      },
    ],
  }

  return (
    <Doughnut
      data={chartData}
      options={{
        responsive: true,
        plugins: {
          legend: { labels: { color: "#cbd5e1" } },
        },
      }}
    />
  )
}

DonutChart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      status: PropTypes.string,
      count: PropTypes.number,
    }),
  ),
}

export default DonutChart
