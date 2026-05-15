import { useState, useEffect } from "react"

function ActiveSecurityDashboard() {
  const [settings, setSettings] = useState({ email_alert_threshold: 1, security_active: true })
  const [history, setHistory] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [message, setMessage] = useState("")

  useEffect(() => {
    fetchSettings()
    fetchHistory()
  }, [])

  const fetchSettings = async () => {
    try {
      const res = await fetch("/settings")
      if (res.ok) {
        const data = await res.json()
        setSettings(data)
      }
    } catch (err) {
      console.error("Failed to fetch settings", err)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchHistory = async () => {
    try {
      const res = await fetch("/alerts/history")
      if (res.ok) {
        const data = await res.json()
        setHistory(data.history)
      }
    } catch (err) {
      console.error("Failed to fetch history", err)
    }
  }

  const handleUpdateSettings = async (newSettings) => {
    setIsSaving(true)
    setMessage("")
    try {
      const res = await fetch("/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newSettings),
      })
      if (res.ok) {
        setSettings((prev) => ({ ...prev, ...newSettings }))
        setMessage("Paramètres mis à jour avec succès.")
        setTimeout(() => setMessage(""), 3000)
      }
    } catch (err) {
      console.error("Failed to update settings", err)
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) return <div className="animate-pulse text-slate-400">Chargement de la sécurité active...</div>

  return (
    <div className="grid gap-6">
      {/* Configuration Section */}
      <div className="rounded-[2rem] border border-slate-800 bg-slate-900/40 p-8 backdrop-blur-xl shadow-2xl">
        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-white">Sécurité Active</h2>
            <p className="mt-2 text-slate-400 text-sm">Configurez les seuils d'alerte et l'état du système de défense.</p>
          </div>
          <div className="flex items-center gap-4">
            <span className={`text-sm font-medium ${settings.security_active ? 'text-emerald-400' : 'text-rose-400'}`}>
              {settings.security_active ? 'SYSTÈME ARMÉ' : 'DÉSACTIVÉ'}
            </span>
            <button
              onClick={() => handleUpdateSettings({ security_active: !settings.security_active })}
              className={`relative h-7 w-14 rounded-full transition-colors duration-300 ${settings.security_active ? 'bg-emerald-500' : 'bg-slate-700'}`}
            >
              <div className={`absolute top-1 h-5 w-5 rounded-full bg-white shadow-md transition-transform duration-300 ${settings.security_active ? 'translate-x-8' : 'translate-x-1'}`} />
            </button>
          </div>
        </div>

        <div className="mt-10 grid gap-8 md:grid-cols-2">
          <div className="space-y-4">
            <label className="flex justify-between text-sm font-medium text-slate-300">
              <span>Seuil d'anomalies pour alerte</span>
              <span className="text-cyan-400 font-bold">{settings.email_alert_threshold}</span>
            </label>
            <input
              type="range"
              min="1"
              max="50"
              value={settings.email_alert_threshold}
              onChange={(e) => setSettings({ ...settings, email_alert_threshold: parseInt(e.target.value) })}
              onMouseUp={() => handleUpdateSettings({ email_alert_threshold: settings.email_alert_threshold })}
              className="w-full h-2 rounded-lg bg-slate-800 appearance-none cursor-pointer accent-cyan-500"
            />
            <p className="text-xs text-slate-500 italic">Nombre d'anomalies détectées dans un fichier de log avant l'envoi d'un rapport email.</p>
          </div>

          <div className="flex items-end justify-end">
            {message && (
              <span className="text-sm text-emerald-400 font-medium animate-fade-in">{message}</span>
            )}
          </div>
        </div>
      </div>

      {/* History Section */}
      <div className="rounded-[2rem] border border-slate-800 bg-slate-900/40 p-8 backdrop-blur-xl shadow-2xl overflow-hidden">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl font-semibold text-white">Journal des Alertes</h2>
          <button 
            onClick={fetchHistory}
            className="text-xs uppercase tracking-widest text-slate-500 hover:text-cyan-400 transition-colors"
          >
            Rafraîchir
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="pb-4 text-xs font-semibold uppercase tracking-widest text-slate-500">Date & Heure</th>
                <th className="pb-4 text-xs font-semibold uppercase tracking-widest text-slate-500">Sujet</th>
                <th className="pb-4 text-xs font-semibold uppercase tracking-widest text-slate-500">Destinataire</th>
                <th className="pb-4 text-xs font-semibold uppercase tracking-widest text-slate-500">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {history.length === 0 ? (
                <tr>
                  <td colSpan="4" className="py-8 text-center text-slate-500 text-sm">Aucune alerte enregistrée.</td>
                </tr>
              ) : (
                history.map((alert) => (
                  <tr key={alert.id} className="group hover:bg-slate-800/20 transition-colors">
                    <td className="py-4 text-sm text-slate-400">
                      {new Date(alert.timestamp).toLocaleString('fr-FR')}
                    </td>
                    <td className="py-4 text-sm font-medium text-slate-200">
                      {alert.subject}
                    </td>
                    <td className="py-4 text-sm text-slate-400">
                      {alert.recipient}
                    </td>
                    <td className="py-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        alert.status === 'Sent' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                      }`}>
                        {alert.status === 'Sent' ? 'ENVOYÉ' : 'ÉCHEC'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default ActiveSecurityDashboard
