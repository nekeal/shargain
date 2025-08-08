import type { ScrapingUrlResponse, TargetResponse } from "@/lib/api";

export interface OfferMonitor extends TargetResponse {
    notificationConfigId: string | null;
    notification_config: {
        telegram: boolean;
        email: boolean;
    };
}

export interface MonitoredUrl extends ScrapingUrlResponse {
    lastChecked?: string;
    offersFound?: number;
}
