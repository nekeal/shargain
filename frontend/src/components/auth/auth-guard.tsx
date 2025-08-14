import { useEffect, useState } from "react"
import { useRouter } from "@tanstack/react-router"
import { Bell } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

interface AuthGuardProps {
  children: React.ReactNode
}

export function AuthGuard({ children }: AuthGuardProps) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)
  const router = useRouter()

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem("auth_token")
      const user = localStorage.getItem("user")

      if (token && user) {
        setIsAuthenticated(true)
      } else {
        setIsAuthenticated(false)
        router.navigate({ to: "/auth" })
      }
    }

    checkAuth()
  }, [router])

  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-100 flex items-center justify-center">
        <Card className="border-0 bg-white/60 backdrop-blur-sm">
          <CardContent className="flex items-center justify-center p-8">
            <div className="text-center">
              <Bell className="h-12 w-12 text-violet-600 mx-auto mb-4 animate-pulse" />
              <div className="text-lg font-medium text-gray-900 mb-2">Loading...</div>
              <div className="text-sm text-gray-600">Checking authentication status</div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null // Will redirect to auth page
  }

  return children
}
