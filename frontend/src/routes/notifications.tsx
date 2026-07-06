import { createFileRoute, redirect } from '@tanstack/react-router'
import { Bell } from 'lucide-react'
import {NotificationListPage} from "@/components/notifications";

export const Route = createFileRoute('/notifications')({
  component: NotificationsPage,
  beforeLoad: ({ context }) => {
    if (!context.auth.isAuthenticated) {
      throw redirect({
        to: '/auth/signin',
      })
    }
  },
})

function NotificationsPage() {
  return (
    <div className="min-h-screen bg-secondary">
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="mb-8">
          <h1 className="flex items-center gap-3 text-2xl font-semibold text-foreground">
            <Bell className="w-6 h-6 text-primary" aria-hidden="true" />
            Notification Configurations
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Manage your notification configurations for receiving alerts when new offers are found.
          </p>
        </div>
        <div className="bg-card border border-border rounded-xl">
          <NotificationListPage />
        </div>
      </main>
    </div>
  )
}
