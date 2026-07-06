"use client"

import { createContext, useContext, useEffect, useState } from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import type { OfferMonitor } from "@/types/dashboard"
import type { TargetSummaryResponse } from "@/lib/api/types.gen"
import { getQuotaStatus, listNotificationConfigs } from "@/lib/api/sdk.gen"

interface DashboardContextValue {
  quotaStatus: {
    data: {
      quotas: Array<{
        slug: string
        targetId: number
        used: number
        limit: number
        periodEnd?: string
      }>
    }
  } | undefined
  notificationConfigs: {
    data: {
      configs: Array<{
        id: number
        name?: string
      }>
    }
  } | undefined
  isQuotaLoading: boolean
  isNotificationConfigsLoading: boolean
  refetchQuota: () => void
  refetchNotificationConfigs: () => void
}

const DashboardContext = createContext<DashboardContextValue | null>(null)

export function useDashboardContext(): DashboardContextValue {
  const context = useContext(DashboardContext)
  if (!context) {
    throw new Error("useDashboardContext must be used within a DashboardProvider")
  }
  return context
}

interface DashboardProviderProps {
  children: React.ReactNode
  offerMonitor: OfferMonitor
  targets?: Array<TargetSummaryResponse>
}

export function DashboardProvider({ children, offerMonitor, targets }: DashboardProviderProps) {
  const queryClient = useQueryClient()
  const [refetchTrigger, setRefetchTrigger] = useState(0)

  const { data: quotaStatus, isLoading: isQuotaLoading, refetch: refetchQuota } = useQuery({
    queryKey: ["quotaStatus", refetchTrigger, offerMonitor.id],
    queryFn: () => getQuotaStatus(),
    staleTime: 30_000,
  })

  const { data: notificationConfigs, isLoading: isNotificationConfigsLoading, refetch: refetchNotificationConfigs } = useQuery({
    queryKey: ["notificationConfigs", refetchTrigger],
    queryFn: () => listNotificationConfigs(),
    staleTime: 30_000,
  })

  // Invalidate quota when target changes
  useEffect(() => {
    setRefetchTrigger((prev) => prev + 1)
  }, [offerMonitor.id])

  const handleRefetchQuota = () => {
    queryClient.invalidateQueries({ queryKey: ["quotaStatus"] })
  }

  const handleRefetchNotificationConfigs = () => {
    queryClient.invalidateQueries({ queryKey: ["notificationConfigs"] })
  }

  return (
    <DashboardContext.Provider
      value={{
        quotaStatus,
        notificationConfigs,
        isQuotaLoading,
        isNotificationConfigsLoading,
        refetchQuota: handleRefetchQuota,
        refetchNotificationConfigs: handleRefetchNotificationConfigs,
      }}
    >
      {children}
    </DashboardContext.Provider>
  )
}