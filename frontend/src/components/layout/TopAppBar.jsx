import Icon from '../shared/Icon.jsx'

export default function TopAppBar({ title }) {
  return (
    <header className="flex justify-between items-center px-lg py-md w-full sticky top-0 z-40 bg-surface/80 backdrop-blur-md border-b border-outline-variant">
      <h2 className="font-headline-md text-headline-md font-bold text-on-surface">{title}</h2>
      <button className="w-10 h-10 flex items-center justify-center rounded-lg border border-outline-variant bg-surface-container-lowest hover:bg-surface-container transition-colors">
        <Icon name="notifications" className="text-primary" />
      </button>
    </header>
  )
}