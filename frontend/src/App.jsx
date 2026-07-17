import { SessionProvider } from './context/SessionContext.jsx'

function App() {
  return (
    <SessionProvider>
      <div className="min-h-screen bg-background flex items-center justify-center">
        <h1 className="font-display text-display text-primary">SpendSense</h1>
      </div>
    </SessionProvider>
  )
}

export default App