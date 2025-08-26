import { useEffect, useState } from 'react'
import { shargainPublicApiAuthGetCsrfToken } from '@/lib/api/sdk.gen'

export const useCsrfToken = () => {
  const [csrfToken, setCsrfToken] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    const fetchCsrfToken = async () => {
      try {
        setLoading(true)
        const response = await shargainPublicApiAuthGetCsrfToken()
        setCsrfToken(response.data.csrfToken || '')
      } catch (err) {
        console.error('Failed to fetch CSRF token:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchCsrfToken()
  }, [])

  return { csrfToken, loading }
}
