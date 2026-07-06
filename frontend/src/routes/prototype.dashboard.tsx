import { createFileRoute, useSearch, useNavigate } from '@tanstack/react-router'
import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from '@/components/ui/dropdown-menu'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import cn from '@/lib/utils'
import {
  MoreHorizontal, Pause, Play, Filter, MapPin, Trash2, Plus, X, ChevronLeft, ChevronRight,
  Bell, AlertCircle, Globe, ExternalLink, Eye, EyeOff, Target, Wifi, WifiOff,
  Clock, LayoutDashboard, Columns, LayoutList, Pin, PinOff,
  Mail, MessageCircle,
} from 'lucide-react'

// ── Mock Data ─────────────────────────────────────────────

const mockUrlRecords = [
  { id: 1, name: 'Rare Lego Sets', url: 'https://olx.pl/lego/star-wars/q-lego-star-wars/', isActive: true, filterCount: 3, lastChecked: '2 min ago', offersToday: 2, showLocationMap: true, waypoints: [{ name: 'Warsaw Center', lat: 52.2297, lon: 21.0122 }] },
  { id: 2, name: 'Vintage Cameras', url: 'https://olx.pl/foto/kamery-analogowe/', isActive: true, filterCount: 0, lastChecked: '5 min ago', offersToday: 0, showLocationMap: false, waypoints: [] },
  { id: 3, name: 'Mechanical Keyboards', url: 'https://olx.pl/komputery/klasyczne-mechaniczne/', isActive: false, filterCount: 2, lastChecked: '1 hour ago', offersToday: 0, showLocationMap: true, waypoints: [{ name: 'Krakow Old Town', lat: 50.0614, lon: 19.9366 }] },
  { id: 4, name: 'Mid-Century Furniture', url: 'https://olx.pl/meblo-antyk/', isActive: true, filterCount: 1, lastChecked: '15 min ago', offersToday: 5, showLocationMap: false, waypoints: [] },
  { id: 5, name: 'Used Books', url: 'https://vinted.pl/ksiazki/', isActive: false, filterCount: 0, lastChecked: '2 days ago', offersToday: 0, showLocationMap: false, waypoints: [] },
]

const mockTargets = [
  { id: 1, name: 'Home Monitor', channelId: 'tg-personal', urls: mockUrlRecords },
  { id: 2, name: 'Work Monitor', channelId: 'email-gmail', urls: [] },
]

const mockFilterGroups: RuleGroup[] = [
  { logic: 'and', rules: [
    { field: 'title', operator: 'contains', value: 'lego', caseSensitive: false },
    { field: 'title', operator: 'not_contains', value: 'damaged', caseSensitive: false },
    { field: 'title', operator: 'contains', value: 'star wars', caseSensitive: false },
  ]},
  { logic: 'and', rules: [
    { field: 'price', operator: 'less_than', value: '500', caseSensitive: false },
    { field: 'title', operator: 'contains', value: 'collection', caseSensitive: false },
  ]},
]

const mockQuota = { used: 67, limit: 100, periodEnd: 'Aug 1, 2026' }
const mockUrlQuota = { used: 4, limit: 10 }

// ── Types ─────────────────────────────────────────────────

type ViewVariant = 'A' | 'B' | 'C'

interface Channel {
  id: string
  name: string
  provider: string
  connected: boolean
}

const mockChannels: Channel[] = [
  { id: 'tg-personal', name: 'Telegram - Personal', provider: 'telegram', connected: true },
  { id: 'tg-work', name: 'Telegram - Work', provider: 'telegram', connected: true },
  { id: 'email-gmail', name: 'Email - Gmail', provider: 'email', connected: true },
  { id: 'discord-alerts', name: 'Discord - Server Alerts', provider: 'discord', connected: false },
]

const providerIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  telegram: Bell,
  email: Mail,
  discord: MessageCircle,
}

interface UrlRecord {
  id: number; name: string; url: string; isActive: boolean; filterCount: number;
  lastChecked: string; offersToday: number; showLocationMap: boolean;
  waypoints: Array<{ name: string; lat: number; lon: number }>;
}

interface Rule { field: string; operator: string; value: string; caseSensitive: boolean }
interface RuleGroup { logic: 'and'; rules: Rule[] }

// ── Route ──────────────────────────────────────────────────

export const Route = createFileRoute('/prototype/dashboard')({
  validateSearch: (search: Record<string, unknown>) => ({
    variant: (search.variant as ViewVariant) || 'A',
  }),
  component: PrototypeDashboard,
})

// ── Main ──────────────────────────────────────────────────

function PrototypeDashboard() {
  const { variant } = useSearch({ from: Route.id })
  const navigate = useNavigate()

  const setVariant = (v: ViewVariant) => {
    navigate({ to: '/prototype/dashboard', search: { variant: v }, replace: true })
  }

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement || (e.target as HTMLElement)?.isContentEditable) return
      if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
        const variants: ViewVariant[] = ['A', 'B', 'C']
        const ci = variants.indexOf(variant || 'A')
        const delta = e.key === 'ArrowLeft' ? -1 : 1
        setVariant(variants[(ci + delta + 3) % 3])
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [variant, navigate])

  return (
    <div className="min-h-screen bg-background">
      {variant === 'A' && <VariantA target={mockTargets[0]} />}
      {variant === 'B' && <VariantB target={mockTargets[0]} />}
      {variant === 'C' && <VariantC target={mockTargets[0]} />}
      <PrototypeSwitcher current={variant} setVariant={setVariant} />
    </div>
  )
}

// ── Variant A: Three-Panel Split ──────────────────────────

