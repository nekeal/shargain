import { createFileRoute, useLoaderData } from '@tanstack/react-router'
import { useEffect, useState } from 'react'
import type { OfferMonitor } from '@/types/dashboard';
import { DashboardHeader } from "@/components/dashboard/dashboard-header.tsx";
import { MonitorSettings } from '@/components/dashboard/monitor-settings';
import { MonitoredWebsites } from '@/components/dashboard/monitored-websites';
import { DashboardSidebar } from '@/components/dashboard/dashboard-sidebar';
import { shargainPublicApiApiGetMyTarget } from '@/lib/api';

export const Route = createFileRoute('/dashboard')({
    component: DashboardContent,
    loader: async () => {
        const response = await shargainPublicApiApiGetMyTarget();
        return response.data as OfferMonitor;
    }
})

function DashboardContent() {
    const offerMonitor = useLoaderData({ from: Route.fullPath });
    const [isVisible, setIsVisible] = useState(false)

    useEffect(() => {
        setIsVisible(true)
    }, [])

    return (
        <div key={offerMonitor.id} className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-100">
            <DashboardHeader />

            <div className="container mx-auto px-4 py-8 max-w-6xl">
                <div
                    className={`mb-8 transition-all duration-1000 ${isVisible ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"
                        }`}
                >
                    <h1 className="text-4xl font-bold text-gray-900 mb-2">Offer Monitor Dashboard</h1>
                    <p className="text-gray-600">Manage your watched websites and notification preferences</p>
                </div>

                <div className="grid lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-2 space-y-6">
                        <MonitorSettings key={offerMonitor.enableNotifications.toString()} offerMonitor={offerMonitor} isVisible={isVisible} />
                        <MonitoredWebsites offerMonitor={offerMonitor} isVisible={isVisible} />
                    </div>
                    <DashboardSidebar offerMonitor={offerMonitor} isVisible={isVisible} />
                </div>
            </div>
        </div>
    )
}
''
