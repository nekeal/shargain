import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createContext, useContext, useEffect, useState } from "react";
import type { User } from "@/types/user";
import { getMe } from "@/lib/api/sdk.gen";
import { set } from "zod";

export type AuthContextType = {
  isAuthenticated: boolean;
  user: User | null;
  login: (user: User) => void;
  logout: () => void;
};

export const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const queryClient = useQueryClient();
  const [user, setUser] = useState<User | null>(null);
  // const [isLoading, setIsLoading] = useState(true);
  const { data, isLoading } = useQuery<User | null>({
    queryKey: ["me"],
    queryFn: () => getMe().then(response => response.data),
    throwOnError: false,
    retry: 1,
  })

  console.log("RENDER PROVIDER", data)
  if (isLoading) {
    return <div>Loading...</div>
  }
  const login = (user: User) => {
    setUser(user)
    queryClient.setQueryData(["me"], user);
  };

  const logout = () => {
    // setUser(null)
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
