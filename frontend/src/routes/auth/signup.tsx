import { createFileRoute } from '@tanstack/react-router'
import { SignupForm } from '@/components/auth/signup-form'

export const Route = createFileRoute('/auth/signup')({
  component: Signup,
})

function Signup() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <SignupForm />
      </div>
    </div>
  )
}
