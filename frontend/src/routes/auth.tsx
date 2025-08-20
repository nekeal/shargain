import { createFileRoute } from '@tanstack/react-router'
import { LoginForm } from '@/components/auth/login-form'
import { Card, CardContent } from '@/components/ui/card'

export const Route = createFileRoute('/auth')({
  component: Auth,
})

function Auth() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="border-0 bg-white/60 backdrop-blur-sm shadow-xl">
        <CardContent className="p-8">
          <LoginForm />
        </CardContent>
      </Card>
    </div>
  )
}