function VariantA({ target }: { target: typeof mockTargets[0] }) {
  const [selectedTargetId, setSelectedTargetId] = useState(target.id)
  const [targetChannels, setTargetChannels] = useState<Record<number, string>>({
    1: mockTargets[0].channelId,
    2: mockTargets[1].channelId,
  })
  const currentTarget = mockTargets.find(t => t.id === selectedTargetId)!
  const currentChannelId = targetChannels[selectedTargetId]

  const [panelUrlId, setPanelUrlId] = useState<number | null>(null)
  const [activeTab, setActiveTab] = useState<'filters' | 'location'>('filters')
  const [isPinned, setIsPinned] = useState(false)
  const [leftCollapsed, setLeftCollapsed] = useState(false)
  const [showAddForm, setShowAddForm] = useState(false)
  const [showWelcome, setShowWelcome] = useState(target.urls.length === 0)
  const [deleteTargetId, setDeleteTargetId] = useState<number | null>(null)

  const panelUrl = panelUrlId ? currentTarget.urls.find(u => u.id === panelUrlId) : null

  const openPanel = (urlId: number, tab: 'filters' | 'location') => {
    if (panelUrlId === urlId) {
      setPanelUrlId(null); return
    }
    setPanelUrlId(urlId); setActiveTab(tab)
  }

  const closePanel = () => { if (!isPinned) setPanelUrlId(null) }

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Left Panel */}
      <div className={cn(
        'border-r border-border bg-card flex flex-col shrink-0 transition-all duration-200',
        leftCollapsed ? 'w-14' : 'w-[280px]'
      )}>
        <div className={cn('flex items-center border-b border-border h-14', leftCollapsed ? 'justify-center' : 'justify-between px-4')}>
          {!leftCollapsed && (
            <div className="flex items-center gap-2">
              <Target className="w-5 h-5 text-primary" aria-hidden="true" />
              <span className="font-semibold text-sm text-foreground">Shargain</span>
            </div>
          )}
          <Button variant="ghost" size="icon" onClick={() => setLeftCollapsed(!leftCollapsed)} className="h-8 w-8" aria-label="Toggle sidebar">
            <ChevronLeft className={cn('w-4 h-4 transition-transform', leftCollapsed && 'rotate-180')} aria-hidden="true" />
          </Button>
        </div>

        {!leftCollapsed ? (
          <div className="flex-1 overflow-y-auto p-4 space-y-5">
            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground uppercase tracking-wider" htmlFor="varianta-target-select">Target</Label>
              <Select value={String(selectedTargetId)} onValueChange={(v) => setSelectedTargetId(Number(v))}>
                <SelectTrigger id="varianta-target-select"><SelectValue placeholder="Select target" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">Home Monitor</SelectItem>
                  <SelectItem value="2">Work Monitor</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground uppercase tracking-wider">Quota</Label>
              <div className="space-y-2">
                <div className="flex items-center justify-between p-2 bg-secondary/50 rounded-md text-sm">
                  <span className="text-muted-foreground">Notifications</span>
                  <Badge className={cn(
                    mockQuota.used >= mockQuota.limit ? 'bg-destructive text-destructive-foreground' :
                    mockQuota.used / mockQuota.limit >= 0.8 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  )}>{mockQuota.used}/{mockQuota.limit}</Badge>
                </div>
                <div className="flex items-center justify-between p-2 bg-secondary/50 rounded-md text-sm">
                  <span className="text-muted-foreground">URLs</span>
                  <Badge className={cn(
                    mockUrlQuota.used >= mockUrlQuota.limit ? 'bg-destructive text-destructive-foreground' :
                    mockUrlQuota.used / mockUrlQuota.limit >= 0.8 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  )}>{mockUrlQuota.used}/{mockUrlQuota.limit}</Badge>
                </div>
              </div>
              {mockQuota.used / mockQuota.limit >= 0.8 && (
                <p className="text-xs text-amber-700 flex items-center gap-1"><AlertCircle className="w-3 h-3" aria-hidden="true" /> Resets {mockQuota.periodEnd}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground uppercase tracking-wider" htmlFor="varianta-channel-select">Notification Channel</Label>
              <Select value={currentChannelId} onValueChange={(v) => setTargetChannels(prev => ({ ...prev, [selectedTargetId]: v }))}>
                <SelectTrigger id="varianta-channel-select" className="h-9 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {mockChannels.map(ch => {
                    const Icon = providerIcons[ch.provider] || Bell
                    return (
                      <SelectItem key={ch.id} value={ch.id} className="text-xs">
                      <span className="flex items-center gap-2">
                        <Icon className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
                        <span className="flex-1 min-w-0 truncate">{ch.name}</span>
                        <Badge className={cn(
                          'border-0 text-xs px-1 py-0 shrink-0',
                          ch.connected ? 'bg-green-100 text-green-800' : 'bg-muted text-muted-foreground'
                        )}>
                          {ch.connected ? '✓' : '✗'}
                        </Badge>
                      </span>
                      </SelectItem>
                    )
                  })}
                </SelectContent>
              </Select>
              <Button variant="outline" size="sm" className="w-full text-xs justify-start">
                <Bell className="w-3.5 h-3.5 mr-2" aria-hidden="true" /> Test notification
              </Button>
            </div>

            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground uppercase tracking-wider">Settings</Label>
              <div className="flex items-center justify-between py-1">
                <span className="text-sm text-muted-foreground">Monitor active</span>
                <Switch defaultChecked aria-label="Monitor active" />
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center gap-5 py-5">
            <Button variant="ghost" size="icon" className="h-9 w-9 text-muted-foreground" title="Target" aria-label="Target"><Target className="w-4 h-4" aria-hidden="true" /></Button>
            <Button variant="ghost" size="icon" className="h-9 w-9 text-muted-foreground relative" title="Quota" aria-label="Quota">
              <Bell className="w-4 h-4" aria-hidden="true" />
              <span className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-yellow-400 rounded-full" />
            </Button>
            <Button variant="ghost" size="icon" className="h-9 w-9 text-muted-foreground" title="Channel" aria-label="Channel"><Bell className="w-4 h-4" aria-hidden="true" /></Button>
          </div>
        )}
      </div>

      {/* Middle Panel */}
      <div className="flex-1 flex flex-col min-w-0">
        <div className="border-b border-border bg-secondary/20 px-4 sm:px-6 py-3 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-4">
            <div>
              <h1 className="text-base font-semibold text-foreground">{currentTarget.name}</h1>
              <div className="flex items-center gap-2 mt-0.5">
                <div className="w-1.5 h-1.5 rounded-full bg-green-500" />
                <span className="text-xs text-muted-foreground">Active</span>
              </div>
            </div>
            <div className="hidden sm:flex items-center gap-2.5 text-xs text-muted-foreground">
              <div className="h-1.5 w-16 bg-secondary rounded-full overflow-hidden">
                <div className={cn('h-full rounded-full', mockQuota.used / mockQuota.limit >= 0.8 ? 'bg-yellow-400' : 'bg-primary')}
                  style={{ width: `${(mockQuota.used / mockQuota.limit) * 100}%` }} />
              </div>
              <span>{mockQuota.used}/{mockQuota.limit}</span>
            </div>
          </div>
          <Button size="sm" className="h-8 px-3 text-xs" onClick={() => setShowAddForm(true)}>
            <Plus className="w-3.5 h-3.5 mr-1" aria-hidden="true" /> Add URL
          </Button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-3">
          {/* Empty state */}
          {currentTarget.urls.length === 0 && showWelcome && (
            <div className="flex flex-col items-center justify-center h-full text-center max-w-sm mx-auto">
              <div className="w-16 h-16 bg-secondary rounded-full flex items-center justify-center mb-4">
                <Globe className="w-8 h-8 text-muted-foreground" aria-hidden="true" />
              </div>
              <h2 className="text-lg font-semibold text-foreground mb-1">Start monitoring</h2>
              <p className="text-sm text-muted-foreground mb-4">Add your first URL to start tracking offers from OLX, Vinted, Otomoto, and Otodom.</p>
              <Button onClick={() => { setShowWelcome(false); setShowAddForm(true) }}>
                <Plus className="w-4 h-4 mr-1" aria-hidden="true" /> Add your first URL
              </Button>
            </div>
          )}

          {/* Add URL form */}
          {showAddForm && (
            <div className="p-4 bg-card border border-border rounded-xl space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium text-foreground">Add URL to monitor</h3>
                <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setShowAddForm(false)}>
                  <X className="w-4 h-4" aria-hidden="true" />
                </Button>
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="space-y-1">
                  <Label className="text-xs">URL</Label>
                  <Input placeholder="https://olx.pl/..." />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Name</Label>
                  <Input placeholder="My monitor" />
                </div>
              </div>
              <Button size="sm"><Plus className="w-4 h-4 mr-1" aria-hidden="true" /> Add URL</Button>
            </div>
          )}

          {/* URL rows */}
          {currentTarget.urls.map((url) => (
            <UrlRowA
              key={url.id}
              url={url}
              isActive={panelUrlId === url.id}
              onSelect={() => openPanel(url.id, 'filters')}
              onOpenLocation={() => openPanel(url.id, 'location')}
              onDelete={() => setDeleteTargetId(url.id)}
            />
          ))}
        </div>
      </div>

      {/* Right Panel */}
      {panelUrl && (
        <>
          <div className="fixed inset-0 bg-black/20 z-30 lg:hidden" onClick={closePanel} />
          <div className={cn(
            'border-l border-border bg-card flex flex-col',
            'fixed right-0 top-0 bottom-0 w-full max-w-[85vw] sm:w-[448px] z-40 shadow-xl',
            'lg:static lg:shadow-none lg:shrink-0'
          )}>
            {/* Header with close + tabs */}
            <div className="px-3 pt-2 pb-0 border-b border-border shrink-0 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 min-w-0">
                  <Button variant="ghost" size="icon" className="h-7 w-7 shrink-0" onClick={closePanel} aria-label="Close panel">
                    <X className="w-4 h-4" aria-hidden="true" />
                  </Button>
                  <p className="text-sm font-medium text-foreground truncate">{panelUrl.name}</p>
                  <span className="hidden sm:inline text-xs text-muted-foreground">
                    {activeTab === 'filters' ? `${mockFilterGroups.reduce((a, g) => a + g.rules.length, 0)} rules` : `${panelUrl.waypoints.length} waypoints`}
                  </span>
                </div>
                <Button variant="ghost" size="sm" onClick={() => setIsPinned(!isPinned)} className="gap-1 text-xs shrink-0">
                  {isPinned ? <PinOff className="w-3 h-3" aria-hidden="true" /> : <Pin className="w-3 h-3" aria-hidden="true" />}
                  {isPinned ? 'Unpin' : 'Pin'}
                </Button>
              </div>
              <div className="flex gap-1 pb-2">
                <button
                  role="tab"
                  aria-selected={activeTab === 'filters'}
                  onClick={() => setActiveTab('filters')}
                  className={cn(
                    'px-3 py-1.5 text-xs font-medium rounded-md transition-colors',
                    activeTab === 'filters' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-secondary'
                  )}
                >
                  <Filter className="w-3.5 h-3.5 inline mr-1.5" aria-hidden="true" />Filters
                </button>
                <button
                  role="tab"
                  aria-selected={activeTab === 'location'}
                  onClick={() => setActiveTab('location')}
                  className={cn(
                    'px-3 py-1.5 text-xs font-medium rounded-md transition-colors',
                    activeTab === 'location' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-secondary'
                  )}
                >
                  <MapPin className="w-3.5 h-3.5 inline mr-1.5" aria-hidden="true" />Location
                </button>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto p-3">
              {activeTab === 'filters' && <FilterEditor />}
              {activeTab === 'location' && <LocationEditor />}
            </div>
          </div>
        </>
      )}

      <Dialog open={deleteTargetId !== null} onOpenChange={(o) => !o && setDeleteTargetId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete URL?</DialogTitle>
            <DialogDescription>This will permanently remove this URL and its settings. Monitoring will stop immediately.</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteTargetId(null)}>Cancel</Button>
            <Button variant="destructive">Delete</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

