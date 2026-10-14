import { Link } from 'react-router-dom'
import { Frame } from '../components/ui/Frame'

export default function NotFound() {
  return (
    <div className="mx-auto max-w-lg py-16">
      <Frame label="err://404" bodyClassName="space-y-4 p-8 text-center">
        <p className="font-display text-7xl leading-none text-alert">404</p>
        <p className="font-display text-2xl uppercase text-ink">Signal lost</p>
        <p className="text-xs text-dim">
          The requested path does not exist in this catalog.
        </p>
        <div className="pt-2">
          <Link to="/" className="btn btn-primary">
            [ return to root ]
          </Link>
        </div>
      </Frame>
    </div>
  )
}
