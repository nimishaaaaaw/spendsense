import { NavLink } from 'react-router-dom'
import Icon from '../shared/Icon.jsx'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: 'dashboard' },
  { to: '/upload', label: 'Upload', icon: 'cloud_upload' },
  { to: '/insights', label: 'Insights', icon: 'insights' },
  { to: '/subscriptions', label: 'Subscriptions', icon: 'loyalty' },
]

export default function Sidebar() {
  return (
    <aside className="hidden md:flex fixed left-0 top-0 h-full flex-col gap-lg p-lg bg-surface-container-lowest border-r border-outline-variant w-64 z-50">
      <div className="flex items-center gap-sm mb-md">
        <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
          <Icon name="account_balance_wallet" className="text-on-primary" filled />
        </div>
        <h1 className="font-headline-md text-headline-md font-bold text-on-surface">SpendSense</h1>
      </div>

      <nav className="flex flex-col gap-xs flex-grow">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-md px-md py-sm rounded-lg transition-all ${
                isActive
                  ? 'bg-secondary-container text-on-secondary-container'
                  : 'text-on-surface-variant hover:bg-surface-container-low'
              }`
            }
          >
            <Icon name={item.icon} />
            <span className="font-label-md text-label-md">{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}