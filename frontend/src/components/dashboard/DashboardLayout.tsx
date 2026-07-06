"use client"

import { useState } from 'react';
import { Menu } from 'lucide-react';
import type { OfferMonitor } from '@/types/dashboard';
import type { TargetSummaryResponse } from '@/lib/api/types.gen';
import { Button } from '@/components/ui/button';
import { MonitoredWebsites } from '@/components/dashboard/monitored-websites/index2';
import DashboardSidebar from '@/components/dashboard/dashboard-sidebar2';
import { MobileSidebarDrawer } from '@/components/dashboard/MobileSidebarDrawer';

interface DashboardLayoutProps {
    offerMonitor: OfferMonitor;
    targets?: Array<TargetSummaryResponse>;
    selectedTargetId?: number;
    onSelectTarget?: (targetId: number) => void;
}

export function DashboardLayout({ offerMonitor, targets, selectedTargetId, onSelectTarget }: DashboardLayoutProps) {
    const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
    return (
        <div className="flex min-h-screen bg-background">
            {/* Desktop Sidebar - hidden on mobile */}
            <div className="hidden lg:w-[260px] lg:border-r lg:border-border lg:bg-card lg:shrink-0 lg:flex lg:flex-col" aria-hidden="true">
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
                onOpenChange={(open) => setMobileSidebarOpen(open)}
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
                        aria-label="Open sidebar"
                        onClick={() => setMobileSidebarOpen(true)}
                    >
                        <Menu className="w-5 h-5" aria-hidden="true" />
                    </Button>
                </div>
                <MonitoredWebsites offerMonitor={offerMonitor} />
            </div>
        </div>
    );
}
