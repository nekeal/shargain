import { createFileRoute, redirect } from '@tanstack/react-router';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { AlertCircle, Globe } from 'lucide-react';
import type { OfferMonitor } from '@/types/dashboard';
import { useAuth } from '@/context/auth';
import MonitorSettings from '@/components/dashboard/monitor-settings';
import { MonitoredWebsites } from '@/components/dashboard/monitored-websites';
import DashboardSidebar from '@/components/dashboard/dashboard-sidebar';
import { TargetSelector } from '@/components/dashboard/target-selector';
import { useGetMyTarget, useGetTarget, useGetTargets } from '@/components/dashboard/monitored-websites/useMonitors';

const STORAGE_KEY = 'shargain_selected_target_id';

function loadStoredTargetId(): number | null {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        return stored ? parseInt(stored, 10) : null;
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

function clearStoredTargetId() {
    try {
        localStorage.removeItem(STORAGE_KEY);
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

function DashboardLayout({ offerMonitor }: { offerMonitor: OfferMonitor }) {
    const { t } = useTranslation();
    const { user } = useAuth();
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        setIsVisible(true);
    }, []);

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

function DashboardContent() {
    const { t } = useTranslation();

    const [selectedTargetId, setSelectedTargetId] = useState<number | null>(loadStoredTargetId);
    const storedValidatedRef = useRef(false);

    const { data: targetList, isLoading: listLoading, isError: listError } = useGetTargets();
    const { data: myTarget, isLoading: myTargetLoading, isError: myTargetError } = useGetMyTarget();
    const { data: fetchedTarget, isLoading: targetLoading, isError: targetError } = useGetTarget(selectedTargetId);

    const handleSelectTarget = useCallback((targetId: number) => {
        saveStoredTargetId(targetId);
        setSelectedTargetId(targetId);
    }, []);

    useEffect(() => {
        if (!targetList || storedValidatedRef.current) return;
        storedValidatedRef.current = true;

        if (selectedTargetId !== null && !targetList.some(t => t.id === selectedTargetId)) {
            clearStoredTargetId();
            setSelectedTargetId(null);
        }
    }, [targetList, selectedTargetId]);

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
        if (!selectedTargetId) {
            return (
                <TargetSelector
                    targets={targetList}
                    selectedTargetId={null}
                    onSelect={handleSelectTarget}
                />
            );
        }

        if (targetLoading) {
            return <LoadingSkeleton />;
        }

        if (targetError || !fetchedTarget) {
            return <ErrorState message={t('dashboard.error')} />;
        }

        return <DashboardLayout offerMonitor={fetchedTarget} />;
    }

    if (myTargetLoading) {
        return <LoadingSkeleton />;
    }

    if (myTargetError) {
        return <ErrorState message={t('dashboard.error')} />;
    }

    if (!myTarget) {
        return <EmptyState />;
    }

    return <DashboardLayout offerMonitor={myTarget} />;
}
