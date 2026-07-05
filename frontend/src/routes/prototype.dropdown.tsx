import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator } from '@/components/ui/dropdown-menu'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { MoreHorizontal, Pause, Play, Filter, MapPin, Trash2, Plus, X, MapPin as MapPinIcon, Save, ChevronDown, LayoutDashboard, Columns, SquareMousePointer } from 'lucide-react'

const mockUrls = [
  { id: 1, name: 'Rare Lego Sets', url: 'https://olx.pl/lego/star-wars/q-lego-star-wars/', isActive: true, filterCount: 3 },
  { id: 2, name: 'Vintage Cameras', url: 'https://olx.pl/foto/kamery-analogowe/', isActive: true, filterCount: 0 },
  { id: 3, name: 'Mechanical Keyboards', url: 'https://olx.pl/komputery/klasyczne-mechaniczne/', isActive: false, filterCount: 2 },
]

const mockFilters = {
  ruleGroups: [
    { logic: 'and', rules: [
      { field: 'title', operator: 'contains', value: 'lego', caseSensitive: false },
      { field: 'title', operator: 'not_contains', value: 'damaged', caseSensitive: false },
      { field: 'title', operator: 'contains', value: 'star wars', caseSensitive: false },
    ]}
  ]
}

const mockLocation = {
  showLocationMap: true,
  waypoints: [
    { name: 'Warsaw Center', lat: 52.2297, lon: 21.0122 },
    { name: 'Krakow Old Town', lat: 50.0614, lon: 19.9366 },
  ]
}

type ViewMode = 'collapsible' | 'side-panel' | 'modal'

export const Route = createFileRoute('/prototype/dropdown')({
  component: PrototypeDropdown,
})

function PrototypeDropdown() {
  const [viewMode, setViewMode] = useState<ViewMode>('side-panel')
  const [deleteTarget, setDeleteTarget] = useState<typeof mockUrls[0] | null>(null)
  const [filterTarget, setFilterTarget] = useState<typeof mockUrls[0] | null>(null)
  const [locationTarget, setLocationTarget] = useState<typeof mockUrls[0] | null>(null)
  const [filterGroups, setFilterGroups] = useState(mockFilters.ruleGroups)
  const [locationSettings, setLocationSettings] = useState(mockLocation)
  const [pinned, setPinned] = useState(false)

  const openFilters = (url: typeof mockUrls[0]) => {
    setFilterTarget(url)
    setFilterGroups(mockFilters.ruleGroups)
  }
  const openLocation = (url: typeof mockUrls[0]) => {
    setLocationTarget(url)
    setLocationSettings(mockLocation)
  }

  // For side-panel mode: which URL's panel is open
  const [panelUrlId, setPanelUrlId] = useState<number | null>(null)
  const [panelType, setPanelType] = useState<'filters' | 'location' | null>(null)

  const panelUrl = panelUrlId ? mockUrls.find(u => u.id === panelUrlId) : null

  return (
    <div className="container mx-auto px-4 py-6 max-w-[1400px]">
      {/* Header with view mode toggle */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-semibold">Prototype: URL Row Actions</h1>
          <p className="text-muted-foreground text-sm">
            Compare three patterns for filter/location editing. Switch modes to test cross-URL comparison.
          </p>
        </div>
        
        <Tabs value={viewMode} onValueChange={setViewMode} className="w-full sm:w-auto">
          <TabsList className="grid grid-cols-3">
            <TabsTrigger value="collapsible">
              <LayoutDashboard className="h-4 w-4 mr-2" />
              Collapsible
            </TabsTrigger>
            <TabsTrigger value="side-panel">
              <Columns className="h-4 w-4 mr-2" />
              Side Panel
            </TabsTrigger>
            <TabsTrigger value="modal">
              <SquareMousePointer className="h-4 w-4 mr-2" />
              Modal
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Side Panel Mode Layout */}
      {viewMode === 'side-panel' && (
        <div className="flex gap-4">
          {/* URL List - takes remaining space */}
          <div className="flex-1 min-w-0">
            <UrlList 
              urls={mockUrls}
              onDelete={setDeleteTarget}
              onOpenFilters={openFilters}
              onOpenLocation={openLocation}
              viewMode="side-panel"
              panelUrlId={panelUrlId}
              setPanelUrlId={setPanelUrlId}
              setPanelType={setPanelType}
            />
          </div>
          
          {/* Side Panel */}
          {(panelUrlId || panelType) && (
            <SidePanel
              url={panelUrl}
              type={panelType}
              filterGroups={filterGroups}
              setFilterGroups={setFilterGroups}
              locationSettings={locationSettings}
              setLocationSettings={setLocationSettings}
              onClose={() => { setPanelUrlId(null); setPanelType(null); }}
              onPin={setPinned}
              pinned={pinned}
            />
          )}
        </div>
      )}

      {/* Collapsible Mode - Traditional List */}
      {viewMode === 'collapsible' && (
        <UrlList
          urls={mockUrls}
          onDelete={setDeleteTarget}
          onOpenFilters={openFilters}
          onOpenLocation={openLocation}
          viewMode="collapsible"
        />
      )}

      {/* Modal Mode - Traditional List */}
      {viewMode === 'modal' && (
        <UrlList
          urls={mockUrls}
          onDelete={setDeleteTarget}
          onOpenFilters={openFilters}
          onOpenLocation={openLocation}
          viewMode="modal"
        />
      )}

      {/* Delete Confirm Modal (shared) */}
      <Dialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete URL?</DialogTitle>
            <DialogDescription>
              This will permanently remove <strong>{deleteTarget?.name}</strong> and its filters/location settings.
              Monitoring will stop immediately.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteTarget(null)}>Cancel</Button>
            <Button variant="destructive" onClick={() => { alert(`Deleted: ${deleteTarget?.name}`); setDeleteTarget(null); }}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Filter Builder Modal (for modal mode) */}
      {viewMode === 'modal' && (
        <FilterBuilderModal
          open={!!filterTarget}
          onClose={() => setFilterTarget(null)}
          target={filterTarget}
          groups={filterGroups}
          setGroups={setFilterGroups}
        />
      )}

      {/* Location Modal (for modal mode) */}
      {viewMode === 'modal' && (
        <LocationModal
          open={!!locationTarget}
          onClose={() => setLocationTarget(null)}
          target={locationTarget}
          settings={locationSettings}
          setSettings={setLocationSettings}
        />
      )}

      {/* Instructions */}
      <details className="mt-8 p-4 bg-gray-50 rounded-lg">
        <summary className="font-medium cursor-pointer">Test Instructions by Mode</summary>
        <pre className="mt-2 text-sm text-gray-600 whitespace-pre-wrap">
