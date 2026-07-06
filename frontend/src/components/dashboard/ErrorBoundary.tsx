"use client"

import { Component, ErrorInfo, ReactNode } from "react"
import { AlertCircle, RotateCcw } from "lucide-react"
import { useTranslation } from "react-i18next"
import { Button } from "@/components/ui/button"

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Dashboard ErrorBoundary caught an error:", error, errorInfo)
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    const { t } = useTranslation()

    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="flex min-h-screen bg-background items-center justify-center" role="alert" aria-live="assertive">
          <div className="bg-card border border-border rounded-2xl p-8 max-w-md text-center">
            <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
            <h2 className="text-lg font-semibold text-foreground mb-2">
              {t("dashboard.errorBoundary.title", "Something went wrong")}
            </h2>
            <p className="text-sm text-muted-foreground mb-6">
              {t("dashboard.errorBoundary.description", "An unexpected error occurred. Please try again.")}
            </p>
            <Button variant="outline" onClick={this.handleRetry} className="mt-4">
              <RotateCcw className="w-4 h-4 mr-2" />
              {t("dashboard.retry", "Retry")}
            </Button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}