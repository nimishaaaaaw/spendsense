import { NavLink } from 'react-router-dom'
import Icon from '../shared/Icon.jsx'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: 'dashboard' },
  { to: '/upload', label: 'Upload', icon: 'cloud_upload' },
  { to: '/insights', label: 'Insights', icon: 'insights' },
  { to: '/subscriptions', label: 'Subs', icon: 'event_repeat' },
]

export default function BottomNav() {
  return (
    <nav className="md:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-md pb-md pt-sm bg-surface-container-lowest/95 backdrop-blur-md border-t border-outline-variant">
      {NAV_ITEMS.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            `flex flex-col items-center justify-center p-sm rounded-xl transition-all active:scale-95 ${
              isActive ? 'text-primary bg-primary/5' : 'text-on-surface-variant'
            }`
          }
        >
          {({ isActive }) => (
            <>
              <Icon name={item.icon} filled={isActive} />
              <span className="font-label-sm text-label-sm mt-1">{item.label}</span>
            </>
          )}
        </NavLink>
      ))}
    </nav>
  )
}