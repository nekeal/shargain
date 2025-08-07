import { createFileRoute } from '@tanstack/react-router'
import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query';
import type { OfferMonitor } from "@/types/dashboard";
import { DashboardHeader } from "@/components/dashboard/dashboard-header.tsx";
import { MonitorSettings } from '@/components/dashboard/monitor-settings';
import { MonitoredWebsites } from '@/components/dashboard/monitored-websites';
import { DashboardSidebar } from '@/components/dashboard/dashboard-sidebar';
import { DefaultService } from '@/lib/api';

export const Route = createFileRoute('/dashboard')({
    component: DashboardContent,
})

function DashboardContent() {
    const { data: targetResponse, isLoading, error } = useQuery({
        queryKey: ['myTarget'],
        queryFn: () => DefaultService.shargainPublicApiApiGetMyTarget(),
    });

    const [isVisible, setIsVisible] = useState(false)
    const [offerMonitor, setOfferMonitor] = useState<OfferMonitor | undefined>()

    const updateOfferMonitor = (updater: (prev: OfferMonitor) => OfferMonitor) => {
        setOfferMonitor(prev => prev ? updater(prev) : undefined);
    }

    useEffect(() => {
        if (targetResponse) {
            setOfferMonitor({
                ...targetResponse,
                notification_config: {
                    telegram: true,
                    email: false,
                }
            })
        }
    }, [targetResponse])


    useEffect(() => {
        setIsVisible(true)
    }, [])

    if (isLoading) {
        return <div>Loading...</div>
    }

    if (error) {
        return <div>Error fetching data</div>
    }

    if (!offerMonitor) {
        return <div>No data</div>
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-100">
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
                        <MonitorSettings offerMonitor={offerMonitor} setOfferMonitor={updateOfferMonitor} isVisible={isVisible} />
                        <MonitoredWebsites offerMonitor={offerMonitor} setOfferMonitor={updateOfferMonitor} isVisible={isVisible} />
                    </div>
                    <DashboardSidebar offerMonitor={offerMonitor} isVisible={isVisible} />
                </div>
            </div>
        </div>
    )
}
