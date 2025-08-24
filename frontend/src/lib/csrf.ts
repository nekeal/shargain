import {shargainPublicApiAuthGetCsrfToken} from "@/lib/api";

export const refreshCsrfToken = async (): Promise<string | null> => {
    try {
        const response = await shargainPublicApiAuthGetCsrfToken();
        const newCsrfToken = response.data.csrfToken || '';
        sessionStorage.setItem('csrfToken', newCsrfToken);
        return newCsrfToken;
    } catch (error) {
        console.error('Failed to fetch new CSRF token:', error);
        return null;
    }
};
