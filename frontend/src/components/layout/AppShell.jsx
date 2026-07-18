import Sidebar from './Sidebar.jsx'
import BottomNav from './BottomNav.jsx'
import TopAppBar from './TopAppBar.jsx'

export default function AppShell({ title, children }) {
  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <div className="md:ml-64 pb-24 md:pb-0">
        <TopAppBar title={title} />
        <main className="max-w-container-max mx-auto px-gutter md:px-xl py-lg">
          {children}
        </main>
      </div>
      <BottomNav />
    </div>
  )
}