import { Scatter } from "react-chartjs-2"
import PropTypes from "prop-types"
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
} from "chart.js"

ChartJS.register(LinearScale, PointElement, Tooltip, Legend)

function ClusterChart({ data }) {
  const chartData = {
    datasets: data.map((cluster) => ({
      label: `${cluster.pattern_name}`,
      data: [
        {
          x: cluster.avg_requests ?? cluster.ips.length,
          y: cluster.avg_endpoints ?? cluster.ips.length,
          r: Math.max(5, Math.min(15, cluster.ips.length * 2)),
        },
      ],
      backgroundColor: cluster.severity_profile === "CRITICAL" ? "#ef4444" : cluster.severity_profile === "HIGH" ? "#f97316" : "#22c55e",
    })),
  }

  const options = {
    responsive: true,
    plugins: {
      legend: {
        labels: {
          color: "#cbd5e1",
        },
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: "req_per_minute",
          color: "#94a3b8",
        },
        ticks: { color: "#cbd5e1" },
      },
      y: {
        title: {
          display: true,
          text: "unique_endpoints",
          color: "#94a3b8",
        },
        ticks: { color: "#cbd5e1" },
      },
    },
  }

  return <Scatter data={chartData} options={options} />
}

ClusterChart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      cluster_id: PropTypes.number,
      pattern_name: PropTypes.string,
      ips: PropTypes.arrayOf(PropTypes.string),
      avg_requests: PropTypes.number,
      avg_endpoints: PropTypes.number,
      severity_profile: PropTypes.string,
    }),
  ).isRequired,
}

export default ClusterChart
