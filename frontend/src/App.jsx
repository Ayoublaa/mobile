import Dashboard from "./Dashboard"

function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <header className="mb-6 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.3em] text-cyan-400">Mobile API Misuse Detector</p>
            <h1 className="mt-2 text-3xl font-semibold text-white">Dashboard des abus API mobiles</h1>
            <p className="mt-2 max-w-2xl text-slate-300">Surveillez les spikes, le bruteforce, les scans et recevez des recommandations d’atténuation.</p>
          </div>
        </header>
        <main>
          <Dashboard />
        </main>
      </div>
    </div>
  )
}

export default App
