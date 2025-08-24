import { createFileRoute } from '@tanstack/react-router';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { AppHeader } from '@/components/app-header';
import MonitorSettings from '@/components/dashboard/monitor-settings';
import { MonitoredWebsites } from '@/components/dashboard/monitored-websites';
import DashboardSidebar from '@/components/dashboard/dashboard-sidebar';
import { useGetMyTarget } from '@/components/dashboard/monitored-websites/useMonitors';

export const Route = createFileRoute('/dashboard')({
    component: DashboardContent,
});

function DashboardContent() {
    const { t } = useTranslation();
    const { data: offerMonitor, isLoading, isError } = useGetMyTarget();

    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        setIsVisible(true);
    }, []);

    if (isLoading) {
        return <div>{t('dashboard.loading')}</div>;
    }

    if (isError) {
        return <div>{t('dashboard.error')}</div>;
    }

    if (!offerMonitor) {
        return <div>{t('dashboard.noData')}</div>;
    }

    return (
        <div key={offerMonitor.id} className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-100">
            <AppHeader />

            <div className="container mx-auto px-4 py-8 max-w-6xl">
                <div
                    className={`mb-8 transition-all duration-1000 ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
                    <h1 className="text-4xl font-bold text-gray-900 mb-2">{t('dashboard.title')}</h1>
                    <p className="text-gray-600">{t('dashboard.subtitle')}</p>
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
