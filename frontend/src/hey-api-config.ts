import type { CreateClientConfig } from "./lib/api/client";

export const createClientConfig: CreateClientConfig = (config) => ({
  ...config,
  credentials: 'include',
    baseUrl: import.meta.env.VITE_API_URL
});
