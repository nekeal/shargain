import { z } from "zod"
import { useState } from "react"
import { useNavigate } from "@tanstack/react-router"
import { useTranslation } from "react-i18next"
import cn from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

import {
  getMe,
  shargainPublicApiAuthSignupView
} from '@/lib/api/sdk.gen'
import { refreshCsrfToken } from '@/lib/csrf';
import { useCsrfToken } from '@/hooks/useCsrfToken';
import { useAuth } from "@/context/auth";

// Zod schema for signup form validation
const signupSchema = z.object({
  email: z.email("Invalid email address").min(1, "Email is required"),
  password: z.string().min(8, "Password must be at least 8 characters long"),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
})

type SignupFormInputs = z.infer<typeof signupSchema>

export function SignupForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { login } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [errors, setErrors] = useState<Partial<SignupFormInputs>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [apiError, setApiError] = useState("")
  const { csrfToken } = useCsrfToken()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setApiError("")

    // Validate form inputs with Zod
    const formData = { email, password, confirmPassword }
    const result = signupSchema.safeParse(formData)

    if (!result.success) {
      // If validation fails, set errors and stop submission
      const fieldErrors = result.error.flatten().fieldErrors
      setErrors({
        email: fieldErrors.email?.[0],
        password: fieldErrors.password?.[0],
        confirmPassword: fieldErrors.confirmPassword?.[0]
      })
      setIsSubmitting(false)
      return
    }

    setErrors({})

    try {
      // Perform signup
      const response = await shargainPublicApiAuthSignupView({
        body: {
          email,
          password
        },
        headers: {
          "X-CSRFToken": csrfToken
        }
      })

      if (response.data.success) {
        // After successful signup, get a new CSRF token for the authenticated session
        await refreshCsrfToken();
        
        // Get user data and update auth context
        const userResponse = await getMe()
        login(userResponse.data)

        // Redirect to dashboard on successful signup
        navigate({ to: "/dashboard" })
      } else {
        setApiError(response.data.message || t("auth.signup.signupFailed"))
      }
    } catch (error: any) {
      setApiError(error?.message || t("auth.login.networkError"))
      console.error("Signup error:", error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card className="w-full border-0 bg-white shadow-lg rounded-xl overflow-hidden">
        <CardHeader className="text-center pb-6 pt-8">
          <CardTitle className="text-2xl font-bold text-gray-800">{t("auth.signup.title")}</CardTitle>
          <CardDescription className="text-gray-600">
            {t("auth.signup.description")}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-5 px-8">
          <form onSubmit={handleSubmit}>
            <div className="flex flex-col gap-6">
              <div className="space-y-2">
                <Label htmlFor="signup-email" className="text-gray-700">{t("auth.signup.emailLabel")}</Label>
                <Input
                  id="signup-email"
                  type="email"
                  placeholder={t("auth.signup.emailPlaceholder")}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className={`border-2 ${errors.email ? "border-red-500 focus:border-red-500 focus:ring-4 focus:ring-red-100" : "border-gray-200 hover:border-gray-300 focus:border-violet-500 focus:ring-4 focus:ring-violet-100"} transition-all duration-300`}
                />
                {errors.email && (
                  <p className="text-red-500 text-sm mt-1">{errors.email}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="signup-password" className="text-gray-700">{t("auth.signup.passwordLabel")}</Label>
                <Input
                  id="signup-password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className={`border-2 ${errors.password ? "border-red-500 focus:border-red-500 focus:ring-4 focus:ring-red-100" : "border-gray-200 hover:border-gray-300 focus:border-violet-500 focus:ring-4 focus:ring-violet-100"} transition-all duration-300`}
                />
                {errors.password && (
                  <p className="text-red-500 text-sm mt-1">{errors.password}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="signup-confirm-password" className="text-gray-700">{t("auth.signup.confirmPasswordLabel")}</Label>
                <Input
                  id="signup-confirm-password"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  className={`border-2 ${errors.confirmPassword ? "border-red-500 focus:border-red-500 focus:ring-4 focus:ring-red-100" : "border-gray-200 hover:border-gray-300 focus:border-violet-500 focus:ring-4 focus:ring-violet-100"} transition-all duration-300`}
                />
                {errors.confirmPassword && (
                  <p className="text-red-500 text-sm mt-1">{errors.confirmPassword}</p>
                )}
              </div>
              {apiError && (
                <div className="text-red-500 text-sm bg-red-50 p-3 rounded-lg">
                  {apiError}
                </div>
              )}
              <div className="flex flex-col gap-3">
                <Button
                  type="submit"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? t("auth.signup.signingUp") : t("auth.signup.submitButton")}
                </Button>
              </div>
            </div>
            <div className="mt-4 text-center text-sm text-gray-600">
              {t("auth.signup.alreadyHaveAccount")}{" "}
              <a onClick={(e) => { e.preventDefault(); navigate({ to: '/auth/signin' }); }} className="text-violet-600 hover:text-violet-800 transition-colors duration-200">
                {t("auth.signup.loginLink")}
              </a>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