function UrlRowA({ url, isActive, onSelect, onOpenLocation, onDelete }: {
  url: UrlRecord; isActive: boolean; onSelect: () => void; onOpenLocation: () => void; onDelete: () => void
}) {
  return (
    <button type="button"
      onClick={onSelect}
      className={cn(
        'p-4 bg-card border rounded-xl transition-all text-left w-full',
        isActive ? 'border-primary shadow-md' : 'border-border hover:border-primary/40'
      )}
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <div className={cn('w-2 h-2 rounded-full', url.isActive ? 'bg-green-500' : 'bg-gray-300')} />
            <h3 className="font-medium text-sm text-foreground truncate">{url.name}</h3>
            <Badge className={cn('border-0 text-xs', url.isActive ? 'bg-green-100 text-green-800' : 'bg-muted text-muted-foreground')}>
              {url.isActive ? 'Active' : 'Paused'}
            </Badge>
          </div>
          <a href={url.url} target="_blank" rel="noopener noreferrer" className="text-xs text-muted-foreground hover:text-primary truncate block" onClick={e => e.stopPropagation()}>
            <ExternalLink className="w-3 h-3 inline mr-1" aria-hidden="true" />{url.url}
          </a>
          <div className="flex items-center gap-3 mt-1">
            <span className="text-xs text-muted-foreground flex items-center gap-1"><Clock className="w-3 h-3" aria-hidden="true" />{url.lastChecked}</span>
            {url.offersToday > 0 && <span className="text-xs text-green-600 font-medium">{url.offersToday} new</span>}
            {url.filterCount > 0 && <span className="text-xs text-primary/70">{url.filterCount} filter{url.filterCount > 1 ? 's' : ''}</span>}
          </div>
        </div>

        <div className="flex items-center gap-1" onClick={e => e.stopPropagation()}>
          <Button variant="ghost" size="icon" className="h-8 w-8" aria-label={url.isActive ? 'Pause' : 'Resume'}>
            {url.isActive ? <Pause className="w-3.5 h-3.5" aria-hidden="true" /> : <Play className="w-3.5 h-3.5" aria-hidden="true" />}
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8" aria-label="More">
                <MoreHorizontal className="w-3.5 h-3.5" aria-hidden="true" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onSelect={onSelect}><Filter className="w-3.5 h-3.5 mr-2" aria-hidden="true" /> Filters</DropdownMenuItem>
              <DropdownMenuItem onSelect={onOpenLocation}><MapPin className="w-3.5 h-3.5 mr-2" aria-hidden="true" /> Location</DropdownMenuItem>
              <DropdownMenuItem onSelect={onDelete} className="text-destructive"><Trash2 className="w-3.5 h-3.5 mr-2" aria-hidden="true" /> Delete</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </button>
  )
}

