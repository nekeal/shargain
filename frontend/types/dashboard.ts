export interface MonitoredUrl {
  id: string
  name: string
  url: string
  isActive: boolean
  lastChecked?: string
  offersFound?: number
}

export interface OfferMonitor {
  id?: number
  name: string
  urls: MonitoredUrl[]
  enable_notifications: boolean
  notification_config: {
    telegram: boolean
    email: boolean
  }
}
