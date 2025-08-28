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
  shargainPublicApiAuthLoginView
} from '@/lib/api/sdk.gen'

import {refreshCsrfToken} from "@/lib/csrf.ts";

const loginSchema = z.object({
  email: z.string().min(1, "Username or email is required"),
  password: z.string().min(1, "Password is required"),
})

type LoginFormInputs = z.infer<typeof loginSchema>

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [errors, setErrors] = useState<Partial<LoginFormInputs>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [apiError, setApiError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setApiError("")

    // Validate form inputs with Zod
    const result = loginSchema.safeParse({ email: username, password })

    if (!result.success) {
      // If validation fails, set errors and stop submission
      const fieldErrors = result.error.flatten().fieldErrors
      setErrors({
        email: fieldErrors.email?.[0],
        password: fieldErrors.password?.[0]
      })
      setIsSubmitting(false)
      return
    }

    setErrors({})

    try {
      const response = await shargainPublicApiAuthLoginView({
        body: {
          username,
          password
        }
      })

      if (response.data.success) {
        // After successful login, get a new CSRF token for the authenticated session
        await refreshCsrfToken();

        // Redirect to dashboard on successful login
        navigate({ to: "/dashboard" })
      } else {
        // Set error message from API response
        setApiError(response.data.message || t("auth.login.loginFailed"))
      }
    } catch (error: any) {
      // Handle network errors
      setApiError(error?.message || t("auth.login.networkError"))
      console.error("Login error:", error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card className="w-full border-0 bg-white shadow-lg rounded-xl overflow-hidden">
        <CardHeader className="text-center pb-6 pt-8">
          <CardTitle className="text-2xl font-bold text-gray-800">{t("auth.login.title")}</CardTitle>
          <CardDescription className="text-gray-600">
            {t("auth.login.description")}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-5 px-8">
          <form onSubmit={handleSubmit}>
            <div className="flex flex-col gap-6">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-gray-700">{t("auth.login.usernameOrEmailLabel")}</Label>
                <Input
                  id="email"
                  type="text"
                  autoComplete="username"
                  placeholder={t("auth.login.usernameOrEmailPlaceholder")}
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  className={`border-2 ${errors.email ? "border-red-500 focus:border-red-500 focus:ring-4 focus:ring-red-100" : "border-gray-200 hover:border-gray-300 focus:border-violet-500 focus:ring-4 focus:ring-violet-100"} transition-all duration-300`}
                />
                {errors.email && (
                  <p className="text-red-500 text-sm mt-1">{errors.email}</p>
                )}
              </div>
              <div className="space-y-2">
                <div className="flex items-center">
                  <Label htmlFor="password" className="text-gray-700">{t("auth.login.passwordLabel")}</Label>
                  <a
                    href="#"
                    className="ml-auto inline-block text-sm text-violet-600 hover:text-violet-800 transition-colors duration-200"
                  >
                    {t("auth.login.forgotPassword")}
                  </a>
                </div>
                <Input
                  id="password"
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
                  {isSubmitting ? t("auth.login.signingIn") : t("auth.login.submitButton")}
                </Button>

                {/*  TODO: implement google login*/}
                {/* <Button */}
                {/*  variant="outline" */}
                {/*  className="border-2 border-gray-200 hover:border-gray-300 text-gray-700 hover:text-gray-900 transition-all duration-300"*/}
                {/* >*/}
                {/*  Login with Google*/}
                {/* </Button>*/}
              </div>
            </div>
            <div className="mt-4 text-center text-sm text-gray-600">
              {t("auth.login.noAccount")}{" "}
              <a href="#" onClick={(e) => { e.preventDefault(); navigate({ to: '/auth/signup' }); }} className="text-violet-600 hover:text-violet-800 transition-colors duration-200">
                {t("auth.login.signUpLink")}
              </a>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
