import { useEffect, useMemo, useRef, useState } from "react"
import { useTranslation } from "react-i18next"
import { ExternalLink, Loader2, Lock, Plus, Save, Trash2 } from "lucide-react"
import { toast } from "sonner"
import { useUpdateUrlMutation } from "./useMonitors"
import type { ScrapingUrlResponse } from "@/lib/api/types.gen"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

const MAX_URL_LENGTH = 1024

interface QueryParamRow {
  id: number
  key: string
  value: string
}

interface ParsedUrlParts {
  baseUrl: string
  hash: string
  params: Array<{ key: string; value: string }>
}

function parseUrlParts(rawUrl: string): ParsedUrlParts | null {
  try {
    const parsed = new URL(rawUrl)
    return {
      baseUrl: `${parsed.origin}${parsed.pathname}`,
      hash: parsed.hash,
      params: Array.from(parsed.searchParams.entries()).map(([key, value]) => ({
        key,
        value,
      })),
    }
  } catch {
    return null
  }
}

function buildUrlFromParams(baseUrl: string, hash: string, params: Array<QueryParamRow>): string {
  const searchParams = new URLSearchParams()
  for (const param of params) {
    const trimmedKey = param.key.trim()
    if (trimmedKey) {
      searchParams.append(trimmedKey, param.value)
    }
  }
  const queryString = searchParams.toString()
  return `${baseUrl}${queryString ? `?${queryString}` : ""}${hash}`
}

interface EditUrlParamsDialogProps {
  targetId: number
  url: ScrapingUrlResponse | null
  isOpen: boolean
  onClose: () => void
}

