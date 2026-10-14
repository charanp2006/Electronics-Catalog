import { useCallback, useEffect, useState } from 'react'
import { extractError } from '../services/api'

export function useApi(fetcher, deps = [], immediate = true) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(immediate)
  const [error, setError] = useState(null)

  const run = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setData(await fetcher())
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    if (immediate) run()
  }, [run, immediate])

  return { data, loading, error, refetch: run, setData }
}