COLLAPSIBLE (current production):
  • Each URL has inline collapsible for Filters + Location
  • Multiple can be open simultaneously → easy comparison
  • But: discoverability low, vertical growth unbounded

SIDE PANEL (proposed):
  • Click ⋯ → "Edit filters" → opens right panel
  • Click another URL's ⋯ → panel updates to that URL
  • Pin button keeps panel while scrolling list
  • Fixed width, no vertical growth, easy comparison

MODAL (prototype):
  • Click ⋯ → modal opens, blocks list interaction
  • Only one at a time → cannot compare across URLs
  • But: focused, full-screen on mobile, familiar pattern

TEST SCENARIOS:
  1. Open filters for Lego Sets, then Cameras, then Keyboards
  2. Try to compare filter rules across 2-3 URLs
  3. Edit a rule, switch URL, see if state persists correctly
  4. Test mobile: resize window &lt; 768px
  5. Keyboard: Tab through all actions, Escape closes
        </pre>
      </details>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────
// URL List Component (adapts to view mode)
// ─────────────────────────────────────────────────────────────

interface UrlListProps {
  urls: typeof mockUrls
  onDelete: (url: typeof mockUrls[0]) => void
  onOpenFilters: (url: typeof mockUrls[0]) => void
  onOpenLocation: (url: typeof mockUrls[0]) => void
  viewMode: ViewMode
  panelUrlId?: number | null
  setPanelUrlId?: (id: number | null) => void
  setPanelType?: (type: 'filters' | 'location' | null) => void
}

function UrlList({ 
  urls, 
  onDelete, 
  onOpenFilters, 
  onOpenLocation, 
  viewMode,
  panelUrlId,
  setPanelUrlId,
  setPanelType,
}: UrlListProps) {
  return (
    <div className="space-y-3">
      {urls.map((url) => (
        <UrlRow
          key={url.id}
          url={url}
          isActivePanel={viewMode === 'side-panel' && panelUrlId === url.id}
          onDelete={onDelete}
          onOpenFilters={onOpenFilters}
          onOpenLocation={onOpenLocation}
          viewMode={viewMode}
          setPanelUrlId={setPanelUrlId}
          setPanelType={setPanelType}
        />
      ))}
      {urls.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg font-medium">No URLs added yet</p>
          <p className="text-sm">Click "Add URL" to start monitoring</p>
        </div>
      )}
    </div>
  )
}

