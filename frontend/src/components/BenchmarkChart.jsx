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

function BenchmarkChart({ benchmark }) {
  if (!benchmark?.summary) {
    return <div className="text-slate-400">Chargement des benchmarks...</div>
  }

  const { model_average, baseline_average } = benchmark.summary
  const labels = ["Precision", "Recall", "F1"]
  const data = {
    labels,
    datasets: [
      {
        label: "Détecteur Mobile API",
        data: [model_average.precision, model_average.recall, model_average.f1_score],
        backgroundColor: "#22c55e",
      },
      {
        label: "Baseline Fail2ban",
        data: [baseline_average.precision, baseline_average.recall, baseline_average.f1_score],
        backgroundColor: "#38bdf8",
      },
    ],
  }

  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-xl shadow-slate-950/30">
      <h2 className="text-xl font-semibold text-white">Benchmark comparatif</h2>
      <p className="mt-2 text-sm text-slate-400">Évaluation sur 9 scénarios synthétiques contre une base Fail2ban.</p>
      <div className="mt-6">
        <Bar
          data={data}
          options={{
            responsive: true,
            plugins: {
              legend: { labels: { color: "#cbd5e1" } },
            },
            scales: {
              x: { ticks: { color: "#cbd5e1" } },
              y: { ticks: { color: "#cbd5e1" }, min: 0, max: 1 },
            },
          }}
        />
      </div>
    </div>
  )
}

BenchmarkChart.propTypes = {
  benchmark: PropTypes.shape({
    summary: PropTypes.shape({
      model_average: PropTypes.object,
      baseline_average: PropTypes.object,
    }),
  }),
}

export default BenchmarkChart
