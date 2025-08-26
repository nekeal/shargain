import { createFileRoute } from '@tanstack/react-router'
import { LoginForm } from '@/components/auth/login-form'

export const Route = createFileRoute('/auth/signin')({
  component: Auth,
})

function Auth() {
  console.log("Auth")
  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <LoginForm />
      </div>
    </div>
  )
}
