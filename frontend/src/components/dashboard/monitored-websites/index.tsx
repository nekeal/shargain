import { useState } from "react"
import { AlertCircle, CheckCircle, ExternalLink, Eye, EyeOff, Globe, Plus, Save, Trash2  } from "lucide-react"
import { z } from "zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useAddUrlMutation, useRemoveUrlMutation, useToggleUrlActiveMutation } from "./useMonitors"
import type { OfferMonitor } from "@/types/dashboard"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import cn from "@/lib/utils"
import { updateTargetName } from "@/lib/api/sdk.gen"

const urlSchema = z.string().url({ message: "Please enter a valid URL." }).nonempty({ message: "URL cannot be empty." })

interface MonitoredWebsitesProps {
  offerMonitor: OfferMonitor
  isVisible: boolean
}

export function MonitoredWebsites({ offerMonitor, isVisible }: MonitoredWebsitesProps) {
  const [newUrl, setNewUrl] = useState("")
  const [newName, setNewName] = useState("")
  const [urlError, setUrlError] = useState<string | null>(null)
  const [targetName, setTargetName] = useState(offerMonitor.name)
  const [updateSuccess, setUpdateSuccess] = useState(false)
  const [updateError, setUpdateError] = useState<string | null>(null)

  const queryClient = useQueryClient()

  const addUrlMutation = useAddUrlMutation(offerMonitor.id)
  const removeUrlMutation = useRemoveUrlMutation(offerMonitor.id)
  const toggleUrlActiveMutation = useToggleUrlActiveMutation(offerMonitor.id)

  const updateNameMutation = useMutation({
    mutationFn: (newMonitorName: string) => {
      setUpdateError(null);
      return updateTargetName({
        path: { target_id: offerMonitor.id },
        body: { name: newMonitorName },
        throwOnError: true,
      });
    },
    onSuccess: () => {
      setUpdateSuccess(true);
      queryClient.invalidateQueries({ queryKey: ['myTarget'] });
      setTimeout(() => setUpdateSuccess(false), 2000);
    },
    onError: (err: any) => {
      setUpdateError(err.message || "An unexpected error occurred.");
    },
  });

  const handleAddUrl = (e: React.FormEvent<HTMLFormElement>) => {
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
          },
        },
      )
    } catch (error) {
      if (error instanceof z.ZodError) {
        setUrlError(error.errors[0].message)
      }
    }
  }

  const handleChangeUrlAddress = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNewUrl(e.target.value)
    addUrlMutation.reset()
    setUrlError(null)
  }

  const handleChangeUrlName = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNewName(e.target.value)
  }

  return (
    <Card
      className={`border-0 bg-white/60 backdrop-blur-sm transition-all duration-700 delay-400 ${isVisible ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"
        }`}
    >
      <CardHeader>
        <CardTitle className="flex items-center text-2xl">
          <Globe className="w-6 h-6 mr-3 text-violet-600" />
          Monitored Websites
        </CardTitle>
        <CardDescription>Add and manage websites you want to monitor for offers</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Target Name Update */}
        <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900">Target Name</h3>
              <p className="text-sm text-gray-600">Update the name of your scraping target.</p>
            </div>
            <div className="flex items-center space-x-2">
              <Input
                value={targetName}
                onChange={(e) => {
                  setTargetName(e.target.value)
                  setUpdateError(null)
                }}
                className="w-48"
                disabled={updateNameMutation.isPending}
              />
              <Button
                onClick={() => updateNameMutation.mutate(targetName)}
                disabled={updateNameMutation.isPending || (targetName === offerMonitor.name && !updateError) || updateSuccess}
                className="w-32 justify-center bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 transition-all duration-300 hover:scale-105"
              >
                {updateNameMutation.isPending ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                    Saving...
                  </>
                ) : updateSuccess ? (
                  <CheckCircle className="w-5 h-5 text-white" />
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Update
                  </>
                )}
              </Button>
            </div>
          </div>
          {updateError && (
            <div className="flex items-center mt-2 text-sm text-red-600">
              <AlertCircle className="w-4 h-4 mr-2" />
              {updateError}
            </div>
          )}
        </div>
        {/* Add New URL */}
        <form
          onSubmit={handleAddUrl}
          className="p-4 bg-gradient-to-r from-violet-50 to-purple-50 rounded-lg border border-violet-100"
        >
          <h4 className="font-medium text-gray-900 mb-4">Add New Website</h4>
          <div className="space-y-2">
            <Label htmlFor="url-address">Website URL</Label>
            <Input
              id="url-address"
              value={newUrl}
              onChange={handleChangeUrlAddress}
              className={cn("bg-white/70 border-violet-200 focus:border-violet-500 focus:ring-violet-500", urlError ? "border-red-500" : "")}
              placeholder="https://example.com/deals"
            />
            {urlError && <div className="text-red-500 text-sm mt-1">{urlError}</div>}
          </div>
          <div className="space-y-2 mt-4">
            <Label htmlFor="url-name">Name</Label>
            <Input
              id="url-name"
              value={newName}
              onChange={handleChangeUrlName}
              className="bg-white/70 border-violet-200 focus:border-violet-500 focus:ring-violet-500"
              placeholder="e.g. Amazon Deals"
            />
          </div>

          {addUrlMutation.isError && (
            <div className="text-red-500 text-sm mt-2">{(addUrlMutation.error as any)?.detail[0].msg}</div>
          )}
          {addUrlMutation.isSuccess && <div className="text-green-500 text-sm mt-2">URL added successfully!</div>}

          <Button
            type="submit"
            disabled={!newUrl || addUrlMutation.isPending}
            className="mt-4 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 transition-all duration-300 hover:scale-105"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Website
          </Button>
        </form>

        {/* URL List */}
        <div className="space-y-4">
          {offerMonitor.urls.map((url) => (
            <div
              key={url.id}
              className="p-4 bg-white/50 rounded-lg border border-gray-200 hover:border-violet-300 transition-all duration-300 group"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <>
                    <div className="flex items-center space-x-3 mb-2">
                      <h4 className="font-medium text-gray-900">{url.name}</h4>
                      <Badge
                        className={`${url.isActive ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-600"
                          } border-0`}
                      >
                        {url.isActive ? "Active" : "Paused"}
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <a
                        href={url.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center hover:text-violet-600 transition-colors duration-300"
                      >
                        <ExternalLink className="w-4 h-4 mr-1" />
                        {url.url}
                      </a>
                    </div>
                  </>
                </div>

                <div className="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => toggleUrlActiveMutation.mutate({ urlId: url.id, isActive: url.isActive })}
                    className={`border-gray-300 ${url.isActive ? "text-gray-600 hover:bg-gray-50" : "text-green-600 hover:bg-green-50"
                      }`}
                  >
                    {url.isActive ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => removeUrlMutation.mutate(url.id)}
                    className="border-red-200 text-red-600 hover:bg-red-50"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          ))}

          {offerMonitor.urls.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <Globe className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium mb-2">No websites added yet</p>
              <p>Add your first website above to start monitoring offers</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
