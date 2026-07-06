import React, { useState } from "react"
import { useTranslation } from "react-i18next"
import { ChevronLeft, Clock, ExternalLink, Eye, EyeOff, Filter, MapPin, Trash2 } from "lucide-react"
import { useRemoveUrlMutation, useToggleUrlActiveMutation, useUpdateUrlMutation } from "./monitored-websites/useMonitors"
import { FilterEditor } from "./FilterEditor"
import { LocationEditor } from "./LocationEditor"
import type { MonitoredUrl } from "@/types/dashboard"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import cn from "@/lib/utils"

interface UrlCardProps {
  url: MonitoredUrl
  targetId: number
}

const UrlCardHeader = React.memo(function UrlCardHeader({ url, targetId }: UrlCardProps) {
  const { t } = useTranslation()
  const toggleUrlActiveMutation = useToggleUrlActiveMutation(targetId)
  const removeUrlMutation = useRemoveUrlMutation(targetId)

  return (
    <div className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1 flex-wrap">
          <h3 className="font-medium text-foreground text-sm truncate">{url.name}</h3>
          <Badge variant={url.isActive ? "success" : "secondary"}>
            {url.isActive ? t("dashboard.monitoredWebsites.active") : t("dashboard.monitoredWebsites.paused")}
          </Badge>
        </div>
        <a
          href={url.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-muted-foreground hover:text-primary transition-colors flex items-center gap-1 truncate block"
        >
          <ExternalLink className="w-3 h-3 inline shrink-0" aria-hidden="true" />
          <span className="truncate max-w-[400px]">{url.url}</span>
        </a>
        <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {url.lastCheckedAt ? new Date(url.lastCheckedAt).toLocaleString() : t("dashboard.monitoredWebsites.pending")}
          </span>
          {url.showLocationMapInNotifications && (
            <span className="flex items-center gap-1">
              <MapPin className="w-3 h-3" />
              {t("dashboard.monitoredWebsites.urlCard.locationOn")}
            </span>
          )}
        </div>
      </div>

      <div className="flex items-center space-x-2 shrink-0">
        <Button
          size="sm"
          variant="outline"
          onClick={() => toggleUrlActiveMutation.mutate({ urlId: url.id, currentlyActive: url.isActive })}
          disabled={toggleUrlActiveMutation.isPending}
          aria-label={url.isActive ? t("dashboard.monitoredWebsites.pause") : t("dashboard.monitoredWebsites.resume")}
        >
          {url.isActive ? <EyeOff className="w-4 h-4" aria-hidden="true" /> : <Eye className="w-4 h-4" aria-hidden="true" />}
          <span className="hidden sm:inline">{url.isActive ? t("dashboard.monitoredWebsites.pause") : t("dashboard.monitoredWebsites.resume")}</span>
        </Button>
        <Button
          size="sm"
          variant="destructive"
          onClick={() => removeUrlMutation.mutate(url.id)}
          disabled={removeUrlMutation.isPending}
          aria-label={t("dashboard.monitoredWebsites.delete")}
        >
          <Trash2 className="w-4 h-4" aria-hidden="true" />
          <span className="hidden sm:inline">{t("dashboard.monitoredWebsites.delete")}</span>
        </Button>
      </div>
    </div>
  )
})

interface UrlCardFiltersProps {
  url: MonitoredUrl
  targetId: number
  filterOpen: boolean
  setFilterOpen: (open: boolean) => void
}

const UrlCardFilters = React.memo(function UrlCardFilters({ url, targetId, filterOpen, setFilterOpen }: UrlCardFiltersProps) {
  const { t } = useTranslation()
  const updateUrlMutation = useUpdateUrlMutation(targetId, url.id)

  const activeRulesCount = url.filters?.ruleGroups.reduce(
    (acc, g) => acc + g.rules.filter((r) => r.value.trim()).length,
    0
  ) ?? 0

  return (
    <div className="border-b border-border">
      <button
        onClick={() => setFilterOpen(!filterOpen)}
        aria-expanded={filterOpen}
        aria-controls={`filter-panel-${url.id}`}
        className="w-full px-4 py-2.5 flex items-center justify-between text-sm hover:bg-secondary/30 transition-colors"
      >
        <span className="flex items-center gap-2 text-muted-foreground">
          <Filter className="w-3.5 h-3.5" aria-hidden="true" />
          {t("dashboard.monitoredWebsites.urlCard.filters")}
          {activeRulesCount > 0 && (
            <Badge variant="secondary" className="text-xs border-0">
              {activeRulesCount}
            </Badge>
          )}
        </span>
        <ChevronLeft
          className={cn("w-3.5 h-3.5 text-muted-foreground transition-transform", filterOpen && "-rotate-90")}
          aria-hidden="true"
        />
      </button>
      {filterOpen && (
        <div id={`filter-panel-${url.id}`} className="px-4 py-3 bg-secondary/20 border-t border-border">
          <FilterEditor
            initialData={url.filters ?? null}
            onSave={(data) => updateUrlMutation.mutate({ filters: data })}
          />
        </div>
      )}
    </div>
  )
})

interface UrlCardLocationProps {
  url: MonitoredUrl
  targetId: number
  locationOpen: boolean
  setLocationOpen: (open: boolean) => void
}

const UrlCardLocation = React.memo(function UrlCardLocation({ url, targetId, locationOpen, setLocationOpen }: UrlCardLocationProps) {
  const { t } = useTranslation()
  const updateUrlMutation = useUpdateUrlMutation(targetId, url.id)

  return (
    <div>
      <button
        onClick={() => setLocationOpen(!locationOpen)}
        aria-expanded={locationOpen}
        aria-controls={`location-panel-${url.id}`}
        className="w-full px-4 py-2.5 flex items-center justify-between text-sm hover:bg-secondary/30 transition-colors"
      >
        <span className="flex items-center gap-2 text-muted-foreground">
          <MapPin className="w-3.5 h-3.5" aria-hidden="true" />
          {t("dashboard.monitoredWebsites.urlCard.location")}
          <Badge
            variant={url.showLocationMapInNotifications ? "success" : "secondary"}
            className="text-xs border-0"
          >
            {url.showLocationMapInNotifications
              ? t("dashboard.monitoredWebsites.urlCard.locationOn")
              : t("dashboard.monitoredWebsites.urlCard.locationOff")}
          </Badge>
        </span>
        <ChevronLeft
          className={cn("w-3.5 h-3.5 text-muted-foreground transition-transform", locationOpen && "-rotate-90")}
          aria-hidden="true"
        />
      </button>
      {locationOpen && (
        <div id={`location-panel-${url.id}`} className="px-4 py-3 bg-secondary/20 border-t border-border">
          <LocationEditor
            initialShowLocationMap={url.showLocationMapInNotifications ?? false}
            initialWaypoints={url.waypoints ?? []}
            onSave={(showLocationMapInNotifications, waypoints) =>
              updateUrlMutation.mutate({ showLocationMapInNotifications, waypoints })
            }
          />
        </div>
      )}
    </div>
  )
})

export function UrlCard2({ url, targetId }: UrlCardProps) {
  const [filterOpen, setFilterOpen] = useState(false)
  const [locationOpen, setLocationOpen] = useState(false)

  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden">
      <UrlCardHeader url={url} targetId={targetId} />
      <div className="border-t border-border">
        <UrlCardFilters url={url} targetId={targetId} filterOpen={filterOpen} setFilterOpen={setFilterOpen} />
        <UrlCardLocation url={url} targetId={targetId} locationOpen={locationOpen} setLocationOpen={setLocationOpen} />
      </div>
    </div>
  )
}
