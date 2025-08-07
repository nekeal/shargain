import { useState } from "react"
import { Bell, CheckCircle2, Edit3, ExternalLink, Eye, EyeOff, Globe, Plus, Trash2 } from "lucide-react"
import type { MonitoredUrl, OfferMonitor } from "@/types/dashboard";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"

interface MonitoredWebsitesProps {
  offerMonitor: OfferMonitor
  setOfferMonitor: (updater: (prev: OfferMonitor) => OfferMonitor) => void
  isVisible: boolean
}

export function MonitoredWebsites({ offerMonitor, setOfferMonitor, isVisible }: MonitoredWebsitesProps) {
  const [newUrl, setNewUrl] = useState({ name: "", url: "" })
  const [editingUrl, setEditingUrl] = useState<number | null>(null)

  const addUrl = () => {
    if (newUrl.name && newUrl.url) {
      const newMonitoredUrl: MonitoredUrl = {
        id: Date.now(),
        name: newUrl.name,
        url: newUrl.url,
        isActive: true
      }
      setOfferMonitor((prev) => ({
        ...prev,
        urls: [...prev.urls, newMonitoredUrl],
      }))
      setNewUrl({ name: "", url: "" })
    }
  }

  const removeUrl = (id: number) => {
    setOfferMonitor((prev) => ({
      ...prev,
      urls: prev.urls.filter((url: MonitoredUrl) => url.id !== id),
    }))
  }

  const toggleUrlActive = (id: number) => {
    setOfferMonitor((prev) => ({
      ...prev,
      urls: prev.urls.map((url: MonitoredUrl) => (url.id === id ? { ...url, isActive: !url.isActive } : url)),
    }))
  }

  const updateUrl = (id: number, updates: Partial<MonitoredUrl>) => {
    setOfferMonitor((prev) => ({
      ...prev,
      urls: prev.urls.map((url: MonitoredUrl) => (url.id === id ? { ...url, ...updates } : url)),
    }))
    setEditingUrl(null)
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
        {/* Add New URL */}
        <div className="p-4 bg-gradient-to-r from-violet-50 to-purple-50 rounded-lg border border-violet-100">
          <h4 className="font-medium text-gray-900 mb-4">Add New Website</h4>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="url-name">Website Name</Label>
              <Input
                id="url-name"
                value={newUrl.name}
                onChange={(e) => setNewUrl((prev) => ({ ...prev, name: e.target.value }))}
                className="bg-white/70 border-violet-200 focus:border-violet-500 focus:ring-violet-500"
                placeholder="e.g., Amazon Electronics"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="url-address">Website URL</Label>
              <Input
                id="url-address"
                value={newUrl.url}
                onChange={(e) => setNewUrl((prev) => ({ ...prev, url: e.target.value }))}
                className="bg-white/70 border-violet-200 focus:border-violet-500 focus:ring-violet-500"
                placeholder="https://example.com/deals"
              />
            </div>
          </div>
          <Button
            onClick={addUrl}
            disabled={!newUrl.name || !newUrl.url}
            className="mt-4 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 transition-all duration-300 hover:scale-105"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Website
          </Button>
        </div>

        {/* URL List */}
        <div className="space-y-4">
          {offerMonitor.urls.map((url: MonitoredUrl) => (
            <div
              key={url.id}
              className="p-4 bg-white/50 rounded-lg border border-gray-200 hover:border-violet-300 transition-all duration-300 group"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  {editingUrl === url.id ? (
                    <div className="space-y-3">
                      <Input
                        value={url.name}
                        onChange={(e) => updateUrl(url.id, { name: e.target.value })}
                        className="bg-white/70 border-violet-200 focus:border-violet-500 focus:ring-violet-500"
                        placeholder="Website name"
                      />
                      <Input
                        value={url.url}
                        onChange={(e) => updateUrl(url.id, { url: e.target.value })}
                        className="bg-white/70 border-violet-200 focus:border-violet-500 focus:ring-violet-500"
                        placeholder="Website URL"
                      />
                      <div className="flex space-x-2">
                        <Button
                          size="sm"
                          onClick={() => setEditingUrl(null)}
                          className="bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700"
                        >
                          <CheckCircle2 className="w-4 h-4 mr-1" />
                          Save
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => setEditingUrl(null)}>
                          Cancel
                        </Button>
                      </div>
                    </div>
                  ) : (
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
                        {url.lastChecked && (
                          <span className="flex items-center">
                            <CheckCircle2 className="w-4 h-4 mr-1 text-green-500" />
                            Last checked: {url.lastChecked}
                          </span>
                        )}
                        {url.offersFound !== undefined && (
                          <span className="flex items-center">
                            <Bell className="w-4 h-4 mr-1 text-violet-500" />
                            {url.offersFound} offers found
                          </span>
                        )}
                      </div>
                    </>
                  )}
                </div>

                {editingUrl !== url.id && (
                  <div className="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setEditingUrl(url.id)}
                      className="border-violet-200 text-violet-600 hover:bg-violet-50"
                    >
                      <Edit3 className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => toggleUrlActive(url.id)}
                      className={`border-gray-300 ${url.isActive ? "text-gray-600 hover:bg-gray-50" : "text-green-600 hover:bg-green-50"
                        }`}
                    >
                      {url.isActive ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => removeUrl(url.id)}
                      className="border-red-200 text-red-600 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                )}
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
