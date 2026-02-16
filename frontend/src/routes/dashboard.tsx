import { createFileRoute, redirect } from '@tanstack/react-router';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { AlertCircle } from 'lucide-react';
import { useAuth } from '@/context/auth';
import MonitorSettings from '@/components/dashboard/monitor-settings';
import { MonitoredWebsites } from '@/components/dashboard/monitored-websites';
import DashboardSidebar from '@/components/dashboard/dashboard-sidebar';
import { useGetMyTarget } from '@/components/dashboard/monitored-websites/useMonitors';

export const Route = createFileRoute('/dashboard')({
    component: DashboardContent,
    beforeLoad: ({ context }) => {
        console.log("RENDERING DASHBOARD", context.auth.user?.username)
        if (!context.auth.isAuthenticated) {
            throw redirect({
                to: '/auth/signin',
            })
        }
    },
});

function DashboardContent() {
    const { t } = useTranslation();
    const { user } = useAuth();
    const { data: offerMonitor, isLoading, isError } = useGetMyTarget();

    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        setIsVisible(true);
    }, []);

    if (isLoading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-100">
                <div className="container mx-auto px-4 py-8 max-w-6xl animate-pulse">
                    {/* Title skeleton */}
                    <div className="mb-8">
                        <div className="h-7 w-64 bg-gray-200 rounded-lg mb-2" />
                        <div className="h-4 w-96 bg-gray-200 rounded-lg" />
                    </div>
                    {/* Card grid skeleton — mirrors real lg:grid-cols-3 layout */}
                    <div className="grid lg:grid-cols-3 gap-8">
                        <div className="lg:col-span-2 space-y-6">
                            {/* MonitoredWebsites skeleton */}
                            <div className="bg-white/70 rounded-2xl p-6 space-y-4">
                                <div className="h-5 w-48 bg-gray-200 rounded-lg" />
                                <div className="h-3 w-72 bg-gray-200 rounded-lg" />
                                <div className="space-y-3 pt-2">
                                    <div className="h-12 bg-gray-200 rounded-xl" />
                                    <div className="h-12 bg-gray-200 rounded-xl" />
                                    <div className="h-12 bg-gray-200 rounded-xl" />
                                </div>
                            </div>
                            {/* MonitorSettings skeleton */}
                            <div className="bg-white/70 rounded-2xl p-6 space-y-4">
                                <div className="h-5 w-40 bg-gray-200 rounded-lg" />
                                <div className="h-10 bg-gray-200 rounded-xl" />
                                <div className="h-10 bg-gray-200 rounded-xl" />
                            </div>
                        </div>
                        {/* Sidebar skeleton */}
                        <div className="space-y-6">
                            <div className="bg-white/70 rounded-2xl p-6 space-y-4">
                                <div className="h-5 w-32 bg-gray-200 rounded-lg" />
                                <div className="h-8 bg-gray-200 rounded-xl" />
                                <div className="h-8 bg-gray-200 rounded-xl" />
                            </div>
                            <div className="bg-white/70 rounded-2xl p-6 space-y-4">
                                <div className="h-5 w-28 bg-gray-200 rounded-lg" />
                                <div className="h-10 bg-gray-200 rounded-xl" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (isError) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-100 flex items-center justify-center">
                <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md text-center">
                    <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
                    <h2 className="text-lg font-semibold text-gray-900 mb-2">{t('dashboard.error')}</h2>
                </div>
            </div>
        );
    }

    if (!offerMonitor) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-100 flex items-center justify-center">
                <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md text-center">
                    <p className="text-lg font-semibold text-gray-900 mb-2">{t('dashboard.noData')}</p>
                    <p className="text-sm text-gray-500">{t('dashboard.subtitle')}</p>
                </div>
            </div>
        );
    }

    return (
        <div key={offerMonitor.id} className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-100">
            <div className="container mx-auto px-4 py-8 max-w-6xl">
                <div
                    className={`mb-8 transition-all duration-1000 ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
                    <h1 className="text-2xl font-semibold text-gray-900">{t('dashboard.greeting', { name: user?.username || '' })}</h1>
                    <p className="text-sm text-gray-500">{t('dashboard.subtitle')}</p>
                </div>

                <div className="grid lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-2 space-y-6">
                        <MonitoredWebsites offerMonitor={offerMonitor} isVisible={isVisible} />
                        <MonitorSettings offerMonitor={offerMonitor} isVisible={isVisible} />
                    </div>
                    <DashboardSidebar offerMonitor={offerMonitor} isVisible={isVisible} />
                </div>
            </div>
        </div>
    );
}
