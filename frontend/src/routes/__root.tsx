import { Outlet, createRootRouteWithContext, useMatchRoute } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'
import Header from '../components/Header'
import { AuthGuard } from '../components/auth/auth-guard'
import type { QueryClient } from '@tanstack/react-query'


interface RouterContext {
  queryClient: QueryClient
}

function RootComponent() {
  const matchRoute = useMatchRoute()
  const isAuthRoute = matchRoute({ to: '/auth/signin' }) || matchRoute({ to: '/auth/signup' })

  return (
    <>
      {isAuthRoute ? (
        <>
          <Outlet />
          <TanStackRouterDevtools />
        </>
      ) : (
        <AuthGuard>
          <>
            <Header />
            <Outlet />
            <TanStackRouterDevtools />
          </>
        </AuthGuard>
      )}
    </>
  )
}

export const Route = createRootRouteWithContext<RouterContext>()({
  component: RootComponent,
})
