import { createFileRoute } from '@tanstack/react-router'
import { useEffect, useState } from 'react'
import type {OfferMonitor} from "types/dashboard.ts";
import { DashboardHeader } from "@/components/dashboard/dashboard-header.tsx";
import { MonitorSettings } from '@/components/dashboard/monitor-settings';
import { MonitoredWebsites } from '@/components/dashboard/monitored-websites';
import { DashboardSidebar } from '@/components/dashboard/dashboard-sidebar';

export const Route = createFileRoute('/dashboard')({
    component: DashboardContent,
})

function DashboardContent() {
    const [isVisible, setIsVisible] = useState(false)
    const [offerMonitor, setOfferMonitor] = useState<OfferMonitor>({
        name: "My Offer Monitor",
        urls: [
            {
                id: "1",
                name: "Amazon Deals",
                url: "https://amazon.com/deals",
                isActive: true,
                lastChecked: "2 minutes ago",
                offersFound: 12,
            },
            {
                id: "2",
                name: "Best Buy Sales",
                url: "https://bestbuy.com/site/sales",
                isActive: true,
                lastChecked: "5 minutes ago",
                offersFound: 8,
            },
        ],
        enable_notifications: true,
        notification_config: {
            telegram: true,
            email: false,
        },
    })

    useEffect(() => {
        setIsVisible(true)
    }, [])

    return (
        <div className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-100">
            <DashboardHeader offerMonitor={offerMonitor} />

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
                        <MonitorSettings offerMonitor={offerMonitor} setOfferMonitor={setOfferMonitor} isVisible={isVisible} />
                        <MonitoredWebsites offerMonitor={offerMonitor} setOfferMonitor={setOfferMonitor} isVisible={isVisible} />
                    </div>
                    <DashboardSidebar offerMonitor={offerMonitor} isVisible={isVisible} />
                </div>
            </div>
        </div>
    )
}

export default function Dashboard() {
    return (
        // <AuthGuard>
        <DashboardContent />
        // </AuthGuard>
    )
}
