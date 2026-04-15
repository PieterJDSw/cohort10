import { BrowserRouter, Link, Route, Routes } from 'react-router-dom'
import { AuditPage } from './pages/AuditPage'
import { DashboardPage } from './pages/DashboardPage'
import { LandingPage } from './pages/LandingPage'
import { ResultPage } from './pages/ResultPage'
import { TestPage } from './pages/TestPage'
import { cn, eyebrow } from './lib/ui'

function App() {
  return (
    <BrowserRouter>
      <div className="relative min-h-screen overflow-hidden">
        <div className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-72 bg-[radial-gradient(circle_at_top,_rgba(15,23,42,0.12),_transparent_60%)]" />
        <header className="sticky top-0 z-20 border-b border-white/50 bg-stone-50/75 backdrop-blur-xl">
          <div className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-4 py-5 sm:px-6 lg:px-8">
            <div>
              <p className={eyebrow}>Developer Assessment Platform</p>
              <Link
                to="/"
                className="font-display text-3xl tracking-tight text-slate-950 transition hover:text-amber-700"
              >
              MVP Assessment
            </Link>
            </div>
            <nav className="flex items-center gap-2 rounded-full border border-white/70 bg-white/75 p-1.5 shadow-lg shadow-slate-900/5">
              {[
                ['/', 'Start'],
                ['/dashboard', 'Dashboard'],
              ].map(([to, label]) => (
                <Link
                  key={to}
                  to={to}
                  className={cn(
                    'rounded-full px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-slate-950',
                  )}
                >
                  {label}
                </Link>
              ))}
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/test/:sessionId" element={<TestPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/result/:sessionId" element={<ResultPage />} />
            <Route path="/audit/:sessionId" element={<AuditPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
