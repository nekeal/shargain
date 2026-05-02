import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { BellRing, CheckCircle, ChevronDown, Save } from "lucide-react";
import { useUpdateUrlMutation } from "./useMonitors";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import cn from "@/lib/utils";

interface UrlNotificationSettingsProps {
  targetId: number;
  urlId: number;
  initialShowLocationMap: boolean;
}

export function UrlNotificationSettings({
  targetId,
  urlId,
  initialShowLocationMap,
}: UrlNotificationSettingsProps) {
  const { t } = useTranslation();
  const [showLocationMap, setShowLocationMap] = useState(initialShowLocationMap);
  const [isOpen, setIsOpen] = useState(false);

  const mutation = useUpdateUrlMutation(targetId, urlId);

  useEffect(() => {
    setShowLocationMap(initialShowLocationMap);
  }, [initialShowLocationMap]);

  const handleSave = () => {
    mutation.mutate({ showLocationMapInNotifications: showLocationMap });
  };

  const hasChanges = showLocationMap !== initialShowLocationMap;

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen} className="mt-2">
      <CollapsibleTrigger asChild>
        <button
          type="button"
          aria-label={isOpen ? t("filters.notificationSettingsCollapse", { defaultValue: "Collapse notification content" }) : t("filters.notificationSettingsExpand", { defaultValue: "Expand notification content" })}
          className={cn(
            "w-full px-3 py-2 flex items-center justify-between",
            "text-sm text-gray-600 hover:text-gray-900",
            "bg-gray-50/80 hover:bg-gray-100/80 rounded-md",
            "transition-colors duration-150",
            "focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 focus-visible:ring-offset-1"
          )}
        >
          <span className="flex items-center gap-2">
            <BellRing className="w-3.5 h-3.5" />
            <span className="font-medium">{t("filters.notificationContent", { defaultValue: "Notification Content" })}</span>
          </span>
          <ChevronDown
            className={cn(
              "w-4 h-4 text-gray-400 transition-transform duration-200",
              isOpen && "rotate-180"
            )}
          />
        </button>
      </CollapsibleTrigger>

      <CollapsibleContent className="mt-2 space-y-3">
        <div className="flex items-center justify-between p-3 bg-white/50 border border-gray-200 rounded-lg">
          <div className="flex flex-col gap-0.5">
            <Label htmlFor="show-location-map-settings" className="text-sm font-medium cursor-pointer">
              {t("filters.includeLocationMap", { defaultValue: "Include location map link" })}
            </Label>
            <span className="text-xs text-gray-500">
              {t("filters.includeLocationMapDescription", { defaultValue: "Adds a Google Maps link to the Telegram message" })}
            </span>
          </div>
          <Switch
            id="show-location-map-settings"
            checked={showLocationMap}
            onCheckedChange={setShowLocationMap}
          />
        </div>

        <div className="flex justify-end pt-2">
          <Button
            size="sm"
            onClick={handleSave}
            disabled={mutation.isPending || !hasChanges}
            className="h-8 text-xs px-3"
          >
            {mutation.isPending ? (
              <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin mr-1.5" />
            ) : mutation.isSuccess ? (
              <CheckCircle className="w-3 h-3 mr-1.5" />
            ) : (
              <Save className="w-3 h-3 mr-1.5" />
            )}
            {t("filters.save")}
          </Button>
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}