interface UrlRowProps {
  url: typeof mockUrls[0]
  isActivePanel: boolean
  onDelete: (url: typeof mockUrls[0]) => void
  onOpenFilters: (url: typeof mockUrls[0]) => void
  onOpenLocation: (url: typeof mockUrls[0]) => void
  viewMode: ViewMode
  setPanelUrlId?: (id: number | null) => void
  setPanelType?: (type: 'filters' | 'location' | null) => void
}

function UrlRow({ 
  url, 
  isActivePanel, 
  onDelete, 
  onOpenFilters, 
  onOpenLocation, 
  viewMode,
  setPanelUrlId,
  setPanelType,
}: UrlRowProps) {
  const handleOpenFilters = () => {
    if (viewMode === 'side-panel') {
      setPanelUrlId?.(url.id)
      setPanelType?.('filters')
    } else {
      onOpenFilters(url)
    }
  }
  const handleOpenLocation = () => {
    if (viewMode === 'side-panel') {
      setPanelUrlId?.(url.id)
      setPanelType?.('location')
    } else {
      onOpenLocation(url)
    }
  }

  return (
    <div 
      className={`p-4 bg-white border border-gray-200 rounded-lg transition-colors ${
        isActivePanel ? 'border-violet-300 shadow-lg' : 'hover:border-violet-300'
      }`}
    >
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <h3 className="font-medium text-gray-900 truncate">{url.name}</h3>
            <Badge className={`border-0 ${url.isActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}`}>
              {url.isActive ? 'Active' : 'Paused'}
            </Badge>
            {url.filterCount > 0 && (
              <Badge className="bg-violet-100 text-violet-800 border-0">{url.filterCount} filters</Badge>
            )}
          </div>
          <a href={url.url} target="_blank" rel="noopener noreferrer" className="text-sm text-gray-600 hover:text-violet-600 break-all">
            {url.url}
          </a>
        </div>
        
        <div className="flex items-center gap-2 flex-wrap">
          <Button
            variant="ghost" size="icon"
            onClick={() => alert(`${url.isActive ? 'Pause' : 'Resume'}: ${url.name}`)}
            aria-label={url.isActive ? `Pause ${url.name}` : `Resume ${url.name}`}
            className="h-9 w-9"
          >
            {url.isActive ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </Button>
          
          <Button
            variant="ghost" size="icon"
            onClick={() => onDelete(url)}
            aria-label={`Delete ${url.name}`}
            className="h-9 w-9 text-red-600 hover:bg-red-50 hover:text-red-700"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" aria-label={`More actions for ${url.name}`}>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" sideOffset={4}>
              <DropdownMenuItem onSelect={handleOpenFilters} className="flex items-center gap-2">
                <Filter className="h-4 w-4" />
                Edit filters
              </DropdownMenuItem>
              <DropdownMenuItem onSelect={handleOpenLocation} className="flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                Location settings
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
      
      {/* Collapsible inline editors (only in collapsible mode) */}
      {viewMode === 'collapsible' && (
        <CollapsibleEditors url={url} />
      )}
    </div>
  )
}

// ─────────────────────────────────────────────────────────────
// Collapsible Editors (Current Production Pattern)
// ─────────────────────────────────────────────────────────────

function CollapsibleEditors({ url }: { url: typeof mockUrls[0] }) {
  const [showFilters, setShowFilters] = useState(false)
  const [showLocation, setShowLocation] = useState(false)
  
  return (
    <div className="mt-4 pt-4 border-t border-gray-100 space-y-4">
      {/* Filters Collapsible */}
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="w-full px-4 py-2 flex items-center justify-between bg-gray-50 hover:bg-gray-100 text-left"
        >
          <span className="flex items-center gap-2 text-sm font-medium text-gray-700">
            <Filter className="h-4 w-4" /> Filters
          </span>
          <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
        </button>
        {showFilters && (
          <div className="p-4 space-y-3 border-t border-gray-100 bg-white">
            <p className="text-sm text-gray-500">Filter builder would go here (inline)</p>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">Add rule</Button>
              <Button variant="outline" size="sm">Add group</Button>
            </div>
          </div>
        )}
      </div>
      
      {/* Location Collapsible */}
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        <button
          onClick={() => setShowLocation(!showLocation)}
          className="w-full px-4 py-2 flex items-center justify-between bg-gray-50 hover:bg-gray-100 text-left"
        >
          <span className="flex items-center gap-2 text-sm font-medium text-gray-700">
            <MapPin className="h-4 w-4" /> Location
          </span>
          <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform ${showLocation ? 'rotate-180' : ''}`} />
        </button>
        {showLocation && (
          <div className="p-4 space-y-3 border-t border-gray-100 bg-white">
            <p className="text-sm text-gray-500">Location settings would go here (inline)</p>
            <Button variant="outline" size="sm">Add waypoint</Button>
          </div>
        )}
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────
// Side Panel Component
// ─────────────────────────────────────────────────────────────

interface SidePanelProps {
  url: typeof mockUrls[0] | null
  type: 'filters' | 'location' | null
  filterGroups: typeof mockFilters.ruleGroups
  setFilterGroups: React.Dispatch<React.SetStateAction<typeof mockFilters.ruleGroups>>
  locationSettings: typeof mockLocation
  setLocationSettings: React.Dispatch<React.SetStateAction<typeof mockLocation>>
  onClose: () => void
  onPin: (pinned: boolean) => void
  pinned: boolean
}

function SidePanel({ 
  url, 
  type, 
  filterGroups, 
  setFilterGroups, 
  locationSettings, 
  setLocationSettings,
  onClose,
  onPin,
  pinned,
}: SidePanelProps) {
  if (!url || !type) return null

  return (
    <div className="fixed right-0 top-16 bottom-0 w-96 bg-white border-l border-gray-200 shadow-xl z-40 flex flex-col"
         style={{ transform: 'translateX(0)' }}>
      {/* Header */}
      <div className="p-4 border-b border-gray-100 flex items-center justify-between bg-gray-50 sticky top-0">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close panel">
            <X className="h-5 w-5" />
          </Button>
          <div>
            <p className="font-medium text-gray-900 truncate">{url.name}</p>
            <p className="text-xs text-gray-500 capitalize">{type === 'filters' ? 'Filters' : 'Location'}</p>
          </div>
        </div>
        <Button 
          variant={pinned ? 'default' : 'outline'} 
          size="sm" 
          onClick={() => onPin(!pinned)}
          className="gap-1"
        >
          <svg className="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            {pinned ? (
              <>
                <path d="M12 17v5"/><path d="M9 17v5"/><path d="M15 17v5"/>
                <path d="M9 7h6a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2z"/>
              </>
            ) : (
              <>
                <path d="M12 17v5"/><path d="M9 17v5"/><path d="M15 17v5"/>
                <rect x="9" y="7" width="6" height="10" rx="2"/>
              </>
            )}
          </svg>
          {pinned ? 'Pinned' : 'Pin'}
        </Button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {type === 'filters' && (
          <FilterBuilderPanel
            groups={filterGroups}
            setGroups={setFilterGroups}
            onSave={() => alert(`Saved ${filterGroups.reduce((a,g)=>a+g.rules.length,0)} rules for ${url?.name}`)}
          />
        )}
        {type === 'location' && (
          <LocationPanel
            settings={locationSettings}
            setSettings={setLocationSettings}
            onSave={() => alert(`Saved location settings for ${url?.name}`)}
          />
        )}
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────
// Filter Builder Panel (for Side Panel)
// ─────────────────────────────────────────────────────────────

interface FilterBuilderPanelProps {
  groups: typeof mockFilters.ruleGroups
  setGroups: React.Dispatch<React.SetStateAction<typeof mockFilters.ruleGroups>>
  onSave: () => void
}

function FilterBuilderPanel({ groups, setGroups, onSave }: FilterBuilderPanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-medium text-gray-900">Filter Rules</h3>
        <span className="text-xs text-gray-500">
          {groups.reduce((a, g) => a + g.rules.length, 0)} rules in {groups.length} group{groups.length !== 1 ? 's' : ''}
        </span>
      </div>
      
      {groups.map((group, gIdx) => (
        <div key={gIdx} className="p-3 bg-gray-50 border border-gray-200 rounded-lg space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Group {gIdx + 1} <span className="text-gray-500">(AND)</span></span>
            {groups.length > 1 && (
              <Button variant="ghost" size="icon" onClick={() => setGroups(groups.filter((_, i) => i !== gIdx))} className="text-red-600">
                <X className="h-3.5 w-3.5" />
              </Button>
            )}
          </div>
          
          <div className="space-y-2">
            {group.rules.map((rule, rIdx) => (
              <div key={rIdx} className="flex flex-col sm:flex-row gap-2">
                <Select value={rule.field} onValueChange={(v) => updateRule(gIdx, rIdx, 'field', v, setGroups)}>
                  <SelectTrigger className="w-full sm:w-20">
                    <SelectValue placeholder="Field" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="title">Title</SelectItem>
                  </SelectContent>
                </Select>
                
                <Select value={rule.operator} onValueChange={(v) => updateRule(gIdx, rIdx, 'operator', v, setGroups)}>
                  <SelectTrigger className="w-full sm:w-28">
                    <SelectValue placeholder="Op" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="contains">Contains</SelectItem>
                    <SelectItem value="not_contains">Not contains</SelectItem>
                  </SelectContent>
                </Select>
                
                <Input
                  value={rule.value}
                  placeholder="Value..."
                  onChange={(e) => updateRule(gIdx, rIdx, 'value', e.target.value, setGroups)}
                  className="flex-1 min-w-0"
                />
                
                {group.rules.length > 1 && (
                  <Button variant="ghost" size="icon" onClick={() => removeRule(gIdx, rIdx, setGroups)} className="text-gray-400 hover:text-red-600">
                    <X className="h-3.5 w-3.5" />
                  </Button>
                )}
              </div>
            ))}
            <Button variant="outline" size="sm" onClick={() => addRule(gIdx, setGroups)} className="w-full sm:w-auto">
              <Plus className="h-3.5 w-3.5 mr-1" /> Add rule
            </Button>
          </div>
        </div>
      ))}
      
      <Button variant="outline" onClick={() => addGroup(setGroups)} className="w-full border-dashed">
        <Plus className="h-3.5 w-3.5 mr-1" /> Add group (OR)
      </Button>
      
      <div className="pt-4 border-t border-gray-100 flex justify-end gap-2">
        <Button variant="outline" onClick={() => {}}>Cancel</Button>
        <Button onClick={onSave}><Save className="h-3.5 w-3.5 mr-1" /> Save</Button>
      </div>
    </div>
  )
}

function updateRule(gIdx: number, rIdx: number, field: string, value: any, setGroups: React.Dispatch<React.SetStateAction<typeof mockFilters.ruleGroups>>) {
  setGroups(prev => prev.map((g, i) => 
    i !== gIdx ? g : { ...g, rules: g.rules.map((r, j) => j !== rIdx ? r : { ...r, [field]: value }) }
  ))
}

function addRule(gIdx: number, setGroups: React.Dispatch<React.SetStateAction<typeof mockFilters.ruleGroups>>) {
  setGroups(prev => prev.map((g, i) => 
    i !== gIdx ? g : { ...g, rules: [...g.rules, { field: 'title', operator: 'contains', value: '', caseSensitive: false }] }
  ))
}

function removeRule(gIdx: number, rIdx: number, setGroups: React.Dispatch<React.SetStateAction<typeof mockFilters.ruleGroups>>) {
  setGroups(prev => prev.map((g, i) => 
    i !== gIdx ? g : { ...g, rules: g.rules.filter((_, j) => j !== rIdx) }
  ))
}

function addGroup(setGroups: React.Dispatch<React.SetStateAction<typeof mockFilters.ruleGroups>>) {
  setGroups(prev => [...prev, { logic: 'and', rules: [{ field: 'title', operator: 'contains', value: '', caseSensitive: false }] }])
}

// ─────────────────────────────────────────────────────────────
// Location Panel (for Side Panel)
// ─────────────────────────────────────────────────────────────

interface LocationPanelProps {
  settings: typeof mockLocation
  setSettings: React.Dispatch<React.SetStateAction<typeof mockLocation>>
  onSave: () => void
}

function LocationPanel({ settings, setSettings, onSave }: LocationPanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
        <div className="flex flex-col gap-0.5">
          <Label className="font-medium">Include location in notifications</Label>
          <span className="text-xs text-gray-500">Adds Google Maps link and distance to each offer alert</span>
        </div>
        <Switch
          checked={settings.showLocationMap}
          onCheckedChange={(v) => setSettings({...settings, showLocationMap: v})}
        />
      </div>
      
      {settings.showLocationMap && (
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-gray-700">Reference points (for distance)</h4>
          {settings.waypoints.map((wp, idx) => (
            <div key={idx} className="p-3 bg-gray-50 border border-gray-200 rounded-lg space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Waypoint {idx + 1}</span>
                <Button variant="ghost" size="icon" onClick={() => removeWaypoint(idx, setSettings)} className="text-gray-400 hover:text-red-600">
                  <X className="h-3.5 w-3.5" />
                </Button>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <Label className="text-xs text-gray-500">Name</Label>
                  <Input value={wp.name} placeholder="Warsaw Center" onChange={(e) => updateWaypoint(idx, 'name', e.target.value, setSettings)} />
                </div>
                <div>
                  <Label className="text-xs text-gray-500">Lat</Label>
                  <Input type="number" step="any" value={wp.lat} onChange={(e) => updateWaypoint(idx, 'lat', parseFloat(e.target.value), setSettings)} />
                </div>
                <div>
                  <Label className="text-xs text-gray-500">Lon</Label>
                  <Input type="number" step="any" value={wp.lon} onChange={(e) => updateWaypoint(idx, 'lon', parseFloat(e.target.value), setSettings)} />
                </div>
              </div>
              <Button variant="outline" size="sm" onClick={() => pasteFromMaps(idx)}>
                <MapPinIcon className="h-3.5 w-3.5 mr-1" /> Paste from Google Maps
              </Button>
            </div>
          ))}
          <Button variant="outline" size="sm" onClick={() => addWaypoint(setSettings)} className="w-full border-dashed">
            <Plus className="h-3.5 w-3.5 mr-1" /> Add waypoint
          </Button>
        </div>
      )}
      
      <div className="pt-4 border-t border-gray-100 flex justify-end gap-2">
        <Button variant="outline" onClick={() => {}}>Cancel</Button>
        <Button onClick={onSave}><Save className="h-3.5 w-3.5 mr-1" /> Save</Button>
      </div>
    </div>
  )
}

function updateWaypoint(idx: number, field: string, value: any, setSettings: React.Dispatch<React.SetStateAction<typeof mockLocation>>) {
  setSettings(prev => ({ ...prev, waypoints: prev.waypoints.map((w, i) => i !== idx ? w : { ...w, [field]: value }) }))
}

function addWaypoint(setSettings: React.Dispatch<React.SetStateAction<typeof mockLocation>>) {
  setSettings(prev => ({ ...prev, waypoints: [...prev.waypoints, { name: '', lat: 0, lon: 0 }] }))
}

function removeWaypoint(idx: number, setSettings: React.Dispatch<React.SetStateAction<typeof mockLocation>>) {
  setSettings(prev => ({ ...prev, waypoints: prev.waypoints.filter((_, i) => i !== idx) }))
}

function pasteFromMaps(idx: number) {
  console.log('Paste from Google Maps for waypoint', idx)
}

// ─────────────────────────────────────────────────────────────
// Filter Builder Modal (for Modal Mode)
// ─────────────────────────────────────────────────────────────

interface FilterBuilderModalProps {
  open: boolean
  onClose: () => void
  target: typeof mockUrls[0] | null
  groups: typeof mockFilters.ruleGroups
  setGroups: React.Dispatch<React.SetStateAction<typeof mockFilters.ruleGroups>>
}

function FilterBuilderModal({ open, onClose, target, groups, setGroups }: FilterBuilderModalProps) {
  if (!open || !target) return null
  
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Edit Filters — {target.name}</DialogTitle>
          <DialogDescription>
            Configure rules to match offers. All rules in a group must match (AND). 
            Add multiple groups for OR logic.
          </DialogDescription>
        </DialogHeader>
        <FilterBuilderPanel groups={groups} setGroups={setGroups} onSave={onClose} />
      </DialogContent>
    </Dialog>
  )
}

// ─────────────────────────────────────────────────────────────
// Location Modal (for Modal Mode)
// ─────────────────────────────────────────────────────────────

interface LocationModalProps {
  open: boolean
  onClose: () => void
  target: typeof mockUrls[0] | null
  settings: typeof mockLocation
  setSettings: React.Dispatch<React.SetStateAction<typeof mockLocation>>
}

function LocationModal({ open, onClose, target, settings, setSettings }: LocationModalProps) {
  if (!open || !target) return null
  
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Location Settings — {target.name}</DialogTitle>
          <DialogDescription>
            Add location to notifications. Get Google Maps links and distance from your waypoints.
          </DialogDescription>
        </DialogHeader>
        <LocationPanel settings={settings} setSettings={setSettings} onSave={onClose} />
      </DialogContent>
    </Dialog>
  )
}