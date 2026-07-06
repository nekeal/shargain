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
import { Button } from '@/components/ui/button';
import { loadStoredTargetId, saveStoredTargetId } from '@/components/dashboard/DashboardShared';
import { useGetMyTarget, useGetTarget, useGetTargets, usePrefetchTargets } from '@/components/dashboard/monitored-websites/useMonitors';

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
        <div className="min-h-screen bg-secondary" role="status" aria-live="polite" aria-busy="true">
            <div className="container mx-auto px-4 py-8 max-w-6xl animate-pulse motion-reduce:animate-none">
                <div className="mb-8">
                    <div className="h-7 w-64 bg-muted rounded-md mb-2" />
                    <div className="h-4 w-96 bg-muted rounded-md" />
                </div>
                <div className="grid lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-2 space-y-6">
                        <div className="bg-card/70 rounded-xl p-6 space-y-4">
                            <div className="h-5 w-48 bg-muted rounded-md" />
                            <div className="h-3 w-72 bg-muted rounded-md" />
                            <div className="space-y-3 pt-2">
                                <div className="h-12 bg-muted rounded-xl" />
                                <div className="h-12 bg-muted rounded-xl" />
                                <div className="h-12 bg-muted rounded-xl" />
                            </div>
                        </div>
                        <div className="bg-card/70 rounded-xl p-6 space-y-4">
                            <div className="h-5 w-40 bg-muted rounded-md" />
                            <div className="h-10 bg-muted rounded-xl" />
                            <div className="h-10 bg-muted rounded-xl" />
                        </div>
                    </div>
                    <div className="space-y-6">
                        <div className="bg-card/70 rounded-xl p-6 space-y-4">
                            <div className="h-5 w-32 bg-muted rounded-md" />
                            <div className="h-8 bg-muted rounded-xl" />
                            <div className="h-8 bg-muted rounded-xl" />
                        </div>
                        <div className="bg-card/70 rounded-xl p-6 space-y-4">
                            <div className="h-5 w-28 bg-muted rounded-md" />
                            <div className="h-10 bg-muted rounded-xl" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function ErrorState({ message }: { message: string }) {
    return (
        <div className="min-h-screen bg-secondary flex items-center justify-center" role="alert" aria-live="assertive">
            <div className="bg-card rounded-xl p-8 max-w-md text-center">
                <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
                <h2 className="text-lg font-semibold text-foreground mb-2">{message}</h2>
            </div>
        </div>
    );
}

function EmptyState({ onAddUrl }: { onAddUrl?: () => void }) {
    const { t } = useTranslation();
    return (
        <div className="min-h-screen bg-secondary flex items-center justify-center" role="status" aria-live="polite">
            <div className="bg-card rounded-xl p-8 max-w-md text-center">
                <Globe className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-lg font-semibold text-foreground mb-2">{t('dashboard.noData')}</p>
                <p className="text-sm text-muted-foreground mb-6">{t('dashboard.subtitle')}</p>
                {onAddUrl && (
                    <Button size="lg" onClick={onAddUrl}>
                        <Globe className="w-4 h-4 mr-2" aria-hidden="true" />
                        {t('dashboard.monitoredWebsites.addWebsite')}
                    </Button>
                )}
            </div>
        </div>
    );
}

function DashboardLayout({ offerMonitor, sidebarTop, onAddUrl }: { offerMonitor: OfferMonitor; sidebarTop?: React.ReactNode; onAddUrl?: () => void }) {
    const { t } = useTranslation();
    const { user } = useAuth();

    return (
        <div className="min-h-screen bg-secondary">
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

function MultiTargetDashboard({ targets, onAddUrl }: { targets: Array<TargetSummaryResponse>; onAddUrl?: () => void }) {
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
            onAddUrl={onAddUrl}
            sidebarTop={
                <Card className="bg-card border border-border">
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

function SingleTargetDashboard({ onAddUrl }: { onAddUrl?: () => void }) {
    const { data: myTarget, isLoading, isError } = useGetMyTarget();

    if (isLoading) {
        return <LoadingSkeleton />;
    }

    if (isError) {
        return <ErrorState message="Failed to load your target" />;
    }

    if (!myTarget) {
        return <EmptyState onAddUrl={onAddUrl} />;
    }

    return <DashboardLayout offerMonitor={myTarget} onAddUrl={onAddUrl} />;
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
