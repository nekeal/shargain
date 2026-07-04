import { createFileRoute, redirect } from '@tanstack/react-router';
import { useCallback, useEffect, useState } from 'react';
import { AlertCircle, Globe, Menu, RotateCcw } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import type { OfferMonitor } from '@/types/dashboard';
import type { TargetSummaryResponse } from '@/lib/api/types.gen';
import { Button } from '@/components/ui/button';
import { MonitoredWebsites } from '@/components/dashboard/monitored-websites/index2';
import DashboardSidebar from '@/components/dashboard/dashboard-sidebar2';
import { MobileSidebarDrawer } from '@/components/dashboard/MobileSidebarDrawer';
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

export const Route = createFileRoute('/dashboard2')({
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
        <div className="flex min-h-screen bg-background animate-fade-in">
            <div className="w-[260px] border-r border-border bg-card shrink-0 flex flex-col animate-pulse">
                <div className="p-4 border-b border-border h-14" />
                <div className="flex-1 overflow-y-auto p-4 space-y-5">
                    <div className="space-y-3">
                        <div className="h-4 w-24 bg-muted rounded" />
                        <div className="h-20 bg-muted rounded-xl p-4 space-y-3">
                            <div className="h-4 w-32 bg-muted rounded" />
                            <div className="h-8 bg-muted rounded" />
                            <div className="h-8 bg-muted rounded" />
                        </div>
                    </div>
                    <div className="space-y-3">
                        <div className="h-4 w-24 bg-muted rounded" />
                        <div className="h-16 bg-muted rounded-xl p-4 space-y-2">
                            <div className="flex justify-between text-xs">
                                <div className="h-4 w-20 bg-muted rounded" />
                                <div className="h-4 w-20 bg-muted rounded" />
                            </div>
                            <div className="h-2 bg-secondary rounded-full overflow-hidden">
                                <div className="h-full bg-primary rounded-full" style={{ width: '67%' }} />
                            </div>
                        </div>
                        <div className="h-16 xl p-4 space-y-2">
                            <div className="flex justify-between text-xs">
                                <div className="h-4 w-20 bg-muted rounded" />
                                <div className="h-4 w-20 bg-muted rounded" />
                            </div>
                            <div className="h-2 bg-secondary rounded-full overflow-hidden">
                                <div className="h-full bg-primary rounded-full" style={{ width: '40%' }} />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div className="flex-1 overflow-y-auto p-6 animate-pulse space-y-6">
                <div className="bg-card border border-border rounded-xl p-6 space-y-4">
                    <div className="h-5 w-48 bg-muted rounded-lg" />
                    <div className="h-3 w-72 bg-muted rounded-lg" />
                    <div className="space-y-3 pt-2">
                        <div className="h-12 bg-muted rounded-xl" />
                        <div className="h-12 bg-muted rounded-xl" />
                        <div className="h-12 bg-muted rounded-xl" />
                    </div>
                </div>
            </div>
        </div>
    );
}

function ErrorState({ message, onRetry, retryLabel }: { message: string; onRetry?: () => void; retryLabel?: string }) {
    const { t } = useTranslation();
    return (
        <div className="flex min-h-screen bg-background items-center justify-center">
            <div className="bg-card border border-border rounded-2xl p-8 max-w-md text-center">
                <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
                <h2 className="text-lg font-semibold text-foreground mb-2">{message}</h2>
                {onRetry && (
                    <Button variant="outline" onClick={onRetry} className="mt-4">
                        <RotateCcw className="w-4 h-4 mr-2" />
                        {retryLabel || t('dashboard.retry')}
                    </Button>
                )}
            </div>
        </div>
    );
}

function EmptyState() {
    const { t } = useTranslation();
    return (
        <div className="flex min-h-screen bg-background items-center justify-center">
            <div className="bg-card border border-border rounded-2xl p-8 max-w-md text-center">
                <Globe className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-lg font-semibold text-foreground mb-2">{t('dashboard.noData')}</p>
                <p className="text-sm text-muted-foreground mb-6">{t('dashboard.subtitle')}</p>
                <Button size="lg" onClick={() => window.location.href = '/dashboard'}>
                    <Globe className="w-4 h-4 mr-2" />
                    {t('dashboard.monitoredWebsites.addWebsite')}
                </Button>
            </div>
        </div>
    );
}

function DashboardLayout({ offerMonitor, targets, selectedTargetId, onSelectTarget }: { 
    offerMonitor: OfferMonitor; 
    targets?: Array<TargetSummaryResponse>;
    selectedTargetId?: number;
    onSelectTarget?: (targetId: number) => void;
}) {
    const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
    return (
        <div className="flex min-h-screen bg-background">
            {/* Desktop Sidebar - hidden on mobile */}
            <div className="hidden lg:w-[260px] lg:border-r lg:border-border lg:bg-card lg:shrink-0 lg:flex lg:flex-col">
                <DashboardSidebar 
                    offerMonitor={offerMonitor} 
                    targets={targets}
                    selectedTargetId={selectedTargetId}
                    onSelectTarget={onSelectTarget}
                />
            </div>

            {/* Mobile Sidebar Drawer */}
            <MobileSidebarDrawer
                isOpen={mobileSidebarOpen}
                onClose={() => setMobileSidebarOpen(false)}
                offerMonitor={offerMonitor}
                targets={targets}
                selectedTargetId={selectedTargetId}
                onSelectTarget={onSelectTarget}
            />

            {/* Main Content */}
            <div className="flex-1 overflow-y-auto lg:p-6 p-4">
                {/* Mobile Header with Hamburger Menu */}
                <div className="lg:hidden mb-4 flex items-center justify-between">
                    <h1 className="text-lg font-semibold text-foreground">{offerMonitor.name}</h1>
                    <Button
                        variant="ghost"
                        size="icon"
                        className="h-10 w-10"
                        onClick={() => setMobileSidebarOpen(true)}
                        aria-label="Open sidebar"
                    >
                        <Menu className="w-5 h-5" aria-hidden="true" />
                    </Button>
                </div>
                <MonitoredWebsites offerMonitor={offerMonitor} />
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
        return <ErrorState message={t('dashboard.failedToLoadTarget')} onRetry={() => setSelectedTargetId(null)} />;
    }

    return (
        <DashboardLayout
            offerMonitor={fetchedTarget}
            targets={targets}
            selectedTargetId={selectedTargetId}
            onSelectTarget={handleSelectTarget}
        />
    );
}

function SingleTargetDashboard() {
    const { data: myTarget, isLoading, isError } = useGetMyTarget();

    if (isLoading) {
        return <LoadingSkeleton />;
    }

    if (isError) {
        return <ErrorState message="Failed to load your target" onRetry={() => window.location.reload()} />;
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