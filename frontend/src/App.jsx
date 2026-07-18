import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { SessionProvider } from './context/SessionContext.jsx'
import AppShell from './components/layout/AppShell.jsx'
import UploadPage from './pages/UploadPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import SubscriptionsPage from './pages/SubscriptionsPage.jsx'
import InsightsPage from './pages/InsightsPage.jsx'
import TransactionsPage from './pages/TransactionsPage.jsx'

function Placeholder({ name }) {
  return <p className="font-body-md text-on-surface-variant">{name} page goes here.</p>
}

function App() {
  return (
    <SessionProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AppShell title="Dashboard"><DashboardPage /></AppShell>} />
          <Route path="/upload" element={<AppShell title="Upload"><UploadPage /></AppShell>} />
          <Route path="/insights" element={<AppShell title="Insights"><InsightsPage /></AppShell>} />
          <Route path="/subscriptions" element={<AppShell title="Subscriptions"><SubscriptionsPage /></AppShell>} />
          <Route path="/transactions" element={<AppShell title="Transactions"><TransactionsPage /></AppShell>} />
          
        </Routes>
      </BrowserRouter>
    </SessionProvider>
  )
}

export default App