// ── Variant B: Sidebar Dashboard ──────────────────────────

function VariantB({ target }: { target: typeof mockTargets[0] }) {
  const [channelId, setChannelId] = useState(target.channelId)
  const [filterOpen, setFilterOpen] = useState<Record<number, boolean>>({})
  const [locationOpen, setLocationOpen] = useState<Record<number, boolean>>({})
  const [showAddUrl, setShowAddUrl] = useState(false)

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <div className="w-[260px] border-r border-border bg-card shrink-0 flex flex-col">
        <div className="p-4 border-b border-border">
          <h2 className="font-semibold text-foreground text-sm flex items-center gap-2">
            <Target className="w-4 h-4 text-primary" aria-hidden="true" /> {target.name}
          </h2>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-5">
          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground uppercase tracking-wider">Details</Label>
            <div className="p-3 bg-secondary/50 rounded-lg space-y-2 text-sm">
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Status</span>
                <Badge className="bg-green-100 text-green-800 border-0 text-xs"><Wifi className="w-3 h-3 mr-1" aria-hidden="true" />Active</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">URLs</span>
                <span className="font-medium">{target.urls.length}</span>
              </div>
            </div>
            <Label className="text-xs text-muted-foreground mt-3 block" htmlFor="variantb-channel-select">Notification Channel</Label>
            <Select value={channelId} onValueChange={setChannelId}>
              <SelectTrigger id="variantb-channel-select" className="h-8 text-xs w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {mockChannels.map(ch => {
                  const Icon = providerIcons[ch.provider] || Bell
                  return (
                    <SelectItem key={ch.id} value={ch.id} className="text-xs">
                      <span className="flex items-center gap-2">
                        <Icon className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
                        <span className="flex-1 min-w-0 truncate">{ch.name}</span>
                        <Badge className={cn(
                          'border-0 text-xs px-1 py-0 shrink-0',
                          ch.connected ? 'bg-green-100 text-green-800' : 'bg-muted text-muted-foreground'
                        )}>
                          {ch.connected ? '✓' : '✗'}
                        </Badge>
                      </span>
                    </SelectItem>
                  )
                })}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground uppercase tracking-wider">Quota</Label>
            <div className="space-y-2">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-muted-foreground">Notifications</span>
                  <span className={mockQuota.used >= mockQuota.limit ? 'text-destructive font-medium' : ''}>{mockQuota.used}/{mockQuota.limit}</span>
                </div>
                <div className="h-2 bg-secondary rounded-full overflow-hidden">
                  <div className={cn('h-full rounded-full', mockQuota.used >= mockQuota.limit ? 'bg-destructive' : mockQuota.used / mockQuota.limit >= 0.8 ? 'bg-warning' : 'bg-green-500')}
                    style={{ width: `${(mockQuota.used / mockQuota.limit) * 100}%` }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-muted-foreground">URLs</span>
                  <span>{mockUrlQuota.used}/{mockUrlQuota.limit}</span>
                </div>
                <div className="h-2 bg-secondary rounded-full overflow-hidden">
                  <div className={cn('h-full rounded-full', mockUrlQuota.used >= mockUrlQuota.limit ? 'bg-destructive' : 'bg-primary')}
                    style={{ width: `${(mockUrlQuota.used / mockUrlQuota.limit) * 100}%` }} />
                </div>
            </div>
          </div>
        </div>

        <div className="space-y-2">
            <Label className="text-xs text-muted-foreground uppercase tracking-wider">Actions</Label>
            <div className="space-y-2">
              <Button variant="outline" size="sm" className="w-full justify-start text-xs" onClick={() => setShowAddUrl(true)}>
                <Plus className="w-3.5 h-3.5 mr-2" aria-hidden="true" /> Add URL
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start text-xs">
                <Bell className="w-3.5 h-3.5 mr-2" aria-hidden="true" /> Test notification
              </Button>
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-border text-xs text-muted-foreground">
          Quota resets {mockQuota.periodEnd}
        </div>
      </div>

      {/* Main */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-semibold text-foreground">Monitored URLs</h1>
            <p className="text-sm text-muted-foreground">{target.urls.length} URL{target.urls.length !== 1 ? 's' : ''}</p>
          </div>
          <Button size="sm" onClick={() => setShowAddUrl(true)}><Plus className="w-4 h-4 mr-1" aria-hidden="true" /> Add URL</Button>
        </div>

        {target.urls.length === 0 && (
          <div className="text-center py-16 text-muted-foreground">
            <Globe className="w-12 h-12 mx-auto mb-3 opacity-40" aria-hidden="true" />
            <p className="font-medium">No URLs added yet</p>
            <p className="text-sm">Click "Add URL" to start monitoring.</p>
          </div>
        )}

        <div className="space-y-4">
          {target.urls.map((url) => (
            <UrlCardB
              key={url.id}
              url={url}
              filterOpen={filterOpen[url.id]}
              locationOpen={locationOpen[url.id]}
              onToggleFilter={() => setFilterOpen(p => ({ ...p, [url.id]: !p[url.id] }))}
              onToggleLocation={() => setLocationOpen(p => ({ ...p, [url.id]: !p[url.id] }))}
            />
          ))}
        </div>
      </div>

      <Dialog open={showAddUrl} onOpenChange={setShowAddUrl}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add URL</DialogTitle>
            <DialogDescription>Enter a URL from OLX, Vinted, Otomoto, or Otodom.</DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div className="space-y-1">
              <Label>URL</Label>
              <Input placeholder="https://olx.pl/..." />
            </div>
            <div className="space-y-1">
              <Label>Name (optional)</Label>
              <Input placeholder="My monitor" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAddUrl(false)}>Cancel</Button>
            <Button onClick={() => setShowAddUrl(false)}><Plus className="w-4 h-4 mr-1" aria-hidden="true" /> Add</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

function UrlCardB({ url, filterOpen, locationOpen, onToggleFilter, onToggleLocation }: {
  url: UrlRecord; filterOpen: boolean; locationOpen: boolean; onToggleFilter: () => void; onToggleLocation: () => void
}) {
  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden">
      <div className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-medium text-foreground text-sm">{url.name}</h3>
            <Badge className={cn('border-0 text-xs', url.isActive ? 'bg-green-100 text-green-800' : 'bg-muted text-muted-foreground')}>
              {url.isActive ? 'Active' : 'Paused'}
            </Badge>
          </div>
          <a href={url.url} target="_blank" className="text-xs text-muted-foreground hover:text-primary truncate block">
            <ExternalLink className="w-3 h-3 inline mr-1" aria-hidden="true" />{url.url}
          </a>
          <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
            <span><Clock className="w-3 h-3 inline mr-0.5" aria-hidden="true" />{url.lastChecked}</span>
            {url.offersToday > 0 && <span className="text-green-600 font-medium">{url.offersToday} new</span>}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" className="text-xs h-8" aria-label="Toggle active">
            {url.isActive ? <EyeOff className="w-3.5 h-3.5 mr-1" aria-hidden="true" /> : <Eye className="w-3.5 h-3.5 mr-1" aria-hidden="true" />}
            {url.isActive ? 'Pause' : 'Resume'}
          </Button>
          <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive" aria-label="Delete">
            <Trash2 className="w-3.5 h-3.5" aria-hidden="true" />
          </Button>
        </div>
      </div>

      <div className="border-t border-border">
        <div className="border-b border-border">
          <button onClick={onToggleFilter}
            className="w-full px-4 py-2.5 flex items-center justify-between text-sm hover:bg-secondary/30 transition-colors">
            <span className="flex items-center gap-2 text-muted-foreground">
              <Filter className="w-3.5 h-3.5" aria-hidden="true" /> Filters
              {url.filterCount > 0 && <Badge className="bg-secondary text-secondary-foreground border-0 text-xs">{url.filterCount}</Badge>}
            </span>
            <ChevronLeft className={cn('w-3.5 h-3.5 text-muted-foreground transition-transform', filterOpen && '-rotate-90')} aria-hidden="true" />
          </button>
          {filterOpen && (
            <div className="px-4 py-3 bg-secondary/20 border-t border-border">
              <FilterEditor />
            </div>
          )}
        </div>

        <div>
          <button onClick={onToggleLocation}
            className="w-full px-4 py-2.5 flex items-center justify-between text-sm hover:bg-secondary/30 transition-colors">
            <span className="flex items-center gap-2 text-muted-foreground">
              <MapPin className="w-3.5 h-3.5" aria-hidden="true" /> Location
                <Badge className={cn('border-0 text-xs', url.showLocationMap ? 'bg-green-100 text-green-800' : 'bg-muted text-muted-foreground')}>
                  {url.showLocationMap ? 'On' : 'Off'}
                </Badge>
            </span>
            <ChevronLeft className={cn('w-3.5 h-3.5 text-muted-foreground transition-transform', locationOpen && '-rotate-90')} aria-hidden="true" />
          </button>
          {locationOpen && (
            <div className="px-4 py-3 bg-secondary/20 border-t border-border">
              <LocationEditor />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ── Variant C: Activity Feed Dashboard ─────────────────────

function VariantC({ target }: { target: typeof mockTargets[0] }) {
  const [channelId, setChannelId] = useState(target.channelId)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [drawerUrl, setDrawerUrl] = useState<UrlRecord | null>(null)
  const [drawerSection, setDrawerSection] = useState<'filters' | 'location'>('filters')
  const [showAddForm, setShowAddForm] = useState(false)

  const openDrawer = (url: UrlRecord, section: 'filters' | 'location') => {
    setDrawerUrl(url); setDrawerSection(section); setDrawerOpen(true)
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Quota Banner */}
      <div className={cn(
        'px-4 sm:px-6 py-2 flex items-center justify-between text-xs sm:text-sm',
        mockQuota.used >= mockQuota.limit ? 'bg-destructive text-destructive-foreground' :
        mockQuota.used / mockQuota.limit >= 0.8 ? 'bg-yellow-50 text-yellow-800 border-b border-yellow-200' :
        'bg-green-50 text-green-800 border-b border-green-200'
      )}>
        <div className="flex items-center gap-2">
          <Bell className="w-3.5 h-3.5 shrink-0" aria-hidden="true" />
          <span>
            <strong>{mockQuota.used}/{mockQuota.limit}</strong> notifications used this month
            {mockQuota.used / mockQuota.limit >= 0.8 && <span> — resets {mockQuota.periodEnd}</span>}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="h-1.5 w-16 sm:w-24 bg-white/40 rounded-full overflow-hidden">
            <div className={cn('h-full rounded-full', mockQuota.used >= mockQuota.limit ? 'bg-white' : mockQuota.used / mockQuota.limit >= 0.8 ? 'bg-yellow-400' : 'bg-green-500')}
              style={{ width: `${(mockQuota.used / mockQuota.limit) * 100}%` }} />
          </div>
          <span className="text-xs opacity-70">{mockUrlQuota.used}/{mockUrlQuota.limit} URLs</span>
        </div>
      </div>

      {/* Header */}
      <div className="border-b border-border px-4 sm:px-6 py-3">
        <div className="flex items-center justify-between max-w-3xl mx-auto">
          <div className="flex items-center gap-3">
            <Target className="w-5 h-5 text-primary" aria-hidden="true" />
            <div>
              <h1 className="text-base font-semibold text-foreground">{target.name}</h1>
              <p className="text-xs text-muted-foreground">
                {target.urls.filter(u => u.isActive).length} active · {target.urls.length} total
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Select value={channelId} onValueChange={(v) => setChannelId(v)}>
              <SelectTrigger className="h-8 text-xs gap-1 w-[150px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {mockChannels.map(ch => {
                  const Icon = providerIcons[ch.provider] || Bell
                  return (
                    <SelectItem key={ch.id} value={ch.id} className="text-xs">
                      <span className="flex items-center gap-2">
                        <Icon className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
                        <span className="flex-1 min-w-0 truncate">{ch.name}</span>
                        <Badge className={cn(
                          'border-0 text-xs px-1 py-0 shrink-0',
                          ch.connected ? 'bg-green-100 text-green-800' : 'bg-muted text-muted-foreground'
                        )}>
                          {ch.connected ? '✓' : '✗'}
                        </Badge>
                      </span>
                    </SelectItem>
                  )
                })}
              </SelectContent>
            </Select>
            <Button size="sm" onClick={() => setShowAddForm(true)}>
              <Plus className="w-4 h-4 mr-1" aria-hidden="true" /> Add URL
            </Button>
          </div>
        </div>
      </div>

      {/* Feed */}
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-4 space-y-1">
        {target.urls.length === 0 && (
          <div className="text-center py-16">
            <Globe className="w-10 h-10 mx-auto mb-3 text-muted-foreground/40" aria-hidden="true" />
            <p className="font-medium text-foreground">No URLs yet</p>
            <p className="text-sm text-muted-foreground mb-4">Start monitoring classifieds in seconds.</p>
            <Button onClick={() => setShowAddForm(true)}><Plus className="w-4 h-4 mr-1" aria-hidden="true" /> Add your first URL</Button>
          </div>
        )}

        {/* Add URL inline */}
        {showAddForm && (
          <div className="p-4 bg-card border border-border rounded-lg mb-4 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium">New URL</h3>
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setShowAddForm(false)}>
                <X className="w-3.5 h-3.5" aria-hidden="true" />
              </Button>
            </div>
            <div className="flex gap-2">
              <Input placeholder="https://olx.pl/..." className="flex-1" />
              <Input placeholder="Name" className="w-36" />
            </div>
            <Button size="sm"><Plus className="w-3.5 h-3.5 mr-1" aria-hidden="true" /> Add</Button>
          </div>
        )}

        {target.urls.map((url, idx) => (
          <div key={url.id}>
            {idx > 0 && <hr className="border-border mx-2" />}
            <div className={cn('py-3 px-2 rounded-lg transition-colors group', url.isActive ? 'hover:bg-secondary/30' : 'opacity-60')}>
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    {url.isActive
                      ? <Wifi className="w-3.5 h-3.5 text-green-500 shrink-0" aria-hidden="true" />
                      : <WifiOff className="w-3.5 h-3.5 text-gray-300 shrink-0" aria-hidden="true" />
                    }
                    <h3 className="text-sm font-medium text-foreground truncate">{url.name}</h3>
                    <span className="text-xs text-muted-foreground hidden sm:inline truncate">{url.url}</span>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground ml-5.5">
                    <span className="flex items-center gap-1"><Clock className="w-3 h-3" aria-hidden="true" />{url.lastChecked}</span>
                    {url.offersToday > 0 && <span className="text-green-600 font-medium">{url.offersToday} new</span>}
                    {url.filterCount > 0 && <span>{url.filterCount} filters</span>}
                    {url.showLocationMap && <span>📍 Location on</span>}
                  </div>
                </div>
                <div className="flex items-center gap-1 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity lg:opacity-60 lg:hover:opacity-100">
                  <Button variant="ghost" size="icon" className="h-7 w-7" aria-label="Toggle">
                    {url.isActive ? <Pause className="w-3.5 h-3.5" aria-hidden="true" /> : <Play className="w-3.5 h-3.5" aria-hidden="true" />}
                  </Button>
                  <Button variant="ghost" size="icon" className="h-7 w-7" aria-label="Filters"
                    onClick={() => openDrawer(url, 'filters')}>
                    <Filter className="w-3.5 h-3.5" aria-hidden="true" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-7 w-7" aria-label="Location"
                    onClick={() => openDrawer(url, 'location')}>
                    <MapPin className="w-3.5 h-3.5" aria-hidden="true" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive" aria-label="Delete">
                    <Trash2 className="w-3.5 h-3.5" aria-hidden="true" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Drawer */}
      {drawerOpen && drawerUrl && (
        <>
          <div className="fixed inset-0 bg-black/20 z-30" onClick={() => setDrawerOpen(false)} />
          <div className="fixed right-0 top-0 bottom-0 w-full sm:w-96 bg-card border-l border-border z-40 shadow-xl flex flex-col">
            <div className="flex items-center justify-between px-4 py-3 border-b border-border shrink-0">
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setDrawerOpen(false)}>
                  <X className="w-4 h-4" aria-hidden="true" />
                </Button>
                <div>
                  <p className="text-sm font-medium text-foreground">{drawerUrl.name}</p>
                  <p className="text-xs text-muted-foreground capitalize">{drawerSection}</p>
                </div>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              {drawerSection === 'filters' && <FilterEditor />}
              {drawerSection === 'location' && <LocationEditor />}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

// ── Shared Editors ─────────────────────────────────────────

function FilterEditor() {
  const [groups, setGroups] = useState<RuleGroup[]>(mockFilterGroups)
  const [snapshot, setSnapshot] = useState(() => JSON.stringify(groups))
  const [status, setStatus] = useState<'idle' | 'applied' | 'fading'>('idle')
  const timerRef = useRef<ReturnType<typeof setTimeout>>(undefined)

  const isDirty = JSON.stringify(groups) !== snapshot
  const totalRules = groups.reduce((a, g) => a + g.rules.length, 0)

  const handleApply = () => {
    setSnapshot(JSON.stringify(groups))
    setStatus('applied')
    clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => {
      setStatus('fading')
      setTimeout(() => setStatus('idle'), 300)
    }, 2000)
  }

  const addRule = (gIdx: number) => {
    setGroups(prev => prev.map((g, i) => i !== gIdx ? g : {
      ...g,
      rules: [...g.rules, { field: 'title', operator: 'contains', value: '', caseSensitive: false }],
    }))
  }

  const removeRule = (gIdx: number, rIdx: number) => {
    setGroups(prev => prev.map((g, i) => i !== gIdx ? g : { ...g, rules: g.rules.filter((_, j) => j !== rIdx) }))
  }

  const updateRule = (gIdx: number, rIdx: number, field: string, val: string) => {
    setGroups(prev => prev.map((g, i) => i !== gIdx ? g : {
      ...g,
      rules: g.rules.map((r, j) => j !== rIdx ? r : { ...r, [field]: val }),
    }))
  }

  const addGroup = () => {
    setGroups(prev => [...prev, { logic: 'and', rules: [{ field: 'title', operator: 'contains', value: '', caseSensitive: false }] }])
  }

  return (
    <div>
      <div className="space-y-3">
        <div className="text-xs text-muted-foreground">
          {totalRules} rule{totalRules !== 1 ? 's' : ''} · {groups.length} group{groups.length !== 1 ? 's' : ''}
        </div>

        {groups.map((group, gIdx) => (
          <div key={gIdx} className="bg-secondary/30 rounded-lg overflow-hidden">
            <div className="flex items-center justify-between px-2.5 py-1.5">
              <span className="text-xs font-medium text-muted-foreground">
                Group {gIdx + 1} <span className="text-muted-foreground/50">(AND)</span>
              </span>
              {groups.length > 1 && (
                <button onClick={() => setGroups(groups.filter((_, i) => i !== gIdx))}
                  className="p-0.5 rounded text-muted-foreground/40 hover:text-destructive hover:bg-destructive/10 transition-colors"
                  aria-label={`Delete group ${gIdx + 1}`}>
                  <X className="w-3 h-3" aria-hidden="true" />
                </button>
              )}
            </div>

            <div className="px-2.5 pb-2 space-y-1">
              {group.rules.map((rule, rIdx) => (
                <div key={rIdx} className="flex items-center gap-1.5">
                  <Select defaultValue={rule.field} onValueChange={(v) => updateRule(gIdx, rIdx, 'field', v)}>
                    <SelectTrigger className="w-[80px] h-7 text-xs px-2 gap-1 [&>svg]:w-3 [&>svg]:h-3 [&>svg]:shrink-0">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="title">Title</SelectItem>
                      <SelectItem value="price">Price</SelectItem>
                      <SelectItem value="description">Desc.</SelectItem>
                      <SelectItem value="location">Loc.</SelectItem>
                    </SelectContent>
                  </Select>

                  <Select defaultValue={rule.operator} onValueChange={(v) => updateRule(gIdx, rIdx, 'operator', v)}>
                    <SelectTrigger className="w-[88px] h-7 text-xs px-2 gap-1 [&>svg]:w-3 [&>svg]:h-3 [&>svg]:shrink-0">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="contains">Contains</SelectItem>
                      <SelectItem value="not_contains">Excludes</SelectItem>
                      <SelectItem value="equals">Equals</SelectItem>
                      <SelectItem value="less_than">Under</SelectItem>
                      <SelectItem value="greater_than">Over</SelectItem>
                    </SelectContent>
                  </Select>

                  <Input defaultValue={rule.value} className="flex-1 min-w-0 h-7 text-xs" placeholder="Value"
                    onChange={(e) => updateRule(gIdx, rIdx, 'value', e.target.value)} />

                  {group.rules.length > 1 && (
                    <button onClick={() => removeRule(gIdx, rIdx)}
                      className="p-0.5 rounded text-muted-foreground/30 hover:text-destructive hover:bg-destructive/10 transition-colors shrink-0"
                      aria-label="Delete rule">
                      <X className="w-3 h-3" aria-hidden="true" />
                    </button>
                  )}
                </div>
              ))}

              <button onClick={() => addRule(gIdx)}
                className="flex items-center gap-1 text-xs text-primary/60 hover:text-primary py-1 transition-colors">
                <Plus className="w-3 h-3" aria-hidden="true" /> Add rule
              </button>
            </div>
          </div>
        ))}

        <button onClick={addGroup}
          className="w-full flex items-center justify-center gap-1.5 text-xs text-muted-foreground hover:text-foreground py-2 border border-dashed border-border/60 hover:border-border rounded-lg transition-colors">
          <Plus className="w-3 h-3" aria-hidden="true" /> Add group (OR)
        </button>
      </div>

      {/* Apply bar */}
      {isDirty && status === 'idle' && (
        <div className="sticky bottom-0 -mx-3 px-3 py-2.5 bg-card border-t border-border mt-3 flex items-center justify-between z-10">
          <span className="text-xs flex items-center gap-1.5 text-yellow-700">
            <span className="w-1.5 h-1.5 rounded-full bg-yellow-400" />
            Unsaved changes
          </span>
          <Button size="sm" className="h-7 text-xs" onClick={handleApply}>
            Apply
          </Button>
        </div>
      )}
      {status === 'applied' && (
        <div className="sticky bottom-0 -mx-3 px-3 py-2.5 bg-card border-t border-border mt-3 flex items-center justify-between z-10 transition-opacity duration-300">
          <span className="text-xs flex items-center gap-1.5 text-green-700">
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12" />
            </svg>
            Applied
          </span>
          <span className="text-xs text-muted-foreground">{totalRules} rule{totalRules !== 1 ? 's' : ''}</span>
        </div>
      )}
    </div>
  )
}

function LocationEditor() {
  const [enabled, setEnabled] = useState(true)
  const [waypoints, setWaypoints] = useState([
    { name: 'Warsaw Center', lat: 52.2297, lon: 21.0122 },
    { name: 'Krakow Old Town', lat: 50.0614, lon: 19.9366 },
  ])
  const [snapshot, setSnapshot] = useState(() =>
    JSON.stringify({ enabled: true, waypoints: [{ name: 'Warsaw Center', lat: 52.2297, lon: 21.0122 }, { name: 'Krakow Old Town', lat: 50.0614, lon: 19.9366 }] })
  )
  const [status, setStatus] = useState<'idle' | 'applied' | 'fading'>('idle')
  const timerRef = useRef<ReturnType<typeof setTimeout>>(undefined)

  const current = JSON.stringify({ enabled, waypoints })
  const isDirty = current !== snapshot

  const handleApply = () => {
    setSnapshot(current)
    setStatus('applied')
    clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => {
      setStatus('fading')
      setTimeout(() => setStatus('idle'), 300)
    }, 2000)
  }

  return (
    <div>
      <div className="space-y-3">
        <div className="flex items-center justify-between p-2.5 bg-secondary/30 rounded-lg">
          <div>
            <Label className="text-sm font-medium">Include location</Label>
            <p className="text-xs text-muted-foreground">Adds map link and distance to alerts</p>
          </div>
          <Switch checked={enabled} onCheckedChange={setEnabled} />
        </div>
        {enabled && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label className="text-xs text-muted-foreground">Reference points</Label>
              <button onClick={() => setWaypoints(prev => [...prev, { name: '', lat: 0, lon: 0 }])}
                className="flex items-center gap-1 text-xs text-primary/60 hover:text-primary transition-colors">
                <Plus className="w-3 h-3" aria-hidden="true" /> Add
              </button>
            </div>
            {waypoints.map((wp, idx) => (
              <div key={idx} className="bg-secondary/30 rounded-lg p-2.5 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-muted-foreground">Waypoint {idx + 1}</span>
                  {waypoints.length > 1 && (
                    <button onClick={() => setWaypoints(prev => prev.filter((_, i) => i !== idx))}
                      className="p-0.5 rounded text-muted-foreground/40 hover:text-destructive hover:bg-destructive/10 transition-colors"
                      aria-label="Remove waypoint">
                      <X className="w-3 h-3" aria-hidden="true" />
                    </button>
                  )}
                </div>
                <Input defaultValue={wp.name} placeholder="Name" className="h-7 text-xs"
                  onChange={(e) => setWaypoints(prev => prev.map((p, i) => i !== idx ? p : { ...p, name: e.target.value }))} />
                <div className="flex gap-1.5">
                  <Input defaultValue={String(wp.lat)} placeholder="Latitude" className="h-7 text-xs flex-1"
                    onChange={(e) => setWaypoints(prev => prev.map((p, i) => i !== idx ? p : { ...p, lat: Number(e.target.value) || 0 }))} />
                  <Input defaultValue={String(wp.lon)} placeholder="Longitude" className="h-7 text-xs flex-1"
                    onChange={(e) => setWaypoints(prev => prev.map((p, i) => i !== idx ? p : { ...p, lon: Number(e.target.value) || 0 }))} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Apply bar */}
      {isDirty && status === 'idle' && (
        <div className="sticky bottom-0 -mx-3 px-3 py-2.5 bg-card border-t border-border mt-3 flex items-center justify-between z-10">
          <span className="text-xs flex items-center gap-1.5 text-yellow-700">
            <span className="w-1.5 h-1.5 rounded-full bg-yellow-400" />
            Unsaved changes
          </span>
          <Button size="sm" className="h-7 text-xs" onClick={handleApply}>
            Apply
          </Button>
        </div>
      )}
      {status === 'applied' && (
        <div className="sticky bottom-0 -mx-3 px-3 py-2.5 bg-card border-t border-border mt-3 flex items-center justify-between z-10 transition-opacity duration-300">
          <span className="text-xs flex items-center gap-1.5 text-green-700">
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12" />
            </svg>
            Applied
          </span>
          <span className="text-xs text-muted-foreground">{waypoints.length} point{waypoints.length !== 1 ? 's' : ''}</span>
        </div>
      )}
    </div>
  )
}

// ── Switcher ───────────────────────────────────────────────

const variantLabels: Record<ViewVariant, string> = {
  A: 'Three-Panel Split',
  B: 'Sidebar Dashboard',
  C: 'Activity Feed',
}

const variantIcons: Record<ViewVariant, React.ComponentType<{ className?: string }>> = {
  A: Columns,
  B: LayoutDashboard,
  C: LayoutList,
}

function PrototypeSwitcher({ current, setVariant }: { current: ViewVariant; setVariant: (v: ViewVariant) => void }) {
  const variants: ViewVariant[] = ['A', 'B', 'C']
  const currentIdx = variants.indexOf(current)

  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50">
      <div className="flex items-center gap-2 bg-foreground text-background rounded-full px-3 py-2 shadow-lg">
        <button
          onClick={() => setVariant(variants[(currentIdx - 1 + 3) % 3])}
          className="p-1.5 rounded-full hover:bg-white/20 transition-colors"
          aria-label="Previous variant"
        >
          <ChevronLeft className="w-4 h-4" aria-hidden="true" />
        </button>

        <div className="flex items-center gap-1">
          {variants.map((v) => {
            const Icon = variantIcons[v]
            return (
              <button
                key={v}
                onClick={() => setVariant(v)}
                className={cn(
                  'flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all',
                  current === v ? 'bg-white text-foreground shadow-sm' : 'text-white/70 hover:text-white hover:bg-white/10'
                )}
              >
                <Icon className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">{variantLabels[v]}</span>
                <span className="sm:hidden">{v}</span>
              </button>
            )
          })}
        </div>

        <button
          onClick={() => setVariant(variants[(currentIdx + 1) % 3])}
          className="p-1.5 rounded-full hover:bg-white/20 transition-colors"
          aria-label="Next variant"
        >
          <ChevronRight className="w-4 h-4" aria-hidden="true" />
        </button>
      </div>
    </div>
  )
}
