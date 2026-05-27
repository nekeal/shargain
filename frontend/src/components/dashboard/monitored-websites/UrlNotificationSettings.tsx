import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { BellRing, CheckCircle, ChevronDown, MapPin, Plus, Save, X } from "lucide-react";
import { useUpdateUrlMutation } from "./useMonitors";
import type { WaypointSchema } from "@/lib/api/types.gen";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import cn from "@/lib/utils";
import { parseGoogleMapsUrl } from "@/lib/google-maps-url";

interface UrlNotificationSettingsProps {
  targetId: number;
  urlId: number;
  initialShowLocationMap: boolean;
  initialWaypoints?: Array<WaypointSchema> | null;
}

interface WaypointRowProps {
  waypoint: WaypointSchema;
  index: number;
  onUpdate: (index: number, field: keyof WaypointSchema, value: string | number) => void;
  onRemove: (index: number) => void;
  onPaste: (index: number) => void;
}

function WaypointRow({ waypoint, index, onUpdate, onRemove, onPaste }: WaypointRowProps) {
  const { t } = useTranslation();

  return (
    <div className="p-3 bg-white/50 border border-gray-200 rounded-lg">
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 w-8 shrink-0">
            {t("filters.waypointName")}
          </span>
          <Input
            value={waypoint.name}
            placeholder={t("filters.waypointNamePlaceholder")}
            onChange={(e) => onUpdate(index, "name", e.target.value)}
            className="h-8 text-xs px-2 flex-1"
          />
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 w-8 shrink-0">
            {t("filters.waypointLat")}
          </span>
          <Input
            type="number"
            step="any"
            value={waypoint.lat}
            placeholder={t("filters.waypointLatPlaceholder")}
            onChange={(e) => onUpdate(index, "lat", parseFloat(e.target.value) || 0)}
            className="h-8 text-xs px-2 flex-1"
          />
          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={() => onPaste(index)}
            aria-label={t("filters.pasteFromClipboard")}
            className="h-7 w-7 shrink-0"
          >
            <MapPin className="w-3.5 h-3.5" />
          </Button>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 w-8 shrink-0">
            {t("filters.waypointLon")}
          </span>
          <Input
            type="number"
            step="any"
            value={waypoint.lon}
            placeholder={t("filters.waypointLonPlaceholder")}
            onChange={(e) => onUpdate(index, "lon", parseFloat(e.target.value) || 0)}
            className="h-8 text-xs px-2 flex-1"
          />
          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={() => onRemove(index)}
            aria-label={t("filters.removeWaypoint")}
            className="h-7 w-7 shrink-0"
          >
            <X className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>
    </div>
  );
}

interface PasteDialogProps {
  open: boolean;
  onClose: () => void;
  onParsed: (parsed: NonNullable<ReturnType<typeof parseGoogleMapsUrl>>) => void;
}

