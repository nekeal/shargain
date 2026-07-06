import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Bell, Edit, Plus, Trash2 } from 'lucide-react'
import { deleteNotificationConfig, listNotificationConfigs } from '@/lib/api/sdk.gen'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { ConfigFormModal } from '@/components/notifications/config-form-modal'

export function NotificationListPage() {
  const queryClient = useQueryClient()
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [configToDelete, setConfigToDelete] = useState<number | null>(null)
  const [isFormModalOpen, setIsFormModalOpen] = useState(false)
  const [configToEdit, setConfigToEdit] = useState<any | null>(null)

  const { data, isLoading, error } = useQuery({
    queryKey: ['notificationConfigs'],
    queryFn: () => listNotificationConfigs(),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteNotificationConfig({ path: { config_id: id } }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notificationConfigs'] })
      setIsDeleteDialogOpen(false)
    },
  })

  const handleDeleteClick = (id: number) => {
    setConfigToDelete(id)
    setIsDeleteDialogOpen(true)
  }

  const handleConfirmDelete = () => {
    if (configToDelete) {
      deleteMutation.mutate(configToDelete)
    }
  }

  const handleEditClick = (config: any) => {
    setConfigToEdit(config)
    setIsFormModalOpen(true)
  }

  const handleCreateClick = () => {
    setConfigToEdit(null)
    setIsFormModalOpen(true)
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary motion-reduce:animate-none"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 text-center">
        <p className="text-destructive font-medium">Error loading notification configurations</p>
      </div>
    )
  }

  const configs = data?.data.configs || []

  return (
    <div className="space-y-3">
      <div className="sm:text-right px-6 pt-6">
        <Button
          onClick={handleCreateClick}
          className="w-full sm:w-auto"
        >
          <Plus className="w-5 h-5 ml-0 mr-2" />
          Create New Configuration
        </Button>
      </div>

      {configs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
          {configs.map((config) => (
            <Card key={config.id}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="truncate">
                  {config.name || 'Unnamed Configuration'}
                </CardTitle>
                <div className="flex space-x-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleEditClick(config)}
                    aria-label="Edit configuration"
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDeleteClick(config.id)}
                    aria-label="Delete configuration"
                    className="text-muted-foreground hover:text-destructive"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground capitalize">{config.channel}</p>
                <div className="mt-4 pt-4 border-t border-border">
                  <p className="text-sm text-muted-foreground">
                    {config.chatId ? `Chat ID: ${config.chatId}` : 'No chat ID configured'}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="p-12 text-center">
          <div className="mx-auto w-16 h-16 bg-secondary rounded-full flex items-center justify-center mb-4">
            <Bell className="w-8 h-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-semibold text-foreground mb-2">No notification configurations yet</h3>
          <p className="text-sm text-muted-foreground mb-6 max-w-sm mx-auto">
            Get started by creating your first notification configuration to receive alerts when new offers are found.
          </p>
          <Button onClick={handleCreateClick} size="lg">
            <Plus className="w-4 h-4 mr-2" />
            Create Your First Configuration
          </Button>
        </div>
      )}

      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Deletion</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this notification configuration? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleConfirmDelete}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ConfigFormModal
        isOpen={isFormModalOpen}
        onClose={() => {
          setIsFormModalOpen(false)
          setConfigToEdit(null)
        }}
        configToEdit={configToEdit}
      />
    </div>
  )
}
