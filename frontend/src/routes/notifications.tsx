import { createFileRoute, redirect } from '@tanstack/react-router'
import { Bell } from 'lucide-react'
import { useTranslation } from 'react-i18next'
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
  const { t } = useTranslation()
  return (
    <div className="min-h-screen bg-secondary">
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="mb-8">
          <h1 className="flex items-center gap-3 text-2xl font-semibold text-foreground">
            <Bell className="w-6 h-6 text-primary" aria-hidden="true" />
            {t('notifications.title')}
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            {t('notifications.subtitle')}
          </p>
        </div>
        <div className="bg-card border border-border rounded-xl">
          <NotificationListPage />
        </div>
      </main>
    </div>
  )
}