function PasteDialog({ open, onClose, onParsed }: PasteDialogProps) {
  const { t } = useTranslation();
  const [url, setUrl] = useState("");
  const [error, setError] = useState<string | null>(null);

  const close = () => {
    setUrl("");
    setError(null);
    onClose();
  };

  const tryParse = (input: string) => {
    const parsed = parseGoogleMapsUrl(input);
    if (parsed) {
      onParsed(parsed);
      close();
      return true;
    }
    return false;
  };

  return (
    <Dialog
      open={open}
      onOpenChange={(open) => {
        if (!open) close();
      }}
    >
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {t("filters.addFromGoogleMaps")}
          </DialogTitle>
          <DialogDescription>
            {t("filters.pasteGoogleMapsDescription")}
          </DialogDescription>
        </DialogHeader>
        <Input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onPaste={(e) => {
            const pastedUrl = e.clipboardData.getData("text");
            setUrl(pastedUrl);
            if (pastedUrl && !tryParse(pastedUrl)) {
              setError(
                t("filters.parseError"),
              );
            }
          }}
          placeholder={t("filters.googleMapsUrlPlaceholder")}
        />
        {error && <p className="text-xs text-red-500">{error}</p>}
        <DialogFooter>
          <Button variant="outline" onClick={close}>
            {t("filters.cancel")}
          </Button>
          <Button
            onClick={() => {
              if (!tryParse(url)) {
                setError(
                  t("filters.parseError"),
                );
              }
            }}
          >
            {t("filters.parse")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export function UrlNotificationSettings({
  targetId,
  urlId,
  initialShowLocationMap,
  initialWaypoints = [],
}: UrlNotificationSettingsProps) {
  const { t } = useTranslation();
  const [showLocationMap, setShowLocationMap] = useState(initialShowLocationMap);
  const [waypoints, setWaypoints] = useState<Array<WaypointSchema>>(initialWaypoints ?? []);
  const [isOpen, setIsOpen] = useState(false);
  const [pasteTargetIndex, setPasteTargetIndex] = useState<number | null>(null);

  const mutation = useUpdateUrlMutation(targetId, urlId);

  useEffect(() => {
    setShowLocationMap(initialShowLocationMap);
    setWaypoints(initialWaypoints ?? []);
  }, [initialShowLocationMap, initialWaypoints]);

  const addWaypoint = () => {
    setWaypoints((prev) => [...prev, { name: "", lat: 0, lon: 0 }]);
  };

  const removeWaypoint = (index: number) => {
    setWaypoints((prev) => prev.filter((_, i) => i !== index));
  };

  const updateWaypoint = (index: number, field: keyof WaypointSchema, value: string | number) => {
    setWaypoints((prev) => {
      const next = [...prev];
      next[index] = { ...next[index], [field]: value };
      return next;
    });
  };

  const fillFromParsed = (index: number, parsed: NonNullable<ReturnType<typeof parseGoogleMapsUrl>>) => {
    setWaypoints((prev) => {
      const next = [...prev];
      next[index] = {
        name: parsed.label || next[index].name,
        lat: parsed.lat,
        lon: parsed.lon,
      };
      return next;
    });
  };

  const handlePaste = async (index: number) => {
    try {
      const text = await navigator.clipboard.readText();
      const parsed = parseGoogleMapsUrl(text);
      if (parsed) {
        fillFromParsed(index, parsed);
        return;
      }
    } catch {
      // Clipboard API not available
    }
    setPasteTargetIndex(index);
  };

  const handleSave = () => {
    mutation.mutate({
      showLocationMapInNotifications: showLocationMap,
      waypoints: waypoints,
    });
  };

  const hasChanges =
    showLocationMap !== initialShowLocationMap ||
    JSON.stringify(waypoints) !== JSON.stringify(initialWaypoints ?? []);

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen} className="mt-2">
      <CollapsibleTrigger asChild>
        <button
          type="button"
          aria-label={
            isOpen
              ? t("filters.notificationSettingsCollapse")
              : t("filters.notificationSettingsExpand")
          }
          className={cn(
            "w-full px-3 py-2 flex items-center justify-between",
            "text-sm text-gray-600 hover:text-gray-900",
            "bg-gray-50/80 hover:bg-gray-100/80 rounded-md",
            "transition-colors duration-150",
            "focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 focus-visible:ring-offset-1",
          )}
        >
          <span className="flex items-center gap-2">
            <BellRing className="w-3.5 h-3.5" />
            <span className="font-medium">
              {t("filters.notificationContent")}
            </span>
          </span>
          <ChevronDown
            className={cn(
              "w-4 h-4 text-gray-400 transition-transform duration-200",
              isOpen && "rotate-180",
            )}
          />
        </button>
      </CollapsibleTrigger>

      <CollapsibleContent className="mt-2 space-y-3">
        <div className="flex items-center justify-between p-3 bg-white/50 border border-gray-200 rounded-lg">
          <div className="flex flex-col gap-0.5">
            <Label
              htmlFor="show-location-map-settings"
              className="text-sm font-medium cursor-pointer"
            >
              {t("filters.includeLocationMap")}
            </Label>
            <span className="text-xs text-gray-500">
              {t("filters.includeLocationMapDescription")}
            </span>
          </div>
          <Switch
            id="show-location-map-settings"
            checked={showLocationMap}
            onCheckedChange={setShowLocationMap}
          />
        </div>

        {showLocationMap && (
          <div className="space-y-2">
            {waypoints.map((wp, index) => (
              <WaypointRow
                key={index}
                waypoint={wp}
                index={index}
                onUpdate={updateWaypoint}
                onRemove={removeWaypoint}
                onPaste={handlePaste}
              />
            ))}
            <button
              type="button"
              onClick={addWaypoint}
              className="w-full py-1.5 flex items-center justify-center gap-1.5 text-xs text-gray-500 hover:text-violet-600 border border-dashed border-gray-300 hover:border-violet-400 rounded-md transition-colors"
            >
              <Plus className="w-3 h-3" />
              {t("filters.addWaypoint")}
            </button>
          </div>
        )}

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

      <PasteDialog
        open={pasteTargetIndex !== null}
        onClose={() => setPasteTargetIndex(null)}
        onParsed={(parsed) => {
          if (pasteTargetIndex !== null) {
            fillFromParsed(pasteTargetIndex, parsed);
          }
        }}
      />
    </Collapsible>
  );
}
