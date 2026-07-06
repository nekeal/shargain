export function getQuotaProgressVariant(used: number, limit: number): "success" | "warning" | "destructive" {
  if (limit <= 0 || used >= limit) {
    return "destructive"
  }
  if (used / limit >= 0.8) {
    return "warning"
  }
  return "success"
}