import { useEffect, useState } from 'react'
import { shargainPublicApiAuthGetCsrfToken } from '@/lib/api/sdk.gen'

const updateCsrfToken = (token: string)=> {
    sessionStorage.setItem('csrfToken', token)

}

export const useCsrfToken = () => {
  const [csrfToken, setCsrfToken] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    const fetchCsrfToken = async () => {
      try {
        setLoading(true)
        const response = await shargainPublicApiAuthGetCsrfToken()
        const token = response.data.csrfToken || ''
        setCsrfToken(token)
        updateCsrfToken(token)
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
