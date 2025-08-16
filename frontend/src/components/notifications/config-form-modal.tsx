import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createNotificationConfig, updateNotificationConfig } from '@/lib/api/sdk.gen'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription
} from '@/components/ui/dialog'
import type { NotificationChannelChoices } from '@/lib/api'

interface ConfigFormModalProps {
  isOpen: boolean
  onClose: () => void
  configToEdit: any | null
}

export function ConfigFormModal({ isOpen, onClose, configToEdit }: ConfigFormModalProps) {
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
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notificationConfigs'] })
      onClose()
    },
    onError: (error: any) => {
      if (error?.body?.detail) {
        setErrors({ general: error.body.detail })
      } else {
        setErrors({ general: 'An error occurred while saving the configuration' })
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
        setErrors({ general: 'An error occurred while updating the configuration' })
      }
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
      setErrors({})

    const newErrors: { name?: string; chatId?: string; general?: string } = {}
    if (!chatId.trim()) {
      newErrors.chatId = 'Chat ID is required'
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
            {configToEdit ? 'Edit Configuration' : 'Create Configuration'}
          </DialogTitle>
          <DialogDescription>
            {configToEdit
              ? 'Edit your notification configuration details.'
              : 'Create a new notification configuration for Telegram.'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            {errors.general && (
              <div className="text-red-500 text-sm">{errors.general}</div>
            )}

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right">
                Display Name
              </Label>
              <div className="col-span-3">
                <Input
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Enter display name (optional)"
                  className="col-span-3"
                />
              </div>
            </div>

            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="chatId" className="text-right">
                Chat ID *
              </Label>
              <div className="col-span-3">
                <Input
                  id="chatId"
                  value={chatId}
                  onChange={(e) => {
                    setChatId(e.target.value)
                    if (errors.chatId) {
                      setErrors(prev => ({ ...prev, chatId: undefined }))
                    }
                  }}
                  placeholder="Enter Telegram chat ID"
                  className={`col-span-3 ${errors.chatId ? 'border-red-500' : ''}`}
                  disabled={!!configToEdit} // Chat ID can't be edited after creation
                />
                {errors.chatId && (
                  <p className="text-red-500 text-xs mt-1">{errors.chatId}</p>
                )}
                {!configToEdit && (
                  <p className="text-gray-500 text-xs mt-1">
                    The Telegram chat ID where notifications will be sent
                  </p>
                )}
              </div>
            </div>

            {configToEdit && (
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="channel" className="text-right">
                  Channel
                </Label>
                <div className="col-span-3">
                  <Input
                    id="channel"
                    value="telegram"
                    disabled
                    className="col-span-3 bg-gray-100"
                  />
                  <p className="text-gray-500 text-xs mt-1">
                    Channel cannot be changed after creation
                  </p>
                </div>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" className="bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 text-white font-bold py-2 px-6 rounded-lg transition-all duration-300 hover:scale-105 shadow-lg" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                  {configToEdit ? 'Updating...' : 'Creating...'}
                </>
              ) : configToEdit ? (
                'Update'
              ) : (
                'Create'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
