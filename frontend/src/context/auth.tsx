import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createContext, useContext } from "react";
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
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery<User | null>({
    queryKey: ["me"],
    queryFn: () => getMe().then(response => response.data),
    throwOnError: false,
    retry: 0,
  })
  if (isLoading) {
    return <div>Loading...</div>
  }
  const login = (user: User) => {
    queryClient.setQueryData(["me"], user);
  };

  const logout = () => {
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
