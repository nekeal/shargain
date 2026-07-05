"use client"

import { useTranslation } from 'react-i18next';
import { AlertCircle, Globe, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';

const STORAGE_KEY = 'shargain_selected_target_id';

export function loadStoredTargetId(): number | null {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored === null) return null;
        const parsed = parseInt(stored, 10);
        return Number.isFinite(parsed) ? parsed : null;
    } catch {
        return null;
    }
}

export function saveStoredTargetId(targetId: number) {
    try {
        localStorage.setItem(STORAGE_KEY, String(targetId));
    } catch {
        // localStorage not available
    }
}

export function LoadingSkeleton() {
    return (
        <div className="flex min-h-screen bg-background animate-fade-in" aria-busy="true" aria-live="polite">
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

export function ErrorState({ message, onRetry, retryLabel }: { message: string; onRetry?: () => void; retryLabel?: string }) {
    const { t } = useTranslation();
    return (
        <div className="flex min-h-screen bg-background items-center justify-center" role="alert" aria-live="assertive">
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

export function EmptyState() {
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
