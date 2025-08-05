export interface MonitoredUrl {
  id: number
  name: string
  url: string
  isActive: boolean
  lastChecked?: string
  offersFound?: number
}

export interface OfferMonitor {
  id: number
  name: string
  urls: Array<MonitoredUrl>
  enableNotifications: boolean
  isActive: boolean
}
