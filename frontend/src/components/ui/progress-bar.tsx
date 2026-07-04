import cn from "@/lib/utils"

interface ProgressBarProps {
  value: number
  max?: number
  className?: string
  variant?: "default" | "success" | "warning" | "destructive"
  showLabel?: boolean
}

export function ProgressBar({
  value,
  max = 100,
  className,
  variant = "default",
  showLabel = false,
}: ProgressBarProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)

  const getTrackClass = () => {
    switch (variant) {
      case "success":
        return percentage >= 100 ? "bg-destructive" : percentage >= 80 ? "bg-warning" : "bg-success"
      case "warning":
        return "bg-warning"
      case "destructive":
        return "bg-destructive"
      default:
        return "bg-primary"
    }
  }

  return (
    <div className={cn("w-full space-y-1", className)}>
      {showLabel && (
        <div className="flex justify-between text-xs">
          <span className="text-muted-foreground">Progress</span>
          <span className="font-medium text-foreground">{value}/{max}</span>
        </div>
      )}
      <div className="h-2 bg-secondary rounded-full overflow-hidden" role="progressbar" aria-valuenow={value} aria-valuemin={0} aria-valuemax={max} aria-label="Progress">
        <div
          className={cn("h-full rounded-full transition-all duration-300 ease-out-quart motion-reduce:transition-none", getTrackClass())}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}