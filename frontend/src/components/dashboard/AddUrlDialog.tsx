import { Plus } from "lucide-react"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { z } from "zod"
import { toast } from "sonner"
import { useAddUrlMutation } from "./monitored-websites/useMonitors"
import type { OfferMonitor } from "@/types/dashboard"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import cn from "@/lib/utils"

const urlSchema = z.url({ message: "Please enter a valid URL." }).min(1, { message: "URL cannot be empty." })

interface AddUrlDialogProps {
  offerMonitor: OfferMonitor
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
}

export function AddUrlDialog({ offerMonitor, isOpen, onClose, onSuccess }: AddUrlDialogProps) {
  const { t } = useTranslation();
  const [newUrl, setNewUrl] = useState("")
  const [newName, setNewName] = useState("")
  const [urlError, setUrlError] = useState<string | null>(null)

  const addUrlMutation = useAddUrlMutation(offerMonitor.id)

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    try {
      urlSchema.parse(newUrl)
      setUrlError(null)
      addUrlMutation.mutate(
        { url: newUrl, name: newName },
        {
          onSuccess: () => {
            setNewUrl("")
            setNewName("")
            onClose()
            toast.success(t('dashboard.monitoredWebsites.toast.added'))
            onSuccess?.()
          },
          onError: (err: Error) => {
            const fallbackMessage = t('dashboard.monitoredWebsites.addError')
            const apiError = err as { code?: string }
            if (apiError.code === "quota_exceeded") {
              toast.error(t('dashboard.monitoredWebsites.quotaExceeded'))
            } else {
              toast.error(fallbackMessage)
            }
          },
        },
      )
    } catch (error) {
      if (error instanceof z.ZodError) {
        setUrlError(error.issues[0].message)
      }
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-lg animate-zoom-in motion-reduce:animate-none">
<DialogHeader>
            <DialogTitle>{t('dashboard.monitoredWebsites.addUrlDialog.title')}</DialogTitle>
            <DialogDescription>{t('dashboard.monitoredWebsites.addUrlDialog.description')}</DialogDescription>
          </DialogHeader>
        <form onSubmit={handleSubmit} id="add-url-form" className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="dialog-url">{t('dashboard.monitoredWebsites.addUrlDialog.urlLabel')}</Label>
            <Input
              id="dialog-url"
              name="url"
              autoComplete="url"
              value={newUrl}
              onChange={(e) => { setNewUrl(e.target.value); setUrlError(null); }}
              className={cn(urlError ? "border-destructive focus-visible:ring-destructive/50" : "")}
              placeholder="https://example.com/deals…"
              aria-invalid={!!urlError}
              aria-describedby={urlError ? "dialog-url-error" : undefined}
              disabled={addUrlMutation.isPending}
            />
            {urlError && <div id="dialog-url-error" className="text-destructive text-sm" role="alert">{urlError}</div>}
          </div>
          <div className="space-y-2">
            <Label htmlFor="dialog-name">{t('dashboard.monitoredWebsites.addUrlDialog.nameLabel')}</Label>
            <Input
              id="dialog-name"
              name="name"
              autoComplete="off"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder={t('dashboard.monitoredWebsites.namePlaceholder')}
              disabled={addUrlMutation.isPending}
              spellCheck={false}
            />
          </div>
        </form>
        <DialogFooter className="flex justify-end gap-2">
          <Button variant="outline" onClick={onClose} disabled={addUrlMutation.isPending}>
            {t('dashboard.monitoredWebsites.addUrlDialog.cancel')}
          </Button>
          <Button type="submit" form="add-url-form" disabled={!newUrl || addUrlMutation.isPending}>
            <Plus className="w-4 h-4 mr-2" aria-hidden="true" />
            {t('dashboard.monitoredWebsites.addUrlDialog.add')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
