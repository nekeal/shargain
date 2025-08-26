import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Edit, Plus, Trash2 } from 'lucide-react'
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
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-violet-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
        <p className="text-red-700 font-medium">Error loading notification configurations</p>
      </div>
    )
  }

  const configs = data?.data.configs || []

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-gray-900">Notification Configurations</h2>
        <Button
          onClick={handleCreateClick}
          className="bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 text-white font-bold py-2 px-6 rounded-lg transition-all duration-300 hover:scale-105 shadow-lg"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create New Configuration
        </Button>
      </div>

      {configs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {configs.map((config) => (
            <Card key={config.id} className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-xl font-semibold text-gray-900">
                  {config.name || 'Unnamed Configuration'}
                </CardTitle>
                <div className="flex space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleEditClick(config)}
                    className="text-violet-600 hover:text-violet-800 transition-colors"
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDeleteClick(config.id)}
                    className="text-red-500 hover:text-red-700 transition-colors"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 capitalize">{config.channel}</p>
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <p className="text-sm text-gray-500">
                    {config.chatId ? `Chat ID: ${config.chatId}` : 'No chat ID configured'}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-lg p-12 text-center">
          <div className="mx-auto w-24 h-24 bg-violet-100 rounded-full flex items-center justify-center mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-violet-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">No notification configurations yet</h3>
          <p className="text-gray-600 mb-8 max-w-md mx-auto">
            Get started by creating your first notification configuration to receive alerts when new offers are found.
          </p>
          <Button
            onClick={handleCreateClick}
            className="bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 text-white font-bold py-3 px-8 rounded-lg transition-all duration-300 hover:scale-105 shadow-lg"
          >
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
