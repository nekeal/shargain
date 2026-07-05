"use client"

import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { TargetSummaryResponse } from '@/lib/api/types.gen';
import { useGetTarget, usePrefetchTargets } from '@/components/dashboard/monitored-websites/useMonitors';
import { DashboardLayout } from '@/components/dashboard/DashboardLayout';
import { LoadingSkeleton, ErrorState, loadStoredTargetId, saveStoredTargetId } from '@/components/dashboard/DashboardShared';

interface MultiTargetDashboardProps {
    targets: Array<TargetSummaryResponse>;
}

export function MultiTargetDashboard({ targets }: MultiTargetDashboardProps) {
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
