import { createFileRoute } from '@tanstack/react-router'
import { AppHeader } from '@/components/app-header'
import {NotificationListPage} from "@/components/notifications";

export const Route = createFileRoute('/notifications')({
  component: NotificationsPage,
})

function NotificationsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 to-purple-50">
      <AppHeader />
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-violet-600 to-purple-600 bg-clip-text text-transparent mb-4">
            Notification Configurations
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Manage your notification configurations for receiving alerts when new offers are found.
          </p>
        </div>
        <div className="rounded-2xl shadow-xl p-6 backdrop-blur-sm bg-white/80">
          <NotificationListPage />
        </div>
      </main>
    </div>
  )
}
