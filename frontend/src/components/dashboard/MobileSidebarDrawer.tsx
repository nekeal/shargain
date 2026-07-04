"use client"

import * as DialogPrimitive from "@radix-ui/react-dialog"
import { Target, X } from "lucide-react"
import DashboardSidebar from "./dashboard-sidebar2"
import type { OfferMonitor } from "@/types/dashboard"
import type { TargetSummaryResponse } from "@/lib/api/types.gen"

interface MobileSidebarDrawerProps {
  isOpen: boolean
  onClose: () => void
  offerMonitor: OfferMonitor
  targets?: Array<TargetSummaryResponse>
  selectedTargetId?: number
  onSelectTarget?: (targetId: number) => void
}

export function MobileSidebarDrawer({
  isOpen,
  onClose,
  offerMonitor,
  targets,
  selectedTargetId,
  onSelectTarget,
}: MobileSidebarDrawerProps) {
  return (
    <DialogPrimitive.Root open={isOpen} onOpenChange={onClose}>
      <DialogPrimitive.Portal>
        <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-black/50 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <DialogPrimitive.Content
          className="
            fixed bottom-0 left-0 right-0 top-auto z-50 
            h-[85dvh] max-h-[85dvh] 
            sm:max-w-[360px] sm:mx-auto sm:rounded-tl-2xl sm:rounded-tr-2xl 
            animate-slide-in-from-bottom 
            motion-reduce:animate-none 
            border-t border-l border-r border-border 
            bg-background 
            data-[state=open]:animate-in 
            data-[state=closed]:animate-out 
            data-[state=closed]:slide-out-to-bottom 
            data-[state=open]:slide-in-from-bottom 
            duration-300
            pb-safe
          "
        >
          <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-border sticky top-0 bg-background/95 backdrop-blur-sm z-10 pt-safe">
              <div className="flex items-center gap-2">
                <Target className="w-5 h-5 text-primary" aria-hidden="true" />
                <span className="text-base font-medium">{offerMonitor.name}</span>
              </div>
              <DialogPrimitive.Close
                className="ring-offset-background focus:ring-ring data-[state=open]:bg-accent data-[state=open]:text-muted-foreground absolute top-4 right-4 rounded-xs opacity-70 transition-opacity hover:opacity-100 focus:ring-2 focus:ring-offset-2 focus:outline-hidden disabled:pointer-events-none [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4 p-2"
              >
                <X className="w-5 h-5" />
                <span className="sr-only">Close</span>
              </DialogPrimitive.Close>
            </div>
            
            {/* Content */}
            <div className="flex-1 overflow-y-auto p-4 sm:p-0 pb-safe">
              <DashboardSidebar
                offerMonitor={offerMonitor}
                targets={targets}
                selectedTargetId={selectedTargetId}
                onSelectTarget={onSelectTarget}
              />
            </div>
          </div>
        </DialogPrimitive.Content>
      </DialogPrimitive.Portal>
    </DialogPrimitive.Root>
  )
}