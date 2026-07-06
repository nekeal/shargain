import { useEffect, useRef, useState } from "react"
import { Plus, X } from "lucide-react"
import type { WaypointSchema } from "@/lib/api/types.gen"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import cn from "@/lib/utils"

interface WaypointWithId extends WaypointSchema {
  id?: string
}

interface LocationEditorProps {
  initialShowLocationMap: boolean
  initialWaypoints: Array<WaypointSchema>
  onSave: (showLocationMap: boolean, waypoints: Array<WaypointSchema>) => void
}

function getValidationError(lat: number, lon: number): string | null {
  if (lat < -90 || lat > 90) return "Latitude must be between -90 and 90"
  if (lon < -180 || lon > 180) return "Longitude must be between -180 and 180"
  return null
}

export function LocationEditor({
  initialShowLocationMap,
  initialWaypoints,
  onSave,
}: LocationEditorProps) {
  const [enabled, setEnabled] = useState(initialShowLocationMap)
  const [waypoints, setWaypoints] = useState<Array<WaypointWithId>>(
    initialWaypoints.map(w => ({ ...w, id: crypto.randomUUID() }))
  )
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [snapshot, setSnapshot] = useState(() =>
    JSON.stringify({ enabled: initialShowLocationMap, waypoints: initialWaypoints })
  )
  const [status, setStatus] = useState<"idle" | "applied" | "fading">("idle")
  const timerRef = useRef<ReturnType<typeof setTimeout>>(undefined)

  // Sync local state when initial props change
  useEffect(() => {
    setEnabled(initialShowLocationMap)
    setWaypoints(initialWaypoints.map(w => ({ ...w, id: crypto.randomUUID() })))
    const newSnapshot = JSON.stringify({ enabled: initialShowLocationMap, waypoints: initialWaypoints })
    setSnapshot(newSnapshot)
    setStatus("idle")
  }, [initialShowLocationMap, initialWaypoints])

  const current = JSON.stringify({ enabled, waypoints })
  const isDirty = current !== snapshot
  const isFading = status === "fading"

  const handleApply = () => {
    const clampedWaypoints = waypoints.map(wp => ({
      ...wp,
      lat: Math.max(-90, Math.min(90, wp.lat)),
      lon: Math.max(-180, Math.min(180, wp.lon)),
    }))
    setWaypoints(clampedWaypoints)
    setSnapshot(JSON.stringify({ enabled, waypoints: clampedWaypoints }))
    setStatus("applied")
    clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => {
      setStatus("fading")
      setTimeout(() => setStatus("idle"), 300)
    }, 2000)

    // Strip id field before sending to API
    const waypointsForApi = clampedWaypoints.map(({ id, ...rest }) => rest)
    onSave(enabled, waypointsForApi)
  }

  return (
    <div>
      <div className="space-y-3">
        <div className="flex items-center justify-between p-2.5 bg-secondary/30 rounded-lg">
          <div>
            <Label className="text-sm font-medium">Include location</Label>
            <p className="text-xs text-muted-foreground">Adds map link and distance to alerts</p>
          </div>
          <Switch checked={enabled} onCheckedChange={setEnabled} aria-label="Include location" />
        </div>

        {enabled && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label className="text-xs text-muted-foreground">Reference points</Label>
              <button
                onClick={() =>
                  setWaypoints((prev) => [...prev, { name: "", lat: 0, lon: 0, id: crypto.randomUUID() }])
                }
                className="flex items-center gap-1 text-xs text-primary/60 hover:text-primary transition-colors"
              >
                <Plus className="w-3 h-3" aria-hidden="true" /> Add
              </button>
            </div>

            {waypoints.map((wp, displayIdx) => (
              <div key={wp.id ?? `${wp.lat},${wp.lon},${wp.name}`} className="bg-secondary/30 rounded-lg p-2.5 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-muted-foreground">
                    Waypoint {displayIdx + 1}
                  </span>
                  {waypoints.length > 1 && (
                    <button
                      onClick={() => setWaypoints((prev) => prev.filter((p) => p.id !== wp.id))}
                      className="p-0.5 rounded text-muted-foreground/40 hover:text-destructive hover:bg-destructive/10 transition-colors"
                      aria-label="Remove waypoint"
                    >
                      <X className="w-3 h-3" aria-hidden="true" />
                    </button>
                  )}
                </div>
                <Input
                  defaultValue={wp.name}
                  placeholder="Name"
                  className="h-7 text-xs"
                  onChange={(e) =>
                    setWaypoints((prev) =>
                      prev.map((p) => (p.id === wp.id ? { ...p, name: e.target.value } : p))
                    )
                  }
                />
                <div className="flex gap-1.5">
                  <Input
                    defaultValue={String(wp.lat)}
                    placeholder="Latitude"
                    className="h-7 text-xs flex-1"
                    onChange={(e) => {
                      const val = Number(e.target.value) || 0
                      const errKey = `lat-${wp.id}`
                      const error = getValidationError(val, wp.lon)
                      setFieldErrors(prev => error ? { ...prev, [errKey]: error } : { ...prev, [errKey]: undefined })
                      setWaypoints((prev) =>
                        prev.map((p) =>
                          p.id === wp.id ? { ...p, lat: val } : p
                        )
                      )
                    }}
                  />
                  <Input
                    defaultValue={String(wp.lon)}
                    placeholder="Longitude"
                    className="h-7 text-xs flex-1"
                    onChange={(e) => {
                      const val = Number(e.target.value) || 0
                      const errKey = `lon-${wp.id}`
                      const error = getValidationError(wp.lat, val)
                      setFieldErrors(prev => error ? { ...prev, [errKey]: error } : { ...prev, [errKey]: undefined })
                      setWaypoints((prev) =>
                        prev.map((p) =>
                          p.id === wp.id ? { ...p, lon: val } : p
                        )
                      )
                    }}
                  />
                </div>
                  {fieldErrors[`lat-${wp.id}`] && (
                    <span className="text-xs text-destructive" role="alert">{fieldErrors[`lat-${wp.id}`]}</span>
                  )}
                  {fieldErrors[`lon-${wp.id}`] && (
                    <span className="text-xs text-destructive" role="alert">{fieldErrors[`lon-${wp.id}`]}</span>
                  )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Apply bar */}
      {isDirty && status === "idle" && (
        <div className="sticky bottom-0 -mx-3 px-3 py-2.5 bg-card border-t border-border mt-3 flex items-center justify-between z-10">
          <span className="text-xs flex items-center gap-1.5 text-warning-muted-foreground">
            <span className="w-1.5 h-1.5 rounded-full bg-warning" />
            Unsaved changes
          </span>
          <Button size="sm" className="h-7 text-xs" onClick={handleApply}>
            Apply
          </Button>
        </div>
      )}
      {status === "applied" && (
        <div
          className={cn(
            "sticky bottom-0 -mx-3 px-3 py-2.5 bg-card border-t border-border mt-3 flex items-center justify-between z-10 transition-opacity duration-300",
            isFading && "opacity-0"
          )}
        >
          <span className="text-xs flex items-center gap-1.5 text-success-muted-foreground">
            <svg
              className="w-3.5 h-3.5 text-success"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
            Applied
          </span>
          <span className="text-xs text-muted-foreground">
            {waypoints.length} point{waypoints.length !== 1 ? "s" : ""}
          </span>
        </div>
      )}
    </div>
  )
}