export function EditUrlParamsDialog({
  targetId,
  url,
  isOpen,
  onClose,
}: EditUrlParamsDialogProps) {
  const { t } = useTranslation()
  const nextRowIdRef = useRef(0)
  const [params, setParams] = useState<Array<QueryParamRow>>([])

  const parsedParts = useMemo(() => (url ? parseUrlParts(url.url) : null), [url])

  useEffect(() => {
    if (!isOpen || !parsedParts) return
    setParams(
      parsedParts.params.map((item) => ({
        id: nextRowIdRef.current++,
        key: item.key,
        value: item.value,
      })),
    )
  }, [isOpen, parsedParts])

  const mutation = useUpdateUrlMutation(targetId, url?.id ?? 0)

  const constructedUrl = useMemo(() => {
    if (!parsedParts) return url?.url ?? ""
    return buildUrlFromParams(parsedParts.baseUrl, parsedParts.hash, params)
  }, [parsedParts, params, url?.url])

  const initialConstructedUrl = useMemo(() => {
    if (!parsedParts) return url?.url ?? ""
    return buildUrlFromParams(
      parsedParts.baseUrl,
      parsedParts.hash,
      parsedParts.params.map((item, id) => ({ id, ...item })),
    )
  }, [parsedParts, url?.url])

  const hasEmptyKey = params.some((p) => p.key.trim() === "")
  const isTooLong = constructedUrl.length > MAX_URL_LENGTH
  const hasChanges = url !== null && constructedUrl !== initialConstructedUrl

  const validationError = !parsedParts && url !== null
    ? t("dashboard.monitoredWebsites.editParamsDialog.invalidUrlError")
    : hasEmptyKey
      ? t("dashboard.monitoredWebsites.editParamsDialog.emptyKeyError")
      : isTooLong
        ? t("dashboard.monitoredWebsites.editParamsDialog.urlTooLongError", { max: MAX_URL_LENGTH })
        : null

  const handleAddParam = () => {
    setParams((prev) => [...prev, { id: nextRowIdRef.current++, key: "", value: "" }])
  }

  const handleRemoveParam = (id: number) => {
    setParams((prev) => prev.filter((row) => row.id !== id))
  }

  const handleUpdateParam = (id: number, field: "key" | "value", value: string) => {
    setParams((prev) =>
      prev.map((row) => (row.id === id ? { ...row, [field]: value } : row)),
    )
  }

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!url || validationError || !hasChanges) return

    mutation.mutate(
      { url: constructedUrl },
      {
        onSuccess: () => {
          toast.success(t("dashboard.monitoredWebsites.editParamsDialog.saveSuccess"))
          onClose()
        },
        onError: () => {
          toast.error(t("dashboard.monitoredWebsites.editParamsDialog.saveError"))
        },
      },
    )
  }

  return (
    <Dialog open={isOpen} onOpenChange={(open) => { if (!open) onClose() }}>
      <DialogContent className="sm:max-w-3xl lg:max-w-4xl max-h-[85vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>
            {t("dashboard.monitoredWebsites.editParamsDialog.title")}
          </DialogTitle>
          <DialogDescription>
            {t("dashboard.monitoredWebsites.editParamsDialog.description")}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} id="edit-url-params-form" className="space-y-4 overflow-y-auto pr-1 flex-1">
          {parsedParts && (
            <div className="space-y-1.5">
              <div className="flex items-center justify-between gap-2">
                <Label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5" aria-hidden="true" />
                  {t("dashboard.monitoredWebsites.editParamsDialog.baseUrlLabel")}
                </Label>
                <a
                  href={constructedUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline underline-offset-4"
                >
                  {t("dashboard.monitoredWebsites.editParamsDialog.openSearch")}
                  <ExternalLink className="w-3.5 h-3.5" aria-hidden="true" />
                </a>
              </div>
              <div className="px-3 py-2 rounded-md bg-muted/50 border border-border text-sm font-mono text-muted-foreground break-all select-all">
                {`${parsedParts.baseUrl}${parsedParts.hash}`}
              </div>
            </div>
          )}

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>{t("dashboard.monitoredWebsites.editParamsDialog.paramsLabel")}</Label>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleAddParam}
                disabled={mutation.isPending || !parsedParts}
              >
                <Plus className="w-3.5 h-3.5 mr-1.5" aria-hidden="true" />
                {t("dashboard.monitoredWebsites.editParamsDialog.addParam")}
              </Button>
            </div>

            {params.length === 0 ? (
              <p className="text-sm text-muted-foreground py-6 text-center border border-dashed border-border rounded-md">
                {t("dashboard.monitoredWebsites.editParamsDialog.noParams")}
              </p>
            ) : (
              <div className="border border-border rounded-md overflow-hidden">
                <div className="grid grid-cols-[1.25fr_1fr_auto] gap-2 px-3 py-1.5 bg-muted/40 border-b border-border text-xs font-medium text-muted-foreground">
                  <span>{t("dashboard.monitoredWebsites.editParamsDialog.keyColumn")}</span>
                  <span>{t("dashboard.monitoredWebsites.editParamsDialog.valueColumn")}</span>
                  <span className="w-8" />
                </div>
                <div className="divide-y divide-border">
                  {params.map((param) => (
                    <div
                      key={param.id}
                      className="grid grid-cols-[1.25fr_1fr_auto] items-center gap-2 px-2 py-1.5 bg-background"
                    >
                      <Input
                        value={param.key}
                        onChange={(e) => handleUpdateParam(param.id, "key", e.target.value)}
                        placeholder={t("dashboard.monitoredWebsites.editParamsDialog.keyPlaceholder")}
                        aria-label={t("dashboard.monitoredWebsites.editParamsDialog.keyPlaceholder")}
                        className="h-9 font-mono text-sm"
                        disabled={mutation.isPending}
                        spellCheck={false}
                      />
                      <Input
                        value={param.value}
                        onChange={(e) => handleUpdateParam(param.id, "value", e.target.value)}
                        placeholder={t("dashboard.monitoredWebsites.editParamsDialog.valuePlaceholder")}
                        aria-label={t("dashboard.monitoredWebsites.editParamsDialog.valuePlaceholder")}
                        className="h-9 font-mono text-sm"
                        disabled={mutation.isPending}
                        spellCheck={false}
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        onClick={() => handleRemoveParam(param.id)}
                        aria-label={t("dashboard.monitoredWebsites.editParamsDialog.removeParam")}
                        disabled={mutation.isPending}
                        className="h-8 w-8 shrink-0 text-muted-foreground hover:text-destructive"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {validationError && (
            <p className="text-sm text-destructive" role="alert">
              {validationError}
            </p>
          )}
        </form>

        <DialogFooter className="flex justify-end gap-2 pt-2">
          <Button type="button" variant="outline" onClick={onClose} disabled={mutation.isPending}>
            {t("dashboard.monitoredWebsites.addUrlDialog.cancel")}
          </Button>
          <Button
            type="submit"
            form="edit-url-params-form"
            disabled={!parsedParts || !hasChanges || validationError !== null || mutation.isPending}
          >
            {mutation.isPending ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden="true" />
            ) : (
              <Save className="w-4 h-4 mr-2" aria-hidden="true" />
            )}
            {t("dashboard.monitoredWebsites.editParamsDialog.save")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
