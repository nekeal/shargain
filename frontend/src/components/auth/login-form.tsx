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

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card className="w-full border-0 bg-white shadow-lg rounded-xl overflow-hidden">
        <CardHeader className="text-center pb-6 pt-8">
          <CardTitle className="text-2xl font-bold text-gray-800">Login to your account</CardTitle>
          <CardDescription className="text-gray-600">
            Enter your email below to login to your account
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-5 px-8">
          <form>
            <div className="flex flex-col gap-6">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-gray-700">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="m@example.com"
                  required
                  className="border-2 border-gray-200 hover:border-gray-300 focus:border-violet-500 focus:ring-4 focus:ring-violet-100 transition-all duration-300"
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center">
                  <Label htmlFor="password" className="text-gray-700">Password</Label>
                  <a
                    href="#"
                    className="ml-auto inline-block text-sm text-violet-600 hover:text-violet-800 transition-colors duration-200"
                  >
                    Forgot your password?
                  </a>
                </div>
                <Input 
                  id="password" 
                  type="password" 
                  required 
                  className="border-2 border-gray-200 hover:border-gray-300 focus:border-violet-500 focus:ring-4 focus:ring-violet-100 transition-all duration-300"
                />
              </div>
              <div className="flex flex-col gap-3">
                <Button 
                  type="submit" 
                  className="bg-gradient-to-r from-violet-600 to-indigo-700 hover:from-violet-700 hover:to-indigo-800 shadow-md hover:shadow-lg transition-all duration-300"
                >
                  Login
                </Button>
                <Button 
                  variant="outline" 
                  className="border-2 border-gray-200 hover:border-gray-300 text-gray-700 hover:text-gray-900 transition-all duration-300"
                >
                  Login with Google
                </Button>
              </div>
            </div>
            <div className="mt-4 text-center text-sm text-gray-600">
              Don&apos;t have an account?{" "}
              <a href="#" className="text-violet-600 hover:text-violet-800 transition-colors duration-200">
                Sign up
              </a>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
