export const logout = async (): Promise<boolean> => {
  try {
    // Use the API base URL from environment variables
    const apiUrl = import.meta.env.VITE_API_URL || '';
    const response = await fetch(`${apiUrl}/api/public/auth/logout`, {
      method: "POST",
      credentials: "include",
    })

    if (response.ok) {
      // Redirect to auth page
      window.location.href = "/auth"
      return true
    } else {
      console.error("Logout failed")
      return false
    }
  } catch (error) {
    console.error("Logout error:", error)
    return false
  }
}
