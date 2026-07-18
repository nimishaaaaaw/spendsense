import { useNavigate } from 'react-router-dom'
import { useSession } from '../context/SessionContext.jsx'
import DropZone from '../components/upload/DropZone.jsx'
import Card from '../components/shared/Card.jsx'
import Button from '../components/shared/Button.jsx'
import Icon from '../components/shared/Icon.jsx'

export default function UploadPage() {
  const { uploadStatement, uploadSample, isLoading, error } = useSession()
  const navigate = useNavigate()

  async function handleFileSelected(file) {
    try {
      await uploadStatement(file)
      navigate('/')
    } catch {
      // error is already captured in session context state and rendered below
    }
  }

  async function handleTrySample() {
    try {
      await uploadSample()
      navigate('/')
    } catch {
      // same as above
    }
  }

  return (
    <div className="flex flex-col gap-lg max-w-3xl">
      <div>
        <h1 className="font-headline-lg text-headline-lg text-on-background mb-xs">Upload Statement</h1>
        <p className="text-on-surface-variant font-body-lg">
          Import your bank/UPI export and SpendSense will clean, categorize, and analyze it.
        </p>
      </div>

      <DropZone onFileSelected={handleFileSelected} isLoading={isLoading} />

      <Card className="flex items-center justify-between gap-md flex-wrap">
        <div>
          <h4 className="font-label-md text-label-md text-on-surface font-bold">Want a tour first?</h4>
          <p className="font-body-md text-on-surface-variant">
            Try a realistic 6-month synthetic dataset before uploading your own.
          </p>
        </div>
        <Button variant="secondary" onClick={handleTrySample} disabled={isLoading}>
          <Icon name="play_circle" className="text-sm" /> Try Sample Data
        </Button>
      </Card>

      {error && (
        <Card className="border-error bg-error-container/20">
          <div className="flex items-start gap-md">
            <Icon name="error" className="text-error" filled />
            <div>
              <p className="font-label-md text-label-md text-on-error-container mb-xs">Upload failed</p>
              <p className="font-body-md text-on-surface-variant">{error}</p>
            </div>
          </div>
        </Card>
      )}

      <Card className="bg-secondary-container/10 border-secondary-container/30">
        <div className="flex items-start gap-md">
          <div className="w-10 h-10 bg-secondary-container/30 rounded-lg flex items-center justify-center flex-shrink-0">
            <Icon name="verified_user" className="text-on-secondary-container" />
          </div>
          <div>
            <h4 className="font-label-md text-label-md text-on-surface font-bold uppercase tracking-wide mb-xs">
              Privacy Guarantee
            </h4>
            <p className="font-body-md text-on-surface-variant">
              Your data is processed in-memory for this session only. Nothing is written to a database,
              and everything is gone once your session ends.
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}