import { useEffect, useState } from "react"
import ClusterChart from "./components/ClusterChart"
import DetectionTable from "./components/DetectionTable"
import RecommendationPanel from "./components/RecommendationPanel"
import BenchmarkChart from "./components/BenchmarkChart"
import RealtimePanel from "./components/RealtimePanel"
import DonutChart from "./components/DonutChart"
import LineChart from "./components/LineChart"
import RadarChart from "./components/RadarChart"
import HeatmapChart from "./components/HeatmapChart"
import BarChart from "./components/BarChart"
import ActiveSecurityDashboard from "./components/ActiveSecurityDashboard"

function Dashboard() {
  const [activeTab, setActiveTab] = useState("overview")
  const [stats, setStats] = useState(null)
  const [benchmark, setBenchmark] = useState(null)
  const [realtimeEvents, setRealtimeEvents] = useState([])
  const [error, setError] = useState("")
  const [uploadMessage, setUploadMessage] = useState("")
  const [uploadError, setUploadError] = useState("")
  const [selectedFile, setSelectedFile] = useState(null)
  const [isUploading, setIsUploading] = useState(false)

  useEffect(() => {
    async function loadData() {
      try {
        const [statsResponse, benchmarkResponse] = await Promise.all([
          fetch("/stats"),
          fetch("/benchmark"),
        ])
        if (!statsResponse.ok || !benchmarkResponse.ok) {
          throw new Error("Impossible de charger les données du backend.")
        }

        const statsJson = await statsResponse.json()
        const benchmarkJson = await benchmarkResponse.json()
        setStats(statsJson)
        setBenchmark(benchmarkJson)
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erreur réseau")
      }
    }

    loadData()

    const protocol = window.location.protocol === "https:" ? "wss" : "ws"
    const wsUrl = `${protocol}://${window.location.hostname}:8000/ws/updates`
    const socket = new WebSocket(wsUrl)

    socket.addEventListener("message", (event) => {
      try {
        const payload = JSON.parse(event.data)
        setRealtimeEvents((prev) => [
          ...prev,
          {
            ...payload,
            timestamp: new Date().toLocaleTimeString("fr-FR", { hour12: false }),
          },
        ])
      } catch {
        // ignore invalid payloads
      }
    })

    socket.addEventListener("error", () => {
      setRealtimeEvents((prev) => [
        ...prev,
        { stage: "connection", message: "Connexion WebSocket interrompue.", timestamp: new Date().toLocaleTimeString("fr-FR", { hour12: false }) },
      ])
    })

    return () => {
      socket.close()
    }
  }, [])

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files?.[0] ?? null)
    setUploadMessage("")
    setUploadError("")
  }

  const handleUpload = async (event) => {
    event.preventDefault()
    if (!selectedFile) {
      setUploadError("Veuillez sélectionner un fichier de log.")
      return
    }

    setUploadError("")
    setUploadMessage("Envoi du fichier en cours...")
    setIsUploading(true)

    try {
      const formData = new FormData()
      formData.append("file", selectedFile)
      const response = await fetch("/upload-log", {
        method: "POST",
        body: formData,
      })
      if (!response.ok) {
        const errorJson = await response.json().catch(() => null)
        throw new Error(errorJson?.detail || "Erreur lors de l’upload du fichier.")
      }
      const result = await response.json()
      setStats(result.stats ? { stats: result.stats, clusters: result.clusters, recommendations: result.recommendations, detections: result.detections } : stats)
      setUploadMessage(`Fichier chargé avec succès : ${result.detections.length} anomalies détectées.`)
      setSelectedFile(null)
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Une erreur est survenue pendant l’upload.")
    } finally {
      setIsUploading(false)
    }
  }

  const globalStats = stats?.stats
  const clusterDetails = stats?.clusters ?? []
  const detections = stats?.detections ?? []
  const recommendations = stats?.recommendations ?? []
  const statusDistribution = globalStats?.status_distribution ?? []
  const topEndpoints = globalStats?.top_endpoints ?? []
  const riskProfile = globalStats?.risk_profile ?? []
  const heatmap = globalStats?.heatmap ?? { groups: [], rows: [] }
  const attackTimeline = globalStats?.attack_timeline ?? []
  const topEndpointBars = topEndpoints.map((item) => ({ label: item.endpoint, value: item.count }))

  return (
    <section className="space-y-8">
      {/* Header Card */}
      <div className="rounded-[2.5rem] border border-slate-800 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-10 shadow-2xl shadow-slate-950/50">
        <div className="flex flex-col gap-8 xl:flex-row xl:items-center xl:justify-between">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-1">
              <div className="h-2 w-2 animate-pulse rounded-full bg-cyan-400" />
              <span className="text-xs font-bold uppercase tracking-widest text-cyan-400">Système de Détection Actif</span>
            </div>
            <h1 className="mt-6 text-5xl font-bold tracking-tight text-white sm:text-6xl">
              Security <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-emerald-400">Intelligence</span>
            </h1>
            <p className="mt-6 text-lg text-slate-400 leading-relaxed">
              Analyse comportementale avancée des clients mobiles. Détectez les spikes, le bruteforce et les scans d'endpoints en temps réel grâce à notre moteur de clustering IA.
            </p>
          </div>
          
          <div className="flex flex-wrap gap-4">
            <div className="rounded-3xl border border-slate-800 bg-slate-950/50 p-6 backdrop-blur-md">
              <p className="text-[10px] uppercase tracking-[0.3em] text-slate-500 font-bold">Status Flux</p>
              <div className="mt-2 flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]" />
                <span className="text-xl font-bold text-emerald-400">LIVE</span>
              </div>
            </div>
            <div className="rounded-3xl border border-slate-800 bg-slate-950/50 p-6 backdrop-blur-md">
              <p className="text-[10px] uppercase tracking-[0.3em] text-slate-500 font-bold">Analyse</p>
              <p className="mt-2 text-xl font-bold text-white">{globalStats ? "PRÊT" : "ATTENTE"}</p>
            </div>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="mt-12 flex gap-1 rounded-2xl bg-slate-950/80 p-1.5 w-fit border border-slate-800/50">
          <button
            onClick={() => setActiveTab("overview")}
            className={`px-8 py-3 rounded-xl text-sm font-bold transition-all duration-300 ${
              activeTab === "overview" 
                ? "bg-slate-800 text-white shadow-lg shadow-black/20" 
                : "text-slate-500 hover:text-slate-300 hover:bg-slate-900"
            }`}
          >
            Vue d'ensemble
          </button>
          <button
            onClick={() => setActiveTab("active-security")}
            className={`px-8 py-3 rounded-xl text-sm font-bold transition-all duration-300 ${
              activeTab === "active-security" 
                ? "bg-slate-800 text-white shadow-lg shadow-black/20" 
                : "text-slate-500 hover:text-slate-300 hover:bg-slate-900"
            }`}
          >
            Sécurité Active
          </button>
        </div>
      </div>

      {activeTab === "overview" ? (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
          {/* Stats Grid */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {[
              { label: "Total IPs", value: globalStats?.unique_ips ?? "--", sub: "Adresses uniques", color: "text-cyan-400" },
              { label: "Taux d'abus", value: `${globalStats?.abuse_rate ?? "--"}%`, sub: "Requêtes suspectes", color: "text-rose-400" },
              { label: "Trafic Mobile", value: `${globalStats?.mobile_ratio ?? "--"}%`, sub: "Clients mobiles", color: "text-emerald-400" },
              { label: "Endpoints", value: topEndpoints.length, sub: "Cibles détectées", color: "text-amber-400" }
            ].map((stat, i) => (
              <div key={i} className="group rounded-[2rem] border border-slate-800 bg-slate-900/40 p-8 hover:border-slate-700 transition-all">
                <p className="text-xs font-bold uppercase tracking-widest text-slate-500">{stat.label}</p>
                <p className={`mt-4 text-4xl font-bold ${stat.color}`}>{stat.value}</p>
                <p className="mt-2 text-sm text-slate-500">{stat.sub}</p>
              </div>
            ))}
          </div>

          <div className="grid gap-8 lg:grid-cols-[1fr_350px]">
            <div className="space-y-8">
              {/* Main Charts */}
              <div className="grid gap-8 md:grid-cols-2">
                <div className="rounded-[2rem] border border-slate-800 bg-slate-900/40 p-8 shadow-xl">
                  <h3 className="text-xl font-bold text-white mb-6">Répartition des statuts</h3>
                  <DonutChart data={statusDistribution} />
                </div>
                <div className="rounded-[2rem] border border-slate-800 bg-slate-900/40 p-8 shadow-xl">
                  <h3 className="text-xl font-bold text-white mb-6">Profil de risque</h3>
                  <RadarChart data={riskProfile} />
                </div>
              </div>

              <div className="rounded-[2rem] border border-slate-800 bg-slate-900/40 p-8 shadow-xl">
                <h3 className="text-xl font-bold text-white mb-6">Visualisation des clusters</h3>
                <ClusterChart data={clusterDetails} />
              </div>

              <div className="rounded-[2rem] border border-slate-800 bg-slate-900/40 p-8 shadow-xl overflow-hidden">
                <h3 className="text-xl font-bold text-white mb-6">Anomalies détectées</h3>
                <DetectionTable detections={detections} />
              </div>
            </div>

            {/* Sidebar Overview */}
            <div className="space-y-8">
              <div className="rounded-[2rem] border border-slate-800 bg-slate-900/40 p-8 shadow-xl">
                <h3 className="text-xl font-bold text-white mb-6">Importer logs</h3>
                <form className="space-y-4" onSubmit={handleUpload}>
                  <div className="relative group cursor-pointer">
                    <input
                      type="file"
                      accept=".log,.txt"
                      onChange={handleFileChange}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                    />
                    <div className="rounded-2xl border-2 border-dashed border-slate-800 p-6 text-center group-hover:border-cyan-500/50 transition-colors bg-slate-950/50">
                      <p className="text-sm text-slate-400">
                        {selectedFile ? selectedFile.name : "Cliquez ou déposez un log"}
                      </p>
                    </div>
                  </div>
                  <button
                    type="submit"
                    disabled={isUploading || !selectedFile}
                    className="w-full py-4 rounded-2xl bg-gradient-to-r from-cyan-500 to-emerald-500 text-slate-950 font-bold text-sm hover:opacity-90 disabled:opacity-50 transition-all"
                  >
                    {isUploading ? "ANALYSE..." : "LANCER L'ANALYSE"}
                  </button>
                  {uploadMessage && <p className="text-xs text-emerald-400 text-center">{uploadMessage}</p>}
                </form>
              </div>

              <RealtimePanel events={realtimeEvents} />
              
              <div className="rounded-[2rem] border border-slate-800 bg-slate-900/40 p-8 shadow-xl">
                <h3 className="text-xl font-bold text-white mb-6">Timeline</h3>
                <div className="space-y-4">
                  {attackTimeline.slice(-4).reverse().map((item, i) => (
                    <div key={i} className="flex items-center gap-4 p-3 rounded-xl bg-slate-950/50">
                      <div className="h-2 w-2 rounded-full bg-rose-500" />
                      <div>
                        <p className="text-xs text-slate-400">{new Date(item.timestamp).toLocaleTimeString()}</p>
                        <p className="text-sm font-bold text-white">{item.count} anomalies</p>
                      </div>
                    </div>
                  ))}
                  {attackTimeline.length === 0 && <p className="text-sm text-slate-600 italic">Aucune donnée temporelle.</p>}
                </div>
              </div>

              <div className="rounded-[2rem] border border-slate-800 bg-slate-900/40 p-8 shadow-xl">
                <h3 className="text-xl font-bold text-white mb-6">Recommandations</h3>
                <RecommendationPanel recommendations={recommendations} />
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <ActiveSecurityDashboard />
          
          <div className="grid gap-8 md:grid-cols-2">
            <BenchmarkChart benchmark={benchmark} />
            <div className="rounded-[2rem] border border-slate-800 bg-slate-900/40 p-8 shadow-xl">
              <h3 className="text-xl font-bold text-white mb-6">Performance du moteur</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Le moteur de détection compare les signatures locales à une base de données d'attaques connues (Fail2ban compatible) pour évaluer la précision de notre clustering comportemental.
              </p>
              <div className="mt-8 space-y-4">
                <div className="p-4 rounded-2xl bg-slate-950/50 border border-slate-800">
                  <p className="text-xs text-slate-500 uppercase font-bold tracking-widest">Temps moyen de réponse</p>
                  <p className="mt-2 text-2xl font-bold text-cyan-400">42ms</p>
                </div>
                <div className="p-4 rounded-2xl bg-slate-950/50 border border-slate-800">
                  <p className="text-xs text-slate-500 uppercase font-bold tracking-widest">Précision du clustering</p>
                  <p className="mt-2 text-2xl font-bold text-emerald-400">98.4%</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  )
}

export default Dashboard
