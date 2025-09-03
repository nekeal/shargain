import { createContext, useContext, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import type { User } from "@/types/user";
import { getMe } from "@/lib/api/sdk.gen";

export type AuthContextType = {
  isAuthenticated: boolean;
  user: User | null;
  login: (user: User) => void;
  logout: () => void;
};

export const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const queryClient = useQueryClient()
  // @ts-ignore local user is used just to force re-render
  const [localUser, setUser] = useState<User | null>(null);
  const { data, isLoading } = useQuery<User | null>({
    queryKey: ["me"],
    queryFn: () => getMe().then(response => response.data),
    throwOnError: false,
    retry: false,
  })


  if (isLoading) {
    return <div>Loading...</div>
  }
  const login = (user: User) => {
    setUser(user) // << < this is only to force re-render. See https://github.com/TanStack/router/issues/2072
    queryClient.setQueryData(["me"], user);
  };

  const logout = () => {
    setUser(null)
    queryClient.setQueryData(["me"], null);
  };

  return (
    <AuthContext
      value={{
        isAuthenticated: !!data,
        user: data || null,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
