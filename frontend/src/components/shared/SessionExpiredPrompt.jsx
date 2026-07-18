import { Link } from 'react-router-dom'
import Card from './Card.jsx'
import Button from './Button.jsx'
import Icon from './Icon.jsx'

export default function SessionExpiredPrompt() {
  return (
    <Card className="max-w-md mx-auto text-center flex flex-col items-center gap-md">
      <div className="w-14 h-14 bg-tertiary-fixed rounded-full flex items-center justify-center">
        <Icon name="hourglass_disabled" className="text-tertiary" filled />
      </div>
      <div>
        <h2 className="font-headline-md text-headline-md mb-xs">Your session has ended</h2>
        <p className="font-body-md text-on-surface-variant">
          For your privacy, we don't keep your data between long gaps of inactivity.
          Upload your statement again to pick up where you left off.
        </p>
      </div>
      <Link to="/upload">
        <Button variant="primary">Upload statement</Button>
      </Link>
    </Card>
  )
}