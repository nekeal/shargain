import { Outlet, createRootRouteWithContext, useMatchRoute } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'
import Header from '../components/Header'
import type { QueryClient } from '@tanstack/react-query'


interface RouterContext {
  queryClient: QueryClient
}

function RootComponent() {
  const matchRoute = useMatchRoute()
  const hideHeader = matchRoute({ to: '/auth' })
  
  return (
    <>
      {!hideHeader && <Header />}
      <Outlet />
      <TanStackRouterDevtools />
    </>
  )
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootComponent,
})
