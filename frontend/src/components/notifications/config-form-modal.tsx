import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { NotificationChannelChoices } from '@/lib/api'
import { createNotificationConfig, updateNotificationConfig } from '@/lib/api/sdk.gen'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'

interface ConfigFormModalProps {
  isOpen: boolean
  onClose: () => void
  configToEdit: any | null
  onSuccess?: (configId: number) => void
}

export function ConfigFormModal({ isOpen, onClose, configToEdit, onSuccess }: ConfigFormModalProps) {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [chatId, setChatId] = useState('')
  const [errors, setErrors] = useState<{ name?: string; chatId?: string; general?: string }>({})

  useEffect(() => {
    if (configToEdit) {
      setName(configToEdit.name || '')
      setChatId(configToEdit.chatId || '')
    } else {
      setName('')
      setChatId('')
    }
    setErrors({})
  }, [configToEdit, isOpen])

  const createMutation = useMutation({
    mutationFn: (data: { name: string | null; chatId: string; channel: NotificationChannelChoices }) =>
      createNotificationConfig({ body: { name: data.name, chatId: data.chatId, channel: data.channel } }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['notificationConfigs'] })
      if (onSuccess) {
        onSuccess(data.data.id)
      }
      onClose()
    },
    onError: (error: any) => {
      if (error?.body?.detail) {
        setErrors({ general: error.body.detail })
      } else {
        setErrors({ general: t('notifications.form.saveError') })
      }
    }
  })

  const updateMutation = useMutation({
    mutationFn: (data: { config_id: number; body: { name: string | null } }) =>
      updateNotificationConfig({ path: { config_id: data.config_id }, body: data.body }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notificationConfigs'] })
      onClose()
    },
    onError: (error: any) => {
      if (error?.body?.detail) {
        setErrors({ general: error.body.detail })
      } else {
        setErrors({ general: t('notifications.form.updateError') })
      }
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setErrors({})

    const newErrors: { name?: string; chatId?: string; general?: string } = {}
    if (!chatId.trim()) {
      newErrors.chatId = t('notifications.form.chatIdRequired')
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    if (configToEdit) {
      updateMutation.mutate({
        config_id: configToEdit.id,
        body: { name: name || null }
      })
    } else {
      createMutation.mutate({
        name: name || null,
        chatId,
        channel: 'telegram' // Only telegram is supported for now
      })
    }
  }

  const isSubmitting = createMutation.isPending || updateMutation.isPending

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>
              {configToEdit ? t('notifications.form.editTitle') : t('notifications.form.createTitle')}
            </DialogTitle>
            <DialogDescription>
              {configToEdit
                ? t('notifications.form.editDescription')
                : t('notifications.form.createDescription')}
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSubmit}>
            <div className="grid gap-4 py-4">
              {errors.general && (
                <div className="text-destructive text-sm">{errors.general}</div>
              )}

              <div className="space-y-2">
                <Label htmlFor="name">
                  {t('notifications.form.nameLabel')}
                </Label>
                <Input
                  id="name"
                  name="name"
                  autoComplete="off"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder={t('notifications.form.namePlaceholder')}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="chatId">
                  {t('notifications.form.chatIdLabel')}
                </Label>
                <Input
                  id="chatId"
                  name="chatId"
                  autoComplete="off"
                  spellCheck={false}
                  value={chatId}
                  onChange={(e) => {
                    setChatId(e.target.value)
                    if (errors.chatId) {
                      setErrors(prev => ({ ...prev, chatId: undefined }))
                    }
                  }}
                  placeholder={t('notifications.form.chatIdPlaceholder')}
                  className={errors.chatId ? 'border-destructive' : ''}
                  disabled={!!configToEdit} // Chat ID can't be edited after creation
                />
                {errors.chatId && (
                  <p className="text-destructive text-xs">{errors.chatId}</p>
                )}
                {!configToEdit && (
                  <p className="text-muted-foreground text-xs">
                    {t('notifications.form.helpTelegram')}
                  </p>
                )}
              </div>
            </div>

            {configToEdit && (
              <div className="space-y-2">
                <Label htmlFor="channel">
                  {t('notifications.form.channelLabel')}
                </Label>
                <Input
                  id="channel"
                  value="telegram"
                  disabled
                  className="bg-muted"
                />
                <p className="text-muted-foreground text-xs">
                  {t('notifications.form.channelLocked')}
                </p>
              </div>
            )}

            <DialogFooter>
              <Button type="button" variant="outline" onClick={onClose}>
                {t('notifications.form.cancel')}
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                    {configToEdit ? t('notifications.form.updating') : t('notifications.form.creating')}
                  </>
                ) : configToEdit ? (
                  t('notifications.form.update')
                ) : (
                  t('notifications.form.create')
                )}
              </Button>
            </DialogFooter>
        </form>
      </DialogContent >
    </Dialog >
  )
}
