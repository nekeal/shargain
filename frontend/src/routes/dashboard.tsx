import { createFileRoute, redirect } from '@tanstack/react-router';
import { useCallback, useEffect, useState } from 'react';
import { AlertCircle, Globe } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import type { OfferMonitor } from '@/types/dashboard';
import type { TargetSummaryResponse } from '@/lib/api/types.gen';
import { useAuth } from '@/context/auth';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import MonitorSettings from '@/components/dashboard/monitor-settings';
import { MonitoredWebsites } from '@/components/dashboard/monitored-websites';
import DashboardSidebar from '@/components/dashboard/dashboard-sidebar';
import { TargetSelectorInline } from '@/components/dashboard/target-selector-inline';
import { useGetMyTarget, useGetTarget, useGetTargets, usePrefetchTargets } from '@/components/dashboard/monitored-websites/useMonitors';

const STORAGE_KEY = 'shargain_selected_target_id';

function loadStoredTargetId(): number | null {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored === null) return null;
        const parsed = parseInt(stored, 10);
        return Number.isFinite(parsed) ? parsed : null;
    } catch {
        return null;
    }
}

function saveStoredTargetId(targetId: number) {
    try {
        localStorage.setItem(STORAGE_KEY, String(targetId));
    } catch {
        // localStorage not available
    }
}

export const Route = createFileRoute('/dashboard')({
    component: DashboardContent,
    beforeLoad: ({ context }) => {
        if (!context.auth.isAuthenticated) {
            throw redirect({
                to: '/auth/signin',
            })
        }
    },
});

function LoadingSkeleton() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-100">
            <div className="container mx-auto px-4 py-8 max-w-6xl animate-pulse">
                <div className="mb-8">
                    <div className="h-7 w-64 bg-gray-200 rounded-lg mb-2" />
                    <div className="h-4 w-96 bg-gray-200 rounded-lg" />
                </div>
                <div className="grid lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-2 space-y-6">
                        <div className="bg-white/70 rounded-2xl p-6 space-y-4">
                            <div className="h-5 w-48 bg-gray-200 rounded-lg" />
                            <div className="h-3 w-72 bg-gray-200 rounded-lg" />
                            <div className="space-y-3 pt-2">
                                <div className="h-12 bg-gray-200 rounded-xl" />
                                <div className="h-12 bg-gray-200 rounded-xl" />
                                <div className="h-12 bg-gray-200 rounded-xl" />
                            </div>
                        </div>
                        <div className="bg-white/70 rounded-2xl p-6 space-y-4">
                            <div className="h-5 w-40 bg-gray-200 rounded-lg" />
                            <div className="h-10 bg-gray-200 rounded-xl" />
                            <div className="h-10 bg-gray-200 rounded-xl" />
                        </div>
                    </div>
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

function ErrorState({ message }: { message: string }) {
    return (
        <div className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-100 flex items-center justify-center">
            <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md text-center">
                <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
                <h2 className="text-lg font-semibold text-gray-900 mb-2">{message}</h2>
            </div>
        </div>
    );
}

function EmptyState() {
    const { t } = useTranslation();
    return (
        <div className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-100 flex items-center justify-center">
            <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md text-center">
                <Globe className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <p className="text-lg font-semibold text-gray-900 mb-2">{t('dashboard.noData')}</p>
                <p className="text-sm text-gray-500">{t('dashboard.subtitle')}</p>
            </div>
        </div>
    );
}

function DashboardLayout({ offerMonitor, sidebarTop }: { offerMonitor: OfferMonitor; sidebarTop?: React.ReactNode }) {
    const { t } = useTranslation();
    const { user } = useAuth();

    return (
        <div className="min-h-screen bg-background">
            <div className="container mx-auto px-4 py-8 max-w-6xl">
                <div className="mb-8">
                    <h1 className="text-2xl font-semibold text-foreground">{t('dashboard.greeting', { name: user?.username || '' })}</h1>
                    <p className="text-sm text-muted-foreground">{t('dashboard.subtitle')}</p>
                </div>

                {sidebarTop ? (
                    <div className="mb-8 lg:hidden">
                        {sidebarTop}
                    </div>
                ) : null}

                <div className="grid lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-2 space-y-6">
                        <MonitoredWebsites offerMonitor={offerMonitor} />
                        <MonitorSettings offerMonitor={offerMonitor} />
                    </div>
                    <div className="space-y-6">
                        {sidebarTop ? (
                            <div className="hidden lg:block">
                                {sidebarTop}
                            </div>
                        ) : null}
                        <DashboardSidebar offerMonitor={offerMonitor} />
                    </div>
                </div>
            </div>
        </div>
    );
}

function MultiTargetDashboard({ targets }: { targets: Array<TargetSummaryResponse> }) {
    const { t } = useTranslation();
    const [selectedTargetId, setSelectedTargetId] = useState<number | null>(loadStoredTargetId);

    const { data: fetchedTarget, isLoading, isError } = useGetTarget(selectedTargetId);
    const handleSelectTarget = useCallback((targetId: number) => {
        saveStoredTargetId(targetId);
        setSelectedTargetId(targetId);
    }, []);

    usePrefetchTargets(targets, selectedTargetId);

    useEffect(() => {
        if (selectedTargetId === null || !targets.some(target => target.id === selectedTargetId)) {
            saveStoredTargetId(targets[0].id);
            setSelectedTargetId(targets[0].id);
        }
    }, [targets, selectedTargetId]);

    if (selectedTargetId === null) {
        return <LoadingSkeleton />;
    }

    if (isLoading) {
        return <LoadingSkeleton />;
    }

    if (isError || !fetchedTarget) {
        return <ErrorState message={t('dashboard.failedToLoadTarget')} />;
    }

    return (
        <DashboardLayout
            offerMonitor={fetchedTarget}
            sidebarTop={
                <Card className="border-0 bg-white/60 backdrop-blur-sm">
                    <CardHeader>
                        <CardTitle className="text-lg">{t('dashboard.scrapingTarget')}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <TargetSelectorInline
                            targets={targets}
                            selectedTargetId={selectedTargetId}
                            onSelect={handleSelectTarget}
                        />
                    </CardContent>
                </Card>
            }
        />
    );
}

function SingleTargetDashboard() {
    const { data: myTarget, isLoading, isError } = useGetMyTarget();

    if (isLoading) {
        return <LoadingSkeleton />;
    }

    if (isError) {
        return <ErrorState message="Failed to load your target" />;
    }

    if (!myTarget) {
        return <EmptyState />;
    }

    return <DashboardLayout offerMonitor={myTarget} />;
}

function DashboardContent() {
    const { t } = useTranslation();

    const { data: targetList, isLoading: listLoading, isError: listError } = useGetTargets();

    if (listLoading) {
        return <LoadingSkeleton />;
    }

    if (listError) {
        return <ErrorState message={t('dashboard.error')} />;
    }

    if (!targetList || targetList.length === 0) {
        return <EmptyState />;
    }

    if (targetList.length > 1) {
        return <MultiTargetDashboard targets={targetList} />;
    }

    return <SingleTargetDashboard />;
}
