import { Component } from 'react'
import { ErrorState } from './States'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  componentDidCatch(error, info) {
    console.error('Render error:', error, info)
  }

  render() {
    if (this.state.error) {
      return (
        <div className="min-h-screen bg-bg px-4 py-16">
          <div className="mx-auto max-w-2xl">
            <ErrorState
              message={this.state.error?.message || 'Unexpected runtime error.'}
              onRetry={() => window.location.reload()}
            />
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
