"use client"

import { useGetMyTarget } from '@/components/dashboard/monitored-websites/useMonitors';
import { DashboardLayout } from '@/components/dashboard/DashboardLayout';
import { LoadingSkeleton, ErrorState, EmptyState } from '@/components/dashboard/DashboardShared';

export function SingleTargetDashboard() {
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
