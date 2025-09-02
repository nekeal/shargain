import type { QueryClient } from '@tanstack/react-query';

// Augment the TanStack Router module
declare module '@tanstack/react-router' {
  // Define the shape of the context that will be available on the router
  interface RouterContext {
    queryClient: QueryClient;
    auth: {
      isAuthenticated: boolean;
    };
  }
}
