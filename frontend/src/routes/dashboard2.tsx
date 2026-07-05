import { createFileRoute, redirect } from '@tanstack/react-router';
import { useTranslation } from 'react-i18next';
import { useGetTargets } from '@/components/dashboard/monitored-websites/useMonitors';
import { LoadingSkeleton, ErrorState, EmptyState } from '@/components/dashboard/DashboardShared';
import { DashboardLayout } from '@/components/dashboard/DashboardLayout';
import { MultiTargetDashboard } from '@/components/dashboard/MultiTargetDashboard';
import { SingleTargetDashboard } from '@/components/dashboard/SingleTargetDashboard';

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